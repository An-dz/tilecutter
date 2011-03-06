# coding: UTF-8
#
# TileCutter Project Module
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.


import os, sys
import wx

import logger
debug = logger.Log()
import config
config = config.Config()

from tc import Paths
paths = Paths()

from environment import getenvvar

# New project has method to convert old project into new format
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
# view=NSEW, 0,1,2,3 - array - controlled by global enable
# season=summer/winter, 0,1 - array - controlled by global bool enable
# frame=0,++ - array - controlled by global number of frames variable
# image=back/front, 0,1 - array - controlled by global bool enable


# Main object should have a json() function which removes its images and then returns a json formatted version of itself
# Should also have a pickle() function which does the same for the python representation

class Project(object):
    """New Model containing all information about a project."""
    def __init__(self, parent, load=None):
        """Initialise this project, and set default values"""
        self.parent = parent

        # All properties stored in a single dict which is then read from/written to by access functions
        # All values which can exist in a save file must be defined with defaults here to be read in
        # Dicts are checked recursively for validity based on the properties defined within them

        # For replacement
        # Needs overall method to reload a particular image
        # Concept of active image needs to be tied to an image index which can be passed to main parent object
        #  This can then be used in a call to that object to reload the image, rather than going to a child object
        # Properties for each image:
        #   is_backimage - not kept, property used to look up this image so should be a structural thing at higher level
        #  imagedata - wx.Bitmap
        #  path - string
        #  
        #  offset - coords/array
        #   cutimageset - not kept, generated on the fly by cutting routine and not stored in this object

        # Internals used for stuff which shouldn't be saved, e.g. image data
        self.internals = {
            "images": self.init_image_array(),
            "files": {
                "saved": "False",
                "save_location": self.init_save_location(),
            }
        }
        self.defaults = {
            # project[view][season][frame][layer][xdim][ydim][zdim]
            "images": self.init_image_array(),
            "activeimage": {
                "direction": 0,
                "season": 0,
                "frame": 0,
                "layer": 0,
            },
            "dims": {
                "x": 1,
                "y": 1,
                "z": 1,
                "paksize": int(config.default_paksize),
                "directions": 1,
                "frames": 1,
                "winter": 0,
                "frontimage": 0,
            },
            "files": {
                "datfile_location": u"output.dat",
                "datfile_write": True,
                "pngfile_location": os.path.join(u"images", u"output.png"),
                "pakfile_location": u"",
            },
            "dat": {
                "dat_lump": u"Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100",
            },
        }
        # ALL items in validators must be either dicts (implying subkeys) or functions (implying keys to be validated)
        self.validators = {
            "images": self.validate_image_array,
            "activeimage": {
                "direction": self.direction,
                "season": self.season,
                "frame": self.frame,
                "layer": self.layer,
            },
            "dims": {
                "x": self.x,
                "y": self.y,
                "z": self.z,
                "paksize": self.paksize,
                "directions": self.directions,
                "frames": self.frames,
                "winter": self.winter,
                "frontimage": self.frontimage,
            },
            "files": {
                "datfile_location": self.datfile_location,
                "datfile_write": self.datfile_write,
                "pngfile_location": self.pngfile_location,
                "pakfile_location": self.pakfile_location,
            },
            "dat": {
                "dat_lump": self.dat_lump,
            },
        }
        if load is None:
            self.props = self.defaults
        else:
            self.props = self.load_dict(load, self.validators, self.defaults)


    def load_dict(self, loaded, validators, defaults):
        """Load a dict of stuff from config, may be called recursively"""
        props = {}
        for k, v in validators.iteritems():
            if loaded.has_key(k):
                # If this is a key, validate value + set if valid
                if type(v) == type(lambda x: x):
                    if v(loaded[k]):
                        props[k] = loaded[k]
                    else:
                        props[k] = defaults[k]
                # If this is a node call function to determine what to set
                elif type(v) == type({}):
                    if type(loaded[k]) == type({}):
                        props[k] = self.load_dict(loaded[k], v, defaults[k])
                    else:
                        # Validators defines this to be a dict, but the loaded data for this key isn't a dict - data must be invalid so use defaults
                        props[k] = defaults[k]
                else:
                    # This should not happen, panic
                    debug(u"ERROR: invalid state for load_dict decode")
                    raise ValueError
            else:
                props[k] = defaults[k]
        return props


    def init_image_array(self):
        """Init a default/empty image array"""
        # project[view][season][frame][image][xdim][ydim][zdim]
        viewarray = []
        for view in range(4):
            seasonarray = []
            for season in range(2):
                framearray = []
                for frame in range(1):
                    imagearray = []
                    for image in range(2):
                        imdefault = {
                            "path": u"",
                            "imagedata": None,
                            "bitmapdata": None,
                            "offset": [0,0],
                        }
                        imagearray.append(imdefault)
                    framearray.append(imagearray)
                seasonarray.append(framearray)
            viewarray.append(seasonarray)
        return viewarray
                        

    def validate_image_array(self, imarray):
        """Validate that an image array loaded from file is valid"""

    def init_save_location(self):
        """Return our initial save location based on platform-specific settings"""
        # Use userprofile on all platforms as default
        if sys.platform == "darwin":
            save_location = os.path.expanduser(u"~")
        elif sys.platform == "win32":
            save_location = getenvvar(u"USERPROFILE")
        else:
            save_location = os.path.expanduser(u"~")

        # Otherwise use location of program
        # Depending on how/when os.path.expanduser can fail this may not be needed but just in case!
        if save_location == u"~":
            save_location = self.test_path(self.parent.parent.start_directory)
        else:
            save_location = self.test_path(save_location)

        debug(u"save_location: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (self.save_location,
                                                                                                       self.datfile_location,
                                                                                                       self.pngfile_location,
                                                                                                       self.pakfile_location))
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
        debug(u"Root on_change triggered, sending message to App")
        self.parent.project_has_changed()

    def __getitem__(self, key):
        return self.props["images"][key]


    # These functions deal with dat file properties
    def temp_dat_properties(self, set=None):
        debug(u"Deprecation warning: temp_dat_properties() method called!")
        return self.dat_lump(set)
    def dat_lump(self, set=None):
        """Sets or returns a string containing arbitrary .dat file properties"""
        if set is not None:
            self.props["dat"]["dat_lump"] = set
            self.val_temp_dat = set
            debug(u"dat_lump properties set to %s" % self.props["dat"]["dat_lump"])
            self.on_change()
            return True
        else:
            return self.props["dat"]["dat_lump"]


    def get_image(self, d, s, f, l):
        """Return a wxImage representation of the specified image"""
        self.reload_image(d, s, f, l)
        return self.internals["images"][d][s][f][l]["imagedata"]

    def get_active_image(self):
        """Return a wxImage representation of the active image"""
        return self.get_image(self.props["activeimage"]["direction"], 
                              self.props["activeimage"]["season"], 
                              self.props["activeimage"]["frame"], 
                              self.props["activeimage"]["layer"])

    def get_bitmap(self, d, s, f, l):
        """Return a wxBitmap representation of the specified image"""
        self.reload_image(d, s, f, l)
        return self.internals["images"][d][s][f][l]["bitmapdata"]

    def get_active_bitmap(self):
        """Return a wxBitmap representation of the active image"""
        return self.get_bitmap(self.props["activeimage"]["direction"], 
                               self.props["activeimage"]["season"], 
                               self.props["activeimage"]["frame"], 
                               self.props["activeimage"]["layer"])

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

