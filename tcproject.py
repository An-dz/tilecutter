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

# Image should store:
# Last path entered
# Path of current image
# Image itself (cached)
# As user enters a path in the box, it updates the active image, only when the path points to a valid
# file should the current image path be set, and the image loaded from file into the cache
# File validity is measured relative to the current project save location

class ProjectImage(object):
    """An individual image object, consisting of a cached image, path to that image and offset dimensions"""
    def __init__(self, parent, b):
        """Initialise default values, new image, empty path, zeroed offsets"""
        self.parent = parent
        # Also needs some provision for setting the cutting mask on a per-image basis (like the offset)
        # given that fine-tuning of the mask is a desirable feature
        if b in [True, 1]:
            self.b = True
        elif b in [False, 0]:
            self.b = False
        # Whatever is in the path entry box
        self.value_path = ""
        # Last valid/real path entered
        self.value_valid_path = ""
        self.reloadImage()
        self.offset = [0,0]
        self.cutimageset = None
    def __getitem__(self, key):
        return self.cutimageset[key]
    def cutImage(self, cutting_function, dims, p):
        """Generates an array of cut images based on this image
        using the cutting routine"""
        self.reloadImage()
        self.cutimageset = cutting_function(self.bitmap(), dims, self.offset, p)

    def image(self):
        """Return a wxImage representation of the cached image"""
        if self.value_image == None:
            self.reloadImage()
        return self.value_image
    def bitmap(self):
        """Return a wxBitmap representation of the cached image"""
        if self.value_bitmap == None:
            self.reloadImage()
        return self.value_bitmap
    def delImage(self):
        """Delete stored images, to enable pickling"""
        self.value_image = None
        self.value_bitmap = None
        self.cutimageset = None
    def reloadImage(self):
        """Refresh the cached image"""
        if self.value_valid_path == "":
            self.value_image = wx.EmptyImage(1,1)
            self.value_bitmap = wx.BitmapFromImage(self.value_image)
        else:
            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_valid_path)
            self.value_image = wx.EmptyImage(1,1)
            self.value_image.LoadFile(abspath, wx.BITMAP_TYPE_ANY)
            self.value_bitmap = wx.BitmapFromImage(self.value_image)
##    def lastpath(self, path=None):
##        """Set or return the non-valid path set for this image"""
##        # Non-valid path keeps track of user entries in the text entry box which aren't valid files
##        # This may also be a valid file, but shouldn't be relied upon
##        if path != None:
##            self.value_lastpath = path
##            debug(u"Image lastpath set to \"%s\"" % unicode(path))
##        else:
##            return self.value_lastpath
    def valid_path(self):
        """Return the valid/real path of this image"""
        return self.value_valid_path
    def path(self, path=None):
        """Set or return the path of this image as entered"""
        if path != None:
            self.value_path = path
            debug(u"value_path set to: \"%s\"" % self.value_path)
            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_path)
            if (paths.is_input_file(abspath) and os.path.exists(abspath)) or path == "":
                self.value_valid_path = path
                self.reloadImage()
                debug(u"Valid image path set to \"%s\", new cached image will be loaded" % unicode(self.value_valid_path))
                self.on_change()
        else:
            return self.value_path
    def back(self):
        """Returns True if this is a backimage, false if it is a frontimage"""
        return self.b
    def on_change(self):
        # When something in the project has changed
        self.parent.on_change()

class ProjectFrame(object):
    """Contains a single frame of the project, with a front and back image"""
    def __init__(self, parent):
        """Initialise array containing two images"""
        self.parent = parent
        self.images = []
        self.images.append(ProjectImage(self, 0))
        self.images.append(ProjectImage(self, 1))
    def __getitem__(self, key):
        return self.images[key]
    def __len__(self):
        return len(self.images)
    def on_change(self):
        # When something in the project has changed
        self.parent.on_change()

