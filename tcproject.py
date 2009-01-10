# coding: UTF-8

import os, sys
import wx

from debug import DebugFrame as debug

# TileCutter Project module

# Static variables
South = 0
East = 1
North = 2
West = 3

DEFAULT_IMPATH = "dino.png"
VALID_IMAGE_EXTENSIONS = [".png"]
OFFSET_NEGATIVE_ALLOWED = False

choicelist_paksize_int = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240]
choicelist_views_int = [1,2,4]
choicelist_dims_int = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
choicelist_dims_z_int = [1,2,3,4]

class ProjectImage:
    """An individual image object, consisting of a cached image, path to that image and offset dimensions"""
    def __init__(self, b):
        """Initialise default values, new image, empty path, zeroed offsets"""
        # Also needs some provision for setting the cutting mask on a per-image basis (like the offset)
        # given that fine-tuning of the mask is a desirable feature
        if b in [True, 1]:
            self.b = True
        elif b in [False, 0]:
            self.b = False
        self.value_path = DEFAULT_IMPATH
        self.value_lastpath = DEFAULT_IMPATH          # Used to check if the text in the entry box has really changed (temporary)
        self.reloadImage()
        self.offset = [0,0]
        self.cutimageset = 0
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
    def reloadImage(self):
        """Refresh the cached image"""
        if self.value_path == "":
            self.value_image = wx.EmptyImage(1,1)
            self.value_bitmap = wx.BitmapFromImage(self.value_image)
        else:
            self.value_image = wx.EmptyImage(1,1)
            self.value_image.LoadFile(self.value_path, wx.BITMAP_TYPE_ANY)
            self.value_bitmap = wx.BitmapFromImage(self.value_image)
    def lastpath(self, path=None):
        """Set or return the non-valid path set for this image"""
        # Non-valid path keeps track of user entries in the text entry box which aren't valid files
        # This may also be a valid file, but shouldn't be relied upon
        if path != None:
            self.value_lastpath = path
            debug("Image lastpath set to \"%s\"" % str(path))
        else:
            return self.value_lastpath
    def path(self, path=None):
        """Set or return the path of this image"""
        if path != None:
            # Check that path exists and is a file of the right type (if it's an empty string, reset to empty image)
            if (os.path.isfile(path) and os.path.splitext(path)[1] in VALID_IMAGE_EXTENSIONS) or path == "":
                self.value_path = path
                self.reloadImage()
                debug("Image path set to \"%s\", new cached image loaded" % str(path))
            else:
                debug("Attempt to set image path failed - Path \"%s\" invalid" % str(path))
                return 1
            # Otherwise raise an error (path must be to a file that exists)
        else:
            return self.value_path
    def back(self):
        """Returns True if this is a backimage, false if it is a frontimage"""
        return self.b

class ProjectFrame:
    """Contains a single frame of the project, with a front and back image"""
    def __init__(self):
        """Initialise array containing two images"""
        self.images = []
        self.images.append(ProjectImage(0))
        self.images.append(ProjectImage(1))
    def __getitem__(self, key):
        return self.images[key]
    def __len__(self):
        return len(self.images)

class ProjectFrameset:
    """Contains a sequence of ProjectFrame objects for each animation frame of this direction/season combination"""
    def __init__(self, season):
        self.season = season    # 0 for summer, 1 for winter
        self.frames = []
        self.frames.append(ProjectFrame())
    def __getitem__(self, key):
        return self.frames[key]
    def __len__(self):
        return len(self.frames)
    # Needs methods to add a frame, remove a frame, move frames up/down etc. (To be added with animation support)

class Project:
    """The project is our model, it contains all information about a project."""
    def __init__(self):
        """Initialise this project, and set default values"""
        # Create a 4/2 array of ProjectImages arrays, which can then contain a variable number of
        # Frame objects (each of which contains a Front and Back Image)
        # [0]->South, [1]->East, [2]->North, [3]->West
        # [0][0]->Summer, [0][1]->Winter
        self.images = []
        for a in range(4):
            b = []
            b.append(ProjectFrameset(0))
            b.append(ProjectFrameset(1))
            self.images.append(b)
        self.south = self.images[0]
        self.east  = self.images[1]
        self.north = self.images[2]
        self.west  = self.images[3]

        self.dims = ProjectDims(self)
        self.files = ProjectFile(self)
        self.active = ActiveImage(self)
    def __getitem__(self, key):
        return self.images[key]

    def cutImages(self, cutting_function):
        """Produce cut imagesets for all images in this project"""
        # Can make this work conditionally based on which images are enabled later