#    def cutImages(self, cutting_function):
    def cut_images(self, cutting_function):
        """Produce cut imagesets for all images in this project"""
        # Can make this work conditionally based on which images are enabled later
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        # Reload the image to obtain most recent version
                        self.reload_image(d,s,f,l)
                        # Call cutting function on image and store data on the internals array
                        # Cutting function by convention takes args: wxbitmap, dims(x,y,z,direction), offset, paksize
#                        self.props["images"][d][s][f][l].cutImage(cutting_function, (self.x(), self.y(), self.z(), d), self.paksize())
                        self.internals["images"][d][s][f][l]["cutimageset"] = cutting_function(self.internals["images"][d][s][f][l]["bitmapdata"],
                                                                                               (self.props["dims"]["x"], 
                                                                                                self.props["dims"]["y"], 
                                                                                                self.props["dims"]["z"], d),
                                                                                               self.props["images"][d][s][f][l]["offset"],
                                                                                               self.props["dims"]["paksize"])

    def reload_active_image(self):
        """Refresh the active image"""
        return self.reload_image(self.props["activeimage"]["direction"], 
                                 self.props["activeimage"]["season"], 
                                 self.props["activeimage"]["frame"], 
                                 self.props["activeimage"]["layer"])
    def reload_image(self, d, s, f, l):
        """Refresh the specified image, inputs are: direction, season, frame, layer"""
        # If path is valid, use it, otherwise use a blank image/image with error message
        abspath = paths.join_paths(self.internals["files"]["save_location"], self.props["images"][d][s][f][l]["path"])
        # If path is valid, load file
        self.internals["images"][d][s][f][l]["imagedata"] = wx.EmptyImage(1,1)
        if (paths.is_input_file(abspath) and os.path.exists(abspath)):
            self.internals["images"][d][s][f][l]["imagedata"].LoadFile(abspath, wx.BITMAP_TYPE_ANY)
        # If path isn't valid, just leave it as an empty image (or could display an error image?)
        else:
            pass
        self.internals["images"][d][s][f][l]["bitmapdata"] = wx.BitmapFromImage(self.internals["images"][d][s][f][l]["imagedata"])

