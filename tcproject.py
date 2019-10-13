# TileCutter Project Module (Old version)

import logging, os, sys
import wx
import config
from tc import Paths
from environment import getenvvar
config = config.Config()
paths = Paths()


# project[view][season][frame][image][xdim][ydim][zdim]
# view=NSEW, 0,1,2,3 - array - controlled by global enable
# season=summer/winter, 0,1 - array - controlled by global bool enable
# frame=0,++ - array - controlled by global number of frames variable
# image=back/front, 0,1 - array - controlled by global bool enable
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
        self.reload_image()
        self.offset = [0, 0]
        self.cutimageset = None

    def __getitem__(self, key):
        return self.cutimageset[key]

    def cut_image(self, cutting_function, dims, p):
        """Generates an array of cut images based on this image
        using the cutting routine"""
        self.reload_image()
        self.cutimageset = cutting_function(self.bitmap(), dims, self.offset, p)

    def image(self):
        """Return a wxImage representation of the cached image"""
        if self.value_image is None:
            self.reload_image()

        return self.value_image

    def bitmap(self):
        """Return a wxBitmap representation of the cached image"""
        if self.value_bitmap is None:
            self.reload_image()

        return self.value_bitmap

    def del_image(self):
        """Delete stored images, to enable pickling"""
        self.value_image = None
        self.value_bitmap = None
        self.cutimageset = None

    def reload_image(self):
        """Refresh the cached image"""
        if self.value_valid_path == "":
            self.value_image = wx.Image(1, 1)
            self.value_bitmap = wx.Bitmap(self.value_image)
        else:
            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_valid_path)
            self.value_image = wx.Image(1, 1)
            self.value_image.LoadFile(abspath, wx.BITMAP_TYPE_ANY)
            self.value_bitmap = wx.Bitmap(self.value_image)

    def valid_path(self):
        """Return the valid/real path of this image"""
        return self.value_valid_path

    def path(self, path=None):
        """Set or return the path of this image as entered"""
        if path is not None:
            self.value_path = path
            logging.debug("value_path set to: '%s'" % self.value_path)
            abspath = paths.join_paths(self.parent.parent.parent.savefile(), self.value_path)

            if (paths.is_input_file(abspath) and os.path.exists(abspath)) or path == "":
                self.value_valid_path = path
                self.reload_image()
                logging.debug("Valid image path set to '%s', new cached image will be loaded" % str(self.value_valid_path))
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

        for _a in range(4):
            b = []
            b.append(ProjectFrameset(self, 0))
            b.append(ProjectFrameset(self, 1))
            self.images.append(b)

        self.dims = ProjectDims(self)
        self.files = ProjectFiles(self)
        self.active = ActiveImage(self)

        self.val_temp_dat = "Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100"

    def on_change(self):
        # When something in the project has changed, notify containing app to
        # allow for updating of UI
        logging.info("Root on_change triggered, sending message to App")
        self.parent.project_has_changed()

    def __getitem__(self, key):
        return self.images[key]

    def temp_dat_properties(self, value=None):
        """References a string containing arbitrary dat properties for the project"""
        if value is not None:
            self.val_temp_dat = value
            logging.debug("TEMP dat properties set to %s" % self.val_temp_dat)
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

    def cut_images(self, cutting_function):
        """Produce cut imagesets for all images in this project"""
        # Can make this work conditionally based on which images are enabled later
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].cut_image(cutting_function, (self.x(), self.y(), self.z(), d), self.paksize())

    def del_images(self):
        """Delete all image data representations, ready for pickling"""
        for d in range(len(self.images)):
            for s in range(len(self.images[d])):
                for f in range(len(self.images[d][s])):
                    for i in range(len(self.images[d][s][f])):
                        self.images[d][s][f][i].del_image()

    def prep_serialise(self):
        """Prepare this object for serialisation"""
        # Remove images as we cannot pickle these and do not want to
        self.del_images()
        # Return parent reference so it can be added back by post_serialise
        parent = self.parent
        self.del_parent()
        return [parent]

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
        elif x is not None:
            self.active.image.offset[0] += x

            if not config.negative_offset_allowed:
                if self.active.image.offset[0] < 0:
                    self.active.image.offset[0] = 0 # Limit to 0

            changed = True

        if y == 0:
            self.active.image.offset[1] = 0
            changed = True
        elif y is not None:
            self.active.image.offset[1] += y

            if not config.negative_offset_allowed:
                if self.active.image.offset[1] < 0:
                    self.active.image.offset[1] = 0 # Limit to 0

            changed = True

        if changed is True:
            logging.debug("Active Image offset changed to: %s" % str(self.active.image.offset))
            self.on_change()

            if old_x != self.active.image.offset[0] or old_y != self.active.image.offset[1]:
                return 1
            else:
                return 0
        else:
            return self.active.image.offset

    def active_image_path(self, path=None):
        """Set or return the path of the active image"""
        return self.active_image().path(path)

    def active_image(self, direction=None, season=None, frame=None, layer=None):
        """Set or return the currently active image"""
        # If parameters have been changed at all, update
        changed = False
        if direction is not None and direction != self.active.direction:
            self.active.direction = direction
            changed = True
            logging.debug("Active Image direction changed to: %s" % str(self.active.direction))

        if season is not None and season != self.active.season:
            self.active.season = season
            changed = True
            logging.debug("Active Image season changed to: %s" % str(self.active.season))

        if frame is not None and frame != self.active.frame:
            self.active.frame = frame
            changed = True
            logging.debug("Active Image frame changed to: %s" % str(self.active.frame))

        if layer is not None and layer != self.active.layer:
            self.active.layer = layer
            changed = True
            logging.debug("Active Image layer changed to: %s" % str(self.active.layer))

        if changed is True:
            self.active.update_image()
        else:
            return self.active.image

    def x(self, value=None):
        """Set or return X dimension"""
        if value is not None:
            if value in config.choicelist_dims:
                self.dims.x = int(value)
                logging.info("X dimension set to %i" % self.dims.x)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set X dimension failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.x

    def y(self, value=None):
        """Set or return Y dimension"""
        if value is not None:
            if value in config.choicelist_dims:
                self.dims.y = int(value)
                logging.info("Y dimension set to %i" % self.dims.y)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.y

    def z(self, value=None):
        """Set or return Z dimension"""
        if value is not None:
            if value in config.choicelist_dims_z:
                self.dims.z = int(value)
                logging.info("Z dimension set to %i" % self.dims.z)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.z

    def paksize(self, value=None):
        """Set or return paksize"""
        if value is not None:
            if int(value) in range(16, 32766):
                self.dims.paksize = int(value)
                logging.info("Paksize set to %i" % self.dims.paksize)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set Paksize failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.paksize

    def winter(self, value=None):
        """Set or return if Winter image is enabled"""
        if value is not None:
            if value == 1 or value is True:
                self.dims.winter = 1
                logging.info("WinterViewEnable set to %i" % self.dims.winter)
                self.on_change()
                return 0
            elif value == 0 or value is False:
                self.dims.winter = 0
                logging.info("WinterViewEnable set to %i" % self.dims.winter)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set WinterViewEnable failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.winter

    def frontimage(self, value=None):
        """Set or return if Front image is enabled"""
        if value is not None:
            if value == 1 or value is True:
                self.dims.frontimage = 1
                logging.info("FrontImageEnable set to %i" % self.dims.frontimage)
                self.on_change()
                return 0
            elif value == 0 or value is False:
                self.dims.frontimage = 0
                logging.info("FrontImageEnable set to %i" % self.dims.frontimage)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set FrontImageEnable failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        else:
            return self.dims.frontimage

    def views(self, value=None):
        """Set or return number of views (1, 2 or 4)"""
        if value is not None:
            if value in config.choicelist_views:
                self.dims.views = int(value)
                logging.info("Views set to %i" % self.dims.views)
                self.on_change()
                return 0
            else:
                logging.warn("Attempt to set Views failed - Value (%s) outside of acceptable range" % str(value))
                return 1
        return self.dims.views

    def datfile(self, value=None):
        """Set or return (relative) path to dat file"""
        if value is not None:
            self.files.datfile_location = str(value)
            self.on_change()
        else:
            return self.files.datfile_location

    def writedat(self, value=None):
        """Set or return if dat file should be written"""
        if value in [True, 1]:
            self.files.writedat = True
            self.on_change()
        elif value in [False, 0]:
            self.files.writedat = False
            self.on_change()
        else:
            return self.files.writedat

    def pngfile(self, value=None):
        """Set or return (relative) path to png file"""
        if value is not None:
            self.files.pngfile_location = str(value)
            self.on_change()
        else:
            return self.files.pngfile_location

    def pakfile(self, value=None):
        """Set or return (relative) path to pak file"""
        if value is not None:
            self.files.pakfile_location = str(value)
            self.on_change()
        else:
            return self.files.pakfile_location

    def has_save_location(self):
        """Return True if project has a save location, False otherwise"""
        return self.files.saved

    def saved(self, value=None):
        """Set or return whether a save path has been set for this project"""
        if value is not None:
            if value in [True, 1]:
                self.files.saved = True
                self.on_change()
            elif value in [False, 0]:
                self.files.saved = False
                self.on_change()
            else:
                logging.warn("Attempt to set project saved status failed - Value (%s) outside of acceptable range" % str(value))
        else:
            return self.files.saved

    def savefile(self, value=None):
        """Set or return (absolute) path to project save file location"""
        if value is not None:
            self.files.save_location = str(value)
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

        # Use userprofile on all platforms as default
        if sys.platform == "darwin":
            location = os.path.expanduser("~")
        elif sys.platform == "win32":
            location = getenvvar("USERPROFILE")
        else:
            location = os.path.expanduser("~")

        # Otherwise use location of program
        # Depending on how/when os.path.expanduser can fail this may not be needed but just in case!
        if location == "~":
            self.save_location = self.test_path(self.parent.parent.start_directory)
        else:
            self.save_location = self.test_path(location)

        # As initialised, project is unsaved, so other paths relative to the default value
        self.saved = False

        # Location of .dat file output (relative to save location)
        self.datfile_location = "output.dat"
        self.writedat = True
        # Location of .png file output (relative to dat file)
        self.pngfile_location = os.path.join("images", "output.png")

        # Location of .pak output file (relative to save location)
        # Blank by default so that pak file name is produced by building type/name
        self.pakfile_location = ""

        try:
            logging.info("save_location: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (
                         self.save_location, self.datfile_location, self.pngfile_location, self.pakfile_location))
        except UnicodeDecodeError:
            logging.error("Unicode Decode Error")
            logging.error("save_location: %s, datfile_location: %s, pngfile_location: %s, pakfile_location: %s" % (
                self.save_location, self.datfile_location, self.pngfile_location, self.pakfile_location))

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
        self.update_image()      # And set the image this refers to

    def update_image(self):
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
