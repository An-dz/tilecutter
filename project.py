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



#class ProjectImage(object):
#    """An individual image object, consisting of a cached image, path to that image and offset dimensions"""
#    def __init__(self, parent, b):
#        """Initialise default values, new image, empty path, zeroed offsets"""
#        self.parent = parent
#        # Also needs some provision for setting the cutting mask on a per-image basis (like the offset)
#        # given that fine-tuning of the mask is a desirable feature
#        if b in [True, 1]:
#            self.b = True
#        elif b in [False, 0]:
#            self.b = False
#        # Whatever is in the path entry box
#        self.value_path = ""
#        # Last valid/real path entered
#        self.value_valid_path = ""
#        self.reloadImage()
#        self.offset = [0,0]
#        self.cutimageset = None
#    def __getitem__(self, key):
#        return self.cutimageset[key]
#    def cutimage(self, cutting_function, dims, p):
#        """Generates an array of cut images based on this image
#        using the cutting routine"""
#        self.reloadImage()
#        self.cutimageset = cutting_function(self.bitmap(), dims, self.offset, p)
#
#    def image(self):
#        """Return a wxImage representation of the cached image"""
#        if self.value_image == None:
#            self.reloadImage()
#        return self.value_image
#    def bitmap(self):
#        """Return a wxBitmap representation of the cached image"""
#        if self.value_bitmap == None:
#            self.reloadImage()
#        return self.value_bitmap
#    def delImage(self):
#        """Delete stored images, to enable pickling"""
#        self.value_image = None
#        self.value_bitmap = None
#        self.cutimageset = None
#    def reloadImage(self):
#        """Refresh the cached image"""
#        if self.value_valid_path == "":
#            self.value_image = wx.EmptyImage(1,1)
#            self.value_bitmap = wx.BitmapFromImage(self.value_image)
#        else:
#            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_valid_path)
#            self.value_image = wx.EmptyImage(1,1)
#            self.value_image.LoadFile(abspath, wx.BITMAP_TYPE_ANY)
#            self.value_bitmap = wx.BitmapFromImage(self.value_image)
##    def lastpath(self, path=None):
##        """Set or return the non-valid path set for this image"""
##        # Non-valid path keeps track of user entries in the text entry box which aren't valid files
##        # This may also be a valid file, but shouldn't be relied upon
##        if path != None:
##            self.value_lastpath = path
##            debug(u"Image lastpath set to \"%s\"" % unicode(path))
##        else:
##            return self.value_lastpath
#    def valid_path(self):
#        """Return the valid/real path of this image"""
#        return self.value_valid_path
#    def path(self, path=None):
#        """Set or return the path of this image as entered"""
#        if path != None:
#            self.value_path = path
#            debug(u"value_path set to: \"%s\"" % self.value_path)
#            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_path)
#            if (paths.is_input_file(abspath) and os.path.exists(abspath)) or path == "":
#                self.value_valid_path = path
#                self.reloadImage()
#                debug(u"Valid image path set to \"%s\", new cached image will be loaded" % unicode(self.value_valid_path))
#                self.on_change()
#        else:
#            return self.value_path
#    def back(self):
#        """Returns True if this is a backimage, false if it is a frontimage"""
#        return self.b
#    def on_change(self):
#        # When something in the project has changed
#        self.parent.on_change()

#class ProjectFrame(object):
#    """Contains a single frame of the project, with a front and back image"""
#    def __init__(self, parent):
#        """Initialise array containing two images"""
#        self.parent = parent
#        self.images = []
#        self.images.append(ProjectImage(self, 0))
#        self.images.append(ProjectImage(self, 1))
#    def __getitem__(self, key):
#        return self.images[key]
#    def __len__(self):
#        return len(self.images)
#    def on_change(self):
#        # When something in the project has changed
#        self.parent.on_change()
#
#class ProjectFrameset(object):
#    """Contains a sequence of ProjectFrame objects for each animation frame of this direction/season combination"""
#    def __init__(self, parent, season):
#        self.parent = parent
#        # 0 for summer, 1 for winter
#        self.season = season
#        self.frames = []
#        self.frames.append(ProjectFrame(self))
#    def __getitem__(self, key):
#        return self.frames[key]
#    def __len__(self):
#        return len(self.frames)
#    # Needs methods to add a frame, remove a frame, move frames up/down etc. (To be added with animation support)
#    def on_change(self):
#        # When something in the project has changed
#        self.parent.on_change()

