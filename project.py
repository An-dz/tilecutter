# TileCutter Project Module

import logging, os, sys
import numpy
import wx
import config
from environment import getenvvar
from tc import Paths
config = config.Config()
paths = Paths()

# Old project needs to be kept to ensure compatibility with old .tcp files using pickle
# handler in load to check kind of file and use the correct module type
# but it'll always convert it into the new format for use by the program

# Image should store:
# Last path entered
# Path of current image
# Image itself (cached)
# As user enters a path in the box, it updates the active image, only when the path points to a valid
# file should the current image path be set, and the image loaded from file into the cache
# File validity is measured relative to the current project save location

# project[view][season][frame][image][xdim][ydim][zdim]
# view = NSEW, 0,1,2,3 - array - controlled by global enable
# season = summer/snow/autumn/winter/spring, 0,1,2,3,4 - array - controlled by global bool enable
# frame=0,++ - array - controlled by global number of frames variable
# image=back/front, 0,1 - array - controlled by global bool enable


class Project(object):
    """New Model containing all information about a project."""

    def __init__(self, parent=None, load=None, save_location=None, saved=False):
        """Initialise this project, and set default values"""
        self.parent = parent

        # internals is used to store things which shouldn't be saved, e.g. image data, save path etc.
        self.internals = {
            "images": self.init_image_array(),
            "activeimage": {
                "direction": 0,
                "season": 0,
                "frame": 0,
                "layer": 0,
            },
            "files": {
                "saved": saved,
                "save_location": "",
            },
            "hash": 0,
        }

        if self.save_location(save_location, validate=True):
            self.internals["files"]["save_location"] = save_location
        else:
            # Either no save location specified or the one passed in is invalid, use default
            self.internals["files"]["save_location"] = self.init_save_location()

        # defaults defines default values for all project properties
        self.defaults = {
            # project[view][season][frame][layer][xdim][ydim][zdim]
            "images": self.init_image_array(),
            "transparency": True,
            "dims": {
                "x": 1,
                "y": 1,
                "z": 1,
                "paksize": int(config.default_paksize),
                "directions": 1,
                "frames": 1,
                "seasons": {
                    "snow":   0,
                    "autumn": 0,
                    "winter": 0,
                    "spring": 0,
                },
                "frontimage": 0,
            },
            "files": {
                "datfile_location": "output.dat",
                "datfile_write": True,
                "pngfile_location": "output.png",
                "pakfile_location": "",
            },
            "dat": {
                "dat_lump": "Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100",
            },
        }

        # validators defines validation functions for project properties which can be used when loading files to ensure valid data
        # ALL items in validators must be either dicts (implying subkeys) or functions (implying keys to be validated)
        self.validators = {
            "images": self.image_array,
            "transparency": self.transparency,
            "dims": {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "paksize": self.paksize,
                "directions": self.directions,
                "frames": self.frames,
                "seasons": {
                    "snow":   self.seasons,
                    "autumn": self.seasons,
                    "winter": self.seasons,
                    "spring": self.seasons,
                },
                "frontimage": self.frontimage,
            },
            "files": {
                "datfile_location": self.datfile_location,
                "datfile_write":    self.datfile_write,
                "pngfile_location": self.pngfile_location,
                "pakfile_location": self.pakfile_location,
            },
            "dat": {
                "dat_lump": self.dat_lump,
            },
        }

        if load is None:
            # Brand new project
            self.props = self.defaults
        else:
            if "winter" in load["dims"]:
                logging.debug("Old 'winter' value found replaced with 'seasons.snow'")
                load["dims"]["seasons"] = {"snow": load["dims"].pop("winter")}

            # Loading project from potential props dict specified (needs validation)
            self.props = self.load_dict(load, self.validators, self.defaults)

        # Set initial hash value to indicate that the project is unchanged (either having just been loaded in, or being brand new)
        self.update_hash()
        self.colourConversionTables()
        self.reload_active_image()

    def __getitem__(self, key):
        return self.props["images"][key]

    def colourConversionTables(self):
        night = 4
        light_level = 0
        self.RG_night_multiplier = (0.75 ** night) * ((light_level + 8.0) / 8.0)
        self.B_night_multiplier  = (0.83 ** night) * ((light_level + 8.0) / 8.0)

        self.special_colours = {
            # Dark windows, lit yellowish at night
            0x57656F: (0xD3, 0xC3, 0x80),
            # Lighter windows, lit blueish at night
            0x7F9BF1: (0x80, 0xC3, 0xD3),
            # Yellow light
            0xFFFF53: (0xFF, 0xFF, 0x53),
            # Red light
            0xFF211D: (0xFF, 0x21, 0x1D),
            # Green light
            0x01DD01: (0x01, 0xDD, 0x01),
            # Non-darkening grey 1 (menus)
            0x6B6B6B: (0x6B, 0x6B, 0x6B),
            # Non-darkening grey 2 (menus)
            0x9B9B9B: (0x9B, 0x9B, 0x9B),
            # non-darkening grey 3 (menus)
            0xB3B3B3: (0xB3, 0xB3, 0xB3),
            # Non-darkening grey 4 (menus)
            0xC9C9C9: (0xC9, 0xC9, 0xC9),
            # Non-darkening grey 5 (menus)
            0xDFDFDF: (0xDF, 0xDF, 0xDF),
            # Nearly white light at day, yellowish light at night
            0xE3E3FF: (0xFF, 0xFF, 0xE3),
            # Windows, lit yellow
            0xC1B1D1: (0xD3, 0xC3, 0x80),
            # Windows, lit yellow
            0x4D4D4D: (0xD3, 0xC3, 0x80),
            # purple light for signals
            0xE100E1: (0xE1, 0x00, 0xE1),
            # blue light
            0x0101FF: (0x01, 0x01, 0xFF),
        }

        self.player_colours = {
            # primary player colour
            0x244B67: (0x24, 0x4B, 0x67),
            0x395E7C: (0x24, 0x4B, 0x67),
            0x4C7191: (0x24, 0x4B, 0x67),
            0x6084A7: (0x24, 0x4B, 0x67),
            0x7497BD: (0x24, 0x4B, 0x67),
            0x88ABD3: (0x24, 0x4B, 0x67),
            0x9CBEE9: (0x24, 0x4B, 0x67),
            0xB0D2FF: (0x24, 0x4B, 0x67),
            # secondary player colour
            0x7B5803: (0x7B, 0x58, 0x03),
            0x8E6F04: (0x7B, 0x58, 0x03),
            0xA18605: (0x7B, 0x58, 0x03),
            0xB49D07: (0x7B, 0x58, 0x03),
            0xC6B408: (0x7B, 0x58, 0x03),
            0xD9CB0A: (0x7B, 0x58, 0x03),
            0xECE20B: (0x7B, 0x58, 0x03),
            0xFFF90D: (0x7B, 0x58, 0x03),
        }

        for key, _value in self.special_colours.items():
            self.player_colours[key] = (0xFF, 0x00, 0x00)

    def load_dict(self, loaded, validators, defaults):
        """Load a dict of stuff from config, may be called recursively"""
        # This function will alter the current project's representation through the standard access methods
        # It also keeps track of all changes and will eventually return a dict which will match the internal state of the project
        props = {}

        for k, v in list(validators.items()):
            logging.debug("Processing node with key value: %s" % k)
            if k in loaded:
                # If this is a key, validate value + set if valid
                if callable(v):
                    logging.debug("Callable object in validators dict, this is a node, running validation on data: %s" % loaded[k])
                    if v(loaded[k], validate=True):
                        logging.debug("Validation succeeds, using value: %s from input" % loaded[k])
                        props[k] = loaded[k]
                    else:
                        logging.warn("Validation failed, using value: %s from defaults" % defaults[k])
                        props[k] = defaults[k]
                # If this is a node call function to determine what to set
                elif isinstance(v, type({})):
                    if isinstance(loaded[k], type({})):
                        logging.debug("Dict-type object in both validators and input, recursing to process subset of keys: %s" % repr(loaded[k]))
                        props[k] = self.load_dict(loaded[k], v, defaults[k])
                    else:
                        # Validators defines this to be a dict, but the loaded data for this key isn't a dict - data must be invalid so use defaults
                        logging.warn("Validators defines this value to be a dict, but input data isn't, using defaults values from node: %s" % k)
                        props[k] = defaults[k]
                else:
                    # This should not happen, panic
                    logging.error("Invalid state for load_dict decode, offending data is: %s (type: %s)" % (repr(v), type(v)))
                    raise ValueError
            else:
                logging.warn("Input data does not contain key: %s, using defaults for this node" % k)
                props[k] = defaults[k]

        logging.debug("Done processing this level, returning properties dict: %s" % repr(props))
        return props

    def init_image_array(self):
        """Init a default/empty image array"""
        # project[view][season][frame][image][xdim][ydim][zdim]
        viewarray = []
        for _view in range(4):
            seasonarray = []
            for _season in range(5):
                framearray = []
                for _frame in range(1):
                    imagearray = []
                    for _image in range(2):
                        imdefault = {
                            "path": "",
                            "offset": [0, 0],
                        }
                        imagearray.append(imdefault)
                    framearray.append(imagearray)
                seasonarray.append(framearray)
            viewarray.append(seasonarray)
        return viewarray

    def image_array(self, value=None, validate=False):
        """Get or set the entire image array"""
        # input should be a list containing 4 items
        # Produce a fresh image array to read values into
        fresh_image_array = self.init_image_array()

        if value is not None:
            if isinstance(value, type([])) and len(value) == 4:
                for d, direction in enumerate(value):
                    # Each direction should be a list containing 5 seasons
                    if isinstance(direction, type([])) and len(direction) == 5:
                        for s, season in enumerate(direction):
                            # Each season should contain a variable number of frames (greater than 1) of type list
                            if isinstance(season, type([])) and len(season) >= 1:
                                for f, frame in enumerate(season):
                                    # Each frame should be a list containing 2 items
                                    if isinstance(frame, type([])) and len(frame) == 2:
                                        for l, layer in enumerate(frame):
                                            # Each layer should be a dict containing optional keys
                                            if isinstance(layer, type({})):
                                                if "path" in layer:
                                                    if self.image_path(d, s, f, l, layer["path"], validate=True):
                                                        fresh_image_array[d][s][f][l]["path"] = layer["path"]
                                                    else:
                                                        # non-fatal validation error, just use the default instead
                                                        logging.warn("Validation failed for property 'path' with value: %s, using default instead" % layer["path"])

                                                if "offset" in layer:
                                                    if self.offset(d, s, f, l, layer["offset"], validate=True):
                                                        fresh_image_array[d][s][f][l]["offset"] = layer["path"]
                                                    else:
                                                        # non-fatal validation error, just use the default instead
                                                        logging.warn("Validation failed for property 'offset' with value: %s, using default instead" % layer["offset"])
                                            else:
                                                logging.warn("Validation failed, type of potential layer was incorrect, should've been dict but was: %s" % type(layer))
                                                return False
                                    else:
                                        logging.warn("Validation failed, type or length of potential frame was incorrect, should've been array,2 but was: %s, %s" % (type(frame), len(frame)))
                                        return False
                            else:
                                logging.warn("Validation failed, type or length of potential season was incorrect, should've been array,>1 but was: %s, %s" % (type(season), len(season)))
                                return False
                    else:
                        logging.warn("Validation failed, type or length of potential direction was incorrect, should've been array,2 but was: %s, %s" % (type(direction), len(direction)))
                        return False
            else:
                logging.warn("Validation failed, type of potential image array was incorrect, should've been array but was: %s, %s" % type(value))
                return False

            # If nothing is invalid with the image_array set it and return True
            if not validate:
                self.props["images"] = fresh_image_array
                # Need to reload all images so they reflect any changes
                self.reload_all_images()
                self.on_change()

            return True
        else:
            return self.props["images"]

    def init_save_location(self):
        """Return our initial save location based on platform-specific settings"""
        # Use userprofile on all platforms as default
        if sys.platform == "darwin":
            save_location = os.path.expanduser("~")
        elif sys.platform == "win32":
            save_location = getenvvar("USERPROFILE")
        else:
            save_location = os.path.expanduser("~")

        # Otherwise use location of program
        # Depending on how/when os.path.expanduser can fail this may not be needed but just in case!
        if save_location == "~":
            save_location = self.test_path(self.parent.parent.start_directory)
        else:
            save_location = self.test_path(save_location)

        logging.debug("as: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (
            self.save_location, self.datfile_location, self.pngfile_location, self.pakfile_location))
        return save_location

    def test_path(self, path):
        """Used in project initialisation - Test a file for existence, if it exists add a number and try again"""
        if os.path.exists(os.path.join(path, "new_project.tcp")):
            i = 1
            while True:
                if not os.path.exists(os.path.join(path, "new_project%s.tcp" % i)):
                    return os.path.join(path, "new_project%s.tcp" % i)
                i += 1
        else:
            return os.path.join(path, "new_project.tcp")

    def on_change(self):
        # When something in the project has changed, notify containing app to
        # allow for updating of UI
        if self.parent is not None:
            logging.debug("Root on_change triggered, sending message to App")
            self.parent.project_has_changed()
        else:
            logging.warn("Root on_change triggered but no parent specified, doing nothing")

    #################################################################
    # Functions related to checking whether the project has changed #
    #################################################################
    def has_changed(self):
        """An indication of whether this project has been changed since the last time it was saved"""
        current = self.hash_props()

        if current == self.internals["hash"]:
            logging.debug("Check Project for changes - Project Unchanged")
            return False
        else:
            logging.debug("Check Project for changes - Project Changed")
            return True

    def hash_props(self):
        """Return a hash of the representation of the properties dict for use in comparisons"""
        return hash(repr(self.props))

    def update_hash(self):
        """Set intenals hash to the current hash value"""
        self.internals["hash"] = self.hash_props()
        return True

    #################################################
    # These functions deal with dat file properties #
    #################################################
    def dat_lump(self, value=None, validate=False):
        """Sets or returns a string containing arbitrary .dat file properties"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                if not validate:
                    self.props["dat"]["dat_lump"] = value
                    logging.debug("properties set to %s" % self.props["dat"]["dat_lump"])
                    self.on_change()
                return True
            else:
                logging.warn("type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dat"]["dat_lump"]

    ########################################
    # These functions deal with image data #
    ########################################
    @staticmethod
    def transform_night(x, a):
        a *= x
        return a.clip(0, 255).astype(numpy.uint8)

    @staticmethod
    def transform_special(x, a):
        a = x + ((255 - x) // a)
        return a.clip(0, 255).astype(numpy.uint8)

    @staticmethod
    def transform_map(imgbuf, width, height, specials, R_factor, G_factor, B_factor, transform):
        # Convert to array
        img_array = numpy.ndarray((width, height, 4), dtype=numpy.uint8, buffer=imgbuf)
        # Extract channels
        R = img_array.T[0]
        G = img_array.T[1]
        B = img_array.T[2]
        A = img_array.T[3]

        # Find Special colors
        # First, calculate a unique hash
        colour_hashes = (2**16 * R | 2**8 * G | B)

        # Find inidices of special colors
        special_indices = []
        for special_colour, new_colour in specials.items():
            val_arr = numpy.array(list(new_colour))

            special_indices.append(
                {
                    'mask': numpy.where(numpy.isin(colour_hashes, special_colour, True)),
                    'value': val_arr
                }
            )

        # Apply transform to whole image
        R = transform(R, R_factor)
        G = transform(G, G_factor)
        B = transform(B, B_factor)

        # Replace values where special colors were found
        for idx in special_indices:
            R[idx['mask']] = idx['value'][0]
            G[idx['mask']] = idx['value'][1]
            B[idx['mask']] = idx['value'][2]

        return numpy.array([R,G,B,A]).T.tobytes()

    def active_image_path(self, value=None, validate=False):
        """Set or return the path of the active image"""
        return self.image_path(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
            value,
            validate,
        )

    def image_path(self, d, s, f, l, value=None, validate=False):
        """Set or return the path of the specified image"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                if not validate:
                    self.props["images"][d][s][f][l]["path"] = value
                    logging.debug("For image d:%s, s:%s, f:%s, l:%s set to %s" % (d, s, f, l, self.props["images"][d][s][f][l]["path"]))
                    # This will either load the image (if the path exists) or set a default image if it doesn't
                    self.reload_image(d, s, f, l)
                    self.on_change()

                return True
            else:
                logging.warn("Type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["images"][d][s][f][l]["path"]

    def get_image(self, d, s, f, l):
        """Return a wxImage representation of the specified image"""
        return self.internals["images"][d][s][f][l]["imagedata"]

    def get_active_image(self):
        """Return a wxImage representation of the active image"""
        return self.get_image(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
        )

    def get_bitmap(self, d, s, f, l):
        """Return a wxBitmap representation of the specified image"""
        return self.internals["images"][d][s][f][l]["bitmapdata"]

    def get_active_bitmap(self):
        """Return a wxBitmap representation of the active image"""
        return self.get_bitmap(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
        )

    def get_night_bitmap(self, d, s, f, l):
        """Return a wxBitmap representation of the specified image in night mode"""
        nightbitmap = self.internals["images"][d][s][f][l].get("nightbitmap")

        if nightbitmap is not None:
            return nightbitmap

        bitmap = self.get_bitmap(d, s, f, l)
        imgbuf = bytearray(bitmap.GetWidth() * bitmap.GetHeight() * 4)
        bitmap.CopyToBuffer(imgbuf, wx.BitmapBufferFormat_RGBA)

        imgbuf = self.transform_map(
            imgbuf,
            bitmap.GetWidth(),
            bitmap.GetHeight(),
            self.special_colours,
            self.RG_night_multiplier,
            self.RG_night_multiplier,
            self.B_night_multiplier,
            self.transform_night,
        )

        nightbitmap = wx.Bitmap.FromBufferRGBA(bitmap.GetWidth(), bitmap.GetHeight(), imgbuf)
        self.internals["images"][d][s][f][l]["nightbitmap"] = nightbitmap

        return nightbitmap

    def get_active_night_bitmap(self):
        """Return a wxBitmap representation of the active image in night mode"""
        return self.get_night_bitmap(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
        )

    def get_special_colour_bitmap(self, d, s, f, l):
        """Return a wxBitmap representation of the specified image with special colours in contrast"""
        specialbitmap = self.internals["images"][d][s][f][l].get("specialbitmap")

        if specialbitmap is not None:
            return specialbitmap

        bitmap = self.get_bitmap(d, s, f, l)
        imgbuf = bytearray(bitmap.GetWidth() * bitmap.GetHeight() * 4)
        bitmap.CopyToBuffer(imgbuf, wx.BitmapBufferFormat_RGBA)

        imgbuf = self.transform_map(
            imgbuf,
            bitmap.GetWidth(),
            bitmap.GetHeight(),
            self.player_colours,
            1.25,
            1.25,
            1.25,
            self.transform_special,
        )

        specialbitmap = wx.Bitmap.FromBufferRGBA(bitmap.GetWidth(), bitmap.GetHeight(), imgbuf)
        self.internals["images"][d][s][f][l]["specialbitmap"] = specialbitmap

        return specialbitmap

    def get_active_special_colour_bitmap(self):
        """Return a wxBitmap representation of the active image with special colours in contrast"""
        return self.get_special_colour_bitmap(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
        )

    def remove_special_bitmaps(self, d, s, f, l):
        self.internals["images"][d][s][f][l]["nightbitmap"] = None
        self.internals["images"][d][s][f][l]["specialbitmap"] = None

    def set_all_images(self, path):
        """Set the path for all images to the same path"""
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        self.props["images"][d][s][f][l]["path"] = path
                        self.reload_image(d, s, f, l)
        self.on_change()

    def get_cut_image(self, d, s, f, l, x, y, z):
        """Return cut image fragments based on full coordinate lookup in wxBitmap format, used by output writer"""
        return self.internals["images"][d][s][f][l]["cutimageset"][x][y][z]

    def cut_images(self, cutting_function):
        """Produce cut imagesets for all images in this project"""
        # Can make this work conditionally based on which images are enabled later
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        # Reload the image to obtain most recent version
                        self.reload_image(d, s, f, l)
                        # Call cutting function on image and store data on the internals array
                        # Cutting function by convention takes args: wxbitmap, dims(x,y,z,direction), offset, paksize
                        self.internals["images"][d][s][f][l]["cutimageset"] = cutting_function(
                            self.internals["images"][d][s][f][l]["bitmapdata"],
                            (
                                self.props["dims"]["x"],
                                self.props["dims"]["y"],
                                self.props["dims"]["z"],
                                d,
                            ),
                            self.props["images"][d][s][f][l]["offset"],
                            self.props["dims"]["paksize"],
                            self.props["transparency"],
                        )

    def reload_all_images(self):
        """Reloads all images"""
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        self.remove_special_bitmaps(d, s, f, l)
                        self.reload_image(d, s, f, l)

    def reload_active_image(self):
        """Refresh the active image"""
        d = self.internals["activeimage"]["direction"]
        s = self.internals["activeimage"]["season"]
        f = self.internals["activeimage"]["frame"]
        l = self.internals["activeimage"]["layer"]
        self.remove_special_bitmaps(d, s, f, l)
        return self.reload_image(d, s, f, l)

    def reload_image(self, d, s, f, l):
        """Refresh the specified image, inputs are: direction, season, frame, layer"""
        # If path is valid, use it, otherwise use a blank image/image with error message
        abspath = paths.join_paths(self.internals["files"]["save_location"], self.props["images"][d][s][f][l]["path"])
        # If path is valid, load file
        self.internals["images"][d][s][f][l]["imagedata"] = wx.Image(1, 1)
        if (paths.is_input_file(abspath) and os.path.exists(abspath)):
            self.internals["images"][d][s][f][l]["imagedata"].LoadFile(abspath, wx.BITMAP_TYPE_ANY)
        # If path isn't valid, just leave it as an empty image (or could display an error image?)

        self.internals["images"][d][s][f][l]["bitmapdata"] = wx.Bitmap(self.internals["images"][d][s][f][l]["imagedata"])

    def active_x_offset(self, value=None, validate=False):
        """Get or set the active image's x offset"""
        return self.x_offset(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
            value,
            validate,
        )

    def x_offset(self, d, s, f, l, value=None, validate=False):
        """Directly set or get the X offset of the specified image"""
        if value is not None:
            if value >= 0:
                if not validate:
                    self.props["images"][d][s][f][l]["offset"][0] = value
                    logging.debug("X Offset for image d:%s, s:%s, f:%s, l:%s set to %i" % (d, s, f, l, self.props["images"][d][s][f][l]["offset"][0]))
                    self.on_change()

                return True
            else:
                logging.warn("Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["images"][d][s][f][l]["offset"][0]

    def active_y_offset(self, value=None, validate=False):
        """Get or set the active image's y offset"""
        return self.y_offset(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
            value,
            validate,
        )

    def y_offset(self, d, s, f, l, value=None, validate=False):
        """Directly set or get the Y offset of the specified image"""
        if value is not None:
            if value >= 0:
                if not validate:
                    self.props["images"][d][s][f][l]["offset"][1] = value
                    logging.debug("Y Offset for image d:%s, s:%s, f:%s, l:%s set to %i" % (d, s, f, l, self.props["images"][d][s][f][l]["offset"][1]))
                    self.on_change()

                return True
            else:
                logging.warn("Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["images"][d][s][f][l]["offset"][1]

    def active_offset(self, value=None, validate=False):
        """Set or get the full offset coordinates for the active image"""
        return self.offset(
            self.internals["activeimage"]["direction"],
            self.internals["activeimage"]["season"],
            self.internals["activeimage"]["frame"],
            self.internals["activeimage"]["layer"],
            value,
            validate,
        )

    def offset(self, d, s, f, l, value=None, validate=False):
        """Set or get the full offset coordinates for the specified image"""
        if value is not None:
            # Call with validate enabled to prevent multiple updates/on_change triggers
            if self.x_offset(d, s, f, l, value[0], True) and self.y_offset(d, s, f, l, value[1], True):
                if not validate:
                    self.props["images"][d][s][f][l]["offset"] = [value[0], value[1]]
                    logging.debug("Offset for image d:%s, s:%s, f:%s, l:%s set to %i" % (d, s, f, l, self.props["images"][d][s][f][l]["offset"][1]))
                    self.on_change()

                return True
            else:
                logging.warn("Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["images"][d][s][f][l]["offset"]

    ######################################################################
    # Functions which deal with properties of the currently active image #
    ######################################################################
    def direction(self, value=None, validate=False):
        """Set or query active image's direction"""
        if value is not None:
            if value in [0, 1, 2, 3]:
                if not validate:
                    self.internals["activeimage"]["direction"] = value
                    logging.debug("Active image direction set to %i" % self.internals["activeimage"]["direction"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set active image direction failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["activeimage"]["direction"]

    def season(self, value=None, validate=False):
        """Set or query active image's season"""
        if value is not None:
            if value in range(5):
                if not validate:
                    self.internals["activeimage"]["season"] = value
                    logging.debug("Active image season set to %i" % self.internals["activeimage"]["season"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set active image season failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["activeimage"]["season"]

    def frame(self, value=None, validate=False):
        """Set or query active image's frame"""
        if value is not None:
            if value in range(self.props["dims"]["frames"]):
                if not validate:
                    self.internals["activeimage"]["frame"] = value
                    logging.debug("Active image frame set to %i" % self.internals["activeimage"]["frame"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set active image frame failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["activeimage"]["frame"]

    def layer(self, value=None, validate=False):
        """Set or query active image's layer"""
        if value is not None:
            if value in [0, 1]:
                if not validate:
                    self.internals["activeimage"]["layer"] = value
                    logging.debug("Active image layer set to %i" % self.internals["activeimage"]["layer"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set active image layer failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["activeimage"]["layer"]

    def active_image(self, direction=None, season=None, frame=None, layer=None, validate=False):
        """Set or return the currently active image"""
        if direction is not None and direction != self.internals["activeimage"]["direction"]:
            return self.direction(direction, validate)

        if season is not None and season != self.internals["activeimage"]["season"]:
            return self.season(season, validate)

        if frame is not None and frame != self.internals["activeimage"]["frame"]:
            return self.frame(frame, validate)

        if layer is not None and layer != self.internals["activeimage"]["layer"]:
            return self.layer(layer, validate)

        # Returns dict containing active image's properties
        return self.props["images"][self.internals["activeimage"]["direction"]][self.internals["activeimage"]["season"]][self.internals["activeimage"]["frame"]][self.internals["activeimage"]["layer"]]

    ##################################################################
    # Functions which deal with dimensions properties of the project #
    ##################################################################
    def x(self, value=None, validate=False):
        """Set or return X dimension"""
        if value is not None:
            if value in config.choicelist_dims:
                if not validate:
                    self.props["dims"]["x"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["x"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set X dimension failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["x"]

    def y(self, value=None, validate=False):
        """Set or return Y dimension"""
        if value is not None:
            if value in config.choicelist_dims:
                if not validate:
                    self.props["dims"]["y"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["y"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["y"]

    def z(self, value=None, validate=False):
        """Set or return Z dimension"""
        if value is not None:
            if value in config.choicelist_dims_z:
                if not validate:
                    self.props["dims"]["z"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["z"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["z"]

    def transparency(self, value=None, validate=False):
        if value is not None:
            if value in [True, 1]:
                if not validate:
                    self.props["transparency"] = True
                    logging.debug("Set to %s" % str(self.props["transparency"]))
                    self.on_change()

                return True
            elif value in [False, 0]:
                if not validate:
                    self.props["transparency"] = False
                    logging.debug("Set to %s" % str(self.props["transparency"]))
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set transparency failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["transparency"]

    def paksize(self, value=None, validate=False):
        """Set or return paksize"""
        if value is not None:
            if int(value) in range(16, 32766):
                if not validate:
                    self.props["dims"]["paksize"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["paksize"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set Paksize failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["paksize"]

    def seasons(self, value=None, validate=False, season="snow"):
        """Set or return if a season image is enabled"""
        if value is not None:
            if value in [True, 1]:
                if not validate:
                    self.props["dims"]["seasons"][season] = 1
                    logging.debug("%s set to %i" % (season, self.props["dims"]["seasons"][season]))
                    self.on_change()

                return True
            elif value in [False, 0]:
                if not validate:
                    self.props["dims"]["seasons"][season] = 0
                    logging.debug("%s set to %i" % (season, self.props["dims"]["seasons"][season]))
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set %s failed - Value (%s) outside of acceptable range" % (str(value), season))
                return False
        else:
            return self.props["dims"]["seasons"][season]

    def frontimage(self, value=None, validate=False):
        """Set or return if Front image is enabled"""
        if value is not None:
            if value in [True, 1]:
                if not validate:
                    self.props["dims"]["frontimage"] = 1
                    logging.debug("Set to %i" % self.props["dims"]["frontimage"])
                    self.on_change()

                return True
            elif value in [False, 0]:
                if not validate:
                    self.props["dims"]["frontimage"] = 0
                    logging.debug("Set to %i" % self.props["dims"]["frontimage"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set frontimage failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["frontimage"]

    def frames(self, value=None, validate=False):
        """Query or validate new value for number of frames"""
        if value is not None:
            if value == 1:
                if not validate:
                    self.props["dims"]["frames"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["frames"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set frames failed - value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["frames"]

    def directions(self, value=None, validate=False):
        """Set or return number of direction views (1, 2 or 4)"""
        if value is not None:
            if value in config.choicelist_views:
                if not validate:
                    self.props["dims"]["directions"] = int(value)
                    logging.debug("Set to %i" % self.props["dims"]["directions"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set directions failed - value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["dims"]["directions"]

    ############################################################
    # Functions which deal with file properties of the project #
    ############################################################
    def datfile_location(self, value=None, validate=False):
        """Set or return (relative) path to dat file"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                if not validate:
                    self.props["files"]["datfile_location"] = str(value)
                    logging.debug("Set to %s" % self.props["files"]["datfile_location"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set datfile_location failed - type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["files"]["datfile_location"]

    def datfile_write(self, value=None, validate=False):
        """Set or return if dat file should be written"""
        if value is not None:
            if value in [True, 1]:
                if not validate:
                    self.props["files"]["datfile_write"] = True
                    logging.debug("Set to %s" % self.props["files"]["datfile_write"])
                    self.on_change()

                return True
            elif value in [False, 0]:
                if not validate:
                    self.props["files"]["datfile_write"] = False
                    logging.debug("Set to %s" % self.props["files"]["datfile_write"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set datfile_write failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["files"]["datfile_write"]

    def pngfile_location(self, value=None, validate=False):
        """Set or return (relative) path to png file"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                if not validate:
                    self.props["files"]["pngfile_location"] = str(value)
                    logging.debug("Set to %s" % self.props["files"]["pngfile_location"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set pngfile_location failed - type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["files"]["pngfile_location"]

    def pakfile_location(self, value=None, validate=False):
        """Set or return (relative) path to pak file"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                if not validate:
                    self.props["files"]["pakfile_location"] = str(value)
                    logging.debug("Set to %s" % self.props["files"]["pakfile_location"])
                    self.on_change()

                return True
            else:
                logging.warn("Attempt to set pakfile_location failed - type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.props["files"]["pakfile_location"]

    ############################################################
    # Functions which deal with the save file for the project  #
    # and are saved to the internals set                       #
    # since we don't need to preserve these values when saving #
    ############################################################
    def saved(self, value=None, validate=False):
        """Set or return whether a save path has been set for this project"""
        if value is not None:
            if value in [True, 1]:
                self.internals["files"]["saved"] = True
                logging.debug("Set to %s" % self.internals["files"]["saved"])
                self.on_change()
                return True
            elif value in [False, 0]:
                self.internals["files"]["saved"] = False
                logging.debug("Set to %s" % self.internals["files"]["saved"])
                self.on_change()
                return True
            else:
                logging.warn("Attempt to set project saved status failed - Value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["files"]["saved"]

    def save_location(self, value=None, validate=False):
        """Set or return (absolute) path to project save file location"""
        if value is not None:
            if type(value) in [type(""), type("")]:
                self.internals["files"]["save_location"] = str(value)
                logging.debug("Set to %s" % self.internals["files"]["save_location"])
                self.on_change()
                return True
            else:
                logging.warn("Attempt to set project save_location status failed - type of value (%s) outside of acceptable range" % str(value))
                return False
        else:
            return self.internals["files"]["save_location"]