class ProjectFrameset(object):
    """Contains a sequence of ProjectFrame objects for each animation frame of this direction/season combination"""
    def __init__(self, parent, season):
        self.parent = parent
        # 0 for summer, 1 for winter
        self.season = season
        self.frames = []
        self.frames.append(ProjectFrame(self))
    def __getitem__(self, key):
        return self.frames[key]
    def __len__(self):
        return len(self.frames)
    # Needs methods to add a frame, remove a frame, move frames up/down etc. (To be added with animation support)
    def on_change(self):
        # When something in the project has changed
        self.parent.on_change()

class Project(object):
    """Model containing all information about a project."""
    def __init__(self, parent):
        """Initialise this project, and set default values"""
        self.parent = parent
        # Create a 4/2 array of ProjectImages arrays, which can then contain a variable number of
        # Frame objects (each of which contains a Front and Back Image)
        # [0]->South, [1]->East, [2]->North, [3]->West
        # [0][0]->Summer, [0][1]->Winter
        self.images = []
        for a in range(4):
            b = []
            b.append(ProjectFrameset(self, 0))
            b.append(ProjectFrameset(self, 1))
            self.images.append(b)

        self.dims = ProjectDims(self)
        self.files = ProjectFiles(self)
        self.active = ActiveImage(self)

        self.val_temp_dat = u"Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100"

    def on_change(self):
        # When something in the project has changed, notify containing app to
        # allow for updating of UI
        debug(u"Root on_change triggered, sending message to App")
        self.parent.project_has_changed()

    def __getitem__(self, key):
        return self.images[key]

    def temp_dat_properties(self, set=None):
        """References a string containing arbitrary dat properties for the project"""
        if set != None:
            self.val_temp_dat = set
            debug(u"TEMP dat properties set to %s" % self.val_temp_dat)
            self.on_change()
            return 0
        else:
            return self.val_temp_dat

    def set_all_images(self, path):
        """Set the path for all images to the same path"""
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].path(path)
        self.on_change()

    def cutImages(self, cutting_function):
        """Produce cut imagesets for all images in this project"""
        # Can make this work conditionally based on which images are enabled later
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].cutImage(cutting_function, (self.x(), self.y(), self.z(), d), self.paksize())

    def delImages(self):
        """Delete all image data representations, ready for pickling"""
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].delImage()

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

    def offset(self, x=None, y=None):
        """Increases/decreases the offset for the active image, if set to 0 that offset dimension is reset"""
        old_x = self.active.image.offset[0]
        old_y = self.active.image.offset[1]
        changed = False
        if x == 0:
            self.active.image.offset[0] = 0
            changed = True
        elif x != None:
            self.active.image.offset[0] += x
            if not config.negative_offset_allowed:
                if self.active.image.offset[0] < 0:
                    self.active.image.offset[0] = 0     # Limit to 0
            changed = True
        if y == 0:
            self.active.image.offset[1] = 0
            changed = True
        elif y != None:
            self.active.image.offset[1] += y
            if not config.negative_offset_allowed:
                if self.active.image.offset[1] < 0:
                    self.active.image.offset[1] = 0     # Limit to 0
            changed = True
        if changed == True:
            debug(u"Active Image offset changed to: %s" % unicode(self.active.image.offset))
            self.on_change()
            if old_x != self.active.image.offset[0] or old_y != self.active.image.offset[1]:
                return 1
            else:
                return 0
        else:
            return self.active.image.offset

    def active_image_path(self, path=None):
        """Set or return the path of the active image"""
        return self.activeImage().path(path)

    def activeImage(self, direction=None, season=None, frame=None, layer=None):
        """Set or return the currently active image"""
        # If parameters have been changed at all, update
        changed = False
        if direction != self.active.direction and direction != None:
            self.active.direction = direction
            changed = True
            debug(u"Active Image direction changed to: %s" % unicode(self.active.direction))
        if season != self.active.season and season != None:
            self.active.season = season
            changed = True
            debug(u"Active Image season changed to: %s" % unicode(self.active.season))
        if frame != self.active.frame and frame != None:
            self.active.frame = frame
            changed = True
            debug(u"Active Image frame changed to: %s" % unicode(self.active.frame))
        if layer != self.active.layer and layer != None:
            self.active.layer = layer
            changed = True
            debug(u"Active Image layer changed to: %s" % unicode(self.active.layer))
        if changed == True:
            self.active.UpdateImage()
        else:
            return self.active.image

    def x(self, set=None):
        """Set or return X dimension"""
        if set != None:
            if set in config.choicelist_dims:
                self.dims.x = int(set)
                debug(u"X dimension set to %i" % self.dims.x)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set X dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.x
    def y(self, set=None):
        """Set or return Y dimension"""
        if set != None:
            if set in config.choicelist_dims:
                self.dims.y = int(set)
                debug(u"Y dimension set to %i" % self.dims.y)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.y
    def z(self, set=None):
        """Set or return Z dimension"""
        if set != None:
            if set in config.choicelist_dims_z:
                self.dims.z = int(set)
                debug(u"Z dimension set to %i" % self.dims.z)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.z
    def paksize(self, set=None):
        """Set or return paksize"""
        if set != None:
            if set in config.choicelist_paksize:
                self.dims.paksize = int(set)
                debug(u"Paksize set to %i" % self.dims.paksize)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set Paksize failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.paksize
    def winter(self, set=None):
        """Set or return if Winter image is enabled"""
        if set != None:
            if set == 1 or set == True:
                self.dims.winter = 1
                debug(u"WinterViewEnable set to %i" % self.dims.winter)
                self.on_change()
                return 0
            elif set == 0 or set == False:
                self.dims.winter = 0
                debug(u"WinterViewEnable set to %i" % self.dims.winter)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set WinterViewEnable failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.winter
    def frontimage(self, set=None):
        """Set or return if Front image is enabled"""
        if set != None:
            if set == 1 or set == True:
                self.dims.frontimage = 1
                debug(u"FrontImageEnable set to %i" % self.dims.frontimage)
                self.on_change()
                return 0
            elif set == 0 or set == False:
                self.dims.frontimage = 0
                debug(u"FrontImageEnable set to %i" % self.dims.frontimage)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set FrontImageEnable failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        else:
            return self.dims.frontimage
    def views(self, set=None):
        """Set or return number of views (1, 2 or 4)"""
        if set != None:
            if set in config.choicelist_views:
                self.dims.views = int(set)
                debug(u"Views set to %i" % self.dims.views)
                self.on_change()
                return 0
            else:
                debug(u"Attempt to set Views failed - Value (%s) outside of acceptable range" % unicode(set))
                return 1
        return self.dims.views

    def datfile(self, set=None):
        """Set or return (relative) path to dat file"""
        if set != None:
            self.files.datfile_location = unicode(set)
            self.on_change()
        else:
            return self.files.datfile_location
    def writedat(self, set=None):
        """Set or return if dat file should be written"""
        if set in [True, 1]:
            self.files.writedat = True
            self.on_change()
        elif set in [False, 0]:
            self.files.writedat = False
            self.on_change()
        else:
            return self.files.writedat
    def pngfile(self, set=None):
        """Set or return (relative) path to png file"""
        if set != None:
            self.files.pngfile_location = unicode(set)
            self.on_change()
        else:
            return self.files.pngfile_location
    def pakfile(self, set=None):
        """Set or return (relative) path to pak file"""
        if set != None:
            self.files.pakfile_location = unicode(set)
            self.on_change()
        else:
            return self.files.pakfile_location
    def has_save_location(self):
        """Return True if project has a save location, False otherwise"""
        return self.files.saved
    def saved(self, set=None):
        """Set or return whether a save path has been set for this project"""
        if set != None:
            if set in [True, 1]:
                self.files.saved = True
                self.on_change()
            elif set in [False, 0]:
                self.files.saved = False
                self.on_change()
            else:
                debug(u"Attempt to set project saved status failed - Value (%s) outside of acceptable range" % unicode(set))
        else:
            return self.files.saved
    def savefile(self, set=None):
        """Set or return (absolute) path to project save file location"""
        if set != None:
            self.files.save_location = unicode(set)
            self.on_change()
        else:
            return self.files.save_location

    # Inputting/extracting information from the project is done via methods of the project class, so we can change the underlying
    # structure without having to change the way every other function interacts with it
    # Should allow for array like behaviour to access images,
    # e.g. blah = Project(), blah[0][0][0][0] = south, summer, frame 1, backimage
    # and: blah[0][0][0][0].setPath("") will set that path