#    def delImages(self):
    def delete_imagedata(self):
        """Delete all image data representations, ready for pickling"""
        # This won't be needed since the image data will be stored in the internals["images"] array rather than props (and only props will be saved)
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        self.props["images"][d][s][f][l]["imagedata"] = None
                        self.props["images"][d][s][f][l]["bitmapdata"] = None
                        #self.props["images"][d][s][f][l]["cutimageset"] = None

    def prep_serialise(self):
        """Prepare this object for serialisation"""
        # Remove images as we cannot pickle these and do not want to
        self.delImages()
        # Return parent reference so it can be added back by post_serialise
        parent = self.parent
        self.del_parent()
        return [parent, ]

    def post_serialise(self, params):
        """After serialisation re-add parameters removed by prep_serialise"""
        self.set_parent(params[0])

    def del_parent(self):
        """Delete the parent reference ready for pickling"""
        self.parent = None
    def set_parent(self, parent):
        """Set the parent for Event references"""
        self.parent = parent


    # Methods which deal with properties of the currently active image
    def offset(self, x=None, y=None):
        """Increases/decreases the offset for the active image, if set to 0 that offset dimension is reset"""
        old_x = self.active_image()["offset"][0]
        old_y = self.active_image()["offset"][1]
        changed = False
        if x == 0:
            self.active_image()["offset"][0] = 0
            changed = True
        elif x != None:
            self.active_image()["offset"][0] += x
            if not config.negative_offset_allowed:
                if self.active_image()["offset"][0] < 0:
                    self.active_image()["offset"][0] = 0     # Limit to 0
            changed = True
        if y == 0:
            self.active_image()["offset"][1] = 0
            changed = True
        elif y != None:
            self.active_image()["offset"][1] += y
            if not config.negative_offset_allowed:
                if self.active_image()["offset"][1] < 0:
                    self.active_image()["offset"][1] = 0     # Limit to 0
            changed = True
        if changed == True:
            debug(u"Active Image offset changed to: %s" % unicode(self.active_image()["offset"]))
            self.on_change()
            if old_x != self.active_image()["offset"][0] or old_y != self.active_image()["offset"][1]:
                return 1
            else:
                return 0
        else:
            return self.active_image()["offset"]

    def active_image_path(self, path=None):
        """Set or return the path of the active image"""
        return self.image_path(self.props["activeimage"]["direction"], 
                               self.props["activeimage"]["season"], 
                               self.props["activeimage"]["frame"], 
                               self.props["activeimage"]["layer"],
                               path)
    def image_path(self, d, s, f, l, path=None):
        """Set or return the path of the specified image"""
        if path is not None:
            self.props["images"][d][s][f][l]["path"] = path
            # This will either load the image (if the path exists) or set a default image if it doesn't
            self.reload_image(d, s, f, l)
            return True
        else:
            return self.props["images"][d][s][f][l]["path"]