##        for d in range(len(self.images)):
##            for s in range(len(self.images[d])):
##                for f in range(len(self.images[d][s])):
##                    for i in range(len(self.images[d][s][f])):
##                        self.images[d][s][f][i].cutImage(cutting_function, (self.x(), self.y(), self.z(), d))

        self.images[0][0][0][0].cutImage(cutting_function, (self.x(), self.y(), self.z(), 0), self.paksize())

    def delImages(self):
        """Delete all image data representations, ready for pickling"""
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].delImage()

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
            if not OFFSET_NEGATIVE_ALLOWED:
                if self.active.image.offset[0] < 0:
                    self.active.image.offset[0] = 0     # Limit to 0
            changed = True
        if y == 0:
            self.active.image.offset[1] = 0
            changed = True
        elif y != None:
            self.active.image.offset[1] += y
            if not OFFSET_NEGATIVE_ALLOWED:
                if self.active.image.offset[1] < 0:
                    self.active.image.offset[1] = 0     # Limit to 0
            changed = True
        if changed == True:
            debug("Active Image offset changed to: %s" % str(self.active.image.offset))
            if old_x != self.active.image.offset[0] or old_y != self.active.image.offset[1]:
                return 1
            else:
                return 0
        else:
            return self.active.image.offset

    def activeImage(self, direction=None, season=None, frame=None, layer=None):
        """Set or return the currently active image"""
        # If parameters have been changed at all, update
        changed = False
        if direction != self.active.direction and direction != None:
            self.active.direction = direction
            changed = True
            debug("Active Image direction changed to: %s" % str(self.active.direction))
        if season != self.active.season and season != None:
            self.active.season = season
            changed = True
            debug("Active Image season changed to: %s" % str(self.active.season))
        if frame != self.active.frame and frame != None:
            self.active.frame = frame
            changed = True
            debug("Active Image frame changed to: %s" % str(self.active.frame))
        if layer != self.active.layer and layer != None:
            self.active.layer = layer
            changed = True
            debug("Active Image layer changed to: %s" % str(self.active.layer))
        if changed == True:
            self.active.UpdateImage()
        else:
            return self.active.image

    def x(self, set=None):
        if set != None:
            if set in choicelist_dims_int:
                self.dims.x = int(set)
                debug("X dimension set to %i" % self.dims.x)
                return 0
            else:
                debug("Attempt to set X dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.x
    def y(self, set=None):
        if set != None:
            if set in choicelist_dims_int:
                self.dims.y = int(set)
                debug("Y dimension set to %i" % self.dims.y)
                return 0
            else:
                debug("Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.y
    def z(self, set=None):
        if set != None:
            if set in choicelist_dims_z_int:
                self.dims.z = int(set)
                debug("Z dimension set to %i" % self.dims.z)
                return 0
            else:
                debug("Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.z
    def paksize(self, set=None):
        if set != None:
            if set in choicelist_paksize_int:
                self.dims.paksize = int(set)
                debug("Paksize set to %i" % self.dims.paksize)
                return 0
            else:
                debug("Attempt to set Paksize failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.paksize
    def winter(self, set=None):
        if set != None:
            if set == 1 or set == True:
                self.dims.winter = 1
                debug("WinterViewEnable set to %i" % self.dims.winter)
                return 0
            elif set == 0 or set == False:
                self.dims.winter = 0
                debug("WinterViewEnable set to %i" % self.dims.winter)
                return 0
            else:
                debug("Attempt to set WinterViewEnable failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.winter
    def frontimage(self, set=None):
        if set != None:
            if set == 1 or set == True:
                self.dims.frontimage = 1
                debug("FrontImageEnable set to %i" % self.dims.frontimage)
                return 0
            elif set == 0 or set == False:
                self.dims.frontimage = 0
                debug("FrontImageEnable set to %i" % self.dims.frontimage)
                return 0
            else:
                debug("Attempt to set FrontImageEnable failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.frontimage
    def views(self, set=None):
        if set != None:
            if set in choicelist_views_int:
                self.dims.views = int(set)
                debug("Views set to %i" % self.dims.views)
                return 0
            else:
                debug("Attempt to set Views failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        return self.dims.views

    def datfile(self, set=None):
        if set != None:
            self.files.datfile_location = str(set)
        else:
            return self.files.datfile_location
    def pngfile(self, set=None):
        if set != None:
            self.files.pngfile_location = str(set)
        else:
            return self.files.pngfile_location
    def save(self, set=None):
        if set != None:
            if set in [True, 1, False, 0]:
                self.files.saved = set
            else:
                debug("Attempt to set Saved status failed - Value (%s) outside of acceptable range" % str(set))
        else:
            return self.files.saved
    # Inputting/extracting information from the project is done via methods of the project class, so we can change the underlying
    # structure without having to change the way every other function interacts with it
    # Should allow for array like behaviour to access images,
    # e.g. blah = Project(), blah[0][0][0][0] = south, summer, frame 1, backimage
    # and: blah[0][0][0][0].setPath("") will set that path


class ProjectFile:
    """Information relating to file paths"""
    def __init__(self, parent):
        # Location of save file, by default this is the user's home directory
        if "HOME" in os.environ:
            self.save_location = os.environ["HOME"]
        elif "USERPROFILE" in os.environ:
            self.save_location = os.environ["USERPROFILE"]
        else:   # Otherwise use location of program
            self.save_location = start_directory
        # Location of .dat/.pak file output, can be either a relative path (relative to save location)
        # or an absolute path. Default is relative path, same as save location (which defaults to home directory)
        self.datfile_location = os.path.join(self.save_location, "output.dat")

        # Location of .png file output (relative to .dat file output), default is "images/output.png"
        self.pngfile_location = os.path.join("images", "output.png")

        # If self.saved is False, then project is not saved, thus datfile_location is absolute path (by default, the
        # same as save_location, i.e. the home directory), if self.saved is True, then the datfile directory should be
        # converted to a relative path, relative to the location of the saved file.
        # This means the user can move the saved project file and retain the same output file hierarchy, while at the
        # same time being able to define output paths without saving the project (and allows for default output
        # paths for quick and easy use)
        self.saved = False

        debug("save_location: %s, datfile_location: %s, pngfile_location: %s" % (self.save_location,
                                                                                     self.datfile_location,
                                                                                     self.pngfile_location))

class ActiveImage:
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

class ProjectDims:
    """Dimensions of the project, X, Y, Z, paksize, also whether winter/frontimage are enabled
    Note that the number of frames per frameset is not set outside of the length of the frameset,
    and can only be altered by adding or removing frames"""
    # All of these defaults should be loaded from a config file, and sanity checked on load
    def __init__(self, parent):
        self.x = 1
        self.y = 1
        self.z = 1
        self.paksize = 64
        self.views = 1
        self.winter = 0
        self.frontimage = 0







