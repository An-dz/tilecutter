# TileCutter Project module

class ProjectImage:
    """An individual image object, consisting of a cached image, path to that image and offset dimensions"""
    def __init__(self, fb):
        """Initialise default values, new image, empty path, zeroed offsets"""
        # Also needs some provision for setting the cutting mask on a per-image basis (like the offset)
        # given that fine-tuning of the mask is a desirable feature
        # Also needs a reload function to refresh the image from disk
        self.f = self.b = False
        if fb == 0:
            self.b = True
        else:
            self.f = True
##        self.image = Image.new("RGBA", (1,1), color=(231,255,255,0))
        self.path = ""
        self.offset = (0,0)
    def setPath(self, path):
        """Set the path of the image after checking path exists, then load that image into the cache"""
        self.path = path
    def back(self):
        """Returns True if this is a backimage, false if not"""
        return self.b
    def front(self):
        """Returns True if this is a frontimage, false if not"""
        return self.f
class ProjectFrame:
    """Contains a single frame of the project, with a front and back image"""
    def __init__(self):
        """Initialise array containing two images"""
        self.images = []
        self.images.append(ProjectImage(0))
        self.images.append(ProjectImage(1))
    def __getitem__(self, key):
        return self.images[key]
    def setBackPath(self, path):
        self.backpath = path
        # And then check to see if the path exists, if so load the image into the cache

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

        self.dims = ProjectDims()
    def __getitem__(self, key):
        return self.images[key]
    def x(self, set=None):
        if set != None:
            if set in choicelist_dims_int or set in choicelist_dims:
                self.dims.x = int(set)
                self.debug("X dimension set to %i" % self.dims.x)
                return 0
            else:
                self.debug("Attempt to set X dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.x
    def y(self, set=None):
        if set != None:
            if set in choicelist_dims_int or set in choicelist_dims:
                self.dims.y = int(set)
                self.debug("Y dimension set to %i" % self.dims.y)
                return 0
            else:
                self.debug("Attempt to set Y dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.y
    def z(self, set=None):
        if set != None:
            if set in choicelist_dims_z_int or set in choicelist_dims_z:
                self.dims.z = int(set)
                self.debug("Z dimension set to %i" % self.dims.z)
                return 0
            else:
                self.debug("Attempt to set Z dimension failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.z
    def paksize(self, set=None):
        if set != None:
            if set in choicelist_paksize_int or set in choicelist_paksize:
                self.dims.paksize = int(set)
                self.debug("Paksize set to %i" % self.dims.paksize)
                return 0
            else:
                self.debug("Attempt to set Paksize failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.paksize
    def winter(self, set=None):
        if set != None:
            if set == 1 or set == True:
                self.dims.winter = 1
                self.debug("WinterViewEnable set to %i" % self.dims.winter)
                return 0
            elif set == 0 or set == False:
                self.dims.winter = 0
                self.debug("WinterViewEnable set to %i" % self.dims.winter)
                return 0
            else:
                self.debug("Attempt to set WinterViewEnable failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.winter
    def frontimage(self, set=None):
        if set != None:
            if set == 1 or set == True:
                self.dims.frontimage = 1
                self.debug("FrontImageEnable set to %i" % self.dims.frontimage)
                return 0
            elif set == 0 or set == False:
                self.dims.frontimage = 0
                self.debug("FrontImageEnable set to %i" % self.dims.frontimage)
                return 0
            else:
                self.debug("Attempt to set FrontImageEnable failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        else:
            return self.dims.frontimage
    def views(self, set=None):
        if set != None:
            if set in choicelist_views or set in choicelist_views_int:
                self.dims.views = int(set)
                self.debug("Views set to %i" % self.dims.views)
                return 0
            else:
                self.debug("Attempt to set Views failed - Value (%s) outside of acceptable range" % str(set))
                return 1
        return self.dims.views
    # Inputting/extracting information from the project is done via methods of the project class, so we can change the underlying
    # structure without having to change the way every other function interacts with it
    # Should allow for array like behaviour to access images,
    # e.g. blah = Project(), blah[0][0][0][0] = south, summer, frame 1, backimage
    # and: blah[0][0][0][0].setPath("") will set that path

    def debug(self, text):
        print text

class ProjectDims:
    """Dimensions of the project, X, Y, Z, paksize, also whether winter/frontimage are enabled
    Note that the number of frames per frameset is not set outside of the length of the frameset,
    and can only be altered by adding or removing frames"""
    # All of these defaults should be loaded from a config file, and sanity checked on load
    def __init__(self):
        self.x = 1
        self.y = 1
        self.z = 1
        self.paksize = 64
        self.views = 1
        self.winter = 0
        self.frontimage = 0

test = Project()

print test.north[0][0]

print test.paksize()

test.paksize(128)
test.paksize("192")

test.paksize(12228)

test.paksize("12228")