#    def active_image_data(self, path=None):
#        """Set or return the image data of the active image"""
#        # This needs to index into internals not props for the image data!
#        return self.active_image()["imagedata"]
#    def active_bitmap_data(self):
#        """Return wxBitmap data for the active image"""
#        # This needs to index into internals not props for the image data!
#        return self.active_image()["bitmapdata"]

    def direction(self, set=None):
        """Set or query active image's direction"""
        if set is not None:
            if set in [0,1,2,3]:
                self.props["activeimage"]["direction"] = set
                debug(u"Active image direction set to %i" % self.props["activeimage"]["direction"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set active image direction failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["activeimage"]["direction"]

    def season(self, set=None):
        """Set or query active image's season"""
        if set is not None:
            if set in [0, 1]:
                self.props["activeimage"]["season"] = set
                debug(u"Active image season set to %i" % self.props["activeimage"]["season"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set active image season failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["activeimage"]["season"]

    def frame(self, set=None):
        """Set or query active image's frame"""
        if set is not None:
            if set in range(self.props["dims"]["frames"]):
                self.props["activeimage"]["frame"] = set
                debug(u"Active image frame set to %i" % self.props["activeimage"]["frame"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set active image frame failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["activeimage"]["frame"]

    def layer(self, set=None):
        """Set or query active image's layer"""
        if set is not None:
            if set in [0, 1]:
                self.props["activeimage"]["layer"] = set
                debug(u"Active image layer set to %i" % self.props["activeimage"]["layer"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set active image layer failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["activeimage"]["layer"]

#    def activeImage(self, direction=None, season=None, frame=None, layer=None):
    def active_image(self, direction=None, season=None, frame=None, layer=None):
        """Set or return the currently active image"""
        # If parameters have been changed at all, update
        changed = False
        if direction != self.props["activeimage"]["direction"] and direction != None:
            if self.direction(direction):
                changed = True
                debug(u"Active Image direction changed to: %s" % unicode(self.props["activeimage"]["direction"]))
            else:
                return False
        if season != self.props["activeimage"]["season"] and season != None:
            if self.season(season):
                changed = True
                debug(u"Active Image season changed to: %s" % unicode(self.props["activeimage"]["season"]))
            else:
                return False
        if frame != self.props["activeimage"]["frame"] and frame != None:
            if self.frame(frame):
                changed = True
                debug(u"Active Image frame changed to: %s" % unicode(self.props["activeimage"]["frame"]))
            else:
                return False
        if layer != self.props["activeimage"]["layer"] and layer != None:
            if self.layer(layer):
                changed = True
                debug(u"Active Image layer changed to: %s" % unicode(self.props["activeimage"]["layer"]))
            else:
                return False
#        if changed == True:
#            self.active.UpdateImage()
#        else:
        # project[direction][season][frame][layer][xdim][ydim][zdim]
        # Returns dict containing active image's properties
        return self.props["images"][self.props["activeimage"]["direction"]][self.props["activeimage"]["season"]][self.props["activeimage"]["frame"]][self.props["activeimage"]["layer"]]


    # Functions which deal with dimensions properties of the project
    def x(self, set=None):
        """Set or return X dimension"""
        if set is not None:
            if set in config.choicelist_dims:
                self.props["dims"]["x"] = int(set)
                debug(u"X dimension set to %i" % self.props["dims"]["x"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set X dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["x"]

    def y(self, set=None):
        """Set or return Y dimension"""
        if set is not None:
            if set in config.choicelist_dims:
                self.props["dims"]["y"] = int(set)
                debug(u"Y dimension set to %i" % self.props["dims"]["y"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["y"]

    def z(self, set=None):
        """Set or return Z dimension"""
        if set is not None:
            if set in config.choicelist_dims_z:
                self.props["dims"]["z"] = int(set)
                debug(u"Z dimension set to %i" % self.props["dims"]["z"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["z"]

    def paksize(self, set=None):
        """Set or return paksize"""
        if set is not None:
            if set in config.choicelist_paksize:
                self.props["dims"]["paksize"] = int(set)
                debug(u"Paksize set to %i" % self.props["dims"]["paksize"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set Paksize failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["paksize"]

    def winter(self, set=None):
        """Set or return if Winter image is enabled"""
        if set is not None:
            if set in [True, 1]:
                self.props["dims"]["winter"] = 1
                debug(u"winter set to %i" % self.props["dims"]["winter"])
                self.on_change()
                return True
            elif set in [False, 0]:
                self.props["dims"]["winter"] = 0
                debug(u"winter set to %i" % self.props["dims"]["winter"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set winter failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["winter"]

    def frontimage(self, set=None):
        """Set or return if Front image is enabled"""
        if set is not None:
            if set in [True, 1]:
                self.props["dims"]["frontimage"] = 1
                debug(u"frontimage set to %i" % self.props["dims"]["frontimage"])
                self.on_change()
                return True
            elif set in [False, 0]:
                self.props["dims"]["frontimage"] = 0
                debug(u"frontimage set to %i" % self.props["dims"]["frontimage"])
                self.on_change()
                return True
            else:
                debug(u"Attempt to set frontimage failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["frontimage"]

    def frames(self, set=None):
        """Query or validate new value for number of frames"""
        if set is not None:
            if set == 1:
                self.props["dims"]["frames"] = int(set)
                return True
            else:
                debug(u"attempt to set frames failed - value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["frames"]

    def views(self, set=None):
        debug(u"Deprecation warning: views() method called!")
        return self.directions(set)
    def directions(self, set=None):
        """Set or return number of direction views (1, 2 or 4)"""
        if set is not None:
            if set in config.choicelist_views:
                self.props["dims"]["directions"] = int(set)
                debug(u"Views set to %i" % self.props["dims"]["directions"])
                self.on_change()
                return True
            else:
                debug(u"attempt to set directions failed - value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["dims"]["directions"]


    # Functions with deal with file properties of the project
    def datfile(self, set=None):
        debug(u"Deprecation warning: datfile() method called!")
        return self.datfile_location(set)
    def datfile_location(self, set=None):
        """Set or return (relative) path to dat file"""
        if set is not None:
            self.props["files"]["datfile_location"] = unicode(set)
            self.on_change()
            return True
        else:
            return self.props["files"]["datfile_location"]

    def writedat(self, set=None):
        debug(u"Deprecation warning: writedat() method called!")
        return self.datfile_write(set)
    def datfile_write(self, set=None):
        """Set or return if dat file should be written"""
        if set is not None:
            if set in [True, 1]:
                self.props["files"]["datfile_write"] = True
                self.on_change()
                return True
            elif set in [False, 0]:
                self.props["files"]["datfile_write"] = False
                self.on_change()
                return True
            else:
                debug(u"Attempt to set datfile_write failed - Value (%s) outside of acceptable range" % unicode(set))
                return False
        else:
            return self.props["files"]["datfile_write"]

    def pngfile(self, set=None):
        debug(u"Deprecation warning: pngfile() method called!")
        return self.pngfile_location(set)
    def pngfile_location(self, set=None):
        """Set or return (relative) path to png file"""
        if set is not None:
            self.props["files"]["pngfile_location"] = unicode(set)
            self.on_change()
            return True
        else:
            return self.props["files"]["pngfile_location"]

    def pakfile(self, set=None):
        debug(u"Deprecation warning: pakfile() method called!")
        return self.pakfile_location(set)
    def pakfile_location(self, set=None):
        """Set or return (relative) path to pak file"""
        if set is not None:
            self.props["files"]["pakfile_location"] = unicode(set)
            self.on_change()
            return True
        else:
            return self.props["files"]["pakfile_location"]


    # The following functions deal with the save file for the project and are saved to the internals set (since we don't need to preserve these values when saving)
    def has_save_location(self):
        debug(u"Deprecation warning: has_save_location() method called!")
        return self.saved(set)
    def saved(self, set=None):
        """Set or return whether a save path has been set for this project"""
        if set is not None:
            if set in [True, 1]:
                self.internals["files"]["saved"] = True
                self.on_change()
                return True
            elif set in [False, 0]:
                self.internals["files"]["saved"] = False
                self.on_change()
                return True
            else:
                debug(u"Attempt to set project saved status failed - Value (%s) outside of acceptable range" % unicode(set))
        else:
            return self.internals["files"]["saved"]

    def savefile(self, set=None):
        debug(u"Deprecation warning: savefile() method called!")
        return self.save_location(set)
    def save_location(self, set=None):
        """Set or return (absolute) path to project save file location"""
        if set is not None:
            self.internals["files"]["save_location"] = unicode(set)
            self.on_change()
            return True
        else:
            return self.internals["files"]["save_location"]

    # Inputting/extracting information from the project is done via methods of the project class, so we can change the underlying
    # structure without having to change the way every other function interacts with it
    # Should allow for array like behaviour to access images,
    # e.g. blah = Project(), blah[0][0][0][0] = south, summer, frame 1, backimage
    # and: blah[0][0][0][0].setPath("") will set that path