class Project(object):
    """New Model containing all information about a project."""
    def __init__(self, parent, load=None):
        """Initialise this project, and set default values"""
        self.parent = parent
#        # Create a 4/2 array of ProjectImages arrays, which can then contain a variable number of
#        # Frame objects (each of which contains a Front and Back Image)
#        # [0]->South, [1]->East, [2]->North, [3]->West
#        # [0][0]->Summer, [0][1]->Winter
#        self.images = []
#        for a in range(4):
#            b = []
#            b.append(ProjectFrameset(self, 0))
#            b.append(ProjectFrameset(self, 1))
#            self.images.append(b)
#
#        self.dims = ProjectDims(self)
#        self.files = ProjectFiles(self)
#        self.active = ActiveImage(self)
#
#        self.val_temp_dat = u"Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100"

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
                "save_location": init_save_location(),
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
                "winter": False,
                "frontimage": False,
            },
            "files": {
                "datfile_location": u"output.dat",
                "datfile_write": True,
                "pngfile_location": ospath.join(u"images", u"output.png"),
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
                elif type(v) == type({}) 
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
                            "path": u"";
                            "imagedata": None;
                            "bitmapdata": None;
                            "offset": [0,0];
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


    # Replaces image() method of the Image object
    #    def image(self):
    #        """Return a wxImage representation of the cached image"""
    #        if self.value_image == None:
    #            self.reloadImage()
    #        return self.value_image
    def get_image(self, d, s, f, l):
        """Return a wxImage representation of the cached image"""
        self.reload_image(d, s, f, l)
        return self.internals["images"][d][s][f][l]["imagedata"]

    # Replaces bitmap() method of the Image object
    #    def bitmap(self):
    #        """Return a wxBitmap representation of the cached image"""
    #        if self.value_bitmap == None:
    #            self.reloadImage()
    #        return self.value_bitmap
    def get_bitmap(self, d, s, f, l):
        self.reload_image(d, s, f, l)
        return self.internals["images"][d][s][f][l]["bitmapdata"]


    def set_all_images(self, path):
        """Set the path for all images to the same path"""
        for d in range(len(self.props["images"])):
            for s in range(len(self.props["images"][d])):
                for f in range(len(self.props["images"][d][s])):
                    for l in range(len(self.props["images"][d][s][f])):
                        self.props["images"][d][s][f][l]["path"] = path
                        self.reload_image(d, s, f, l)
        self.on_change()

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

    def reload_image(self, d, s, f, l):
        """Refresh the cached image, inputs are: direction, season, frame, layer"""
        # If path is valid, use it, otherwise use a blank image/image with error message
        abspath = paths.join_paths(self.props["files"]["save_location"], self.props["images"][d][s][f][l]["path"])
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
        if path is not None:
            self.active_image()["path"] = path
            # If path has been modified call reload_image function for this image
            # This will either load the image (if the path exists) or set a default image if it doesn't
        return self.active_image()["path"]

    def active_image_data(self, path=None):
        """Set or return the image data of the active image"""
        return self.active_image()["imagedata"]

    def direction(self, set=None):
        """Set or query active image's direction"""
        # Must be 0,1,2 or 3
        self.props["active"]["direction"] = direction
    def season(self, set=None):
        """Set or query active image's season"""
        # Must be 0 or 1
        self.props["active"].["season"] = season
    def frame(self, set=None):
        """Set or query active image's frame"""
        # Must be in range of length of number of frames
        self.props["active"]["frame"] = frame
    def layer(self, set=None):
        """Set or query active image's layer"""
        # Must be 0 or 1
        self.props["active"]["layer"] = layer

#    def activeImage(self, direction=None, season=None, frame=None, layer=None):
    def active_image(self, direction=None, season=None, frame=None, layer=None):
        """Set or return the currently active image"""
        # If parameters have been changed at all, update
        changed = False
        if direction != self.props["active"]["direction"] and direction != None:
            if self.direction(direction):
                changed = True
                debug(u"Active Image direction changed to: %s" % unicode(self.props["active"]["direction"]))
            else:
                return False
        if season != self.props["active"]["season"] and season != None:
            if self.season(season):
                changed = True
                debug(u"Active Image season changed to: %s" % unicode(self.props["active"]["season"]))
            else:
                return False
        if frame != self.props["active"]["frame"] and frame != None:
            if self.frame(frame):
                changed = True
                debug(u"Active Image frame changed to: %s" % unicode(self.props["active"]["frame"]))
            else:
                return False
        if layer != self.props["active"]["layer"] and layer != None:
            if self.layer(layer):
                changed = True
                debug(u"Active Image layer changed to: %s" % unicode(self.props["active"]["layer"]))
            else:
                return False
#        if changed == True:
#            self.active.UpdateImage()
#        else:
        # project[direction][season][frame][layer][xdim][ydim][zdim]
        # Returns dict containing active image's properties
        return self.props["images"][self.props["active"]["direction"]][self.props["active"]["season"]][self.props["active"]["frame"]][self.props["active"]["layer"]]


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
                self.props["dims"]["winter"] = True
                debug(u"winter set to %i" % self.props["dims"]["winter"])
                self.on_change()
                return True
            elif set in [False, 0]:
                self.props["dims"]["winter"] = False
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
                self.props["dims"]["frontimage"] = True
                debug(u"frontimage set to %i" % self.props["dims"]["frontimage"])
                self.on_change()
                return True
            elif set in [False, 0]:
                self.props["dims"]["frontimage"] = False
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
        self.datfile_location(set)
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
        self.datfile_write(set)
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
        self.pngfile_location(set)
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
        self.pakfile_location(set)
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
        self.saved(set)
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
        self.save_location(set)
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


#class ProjectFiles(object):
#    """Information relating to file paths"""
#    def __init__(self, parent):
#        self.parent = parent
#        # Location of save file, by default this is the user's home directory
#        # If user has previously selected a place to save project files to, use this as the default save path
#        # Whenever the user does a Save-As this config directive should be updated
#
#        # Use userprofile on all platforms as default
#        if sys.platform == "darwin":
#            location = os.path.expanduser(u"~")
#        elif sys.platform == "win32":
#            location = getenvvar(u"USERPROFILE")
#        else:
#            location = os.path.expanduser(u"~")
#
#        # Otherwise use location of program
#        # Depending on how/when os.path.expanduser can fail this may not be needed but just in case!
#        if location == u"~":
#            self.save_location = self.test_path(self.parent.parent.start_directory)
#        else:
#            self.save_location = self.test_path(location)
#
#        # As initialised, project is unsaved, so other paths relative to the default value
#        self.saved = False
#
#        # Location of .dat file output (relative to save location)
#        self.datfile_location = u"output.dat"
#        self.writedat = True
#        # Location of .png file output (relative to dat file)
#        self.pngfile_location = os.path.join(u"images", u"output.png")
#
#        # Location of .pak output file (relative to save location)
#        # Blank by default so that pak file name is produced by building type/name
#        self.pakfile_location = u""
#
#        try:
#            debug(u"save_location: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (self.save_location,
#                                                                                                           self.datfile_location,
#                                                                                                           self.pngfile_location,
#                                                                                                           self.pakfile_location))
#        except UnicodeDecodeError:
#            debug(u"Unicode Decode Error")
#            debug(self.save_location)
#            debug(self.datfile_location)
#            debug(self.pngfile_location)
#            debug(self.pakfile_location)
#
#    def test_path(self, path):
#        """Test a file for existence, if it exists add a number and try again"""
#        if os.path.exists(os.path.join(path, "new_project.tcp")):
#            i = 1
#            while True:
#                if not os.path.exists(os.path.join(path, "new_project%s.tcp" % i)):
#                    return os.path.join(path, "new_project%s.tcp" % i)
#                i += 1
#        else:
#            return os.path.join(path, "new_project.tcp") 
#
#
#class ActiveImage(object):
#    """Details of the active image"""
#    def __init__(self, parent):
#        self.parent = parent
#        self.direction = 0      # 0 South, 1 East, 2 North, 3 West
#        self.season = 0         # 0 Summer/All, 1 Winter
#        self.frame = 0          # Index
#        self.layer = 0          # 0 BackImage, 1 FrontImage
#
#        self.UpdateImage()      # And set the image this refers to
#    def UpdateImage(self):
#        self.image = self.parent.images[self.direction][self.season][self.frame][self.layer]
#
#class ProjectDims(object):
#    """Dimensions of the project, X, Y, Z, paksize, also whether winter/frontimage are enabled
#    Note that the number of frames per frameset is not set outside of the length of the frameset,
#    and can only be altered by adding or removing frames"""
#    # All of these defaults should be loaded from a config file, and sanity checked on load
#    def __init__(self, parent):
#        self.x = 1
#        self.y = 1
#        self.z = 1
#        self.paksize = int(config.default_paksize)
#        self.views = 1
#        self.winter = 0
#        self.frontimage = 0
#