class ProjectFiles(object):
    """Information relating to file paths"""
    def __init__(self, parent):
        self.parent = parent
        # Location of save file, by default this is the user's home directory
        # If user has previously selected a place to save project files to, use this as the default save path
        # Whenever the user does a Save-As this config directive should be updated

#        if config.last_save_path != "" and os.path.exists(config.last_save_path):
#            self.save_location = self.test_path(config.last_save_path)
#
#        # HOME is on Unix-style systems
#        elif u"HOME" in os.environ and os.path.exists(os.environ[u"HOME"]):
#            self.save_location = self.test_path(os.environ[u"HOME"])
#
#        # USERPROFILE is on Windows
#        elif u"USERPROFILE" in os.environ and os.path.exists(os.environ[u"USERPROFILE"]):
#            self.save_location = self.test_path(os.environ[u"USERPROFILE"])
#            # Convert from native windows codepage if non-ASCII chars involved
#            self.save_location = unicode(self.save_location, sys.getfilesystemencoding())

        # Use userprofile on all platforms as default
        if sys.platform == "darwin":
            location = os.path.expanduser(u"~")
        elif sys.platform == "win32":
            location = getenvvar(u"USERPROFILE")
        else:
            location = os.path.expanduser(u"~")

        # Otherwise use location of program
        # Depending on how/when os.path.expanduser can fail this may not be needed but just in case!
        if location == u"~":
            self.save_location = self.test_path(self.parent.parent.start_directory)
        else:
            self.save_location = self.test_path(location)

        # As initialised, project is unsaved, so other paths relative to the default value
        self.saved = False

        # Location of .dat file output (relative to save location)
        self.datfile_location = u"output.dat"
        self.writedat = True
        # Location of .png file output (relative to dat file)
        self.pngfile_location = os.path.join(u"images", u"output.png")

        # Location of .pak output file (relative to save location)
        # Blank by default so that pak file name is produced by building type/name
        self.pakfile_location = u""

        try:
            debug(u"save_location: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (self.save_location,
                                                                                                           self.datfile_location,
                                                                                                           self.pngfile_location,
                                                                                                           self.pakfile_location))
        except UnicodeDecodeError:
            debug(u"Unicode Decode Error")
            debug(self.save_location)
            debug(self.datfile_location)
            debug(self.pngfile_location)
            debug(self.pakfile_location)

    def test_path(self, path):
        """Test a file for existence, if it exists add a number and try again"""
        if os.path.exists(os.path.join(path, "new_project.tcp")):
            i = 1
            while True:
                if not os.path.exists(os.path.join(path, "new_project%s.tcp" % i)):
                    return os.path.join(path, "new_project%s.tcp" % i)
                i += 1
        else:
            return os.path.join(path, "new_project.tcp") 


class ActiveImage(object):
    """Details of the active image"""
    def __init__(self, parent):
        self.parent = parent
        self.direction = 0      # 0 South, 1 East, 2 North, 3 West
        self.season = 0         # 0 Summer/All, 1 Winter
        self.frame = 0          # Index
        self.layer = 0          # 0 BackImage, 1 FrontImage

        self.UpdateImage()      # And set the image this refers to
    def UpdateImage(self):
        self.image = self.parent.images[self.direction][self.season][self.frame][self.layer]

class ProjectDims(object):
    """Dimensions of the project, X, Y, Z, paksize, also whether winter/frontimage are enabled
    Note that the number of frames per frameset is not set outside of the length of the frameset,
    and can only be altered by adding or removing frames"""
    # All of these defaults should be loaded from a config file, and sanity checked on load
    def __init__(self, parent):
        self.x = 1
        self.y = 1
        self.z = 1
        self.paksize = int(config.default_paksize)
        self.views = 1
        self.winter = 0
        self.frontimage = 0

