#
# TileCutter, version 0.4x
#
# Written by Timothy Baldock (asterix_pop@hotmail.com)
#

# Key Implementation aims for TileCutter v.0.4
# - Full translation support (with on-the-fly translation switching)
# - Stable, segmented backend
# - Multi-project support
# - Overall better code architecture optimised for:
#     - Expandibility
#     - Clarity
#     - Ease of use
# - Fully working cutting engine
# - Cross-platform compatibility

# Hack to make PIL work with py2exe
import Image
import PngImagePlugin
import JpegImagePlugin
import GifImagePlugin
import BmpImagePlugin
Image._initialized=2

import wx
import wx.lib.masked as masked
import wx.lib.scrolledpanel as scrolled
import wx.lib.hyperlink as hl

import ImageDraw, ImageWin
import sys, os
import cPickle, copy, StringIO#, hashlib, subprocess

import tc

### Init tc
##cutter = tc.tc()

debug = 1

VERSION_NUMBER = "0.4a"
TRANSPARENT = (231,255,255)
DEFAULT_PAKSIZE = "64"
# SB_WIDTH may be different on other platforms...
SCROLLBAR_WIDTH = 16

choicelist_paksize = ["16","32","48","64","80","96","112","128","144","160","176","192","208","224","240"]
choicelist_dims = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
choicelist_dims_z = ["1","2","3","4"]
choicelist_anim = ["0",]

# Temporary translation function
def gt(text):
    return text


class ProjectImage:
    """The image itself (with pathname), 4th level under ProjectDirection"""
    def __init__(self, path=0):
        if path == 0:
            self.image = Image.new("RGBA", (1,1), color=(231,255,255,0))
            self.path = ""
        else:
            self.image = Image.open(path)
            self.image.load()
            self.path = path
        self.offset_x = 0
        self.offset_y = 0

        # Initialise the mask data for this image, this is a 16x16x4 grid
        # describing the cutting mask for the possible squares of this image
        # The project dims will determine how much of this mask is actually
        # used. The mask is initialised as "blank" with each tile cut in the
        # basic way.
        # Mask Codes (bitwise):
        #   0[1]: Do not output this tile
        #   1: Top left Triangle
        #   2: Top right Triangle
        #   3: Bottom left Triangle
        #   4: Bottom Right Triangle
        #   5: Top left Box
        #   6: Top right Box
        #   7: Bottom left Box
        #   8: Bottom right Box
        self.mask = []
        for z in range(4):
            a = []
            for x in range(16):
                b = []
                for y in range(16):
                    b.append([0,1,1,1,1,1,1,0,0])
                a.append(b)
            self.mask.append(a)

    def Reload(self):
        if os.path.isfile(self.path):
            self.image = Image.open(self.path)
            self.image.load()
        else:
            self.image = Image.new("RGB", (1,1), color=(231,255,255))
            self.image.load()

class ProjectDirection:
    """An image containing direction, 3rd level under ProjectFrame"""
    def __init__(self):
        self.image = []
        # 0 - Summer/Back
        # 1 - Winter/Back
        # 2 - Summer/Front
        # 3 - Winter/Front
        for x in range(4):
            self.image.append(ProjectImage())

class ProjectFrame:
    """An image-containing frame, 2nd level - Frame-level information,
    anything which is the same for all images in a single frame goes
    here along with the sub-images for this frame"""
    def __init__(self):
        self.direction = []
        for x in range(4):
            self.direction.append(ProjectDirection())

class Good:
    """An input/output good"""
    def __init__(self, name=""):
        self.name = name
        self.capacity = 0
        self.factor = 0
        self.suppliers = 0

class ProjectDatfile:
    """A Datfile rescource object, 3rd level under ProjectRes
    This contains all information stored by the datfile editor
    pane"""
    def __init__(self):
        # 0: Building, 1: Factory, 2: Other
        self.obj = 1
        # General stuff
        self.obj_name = ""
        self.obj_copyright = ""
        self.obj_intromonth = 0
        self.obj_introyear = 0
        self.obj_retiremonth = 0
        self.obj_retireyear = 0
        self.obj_level = 0
        self.obj_noinfo = False
        self.obj_noconstruction = False
        self.obj_drawground = False
        # Climates stuff
        self.obj_climates = [False,False,False,False,False,False,False,False]
        # Building stuff
        self.obj_bui_type = 0
        self.obj_bui_location = 0
        self.obj_bui_chance = 0
        self.obj_bui_buildtime = 0
        self.obj_bui_extension = 0
        self.obj_bui_enableflags = [False,False,False]
        # Factory Stuff
        self.obj_fac_location = 0
        self.obj_fac_chance = 0
        self.obj_fac_productivity = 0
        self.obj_fac_range = 0
        self.obj_fac_mapcolour = 0
        self.obj_fac_inputs = []
        self.obj_fac_outputs = []
        self.obj_active_good = 0
        self.obj_active_good_selection = -1
        # Additional options
        self.obj_additional_ops = ""

class ProjectSmoke:
    """A smoke resource object, 2nd level"""
    def __init__(self, path=0):
        # Image part similar the ProjectImage
        if path == 0:
            self.image = Image.new("RGBA", (1,1), color=(231,255,255,0))
            self.path = ""
        else:
            self.image = Image.open(path)
            self.image.load()
            self.path = path
        self.offset_x = 0
        self.offset_y = 0
        # Smoke unique attributes
        self.smoke_panel = 0
        self.smoke_name = ""
        self.smoke_copyright = ""
        # Project smoke info
        self.p_smoke_name = ""
        self.p_smoke_tile_x = 1
        self.p_smoke_tile_y = 1
        self.p_smoke_offset_x = 0
        self.p_smoke_offset_y = 0
        self.p_smoke_speed = 0

    def Reload(self):
        if os.path.isfile(self.path):
            self.image = Image.open(self.path)
            self.image.load()
        else:
            self.image = Image.new("RGB", (1,1), color=(231,255,255))
            self.image.load()

class ProjectInfo:
    """Info about the project, 2nd level - any information about
    the project as a whole (which isn't covered by the more
    specific subclasses) and which is the same for all frames"""
    def __init__(self):
        self.savepath = ""
        self.filename = ""
        self.paksize = 64

        self.custom_mask = 0

        self.views = 1
        self.winter = 0
        self.frontimage = 0

        self.xdims = 3
        self.ydims = 3
        self.zdims = 1

        self.offset_type = 0
##        self.offset_x = 0
##        self.offset_y = 0

        self.display_mask = 1
        self.display_frames = 1
class ProjectTemp:
    """Temporary project variables - these are project level variables
    which are not saved but which do persist for the time the project
    is open"""
    def __init__(self):
        self.draw_iso = 0
        self.iso_pos = (-1,-1)
        self.update_dims = 1
        # Hash produced whenever the project is saved, allows checking to see
        # if anything has changed since last save
        self.project_hash = ""

class ProjectData:
    """Class container for all data for a single project"""
    def __init__(self):
        self.frame = []
        self.frame.append(ProjectFrame())
        self.info = ProjectInfo()
        self.activeimage = [0,0,0]
        # Project temp should be re-initialised 
        # every time a project is loaded
        self.temp = ProjectTemp()

        # Rescources
        self.datfile = ProjectDatfile()
        self.smoke = ProjectSmoke()

class ProgramOptions:
    def __init__(self):
        self.sidepane = 3
        self.sidepane_show = 1
        self.offset_fine = 0
        self.offset_fine_smoke = 0
        self.show_mask = 1
        self.show_smoke = 1

        # Sidebar width settings
        #                           frames(0),  dat(1), makeobj(2), smoke(3),   icon(4),    log(n-1)
        self.sidebar_widths = [     200,        -1,     400,        -1,         -1,         100]
        self.sidebar_minwidths = [  200,        -1,     400,        -1,         -1,         100]

        # Makeobj interactive window options
        self.mobj_inputtext = (0,0,0)
        self.mobj_outputtext = (0,128,128)
        self.mobj_errortext = (255,0,0)
        self.mobj_infotext = (0,0,255)



def Mask(self, p, bitarray, bg_colour=(255,255,255,0), mask_colour=(231,255,255,255)):
    """Returns a tilemask, input is a tilemask bit array"""
    if bitarray[0] == 0:
        tile_im = Image.new("RGBA", (p,p), color=bg_colour)
        draw = ImageDraw.Draw(tile_im)
        # Triangles - Top
        if bitarray[1] == 1:
            draw.polygon([(0, p/2), (p/2, p/2), (0, p/2 + p/4)], fill=mask_colour)          #Draw top left triangle
        if bitarray[2] == 1:
            draw.polygon([(p/2-1, p/2), (p-1, p/2), (p-1, p/2 + p/4)], fill=mask_colour)    #Draw top right triangle
        # Triangles - Bottom
        if bitarray[3] == 1:
            draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=mask_colour)        #Draw bottom left triangle
        if bitarray[4] == 1:
            draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=mask_colour)    #Draw bottom right triangle
        # Boxes - Top
        if bitarray[5] == 1:
            draw.rectangle(((0,0),(p/2-1, p/2)), fill=mask_colour)                          #Draw top box (left)
        if bitarray[6] == 1:
            draw.rectangle(((p/2, 0),(p, p/2)), fill=mask_colour)                           #Draw top box (right)
        # Boxes - Bottom
        if bitarray[7] == 1:
            draw.rectangle(((0, p/2),(p/2-1, p)), fill=mask_colour)                         #Draw bottom box (left)
        if bitarray[8] == 1:
            draw.rectangle(((p/2, p/2),(p, p)), fill=mask_colour)                           #Draw bottom box (right)

        del draw
        return tile_im
    else:
        tile_im = Image.new("RGBA", (p,p), color=mask_colour)
        return tile_im



def Export(self, export_dat=1, export_png=1):
    """Exports the cut png image and dat file"""

    # Init output filenames
    output_png = "test-output.png"
    output_dat = "test-output.dat"

    if output_png == "" and export_png == 1:
        self.log.Write("ERROR: Write PNG but no filename for output, aborting PNG write")
        export_png = 0
    if output_dat == "" and output_dat == 1:
        self.log.Write("ERROR: Write DAT but no filename for output, aborting DAT write")
        export_dat = 0
    if self.active.info.xdims != self.active.info.ydims and self.active.info.views == 1:
        self.log.Write("WARNING: Odd shaped building but only one image!")

    # Init stringIO
    dat_stringio = StringIO.StringIO("blah\n")
    image_array = StringIO.StringIO()

    # Firstly find the path from dat file to png
    dat_to_png = "test-output"

    # Check that both of these are filled out, if png only then
    # don't export the dat file and throw Warning
    # If dat only then export the dat only, and throw Warning
    # If neither, than stop with Error

    # Init dimensions and stuff like that
    p = self.active.info.paksize
    x_dims = self.active.info.xdims
    y_dims = self.active.info.ydims
    z_dims = self.active.info.zdims
    view_dims = self.active.info.views
    winter_dims = self.active.info.winter
    front_dims = self.active.info.frontimage
    frame_dims = len(self.active.frame)

    unit = (x_dims,y_dims*z_dims)

    width = view_dims * (unit[0] + unit[0]*winter_dims)
    height = frame_dims * (unit[1] + unit[1]*front_dims)

    # Create the wxImage and PILImage for the output
    img = Image.new("RGBA", (width*p,height*p), color=(231,255,255,0))


    # IMAGE writer ----------

    if winter_dims == 0:
        if front_dims == 0:
            ii = [0]
        else:
            ii = [0,2]
    else:
        if front_dims == 0:
            ii = [0,1]
        else:
            ii = [0,1,2,3]

    image_array.write("dims=%i,%i,%i\n"%(self.active.info.ydims,self.active.info.xdims,self.active.info.views))
    for f in range(len(self.active.frame)):
        for d in range(self.active.info.views):
            for i in ii:
                # Make a temp image to copy from
                im = self.active.frame[f].direction[d].image[i].image
                # If offset is negative...
                zz = self.active.info.zdims
                w = (self.active.info.xdims + self.active.info.ydims) * (p/2)
                h = ((self.active.info.xdims + self.active.info.ydims) * (p/4)) + (p/2) + ((zz - 1) * p)
                offset_x = self.active.frame[f].direction[d].image[i].offset_x
                offset_y = self.active.frame[f].direction[d].image[i].offset_y
                abs_off_x = abs(offset_x)
                abs_off_y = abs(offset_y)
                if offset_x < 0:
                    # Image must be moved...
                    image_offset_x = abs_off_x
                else:
                    image_offset_x = 0
                if offset_y < 0:
                    image_offset_y = abs_off_y
                else:
                    image_offset_y = 0
                # Now create a copy of the input image to us...
                tempim = Image.new("RGBA", (max([w,im.size[0]])+abs_off_x, max([h,im.size[1]])+abs_off_y), color=(231,255,255,0))
                # And paste this image into it at the right spot
                # Paste the base image into the output
                tempim.paste(im,(image_offset_x,image_offset_y))

                # Now copy from and mask each bit of the image
                for z in range(zz):
                    for y in range(self.active.info.ydims):
                        for x in range(self.active.info.xdims):
                            
                            # Find offsets for this image/mask
                            if self.active.frame[f].direction[d].image[i].offset_x < 0:
                                mask_offset_x = 0
                            else:
                                mask_offset_x = abs(self.active.frame[f].direction[d].image[i].offset_x)
                            if self.active.frame[f].direction[d].image[i].offset_y < 0:
                                mask_offset_y = 0
                            else:
                                mask_offset_y = abs(self.active.frame[f].direction[d].image[i].offset_y)

                            if d in [0,2]:
                                # If this is a "normal" direction
                                # Work out where to take the square from...
                                from_x = mask_offset_x + (self.active.info.xdims*(p/2)) - x*(p/2) + y*(p/2) - p/2
                                from_y = mask_offset_y + x*(p/4) + y*(p/4) + z*p
                            else:
                                # If this is an inverse direction
                                # Work out where to take the square from...
                                from_x = mask_offset_x + (self.active.info.ydims*(p/2)) - y*(p/2) + x*(p/2) - p/2
                                from_y = mask_offset_y + x*(p/4) + y*(p/4) + z*p

                            # Complex thing to work out where to paste this particular square
                            if winter_dims == 0:
                                xpos = (d * unit[0]) + x
                            else:
                                # Winter image also
                                if i in [0,2]:
                                    # If no winter image
                                    xpos = (d * unit[0] * 2) + x
                                else:
                                    # If winter image
                                    xpos = (d * unit[0] * 2) + unit[0] + x
                            if front_dims == 0:
                                ypos = (f * unit[1]) + y
                            else:
                                # Front image also
                                if i in [0,1]:
                                    # If no front image
                                    ypos = (f * unit[1] * 2) + y
                                else:
                                    # If front image
                                    ypos = (f * unit[1] * 2) + unit[1] + y
                                    
                            # Image array stuff
                            if i == 0:
                                win = 0
                                front = 0
                            elif i == 1:
                                win = 1
                                front = 0
                            elif i == 2:
                                win = 0
                                front = 1
                            elif i == 3:
                                win = 1
                                front = 1
                            
                            if d in [0,2]:
                                # Normal direction
                                yyy = x
                                xxx = y
                            else:
                                # Abnormal direction
                                yyy = y
                                xxx = x
                            if front == 0:
                                # Write image array info (BackImage)
                                image_array.write("BackImage[%i][%i][%i][%i][%i][%i]=%s.%i.%i\n"%(d,yyy,xxx,z,f,win,
                                                                                                  dat_to_png,ypos,xpos))
                            else:
                                # Write image array info (FrontImage)
                                image_array.write("FrontImage[%i][%i][%i][%i][%i][%i]=%s.%i.%i\n"%(d,yyy,xxx,z,f,win,
                                                                                                   dat_to_png,ypos,xpos))

                            # Paste the cut out section into the image
                            img.paste(tempim.crop((from_x,from_y,from_x+p,from_y+p)), (xpos*p,ypos*p,xpos*p+p,ypos*p+p))
                            
                            # Mask this tile
                            mask = Mask(self, p, self.active.frame[f].direction[d].image[i].mask[z][x][y])
                            img.paste(mask, (xpos*p,ypos*p,xpos*p+p,ypos*p+p), mask)


    # DAT writer ----------
    dat_stringio.write("#\n# File created with TileCutter version " + VERSION_NUMBER +
                       "\n# For more information see http://tilecutter.simutrans.com/\n#\n")

    if self.active.datfile.obj in [0,1]:
        # Do stuff common to building/factory
        if self.active.datfile.obj == 0:
            dat_stringio.write("Obj=building\n")
        else:
            dat_stringio.write("Obj=factory\n")
        # Write name
        dat_stringio.write("name=%s\n"%self.active.datfile.obj_name)
        if self.active.datfile.obj_name == "":
            self.log.Write("WARNING: Required parameter \"Name\" not set in datfile")
        # Write copyright
        dat_stringio.write("copyright=%s\n"%self.active.datfile.obj_copyright)
        # Write intro month/year
        if self.active.datfile.obj_introyear == 0:
            if self.active.datfile.obj_intromonth != 0:
                self.log.Write("WARNING: Intro Month set but no Intro Year in datfile")
        else:
            dat_stringio.write("intro_year=%i\n"%self.active.datfile.obj_introyear)
            if self.active.datfile.obj_intromonth != 0:
                dat_stringio.write("intro_month=%i\n"%self.active.datfile.obj_intromonth)
        # Write retire month/year
        if self.active.datfile.obj_retireyear == 0:
            if self.active.datfile.obj_retiremonth != 0:
                self.log.Write("WARNING: Retire Month set but no Retire Year in datfile")
        else:
            dat_stringio.write("retire_year=%i\n"%self.active.datfile.obj_retireyear)
            if self.active.datfile.obj_retiremonth != 0:
                dat_stringio.write("retire_month=%i\n"%self.active.datfile.obj_retiremonth)
        # Write level
        if self.active.datfile.obj_level == 0:
            self.log.Write("WARNING: Level not set")
        dat_stringio.write("level=%i\n"%self.active.datfile.obj_level)
        # Write flags
        if self.active.datfile.obj_noinfo == 1:
            dat_stringio.write("NoInfo=1\n")
        if self.active.datfile.obj_noconstruction == 1:
            dat_stringio.write("NoConstruction=1\n")
        if self.active.datfile.obj_drawground == 1:
            dat_stringio.write("needs_ground=1\n")
        # Climates stuff now...
        climates_options_untrans = ["rocky", "tundra", "temperate", "mediterran", "desert", "arctic", "tropic", "water"]
        self.obj_climates = [False,False,False,False,False,False,False,False]
        climates_string = "climates="
        is_climates = 0
        for x in range(len(self.active.datfile.obj_climates)):
            if self.active.datfile.obj_climates[x] == 1:
                is_climates = 1
                if x == len(self.active.datfile.obj_climates) - 1:
                    climates_string = climates_string + climates_options_untrans[x]
                else:
                    climates_string = climates_string + climates_options_untrans[x] + ","
        if is_climates == 1:
            dat_stringio.write(climates_string)
        # Now move onto the obj specific stuff...
        # Building first
        if self.active.datfile.obj == 0:
            # Write the building datfile things
            building_type_choices_untrans = ["", "carstop","busstop","station","monorailstop",
                                             "harbour","wharf","airport","hall","post","shed",
                                             "res","com","ind","any","misc","mon","cur","tow","hq"]
            # Building Type
            if self.active.datfile.obj_bui_type == 0:
                self.log.Write("WARNING: Required parameter \"Building Type\" not set in datfile")
            else:
                dat_stringio.write("type=%s\n"%building_type_choices_untrans[self.active.datfile.obj_bui_type])
            # Station stuff
            if self.active.datfile.obj_bui_type in [1,2,3,4,5,6,7]:
                if self.active.datfile.obj_bui_extension == 1:
                    dat_stringio.write("extension_building=1\n")
                if self.active.datfile.obj_bui_enableflags[0] == 1:
                    dat_stringio.write("enables_pax=1\n")
                if self.active.datfile.obj_bui_enableflags[1] == 1:
                    dat_stringio.write("enables_post=1\n")
                if self.active.datfile.obj_bui_enableflags[2] == 1:
                    dat_stringio.write("enables_ware=1\n")
            # Location
            building_location_options_untrans = ["","Land","City"]
            if self.active.datfile.obj_bui_type in [17]:
                if self.active.datfile.obj_bui_location == 0:
                    self.log.Write("WARNING: Required parameter \"Building Location\" not set in datfile")
                else:
                    dat_stringio.write("location=%s\n"%building_location_options_untrans[self.active.datfile.obj_bui_location])
            # Chance
            if self.active.datfile.obj_bui_type in [16,17]:
                if self.active.datfile.obj_bui_chance == 0:
                    self.log.Write("WARNING: Required parameter \"Building Chance\" not set in datfile")
                else:
                    dat_stringio.write("chance=%i\n"%self.active.datfile.obj_bui_chance)
            # Build Time
            if self.active.datfile.obj_bui_type in [16]:
                if self.active.datfile.obj_bui_buildtime == 0:
                    self.log.Write("WARNING: Required parameter \"Building Build Time\" not set in datfile")
                else:
                    dat_stringio.write("build_time=%i\n"%self.active.datfile.obj_bui_buildtime)
            dat_stringio.write("")
            dat_stringio.write("")
        else:
            # Write the factory datfile things
            # Factory location
            factory_location_options_untrans = ["","Land","City", "Water"]
            if self.active.datfile.obj_fac_location == 0:
                self.log.Write("WARNING: Required parameter \"Factory Location\" not set in datfile")
            else:
                dat_stringio.write("Location=%s\n"%factory_location_options_untrans[self.active.datfile.obj_fac_location])
            # Factory chance
            if self.active.datfile.obj_fac_chance == 0:
                self.log.Write("WARNING: Required parameter \"Factory Chance\" not set in datfile")
            else:
                dat_stringio.write("chance=%i\n"%self.active.datfile.obj_fac_chance)
            # Factory productivity
            if self.active.datfile.obj_fac_productivity == 0:
                self.log.Write("WARNING: Required parameter \"Factory Productivity\" not set in datfile")
            else:
                dat_stringio.write("Productivity=%i\n"%self.active.datfile.obj_fac_productivity)
            # Factory range
            if self.active.datfile.obj_fac_range == 0:
                self.log.Write("WARNING: Required parameter \"Factory Range\" not set in datfile")
            else:
                dat_stringio.write("Range=%i\n"%self.active.datfile.obj_fac_range)
            # Factory mapcolour
            if self.active.datfile.obj_fac_mapcolour == 0:
                self.log.Write("WARNING: Required parameter \"Factory Mapcolour\" not set in datfile")
            else:
                dat_stringio.write("Range=%i\n"%self.active.datfile.obj_fac_mapcolour)
            # Input/Output goods
            for x in range(len(self.active.datfile.obj_fac_inputs)):
                if self.active.datfile.obj_fac_inputs[x].name == "":
                    self.log.Write("WARNING: Input Good #%i, Required parameter \"InputName\" not set"%x)
                else:
                    dat_stringio.write("InputGood[%i]=%s\n"%(x,self.active.datfile.obj_fac_inputs[x].name))
                    # Input capacity
                    if self.active.datfile.obj_fac_inputs[x].capacity == 0:
                        self.log.Write("WARNING: Input Good #%i, Required parameter \"InputCapacity\" not set"%x)
                    else:
                        dat_stringio.write("InputCapacity[%i]=%s\n"%(x,self.active.datfile.obj_fac_inputs[x].capacity))
                    # Input factor
                    if self.active.datfile.obj_fac_inputs[x].factor == 0:
                        self.log.Write("WARNING: Input Good #%i, Required parameter \"InputFactor\" not set"%x)
                    else:
                        dat_stringio.write("InputFactor[%i]=%s\n"%(x,self.active.datfile.obj_fac_inputs[x].factor))
                    # Input suppliers
                    if self.active.datfile.obj_fac_inputs[x].suppliers == 0:
                        self.log.Write("WARNING: Input Good #%i, Required parameter \"InputSupplier\" not set"%x)
                    else:
                        dat_stringio.write("InputSupplier[%i]=%s\n"%(x,self.active.datfile.obj_fac_inputs[x].suppliers))
            for x in range(len(self.active.datfile.obj_fac_outputs)):
                if self.active.datfile.obj_fac_outputs[x].name == "":
                    self.log.Write("WARNING: Output Good #%i, Required parameter \"OutputName\" not set"%x)
                else:
                    dat_stringio.write("OutputGood[%i]=%s\n"%(x,self.active.datfile.obj_fac_outputs[x].name))
                    # Output capacity
                    if self.active.datfile.obj_fac_outputs[x].capacity == 0:
                        self.log.Write("WARNING: Output Good #%i, Required parameter \"OutputCapacity\" not set"%x)
                    else:
                        dat_stringio.write("OutputCapacity[%i]=%s\n"%(x,self.active.datfile.obj_fac_outputs[x].capacity))
                    # Output factor
                    if self.active.datfile.obj_fac_outputs[x].factor == 0:
                        self.log.Write("WARNING: Output Good #%i, Required parameter \"OutputFactor\" not set"%x)
                    else:
                        dat_stringio.write("OutputFactor[%i]=%s\n"%(x,self.active.datfile.obj_fac_outputs[x].factor))

            # Smoke information goes here!----------------------------

        # Finally write the additional options info if necessary
        if self.active.datfile.obj_additional_ops not in ["", "\n"]:
            if self.active.datfile.obj_additional_ops[-1] == "\n":
                dat_stringio.write(self.active.datfile.obj_additional_ops)
            else:
                dat_stringio.write(self.active.datfile.obj_additional_ops + "\n")

    else:
        # This is something else, just output the Add.Ops. box
        if self.active.datfile.obj_additional_ops not in ["", "\n"]:
            if self.active.datfile.obj_additional_ops[-1] == "\n":
                dat_stringio.write(self.active.datfile.obj_additional_ops)
            else:
                dat_stringio.write(self.active.datfile.obj_additional_ops + "\n")
        else:
            self.log.Write("WARNING: Object type set to \"other\", but nothing specified in the \"any\" field!")

    # Now paste the image array information into the dat file (along with dims info)
    dat_stringio.write(image_array.getvalue())

    # Finally write the end-bar
    dat_stringio.write("--------------------")


    # Save files ----------

    # Now save the files if need be
    if export_png == 1:
        self.log.Write("Write Image to file: %s..."%output_png)
        save_image = Image.new("RGB", img.size)
        save_image.paste(img, (0,0))
        save_image.save(output_png)
        self.log.Write("...Complete!")
    if export_dat == 1:
        self.log.Write("Write DAT info to file: %s..."%output_dat)
        dat = open(output_dat, "w")
        dat.write(dat_stringio.getvalue())
        dat.close()
        self.log.Write("...Complete!")


    # Make image to take outputs from

    # If exporting png:
    # Frames are primary vertical, then direction horizontally,
    # followed by front/back vertically and summer/winter horizontally
    # Then the individual cut images

    # Even if not exporting png:
    # For each one paste into a temporary proto-dat file the image
    # array information

    # If exporting dat:
    # Write out all the necessary file data



class ImageWindow(wx.ScrolledWindow):
    """Window onto which bitmaps may be drawn, background colour is TRANSPARENT"""
    bmp = []
    def __init__(self, parent, id = -1, size = wx.DefaultSize, extended=1):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size)
        self.bmp = wx.EmptyBitmap(1,1)
        self.lines = []
        self.x = self.y = 0
        self.drawing = False

        self.SetVirtualSize((1, 1))
        self.SetScrollRate(20,20)

##        self.Bind(wx.EVT_PAINT, self.OnPaint)
        if extended == 1:
            #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
##            self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
##            self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            self.Bind(wx.EVT_MOTION, self.OnMotion)

        #Need to make intelligent buffer bitmap sizing work!
        
        self.buffer = wx.EmptyBitmap(4000,2500)
        dc = wx.BufferedDC(None, self.buffer)
##        dc.SetBackground(wx.Brush(TRANSPARENT))
        dc.SetBackground(wx.Brush((0,0,0)))
        dc.Clear()
        self.DrawBitmap(dc)
        self.lastisopos = (-1,-1)
        self.isopos = (-1,-1)

    def OnLeftDown(self, e):
        """Called when the left mouse button is pressed"""
        self.pos = self.CalcUnscrolledPosition(e.GetPosition())
        app.debug_frame.WriteLine("DC: MouseLeftClick: %s"%str(self.pos))
        # If the mouse is within the region of the cutting mask
        # then check to see if it's
        #if self.realpos 

    def OnMotion(self, e):
        """Called when the mouse moves over the DC"""
        self.pos = self.CalcUnscrolledPosition(e.GetPosition())
        #app.debug_frame.WriteLine("DC: MouseMoveTo: %s"%str(self.pos))
        # Check if the mouse is within the base of the cutting mask
        offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
        offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y
        self.lastisopos = self.isopos
        self.isopos = self.ScreenToIso(self.pos, (offset_x,offset_y))
        if self.isopos != self.lastisopos:
            app.debug_frame.WriteLine("DC: MouseMoveTo: %s, ISO: %s"%(str(self.pos),str(self.isopos)))
            if self.isopos == (-1,-1):
                self.active.temp.draw_iso = 0
                self.active.temp.iso_pos = self.isopos
                self.GetGrandParent().GetParent().DrawImage()       # Needs alteration
            else:
                self.active.temp.draw_iso = 1
                self.active.temp.iso_pos = self.isopos
                self.GetGrandParent().GetParent().DrawImage()       # Needs alteration

    def ScreenToIso(self, wxy=(0,0), offset=(0,0)):
        """Convert screen coordinates to Iso world coordinates
        returns tuple of iso coords"""
        offx, offy = offset
        if offx < 0:
            offx = 0
        if offy < 0:
            offy = 0

        p = self.active.info.paksize

        # If east/west reverse dims
        if self.active.activeimage[1] in [0,2]:
            xdims = self.active.info.xdims
            ydims = self.active.info.ydims
        else:
            ydims = self.active.info.xdims
            xdims = self.active.info.ydims

        TileRatio = 2
        wx, wy = wxy

        widthx = xdims * (p/2)

        dx = wx - widthx - offx
        dy = wy - ((self.active.info.zdims-1) * p) - offy - p/2
        # Don't really understand how this bit works...
        x = int((dy - dx / TileRatio) * (TileRatio / 2) / (p/2))
        y = int((dy + dx / TileRatio) * (TileRatio / 2) / (p/2))
        if x < 0 or y < 0:
            return (-1,-1)
        if x == 0 and y == 0:
            return (x,y)
        if x >= (xdims) or y >= (ydims):
            return (-1,-1)
        
        return (x,y)


##    def OnPaint(self, e):
##        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    def DrawBitmap(self, dc):
        bitmap = self.bmp
        #self.buffer.SetWidth(bitmap.GetWidth())
        #self.buffer.SetHeight(bitmap.GetHeight())
        self.SetVirtualSize((bitmap.GetWidth(), bitmap.GetHeight()))
        
        if dc == 1:
            cdc = wx.ClientDC(self)
            self.PrepareDC(cdc)            
            dc = wx.BufferedDC(cdc, self.buffer)
            #dc.Clear()
##        dc.SetBackground(wx.Brush(TRANSPARENT))
        dc.SetBackground(wx.Brush((0,0,0)))
        dc.Clear()
        dc.DrawBitmap(bitmap, 0, 0, True)

class DebugFrame(wx.Frame):
    """Debugging output frame, just a text box with some additional functions really"""
    text = "Debug Console\n"
    joiner = ""
    count = 0
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (0,0), (300,200),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        panel = wx.Panel(self, -1, (-1,-1), (500,500))

        self.debug_boxsizer = wx.BoxSizer(wx.VERTICAL)

        self.textbox = wx.TextCtrl(panel, -1, self.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)

        self.debug_boxsizer.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

        #Layout sizers
        panel.SetSizer(self.debug_boxsizer)
        panel.SetAutoLayout(1)
        panel.Layout()
    def WriteLine(self,line):
        self.count += 1
        self.text = self.joiner.join(["[", str(self.count), "] ", line, "\n", self.text]) #self.text.append(line + "\n")
        self.textbox.SetValue(self.text)

class SmokePanel(scrolled.ScrolledPanel):
    """Smoke editor panel, has its own DC child for display of input image"""
    def __init__(self,parent,placenum,type=0,id=-1,size=wx.DefaultSize):
        scrolled.ScrolledPanel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        self.smoke_select_choices = [gt("User Image"),gt("Stock Image")]
        # Inherit imres for bitmap buttons
        self.imres = self.GetGrandParent().GetParent().imres

        # Top is the Image/Stock selection, middle is the controls for each type,
        # bottom are the global controls for preview display
        self.s_panel_top = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_middle = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_bottom = wx.BoxSizer(wx.HORIZONTAL)

        # Top window
        # Image/Stock selector
        self.smoke_selector = wx.RadioBox(self, -1,  gt("Source:"), (-1,-1),(-1,-1), self.smoke_select_choices, 1, style=wx.RA_SPECIFY_ROWS)
        self.smoke_selector.SetToolTipString(gt("ttObject Type"))

        self.s_panel_top.Add(self.smoke_selector, 1, wx.ALL, 0)



        # Middle window
        # Image options
        self.image_controls = []
        self.s_image_box = wx.StaticBox(self, -1, gt("User Image:"))
        self.image_controls.append(self.s_image_box)
        self.s_image = wx.StaticBoxSizer(self.s_image_box, wx.VERTICAL)

        # Name/copyright sizer
        self.s_image_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_image_flex.AddGrowableCol(1)

        # Make the DC for custom image display
        self.image_display = ImageWindow(self,extended=0)
        self.image_controls.append(self.image_display)

        # All controls in this box
        self.s_image_controls = wx.BoxSizer(wx.HORIZONTAL)
        # Left and right parts of control box
        self.s_image_controls_left = wx.BoxSizer(wx.VERTICAL)
        self.s_image_controls_right = wx.BoxSizer(wx.VERTICAL)

        # Left hand controls
        # Label
        self.smoke_image_source_label = wx.StaticText(self, -1, gt("Image Source:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.image_controls.append(self.smoke_image_source_label)
        # Path display box
        self.smoke_image_source = wx.TextCtrl(self, -1, value="", style=wx.TE_READONLY)
        self.smoke_image_source.SetToolTipString(gt("ttinputsmokeimagepath"))
        self.smoke_image_source.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.image_controls.append(self.smoke_image_source)
        # Browse button
        self.smoke_image_source_filebrowse = wx.Button(self, -1, label=gt("Browse..."))
        self.smoke_image_source_filebrowse.SetToolTipString(gt("ttbrowseinputsmokeimagefile"))
        self.image_controls.append(self.smoke_image_source_filebrowse)

        # Name & Copyright
        # Name label
        self.smoke_image_name_label = wx.StaticText(self, -1, gt("Smoke Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.image_controls.append(self.smoke_image_name_label)
        # Name display box
        self.smoke_image_name = wx.TextCtrl(self, -1, value="", style=wx.TE_READONLY)
        self.smoke_image_name.SetToolTipString(gt("ttinputsmokename"))
        self.smoke_image_name.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.image_controls.append(self.smoke_image_name)
        # Copyright label
        self.smoke_image_copyright_label = wx.StaticText(self, -1, gt("Smoke Copyright:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.image_controls.append(self.smoke_image_copyright_label)
        # Copyright display box
        self.smoke_image_copyright = wx.TextCtrl(self, -1, value="", style=wx.TE_READONLY)
        self.smoke_image_copyright.SetToolTipString(gt("ttinputsmokecopyright"))
        self.smoke_image_copyright.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.image_controls.append(self.smoke_image_copyright)

        # Right hand controls (needs to be turned into its own class & code re-used really...!)
        # Label
        self.smoke_image_offset_label = wx.StaticText(self, -1, gt("Source Offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.image_controls.append(self.smoke_image_offset_label)
        # Fine offset select
        self.smoke_image_offset_selector = wx.CheckBox(self, -1, gt("Fine"), (-1,-1), (-1,-1))
        self.smoke_image_offset_selector.SetToolTipString(gt("ttOffsetSelector"))
        self.image_controls.append(self.smoke_image_offset_selector)
        # Offset controls 
        self.smoke_image_offset_up = wx.BitmapButton(self, -1, self.imres.up2, (-1,-1), (18,18))
        self.smoke_image_offset_up.SetToolTipString(gt("ttOffsetUp"))
        self.image_controls.append(self.smoke_image_offset_up)
        self.smoke_image_offset_left = wx.BitmapButton(self, -1, self.imres.left2, (-1,-1), (18,18))
        self.smoke_image_offset_left.SetToolTipString(gt("ttOffsetLeft"))
        self.image_controls.append(self.smoke_image_offset_left)
        self.smoke_image_offset_reset = wx.BitmapButton(self, -1, self.imres.center, (-1,-1), (18,18))
        self.smoke_image_offset_reset.SetToolTipString(gt("ttOffsetReset"))
        self.image_controls.append(self.smoke_image_offset_reset)
        self.smoke_image_offset_right = wx.BitmapButton(self, -1, self.imres.right2, (-1,-1), (18,18))
        self.smoke_image_offset_right.SetToolTipString(gt("ttOffsetRight"))
        self.image_controls.append(self.smoke_image_offset_right)
        self.smoke_image_offset_down = wx.BitmapButton(self, -1, self.imres.down2, (-1,-1), (18,18))
        self.smoke_image_offset_down.SetToolTipString(gt("ttOffsetDown"))
        self.image_controls.append(self.smoke_image_offset_down)





        # Add name/copyright to sizer
        self.s_image_flex.Add(self.smoke_image_name_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_image_flex.Add(self.smoke_image_name, 0, wx.EXPAND|wx.LEFT, 2)
        self.s_image_flex.Add(self.smoke_image_copyright_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_image_flex.Add(self.smoke_image_copyright, 0, wx.EXPAND|wx.LEFT, 2)

        # Add source/copyright/name etc. to the left hand side of the bottom bar
        self.s_image_controls_left.Add(self.smoke_image_source_label, 0, wx.ALL, 0)
        self.s_image_controls_left_filebrowse = wx.BoxSizer(wx.HORIZONTAL)
        self.s_image_controls_left_filebrowse.Add(self.smoke_image_source, 1, wx.EXPAND|wx.ALL, 0)
        self.s_image_controls_left_filebrowse.Add(self.smoke_image_source_filebrowse, 0, wx.ALIGN_RIGHT|wx.ALL, 0)
        self.s_image_controls_left.Add(self.s_image_controls_left_filebrowse, 0, wx.EXPAND|wx.ALIGN_RIGHT|wx.ALL, 0)
        self.s_image_controls_left.Add(self.s_image_flex, 0, wx.EXPAND|wx.ALL, 0)

        # Add Offset controls to the right hand side of the bottom bar
        self.s_image_controls_right.Add(self.smoke_image_offset_label, 0, wx.LEFT, 2)
        self.s_image_controls_right.Add(self.smoke_image_offset_selector, 0, wx.LEFT|wx.TOP, 2)
        self.s_image_controls_right.Add(self.smoke_image_offset_up, 0, wx.ALIGN_CENTER|wx.TOP, 3)
        self.s_image_controls_right_offset = wx.BoxSizer(wx.HORIZONTAL)
        self.s_image_controls_right_offset.Add(self.smoke_image_offset_left, 0, wx.ALIGN_CENTER)
        self.s_image_controls_right_offset.Add(self.smoke_image_offset_reset, 0, wx.ALIGN_CENTER)
        self.s_image_controls_right_offset.Add(self.smoke_image_offset_right, 0, wx.ALIGN_CENTER)
        self.s_image_controls_right.Add(self.s_image_controls_right_offset, 0, wx.ALIGN_CENTER)
        self.s_image_controls_right.Add(self.smoke_image_offset_down, 0, wx.ALIGN_CENTER)

        # Add DC to main control box sizer (goes above the controls below it and covers the entire width)
        self.s_image.Add(self.image_display, 1, wx.EXPAND|wx.ALL, 0)
        # Add control boxes to main control box
        self.s_image_controls.Add(self.s_image_controls_left, 1, wx.EXPAND|wx.ALL, 0)
        self.s_image_controls.Add(self.s_image_controls_right, 0, wx.EXPAND|wx.ALL, 0)
        # Add control box to main image sizer
        self.s_image.Add(self.s_image_controls, 0, wx.EXPAND|wx.ALL, 0)

        # Add the image sizer to the panel sizer (middle)
        self.s_panel_middle.Add(self.s_image, 1, wx.EXPAND|wx.ALL, 0)

        # Bind events for the middle box
        self.smoke_image_source_filebrowse.Bind(wx.EVT_BUTTON, self.OnSmokeImBrowse, self.smoke_image_source_filebrowse)
        self.smoke_image_offset_selector.Bind(wx.EVT_CHECKBOX, self.OnOffsetToggle, self.smoke_image_offset_selector)

        self.smoke_image_offset_up.Bind(wx.EVT_BUTTON, self.OnOffsetUp, self.smoke_image_offset_up)
        self.smoke_image_offset_left.Bind(wx.EVT_BUTTON, self.OnOffsetLeft, self.smoke_image_offset_left)
        self.smoke_image_offset_reset.Bind(wx.EVT_BUTTON, self.OnOffsetReset, self.smoke_image_offset_reset)
        self.smoke_image_offset_right.Bind(wx.EVT_BUTTON, self.OnOffsetRight, self.smoke_image_offset_right)
        self.smoke_image_offset_down.Bind(wx.EVT_BUTTON, self.OnOffsetDown, self.smoke_image_offset_down)





        # Bottom window
        # Box to contain everything
        self.displayops_controls = []
        self.s_displayops_box = wx.StaticBox(self, -1, gt("Display Options:"))
        self.displayops_controls.append(self.s_displayops_box)
        self.s_displayops = wx.StaticBoxSizer(self.s_displayops_box, wx.VERTICAL)

        self.s_displayops_flex = wx.FlexGridSizer(0,4,0,0)
        self.s_displayops_flex.AddGrowableCol(0)
        self.s_displayops_flex.AddGrowableCol(2)

        self.s_displayops_flex_top = wx.FlexGridSizer(0,4,0,0)
        self.s_displayops_flex_top.AddGrowableCol(1)
        self.s_displayops_flex_top.AddGrowableCol(3)

        # Left box contains the tile selection, right box the offset selection
        # Each has direct entry boxes next to them and are thus subdivided into
        # left and right themselves
        self.s_displayops_left_left = wx.BoxSizer(wx.VERTICAL)
        self.s_displayops_left_right = wx.BoxSizer(wx.VERTICAL)
        self.s_displayops_right_left = wx.BoxSizer(wx.VERTICAL)
        self.s_displayops_right_right = wx.BoxSizer(wx.VERTICAL)

        # Bottom box things, smoke name display and smoke speed box
        # Label
        self.smoke_displayops_displayname_label = wx.StaticText(self, -1, gt("Smoke Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_displayname_label)
        # Name display
        self.smoke_displayops_displayname = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_displayname.SetToolTipString(gt("ttSmokeDisplayName"))
        self.smoke_displayops_displayname.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_displayname)
        # Label
        self.smoke_displayops_speed_label = wx.StaticText(self, -1, gt("Smoke Speed:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_speed_label)
        # Name display
        self.smoke_displayops_speed = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_speed.SetToolTipString(gt("ttSmokeSpeed"))
        self.smoke_displayops_speed.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_speed)


        # Left box (tile selection) left part (selector)
        # Label
        self.smoke_displayops_offset_label = wx.StaticText(self, -1, gt("Smoke Offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_offset_label)
        # Tile select controls
        self.smoke_displayops_offset_north = wx.BitmapButton(self, -1, self.imres.upright, (-1,-1), (18,18))
        self.smoke_displayops_offset_north.SetToolTipString(gt("ttOffsetNorth"))
        self.displayops_controls.append(self.smoke_displayops_offset_north)
        self.smoke_displayops_offset_east = wx.BitmapButton(self, -1, self.imres.downright, (-1,-1), (18,18))
        self.smoke_displayops_offset_east.SetToolTipString(gt("ttOffsetEast"))
        self.displayops_controls.append(self.smoke_displayops_offset_east)
        self.smoke_displayops_offset_reset = wx.BitmapButton(self, -1, self.imres.center, (-1,-1), (18,18))
        self.smoke_displayops_offset_reset.SetToolTipString(gt("ttOffsetResetTilePosition"))
        self.displayops_controls.append(self.smoke_displayops_offset_reset)
        self.smoke_displayops_offset_south = wx.BitmapButton(self, -1, self.imres.downleft, (-1,-1), (18,18))
        self.smoke_displayops_offset_south.SetToolTipString(gt("ttOffsetSouth"))
        self.displayops_controls.append(self.smoke_displayops_offset_south)
        self.smoke_displayops_offset_west = wx.BitmapButton(self, -1, self.imres.upleft, (-1,-1), (18,18))
        self.smoke_displayops_offset_west.SetToolTipString(gt("ttOffsetWest"))
        self.displayops_controls.append(self.smoke_displayops_offset_west)

        # Left box (tile selection) right part (direct input)
        self.smoke_displayops_tile_x_label = wx.StaticText(self, -1, gt("x tile:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_tile_x_label)
        self.smoke_displayops_tile_y_label = wx.StaticText(self, -1, gt("y tile:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_tile_y_label)
        self.smoke_displayops_tile_x = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_tile_x.SetToolTipString(gt("ttSmokeXTile"))
        self.smoke_displayops_tile_x.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_tile_x)
        self.smoke_displayops_tile_y = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_tile_y.SetToolTipString(gt("ttSmokeYTile"))
        self.smoke_displayops_tile_y.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_tile_y)

        # Right box (offset selection) left part (selector)
        # Label
        self.smoke_displayops_offset_label2 = wx.StaticText(self, -1, gt("Smoke Tile Select:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_offset_label2)
        # Offset select controls
        self.smoke_displayops_offset_up = wx.BitmapButton(self, -1, self.imres.up, (-1,-1), (18,18))
        self.smoke_displayops_offset_up.SetToolTipString(gt("ttOffsetUp"))
        self.displayops_controls.append(self.smoke_displayops_offset_up)
        self.smoke_displayops_offset_left = wx.BitmapButton(self, -1, self.imres.left, (-1,-1), (18,18))
        self.smoke_displayops_offset_left.SetToolTipString(gt("ttOffsetLeft"))
        self.displayops_controls.append(self.smoke_displayops_offset_left)
        self.smoke_displayops_offset_reset2 = wx.BitmapButton(self, -1, self.imres.center, (-1,-1), (18,18))
        self.smoke_displayops_offset_reset2.SetToolTipString(gt("ttOffsetResetSmokeOffset"))
        self.displayops_controls.append(self.smoke_displayops_offset_reset2)
        self.smoke_displayops_offset_right = wx.BitmapButton(self, -1, self.imres.right, (-1,-1), (18,18))
        self.smoke_displayops_offset_right.SetToolTipString(gt("ttOffsetRight"))
        self.displayops_controls.append(self.smoke_displayops_offset_right)
        self.smoke_displayops_offset_down = wx.BitmapButton(self, -1, self.imres.down, (-1,-1), (18,18))
        self.smoke_displayops_offset_down.SetToolTipString(gt("ttOffsetDown"))
        self.displayops_controls.append(self.smoke_displayops_offset_down)

        # Right box (offset selection) right part (direct input)
        self.smoke_displayops_offset_x_label = wx.StaticText(self, -1, gt("x offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_offset_x_label)
        self.smoke_displayops_offset_y_label = wx.StaticText(self, -1, gt("y offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.displayops_controls.append(self.smoke_displayops_offset_y_label)
        self.smoke_displayops_offset_x = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_offset_x.SetToolTipString(gt("ttSmokeXOffset"))
        self.smoke_displayops_offset_x.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_offset_x)
        self.smoke_displayops_offset_y = wx.TextCtrl(self, -1, value="", size=(50,-1), style=wx.TE_READONLY)
        self.smoke_displayops_offset_y.SetToolTipString(gt("ttSmokeYOffset"))
        self.smoke_displayops_offset_y.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.displayops_controls.append(self.smoke_displayops_offset_y)


        # Add top controls to flex sizer
        self.s_displayops_flex_top.Add(self.smoke_displayops_displayname_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.s_displayops_flex_top.Add(self.smoke_displayops_displayname, 1, wx.EXPAND|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_displayops_flex_top.Add(self.smoke_displayops_speed_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 4)
        self.s_displayops_flex_top.Add(self.smoke_displayops_speed, 1, wx.EXPAND|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)


        # Add Tile select controls to left-left sizer
        self.s_displayops_left_left.AddStretchSpacer()
        self.s_displayops_left_left_top = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_left_left_top.Add(self.smoke_displayops_offset_west, 0, wx.RIGHT, 9)
        self.s_displayops_left_left_top.Add(self.smoke_displayops_offset_north, 0, wx.LEFT, 9)
        self.s_displayops_left_left.Add(self.s_displayops_left_left_top, 0, wx.ALIGN_CENTER)
        self.s_displayops_left_left.Add(self.smoke_displayops_offset_reset, 0, wx.ALIGN_CENTER)
        self.s_displayops_left_left_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_left_left_bottom.Add(self.smoke_displayops_offset_south, 0, wx.RIGHT, 9)
        self.s_displayops_left_left_bottom.Add(self.smoke_displayops_offset_east, 0, wx.LEFT, 9)
        self.s_displayops_left_left.Add(self.s_displayops_left_left_bottom, 0, wx.ALIGN_CENTER)
        # Add smoke tile readout controls to left-right sizer
        self.s_displayops_left_right.Add(self.smoke_displayops_offset_label2, 0, wx.LEFT|wx.BOTTOM, 2)
        self.s_displayops_left_right_x = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_left_right_x.Add(self.smoke_displayops_tile_x_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_displayops_left_right_x.Add(self.smoke_displayops_tile_x, 1, wx.EXPAND|wx.LEFT, 2)
        self.s_displayops_left_right.Add(self.s_displayops_left_right_x, 0, wx.EXPAND|wx.LEFT, 0)
        self.s_displayops_left_right_y = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_left_right_y.Add(self.smoke_displayops_tile_y_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_displayops_left_right_y.Add(self.smoke_displayops_tile_y, 1, wx.EXPAND|wx.LEFT, 2)
        self.s_displayops_left_right.Add(self.s_displayops_left_right_y, 0, wx.EXPAND|wx.LEFT, 0)

        # Add smoke offset to right-left sizer
        self.s_displayops_right_left.AddStretchSpacer()
        self.s_displayops_right_left.Add(self.smoke_displayops_offset_up, 0, wx.ALIGN_CENTER|wx.TOP, 0)
        self.s_displayops_right_left_offset = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_right_left_offset.Add(self.smoke_displayops_offset_left, 0, wx.ALL)
        self.s_displayops_right_left_offset.Add(self.smoke_displayops_offset_reset2, 0, wx.ALL)
        self.s_displayops_right_left_offset.Add(self.smoke_displayops_offset_right, 0, wx.ALL)
        self.s_displayops_right_left.Add(self.s_displayops_right_left_offset, 0, wx.ALIGN_CENTER)
        self.s_displayops_right_left.Add(self.smoke_displayops_offset_down, 0, wx.ALIGN_CENTER)
        # Add smoke offset readout controls to right-right sizer
        self.s_displayops_right_right.Add(self.smoke_displayops_offset_label, 0, wx.LEFT|wx.BOTTOM, 2)
        self.s_displayops_right_right_x = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_right_right_x.Add(self.smoke_displayops_offset_x_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_displayops_right_right_x.Add(self.smoke_displayops_offset_x, 1, wx.EXPAND|wx.LEFT, 2)
        self.s_displayops_right_right.Add(self.s_displayops_right_right_x, 0, wx.EXPAND|wx.LEFT, 0)
        self.s_displayops_right_right_y = wx.BoxSizer(wx.HORIZONTAL)
        self.s_displayops_right_right_y.Add(self.smoke_displayops_offset_y_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_displayops_right_right_y.Add(self.smoke_displayops_offset_y, 1, wx.EXPAND|wx.LEFT, 2)
        self.s_displayops_right_right.Add(self.s_displayops_right_right_y, 0, wx.EXPAND|wx.LEFT, 0)

        # Do bottom panel overall sizers,
        # first add controls
        self.s_displayops_flex.Add(self.s_displayops_left_right, 1, wx.EXPAND, 0)
        self.s_displayops_flex.Add(self.s_displayops_left_left, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 3)
        self.s_displayops_flex.Add(self.s_displayops_right_right, 1, wx.EXPAND|wx.LEFT, 3)
        self.s_displayops_flex.Add(self.s_displayops_right_left, 0, wx.LEFT|wx.BOTTOM, 3)

        self.s_displayops.Add(self.s_displayops_flex, 1, wx.EXPAND|wx.ALL, 0)
        self.s_displayops.Add(self.s_displayops_flex_top, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 4)

        # Then bind bottom panel controls to events
##        self.factory_locationfac.Bind(wx.EVT_COMBOBOX, self.OnFactoryLocation, self.factory_locationfac)
##        self.factory_chancefac.Bind(wx.EVT_TEXT, self.OnFactoryChance, self.factory_chancefac)
        # Smoke offset control
        self.smoke_displayops_offset_up.Bind(wx.EVT_BUTTON, self.OnSmokeOffsetUp, self.smoke_displayops_offset_up)
        self.smoke_displayops_offset_left.Bind(wx.EVT_BUTTON, self.OnSmokeOffsetLeft, self.smoke_displayops_offset_left)
        self.smoke_displayops_offset_reset2.Bind(wx.EVT_BUTTON, self.OnSmokeOffsetReset, self.smoke_displayops_offset_reset2)
        self.smoke_displayops_offset_right.Bind(wx.EVT_BUTTON, self.OnSmokeOffsetRight, self.smoke_displayops_offset_right)
        self.smoke_displayops_offset_down.Bind(wx.EVT_BUTTON, self.OnSmokeOffsetDown, self.smoke_displayops_offset_down)
        # Smoke tile control
        self.smoke_displayops_offset_west.Bind(wx.EVT_BUTTON, self.OnSmokeTileWest, self.smoke_displayops_offset_west)
        self.smoke_displayops_offset_north.Bind(wx.EVT_BUTTON, self.OnSmokeTileNorth, self.smoke_displayops_offset_north)
        self.smoke_displayops_offset_reset.Bind(wx.EVT_BUTTON, self.OnSmokeTileReset, self.smoke_displayops_offset_reset)
        self.smoke_displayops_offset_south.Bind(wx.EVT_BUTTON, self.OnSmokeTileSouth, self.smoke_displayops_offset_south)
        self.smoke_displayops_offset_east.Bind(wx.EVT_BUTTON, self.OnSmokeTileEast, self.smoke_displayops_offset_east)

        # Then add to the main bottom sizer
        self.s_panel_bottom.Add(self.s_displayops, 1, wx.ALL, 0)

        # Add all three main bits of the panel to sizers
        self.s_panel.Add(self.s_panel_top, 0, wx.EXPAND|wx.ALL, 2)
        self.s_panel.Add(self.s_panel_middle, 1, wx.EXPAND|wx.ALL, 2)
        self.s_panel.Add(self.s_panel_bottom, 0, wx.EXPAND|wx.ALL, 2)

        #Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()
        self.SetupScrolling()

    def OnSmokeImBrowse(self,e):
        """Opens a file picking dialog for the smoke image object"""
        app.debug_frame.WriteLine("Browse Source Click")
        dlg = wx.FileDialog(self, gt("Choose a Source Image file..."), "", "", "PNG files (*.png)|*.png|Other Image files (*.bmp, *.gif, *.jpg)|*.bmp;*.gif;*.jpg", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.active.smoke.image = Image.open(dlg.GetPath())
        dlg.Destroy()
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()

    # Control source position of smoke object from source image
    # Left is -ve, up is -ve
    # Events for the Offset controls
    def OnOffsetToggle(self,e):
        """On toggling of the "fine" offset switch"""
        app.debug_frame.WriteLine("Smoke Toggle Fine Mask -> " + str(self.smoke_image_offset_selector.GetValue()))
        self.options.offset_fine_smoke = self.smoke_image_offset_selector.GetValue()
        self.ActivatePanel()

    def OnOffsetUp(self,e):
        """On click of the offset move up button"""
        app.debug_frame.WriteLine("Smoke Offset Up")
        offset_y = self.active.smoke.offset_y
        # Any bounds checks should go here...
        if self.options.offset_fine_smoke == 0:
            offset_y -= self.active.info.paksize / 4
        else:
            offset_y -= 1
        self.active.smoke.offset_y = offset_y
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()
    def OnOffsetDown(self,e):
        """On click of the offset move down button"""
        app.debug_frame.WriteLine("Smoke Offset Down")
        offset_y = self.active.smoke.offset_y
        # Any bounds checks should go here...
        if self.options.offset_fine_smoke == 0:
            offset_y += self.active.info.paksize / 4
        else:
            offset_y += 1
        self.active.smoke.offset_y = offset_y
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()
    def OnOffsetLeft(self,e):
        """On click of the offset move left button"""
        app.debug_frame.WriteLine("Smoke Offset Left")
        offset_x = self.active.smoke.offset_x
        # Any bounds checks should go here...
        if self.options.offset_fine_smoke == 0:
            offset_x -= self.active.info.paksize / 2
        else:
            offset_x -= 1
        self.active.smoke.offset_x = offset_x
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()
    def OnOffsetRight(self,e):
        """On click of the offset move right button"""
        app.debug_frame.WriteLine("Smoke Offset Right")
        offset_x = self.active.smoke.offset_x
        # Any bounds checks should go here...
        if self.options.offset_fine_smoke == 0:
            offset_x += self.active.info.paksize / 2
        else:
            offset_x += 1
        self.active.smoke.offset_x = offset_x
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()
    def OnOffsetReset(self,e):
        """On click of the offset reset button"""
        app.debug_frame.WriteLine("Smoke Offset Reset")
        self.active.smoke.offset_y = 0
        self.active.smoke.offset_x = 0
        self.ActivatePanel()
        self.display.DrawImage()
        self.DrawImage()

    # Control exact positioning of smoke object on screen
    # Left is -ve, up is -ve
    def OnSmokeOffsetUp(self,e):
        """Decrement smoke vertical offset and redisplay"""
        self.active.smoke.p_smoke_offset_y -= 1
        app.debug_frame.WriteLine("Smoke: SmokeOffsetUp => (%i,%i)"%(self.active.smoke.p_smoke_offset_x,self.active.smoke.p_smoke_offset_y))
        self.ActivatePanel()
        self.display.DrawImage()
    def OnSmokeOffsetDown(self,e):
        """Increment smoke vertical offset and redisplay"""
        self.active.smoke.p_smoke_offset_y += 1
        app.debug_frame.WriteLine("Smoke: SmokeOffsetDown => (%i,%i)"%(self.active.smoke.p_smoke_offset_x,self.active.smoke.p_smoke_offset_y))
        self.ActivatePanel()
        self.display.DrawImage()
    def OnSmokeOffsetLeft(self,e):
        """Decrement smoke offset and redisplay"""
        self.active.smoke.p_smoke_offset_x -= 1
        app.debug_frame.WriteLine("Smoke: SmokeOffsetLeft => (%i,%i)"%(self.active.smoke.p_smoke_offset_x,self.active.smoke.p_smoke_offset_y))
        self.ActivatePanel()
        self.display.DrawImage()
    def OnSmokeOffsetRight(self,e):
        """Increment smoke offset and redisplay"""
        self.active.smoke.p_smoke_offset_x += 1
        app.debug_frame.WriteLine("Smoke: SmokeOffsetRight => (%i,%i)"%(self.active.smoke.p_smoke_offset_x,self.active.smoke.p_smoke_offset_y))
        self.ActivatePanel()
        self.display.DrawImage()
    def OnSmokeOffsetReset(self,e):
        """Reset smoke offset to be (0,0) and redisplay"""
        self.active.smoke.p_smoke_offset_x = 0
        self.active.smoke.p_smoke_offset_y = 0
        app.debug_frame.WriteLine("Smoke: SmokeOffsetReset => (%i,%i)"%(self.active.smoke.p_smoke_offset_x,self.active.smoke.p_smoke_offset_y))
        self.ActivatePanel()
        self.display.DrawImage()

    # Control tile that smoke is positioned relative to
    # West is -ve, North is -ve
    def OnSmokeTileWest(self,e):
        """Move smoke tile west and redisplay"""
        # West-East is the Y dimension, North-South is the X dimension
        # No check here to ensure that smoke is in the correct range
        # May add that later, but for now user beware!
        if self.active.smoke.p_smoke_tile_y > 1:
            self.active.smoke.p_smoke_tile_y -= 1
            app.debug_frame.WriteLine("Smoke: SmokeTileWest => (%i,%i)"%(self.active.smoke.p_smoke_tile_x,self.active.smoke.p_smoke_tile_y))
            self.ActivatePanel()
            self.display.DrawImage()
    def OnSmokeTileEast(self,e):
        """Move smoke tile east and redisplay"""
        if self.active.smoke.p_smoke_tile_y < 16:
            self.active.smoke.p_smoke_tile_y += 1
            app.debug_frame.WriteLine("Smoke: SmokeTileEast => (%i,%i)"%(self.active.smoke.p_smoke_tile_x,self.active.smoke.p_smoke_tile_y))
            self.ActivatePanel()
            self.display.DrawImage()
    def OnSmokeTileNorth(self,e):
        """Move smoke tile north and redisplay"""
        if self.active.smoke.p_smoke_tile_x > 1:
            self.active.smoke.p_smoke_tile_x -= 1
            app.debug_frame.WriteLine("Smoke: SmokeTileNorth => (%i,%i)"%(self.active.smoke.p_smoke_tile_x,self.active.smoke.p_smoke_tile_y))
            self.ActivatePanel()
            self.display.DrawImage()
    def OnSmokeTileSouth(self,e):
        """Move smoke tile south and redisplay"""
        if self.active.smoke.p_smoke_tile_x < 16:
            self.active.smoke.p_smoke_tile_x += 1
            app.debug_frame.WriteLine("Smoke: SmokeTileSouth => (%i,%i)"%(self.active.smoke.p_smoke_tile_x,self.active.smoke.p_smoke_tile_y))
            self.ActivatePanel()
            self.display.DrawImage()
    def OnSmokeTileReset(self,e):
        """Reset smoke tile to be (1,1) and redisplay"""
        self.active.smoke.p_smoke_tile_x = 1
        self.active.smoke.p_smoke_tile_y = 1
        app.debug_frame.WriteLine("Smoke: SmokeTileReset => (%i,%i)"%(self.active.smoke.p_smoke_tile_x,self.active.smoke.p_smoke_tile_y))
        self.ActivatePanel()
        self.display.DrawImage()

    def InitPanel(self):
        """Initialise the panel"""
        self.active = self.GetGrandParent().GetParent().active
        self.image_display.active = self.active
        self.display = self.GetGrandParent().GetParent()

        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()
        self.panel_height = self.s_panel.GetSize().GetHeight()

        self.ActivatePanel()

    def DrawImage(self):
        """Draws the smoke image with any necessary options to the smoke viewing pane"""
        im = self.active.smoke.image

        # Overlay is simplified to a p-by-p box at position (x,y) where x & y
        # are set in active.smoke
        p = self.active.info.paksize

        offset_x = self.active.smoke.offset_x
        offset_y = self.active.smoke.offset_y

        # Create the mask
        # Make mask image (p by p)
        mask = Image.new("RGBA", (p,p), color=(231,255,255,0))
        drawmask = ImageDraw.Draw(mask)
        # Top line
        drawmask.line((0,0,p-1,0),fill=(255,0,0,255))
        # Bottom line
        drawmask.line((0,p-1,p-1,p-1),fill=(255,0,0,255))
        # Left line
        drawmask.line((0,0,0,p-1),fill=(255,0,0,255))
        # Right line
        drawmask.line((p-1,0,p-1,p-1),fill=(255,0,0,255))
        del drawmask

        # Mask will always be at either 0,0 or some positive (absolute) offset
        # When the offset is negative, the image must be offset by that amount
        abs_offx = abs(offset_x)
        abs_offy = abs(offset_y)
        if offset_x < 0:
            # If the offset is less than 0, then both image and mask need to be moved
            image_offset_x = abs_offx
            mask_offset_x = 0
        else:
            image_offset_x = 0
            mask_offset_x = abs_offx
        if offset_y < 0:
            # If the offset is less than 0, then both image and mask need to be moved
            image_offset_y = abs_offy
            mask_offset_y = 0
        else:
            image_offset_y = 0
            mask_offset_y = abs_offy

        # Create the wxImage and PILImage for the output
        outimage = wx.EmptyImage(im.size[0] + abs_offx, im.size[1] + abs_offy)
        img = Image.new("RGBA", (im.size[0] + abs_offx, im.size[1] + abs_offy), color=(231,255,255,0))

        # Paste the base image into the output
        img.paste(im,(image_offset_x,image_offset_y))

        # Paste the mask into the output
        img.paste(mask,(mask_offset_x,mask_offset_y),mask)

        # Convert from PIL to wxImage
        outimage.SetData(img.convert("RGB").tostring())
        # Convert from Image to bitmap
        outimage = outimage.ConvertToBitmap()

        # Display the bitmap on the DC
        self.image_display.bmp = outimage
        self.image_display.DrawBitmap(1)


    def ActivatePanel(self):
        """Load panel values from the values stored in the project"""
        # Offset and Tile for smoke
        self.smoke_displayops_offset_x.SetValue(str(self.active.smoke.p_smoke_offset_x))
        self.smoke_displayops_offset_y.SetValue(str(self.active.smoke.p_smoke_offset_y))
        self.smoke_displayops_tile_x.SetValue(str(self.active.smoke.p_smoke_tile_x))
        self.smoke_displayops_tile_y.SetValue(str(self.active.smoke.p_smoke_tile_y))

        # Offset controls
        if self.options.offset_fine_smoke == 0:
            # Change the arrows of the buttons to be double arrows
            self.smoke_image_offset_up.SetBitmapLabel(self.imres.up2)
            self.smoke_image_offset_down.SetBitmapLabel(self.imres.down2)
            self.smoke_image_offset_left.SetBitmapLabel(self.imres.left2)
            self.smoke_image_offset_right.SetBitmapLabel(self.imres.right2)
        else:
            # Change the arrows of the buttons to be single arrows
            self.smoke_image_offset_up.SetBitmapLabel(self.imres.up)
            self.smoke_image_offset_down.SetBitmapLabel(self.imres.down)
            self.smoke_image_offset_left.SetBitmapLabel(self.imres.left)
            self.smoke_image_offset_right.SetBitmapLabel(self.imres.right)

        self.smoke_image_offset_selector.SetValue(self.options.offset_fine_smoke)

        # Finally re-do the layout (as things may have changed)
        self.SetAutoLayout(1)
#        self.SetupScrolling()
        self.Layout()


class IconPanel(wx.Panel):
    """Icon/Cursor editor panel, has its own DC child for display of input image"""
    def __init__(self,parent,placenum,id=-1,size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        #Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()
    def InitPanel(self):
        """Initialise the panel"""
        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()

        self.panel_height = self.s_panel.GetSize().GetHeight()


class LogPanel(wx.Panel):
    """Log output panel, just a text box with some additional functions really"""
    # This panel will also show Makeobj log output, the makeobj output will show up
    # as individual commands, with certain parts highlighted for helpfulness. A box
    # at the bottom of the window will allow for direct interaction with makeobj, and
    # the contents of the log pane should be save-able
    # Will have two views - TileCutter logs (standard) and Makeobj logs/controller
    # Each of these two logs will be independantly save-able
    text = "Log Output\n"
    joiner = ""
    count = 0
    def __init__(self,parent,placenum,id=-1,size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        self.textbox = wx.TextCtrl(self, -1, self.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY|wx.NO_BORDER)

        self.s_panel.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

        #Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()

    def InitPanel(self):
        """Initialise the panel"""
        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()

        self.panel_height = self.s_panel.GetSize().GetHeight()

    def Write(self,line):
        self.count += 1
        self.text = self.joiner.join(["[", str(self.count), "] ", line, "\n", self.text]) #self.text.append(line + "\n")
        self.textbox.SetValue(self.text)


class MakeobjPanel(wx.Panel):
    """Makeobj panel, allows dynamic interaction with makeobj"""
    # This panel will also show Makeobj log output, the makeobj output will show up
    # as individual commands, with certain parts highlighted for helpfulness. A box
    # at the bottom of the window will allow for direct interaction with makeobj, and
    # the contents of the log pane should be save-able
    # Will have two views - TileCutter logs (standard) and Makeobj logs/controller
    # Each of these two logs will be independantly save-able

    text = ""
    joiner = ""
    count = 0
    def __init__(self,parent,placenum,id=-1,size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.s_controls = wx.BoxSizer(wx.HORIZONTAL)

        self.textbox = wx.TextCtrl(self, -1, self.text, (-1,-1), (-1,-1), wx.TE_RICH|wx.TE_MULTILINE|wx.NO_BORDER|wx.TE_PROCESS_ENTER)
        self.save_log = wx.Button(self, -1, label=gt("Save Log As..."))
        self.save_log.SetToolTipString(gt("ttsavemakeobjlog"))

        self.textbox.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.s_panel.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_controls.Add(self.save_log, 0, wx.ALIGN_RIGHT|wx.ALL, 2)
        self.s_panel.Add(self.s_controls, 0, wx.ALIGN_RIGHT, 2)

        self.textbox.Bind(wx.EVT_TEXT, self.OnChangeText, self.textbox)
        self.textbox.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.textbox)
        self.save_log.Bind(wx.EVT_BUTTON, self.SaveLog, self.save_log)

        #Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()

        self.firstrun_makeobj = 0
    def SaveLog(self,e):
        """Saves the makeobj log to a file"""
        savename = wx.FileDialog(self,gt("Choose a file to save to..."),"","",
                                 "Log files (*.log)|*.log",wx.SAVE|wx.OVERWRITE_PROMPT)
        if savename.ShowModal() == wx.ID_OK:
            # OK was pressed, continue saving with new filename
            filename = savename.GetFilename()
            savepath = savename.GetDirectory()
            savename.Destroy()
        else:
            # Else cancel was pressed, abort saving
            return 0
        fileout = file(os.path.join(savepath,filename),"w")
        fileout.write(self.textbox.GetValue())
        fileout.close()

    def InitPanel(self):
        """Initialise the panel"""
        self.program_opts = self.GetGrandParent().GetParent().options

        self.mobj_inputtext = wx.Colour(self.program_opts.mobj_inputtext[0],self.program_opts.mobj_inputtext[1],self.program_opts.mobj_inputtext[2])
        self.mobj_outputtext = wx.Colour(self.program_opts.mobj_outputtext[0],self.program_opts.mobj_outputtext[1],self.program_opts.mobj_outputtext[2])
        self.mobj_errortext = wx.Colour(self.program_opts.mobj_errortext[0],self.program_opts.mobj_errortext[1],self.program_opts.mobj_errortext[2])
        self.mobj_infotext = wx.Colour(self.program_opts.mobj_infotext[0],self.program_opts.mobj_infotext[1],self.program_opts.mobj_infotext[2])

        self.textbox.SetDefaultStyle(wx.TextAttr(self.mobj_infotext))
        self.textbox.AppendText("""Makeobj Interactive Window
Commands:
(Type ? at any time to view this information again,
type ?COMMAND to view more detailed information about a command)
    ls  - List Makeobj Working Directory
    cd  - Change Makeobj Working Directory
    pak - Compile pak file from dat file""")
        self.textbox.SetDefaultStyle(wx.TextAttr(self.mobj_inputtext))
        self.textbox.AppendText("""\n>>> """)

        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()

        self.panel_height = self.s_panel.GetSize().GetHeight()

    def OnEnter(self,e):
        """When the enter key is pressed in the text control,
        this is used to evaluate the makeobj command entered"""
        # Get last line...
        lastline = self.textbox.GetLineText(self.textbox.GetNumberOfLines()-1)
        # Strip the trailing newline (if there is one)
        if lastline[-1:] == "\r":
            lastline = lastline[:-1]
        app.debug_frame.WriteLine("Makeobj: InputLastLine = \"%s\""%lastline)
        if lastline in [""," ",">",">>",">>>",">>> "]:
            # Do nothing, refresh the last line
            self.textbox.AppendText("\n>>> ")
        else:
            a = 0
            while a == 0:
                # Strip off the ">>>"
                if lastline[0] in [" ", ">"]:
                    lastline = lastline[1:]
                else:
                    a = 1
            app.debug_frame.WriteLine("Makeobj: Evaluate = %s"%lastline)
            # Could put an interpreter layer here to pre-check Makeobj input
            # But not right now... Just pass the line into Makeobj
            returnvals = makeobj.Arb(lastline, quiet=self.firstrun_makeobj)
            self.firstrun_makeobj = 1

            # Finally append the return values to the text box and update the
            # text box display
            self.textbox.SetDefaultStyle(wx.TextAttr(self.mobj_outputtext))
            self.textbox.AppendText(returnvals[0])
            self.textbox.SetDefaultStyle(wx.TextAttr(self.mobj_errortext))
            self.textbox.AppendText(returnvals[1])
            self.textbox.SetDefaultStyle(wx.TextAttr(self.mobj_inputtext))
            self.textbox.AppendText("\n>>> ")

    def OnChangeText(self,e):
        """When the text in the text control changes"""
        if self.textbox.IsModified():
            if self.textbox.GetValue()[-1:] == "\n":
                self.textbox.Remove(len(self.textbox.GetValue())-1,len(self.textbox.GetValue()))
            self.textbox.SetInsertionPointEnd()
            self.textbox.ShowPosition(self.textbox.GetInsertionPoint())

class Makeobj:
    """Invoke makeobj with certain command line arguments, output from
    makeobj is directed to the makeobj log window where it is recorded
    (and may optionally be saved), each command sent to makeobj counts
    as a new line in the log window. This class defines several basic
    ways to interact with makeobj as well as allowing you to pass any
    arbitary string as a command to it. All commands pass QUIET as first
    arg to skip the copyright message (show this first time in each
    session though!)"""
    def __init__(self):
        """Initialisation parameters for this class"""
    def Arb(self, args, quiet=0):
        """Run arbitrary input to makeobj"""
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        if quiet == 1:
            quiett = "QUIET "
        else:
            quiett = ""
        retcode = subprocess.Popen("makeobj " + quiett + args,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   startupinfo=startupinfo)
        if quiet == 1:
            makeobj_output = "\n" + retcode.stdout.read()
        else:
            makeobj_output = retcode.stdout.read()
        makeobj_error = "\n" + retcode.stderr.read()
        return (makeobj_output, makeobj_error)

    def Pak(self, paksize, datfile, pakname=-1):
        """Compile a pak file from a source image and dat file, optionally takes
        a pakname argument to specify the name of the outputted .pak file, else uses
        default name"""
        # Makeobj works relative to its location, TileCutter works relative to *its*
        # location, so must ensure that both are in the same folder or this will get
        # complicated! Can specify a relative path to 
        if pakname == -1:
            # If no pakfile output path/name supplied, output it to the same
            # place as the datfile is
            pakname = os.path.split(datfile)
            # If the datfile is in this directory, set it to look here (so as
            # to avoid makeobj misinterpreting commands)
            if pakname == "":
                pakname = "./"
        retcode = subprocess.Popen(["makeobj","pak"+str(paksize), pakname, datfile],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        makeobj_output = retcode.stdout.read()
    def List(self):
        """List the contents of a pak file"""
    def Dump(self):
        """Dump the node info for a pak file"""
    def Merge(self):
        """Merge one or more pak files into a single pak file (also for renaming)"""
    def Extract(self):
        """Extract the individual pak files from a pak file archive"""
    def Unpak(self):
        """Unpak a pak file (experimental)"""
    


class FramesPanel(wx.Panel):
    """Interface for dealing with the multiple frames support"""
    def __init__(self,parent,placenum,id = -1,size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        # The frames are laid out as a tree control
        # Which mirrors the image fork of the project itself
        # Project
        #   |- Frame #1
        #   |       |- North
        #   |       |     |- SummerFront
        #   |       |     |- WinterFront
        #   |       |     |- SummerBack
        #   |       |     |- WinterBack
        #   |       |     |- Any other images that might be added
        #   |       |- South
        #   |       |- East
        #   |       |- West
        #   |- Frame #2
        #   |- Frame #3

        # The frame controls interact with the other set of controls
        # through the image displayer. 1) Call image displayer, 2) Displays
        # correct image, 3) sets controls to reflect image displayed

        # Frames can be ->
        #   Duplicated - copies all image data of the frame into another
        #   Moved - can move a frame back or forward in the list
        #   Deleted - obvious
        #   Created/Created in place - again, obvious


        # Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()
    def InitPanel(self):
        """Initialise the panel"""
        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()

        self.panel_height = self.s_panel.GetSize().GetHeight()


class DatPanel(scrolled.ScrolledPanel):
    """The dat editor panel"""
    def __init__(self,parent,placenum,type=0,id=-1,size=wx.DefaultSize):
        scrolled.ScrolledPanel.__init__(self, parent, id, (-1,-1), size=size)
        self.placenum = placenum
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        self.imres = self.GetGrandParent().GetParent().imres

        self.obj_choices = [gt("Building"), gt("Factory"), gt("Other")]
        self.tc_month_choices = ["",gt("January"),gt("Febuary"),gt("March"),gt("April"),gt("May"),gt("June"),
                            gt("July"),gt("August"),gt("September"),gt("October"),gt("November"),gt("December")]
        self.building_type_choices = ["", gt("carstop"),gt("busstop"),gt("station"),gt("monorailstop"),
                                      gt("harbour"),gt("wharf"),gt("airport"),gt("hall"),gt("post"),gt("shed"),
                                      gt("res"),gt("com"),gt("ind"),gt("any"),gt("misc"),gt("mon"),gt("cur"),
                                      gt("tow"),gt("hq")]
        self.building_type_choices_untrans = ["", "carstop","busstop","station","monorailstop",
                                      "harbour","wharf","airport","hall","post","shed",
                                      "res","com","ind","any","misc","mon","cur",
                                      "tow","hq"]
        # This panel may be displayed in the split panel or in a
        # seperate dialog box. Two different layouts are thus possible,
        # with all the sub-boxes in a vertical column (split panel)
        # or spaced equally (dialog)
        # In both cases each set of controls is put in its own box,
        # these boxes are then arranged differently

        # Object type selector
        self.select_obj_type = wx.RadioBox(self, -1,  gt("Object Type:"), (-1,-1),(-1,-1), self.obj_choices, 1, style=wx.RA_SPECIFY_ROWS)
        self.select_obj_type.SetToolTipString(gt("ttObject Type"))

        # Global options box ------------------------------------------------------------------------------------------------
        # Make an array to hold pointers to everything in this box (for enabling/disabling)
        self.global_controls = []
        self.s_global_box = wx.StaticBox(self, -1, gt("Global Options:"))
        self.global_controls.append(self.s_global_box)
        self.s_global = wx.StaticBoxSizer(self.s_global_box, wx.VERTICAL)

        self.s_global_flex= wx.FlexGridSizer(0,2,0,0)
        self.s_global_flex.AddGrowableCol(1)
        # All of these controls are added to the global_controls list
        # Name text box
        self.global_name_label = wx.StaticText(self, -1, gt("Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_name_label)
        #
        self.global_name = wx.TextCtrl(self, -1, value="", size=(-1,-1))
        self.global_name.SetToolTipString(gt("ttName"))
        self.global_controls.append(self.global_name)

        # Copyright text box
        self.global_copyright_label = wx.StaticText(self, -1, gt("Copyright:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_copyright_label)
        #
        self.global_copyright = wx.TextCtrl(self, -1, value="", size=(-1,-1))
        self.global_copyright.SetToolTipString(gt("ttCopyright"))
        self.global_controls.append(self.global_copyright)

        # Intro year/month controls
        self.global_intro_year_label = wx.StaticText(self, -1, gt("Introduced:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_intro_year_label)
        #
        self.global_intro_month = wx.ComboBox(self, -1, "", (-1, -1), (-1, -1), self.tc_month_choices, wx.CB_READONLY)
        self.global_controls.append(self.global_intro_month)
        self.global_intro_month.SetToolTipString(gt("ttIntroMonth"))
        #
        self.global_intro_year = masked.TextCtrl(self, -1, value="", size=(48,-1),
                                        formatcodes="S",fillChar=" ", mask="####", validRequired=1, validRange=(1,9999)
                                        )
        self.global_controls.append(self.global_intro_year)
        self.global_intro_year.SetToolTipString(gt("ttIntroYear"))

        # Retire year/month controls
        self.global_retire_year_label = wx.StaticText(self, -1, gt("Retires:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_retire_year_label)
        #
        self.global_retire_month = wx.ComboBox(self, -1, "", (-1, -1), (-1, -1), self.tc_month_choices, wx.CB_READONLY)
        self.global_retire_month.SetToolTipString(gt("ttRetiresMonth"))
        self.global_controls.append(self.global_retire_month)
        #
        self.global_retire_year = masked.TextCtrl(self, -1, value="", size=(48,-1),
                                        formatcodes="S",fillChar=" ", mask="####", validRequired=1, validRange=(1,9999)
                                        )
        self.global_retire_year.SetToolTipString(gt("ttRetiresYear"))
        self.global_controls.append(self.global_retire_year)

        # Level controls
        self.global_level_label = wx.StaticText(self, -1, gt("Level:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_level_label)
        self.global_level = masked.TextCtrl(self, -1, value="", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(1,99999)
                                        )
        self.global_level.SetToolTipString(gt("ttLevel"))
        self.global_controls.append(self.global_level)
        #
        self.global_level_info_label = wx.StaticText(self, -1, gt("Level Info:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_level_info_label)
        #
        self.global_level_info = wx.StaticText(self, -1, "level info line 1", (-1, -1), (-1, 15), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_level_info)
        #
        self.global_level_info2 = wx.StaticText(self, -1, "level info line 2", (-1, -1), (-1, 15), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_level_info2)

        # Flags
        self.global_flags_label = wx.StaticText(self, -1, gt("Flags:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.global_controls.append(self.global_flags_label)
        # No info checkbox
        self.global_noinfo = wx.CheckBox(self, -1, gt("No info"))
        self.global_noinfo.SetToolTipString(gt("ttNo info"))
        self.global_controls.append(self.global_noinfo)
        # No construction checkbox
        self.global_noconstruction = wx.CheckBox(self, -1, gt("No Construction"))
        self.global_noconstruction.SetToolTipString(gt("ttNo Construction"))
        self.global_controls.append(self.global_noconstruction)
        # Draw ground checkbox
        self.global_needsground = wx.CheckBox(self, -1, gt("Draw ground"))
        self.global_needsground.SetToolTipString(gt("ttDraw Ground"))
        self.global_controls.append(self.global_needsground)


        # Add the controls to the sizers
        self.s_global_flex.Add(self.global_name_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_flex.Add(self.global_name, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_global_flex.Add(self.global_copyright_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_flex.Add(self.global_copyright, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_global_flex.Add(self.global_intro_year_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_introyear = wx.BoxSizer(wx.HORIZONTAL)
        self.s_global_introyear.Add(self.global_intro_month, 1, wx.LEFT, 0)
        self.s_global_introyear.Add(self.global_intro_year, 0, wx.LEFT, 2)
        self.s_global_flex.Add(self.s_global_introyear, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_global_flex.Add(self.global_retire_year_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_retireyear = wx.BoxSizer(wx.HORIZONTAL)
        self.s_global_retireyear.Add(self.global_retire_month, 1, wx.LEFT, 0)
        self.s_global_retireyear.Add(self.global_retire_year, 0, wx.LEFT, 2)
        self.s_global_flex.Add(self.s_global_retireyear, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_global_flex.Add(self.global_level_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_flex.Add(self.global_level, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_global_flex.Add(self.global_level_info_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_levelinfo = wx.BoxSizer(wx.VERTICAL)
        self.s_global_levelinfo.Add(self.global_level_info, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_levelinfo.Add(self.global_level_info2, 0, wx.EXPAND|wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_global_flex.Add(self.s_global_levelinfo, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)


        self.s_global_flex.Add(self.global_flags_label, 0, wx.LEFT, 2)
        self.s_global_flags = wx.BoxSizer(wx.VERTICAL)
        self.s_global_flags.Add(self.global_noinfo, 0, wx.TOP, 0)
        self.s_global_flags.Add(self.global_noconstruction, 0, wx.TOP, 2)
        self.s_global_flags.Add(self.global_needsground, 0, wx.TOP, 2)
        self.s_global_flex.Add(self.s_global_flags, 0, wx.TOP|wx.LEFT, 2)

        self.s_global.Add(self.s_global_flex, 0, wx.EXPAND|wx.BOTTOM, 0)

        # Bind the controls to events
        self.select_obj_type.Bind(wx.EVT_RADIOBOX, self.OnSelectObjType, self.select_obj_type)

        self.global_name.Bind(wx.EVT_TEXT, self.OnChangeName, self.global_name)
        self.global_copyright.Bind(wx.EVT_TEXT, self.OnChangeCopyright, self.global_copyright)
        self.global_intro_month.Bind(wx.EVT_COMBOBOX, self.OnChangeIntroMonth, self.global_intro_month)
        self.global_intro_year.Bind(wx.EVT_TEXT, self.OnChangeIntroYear, self.global_intro_year)
        self.global_retire_month.Bind(wx.EVT_COMBOBOX, self.OnChangeRetireMonth, self.global_retire_month)
        self.global_retire_year.Bind(wx.EVT_TEXT, self.OnChangeRetireYear, self.global_retire_year)
        self.global_level.Bind(wx.EVT_TEXT, self.OnChangeLevel, self.global_level)
        self.global_noinfo.Bind(wx.EVT_CHECKBOX, self.OnChangeNoInfo, self.global_noinfo)
        self.global_noconstruction.Bind(wx.EVT_CHECKBOX, self.OnChangeNoConstruction, self.global_noconstruction)
        self.global_needsground.Bind(wx.EVT_CHECKBOX, self.OnChangeDrawGround, self.global_needsground)




        # Climates box ------------------------------------------------------------------------------------------------------
        # Make an array to hold pointers to everything in this box (for enabling/disabling)
        self.climates_controls = []
        self.s_climates_box = wx.StaticBox(self, -1, gt("Climate Options:"))
        self.s_climates = wx.StaticBoxSizer(self.s_climates_box, wx.VERTICAL)

        self.s_climates_flex = wx.GridSizer(0,2,0,0)

        self.climates_options_untrans = ["rocky", "tundra", "temperate", "mediterran", "desert", "arctic", "tropic", "water"]
        self.climates_options = [gt("rocky"), gt("tundra"), gt("temperate"), gt("mediterran"), gt("desert"), gt("arctic"),gt("tropic"), gt("water")]
        self.climates_optionstt = [gt("tt_rocky"), gt("tt_tundra"), gt("tt_temperate"), gt("tt_mediterran"), gt("tt_desert"),
                                   gt("tt_arctic"), gt("tt_tropic"), gt("tt_water")]

        # Climates checkboxes
        for x in range(8):
            # Create control
            self.climates_controls.append(wx.CheckBox(self, 2000 + x, self.climates_options[x]))
            self.climates_controls[x].SetToolTipString(self.climates_optionstt[x])
            # Add to sizer
            self.s_climates_flex.Add(self.climates_controls[x], 0, wx.TOP|wx.LEFT, 2)
            # Bind to event
            self.climates_controls[x].Bind(wx.EVT_CHECKBOX, self.OnChangeClimates, self.climates_controls[x])

        self.climates_controls.append(self.s_climates_box)

        # Finally add that sizer to the box sizer
        self.s_climates.Add(self.s_climates_flex, 0, wx.BOTTOM|wx.LEFT, 2)





        # Building options box ----------------------------------------------------------------------------------------------
        # Make an array to hold pointers to everything in this box (for enabling/disabling)
        self.building_controls = []
        self.s_building_box = wx.StaticBox(self, -1, gt("Building Options:"))
        self.building_controls.append(self.s_building_box)
        self.s_building = wx.StaticBoxSizer(self.s_building_box, wx.VERTICAL)

        self.building_location_options_untrans = ["","Land","City"]
        self.building_location_options = ["",gt("Land"),gt("City")]

        self.s_building_flex = wx.FlexGridSizer(0,2,0,0)

        # Building type
        self.building_type_label = wx.StaticText(self, -1, gt("Type:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.building_controls.append(self.building_type_label)
        self.building_type = wx.ComboBox(self, 5700, "", (-1, -1), (-1, -1), self.building_type_choices, wx.CB_READONLY)
        self.building_type.SetToolTipString(gt("ttType"))
        self.building_controls.append(self.building_type)
        # Building location
        self.building_locationbui_label = wx.StaticText(self, -1, gt("buiLocation:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.building_controls.append(self.building_locationbui_label)
        self.building_locationbui = wx.ComboBox(self, -1, "", (-1, -1), (-1, -1), self.building_location_options, wx.CB_READONLY)
        self.building_locationbui.SetToolTipString(gt("ttbuiLocation"))
        self.building_controls.append(self.building_locationbui)
        # Building chance
        self.building_chancebui_label = wx.StaticText(self, -1, gt("buiChance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.building_controls.append(self.building_chancebui_label)
        self.building_chancebui = masked.TextCtrl(self, -1, value="0", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                        )
        self.building_chancebui.SetToolTipString(gt("ttbuiChance"))
        self.building_controls.append(self.building_chancebui)
        # Build time
        self.building_build_time_label = wx.StaticText(self, -1, gt("Build Time:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.building_controls.append(self.building_build_time_label)
        self.building_build_time = masked.TextCtrl(self, -1, value="0", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="########", validRequired=1, validRange=(0,16777216)
                                        )
        self.building_build_time.SetToolTipString(gt("ttBuild Time"))
        self.building_controls.append(self.building_build_time)
        # Flags
        self.building_enables_label = wx.StaticText(self, -1, gt("Flags:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.building_controls.append(self.building_enables_label)
        self.building_extension = wx.CheckBox(self, -1, gt("Is Extension Building"))
        self.building_extension.SetToolTipString(gt("ttIs Extension Building"))
        self.building_controls.append(self.building_extension)
        self.building_enables_pax = wx.CheckBox(self, 2100, gt("EnablesPax"))
        self.building_enables_pax.SetToolTipString(gt("ttEnablesPax"))
        self.building_controls.append(self.building_enables_pax)
        self.building_enables_post = wx.CheckBox(self, 2101, gt("EnablesMail"))
        self.building_enables_post.SetToolTipString(gt("ttEnablesMail"))
        self.building_controls.append(self.building_enables_post)
        self.building_enables_ware = wx.CheckBox(self, 2102, gt("EnablesGoods"))
        self.building_enables_ware.SetToolTipString(gt("ttEnablesGoods"))
        self.building_controls.append(self.building_enables_ware)
        self.building_flags = []
        self.building_flags.append(self.building_enables_pax)
        self.building_flags.append(self.building_enables_post)
        self.building_flags.append(self.building_enables_ware)

                # Needs addition of cursor/icon selection system!!!
        # Add all the building stuff to sizers
        self.s_building_flex.Add(self.building_type_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_building_flex.Add(self.building_type, 0, wx.TOP|wx.LEFT, 2)

        self.s_building_flex.Add(self.building_locationbui_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_building_flex.Add(self.building_locationbui, 0, wx.TOP|wx.LEFT, 2)

        self.s_building_flex.Add(self.building_chancebui_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_building_flex.Add(self.building_chancebui, 0, wx.TOP|wx.LEFT, 2)

        self.s_building_flex.Add(self.building_build_time_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_building_flex.Add(self.building_build_time, 0, wx.TOP|wx.LEFT, 2)

        self.s_building_flex.Add(self.building_enables_label, 0, wx.LEFT, 2)
        self.s_building_enables = wx.BoxSizer(wx.VERTICAL)
        self.s_building_enables.Add(self.building_extension, 0, wx.TOP, 0)
        self.s_building_enables.Add(self.building_enables_pax, 0, wx.TOP, 2)
        self.s_building_enables.Add(self.building_enables_post, 0, wx.TOP, 2)
        self.s_building_enables.Add(self.building_enables_ware, 0, wx.TOP, 2)
        self.s_building_flex.Add(self.s_building_enables, 0, wx.TOP|wx.LEFT, 2)

        # Finally add that sizer to the box sizer
        self.s_building.Add(self.s_building_flex, 0, wx.TOP|wx.LEFT, 0)

        # Bind the controls to events
        self.building_type.Bind(wx.EVT_COMBOBOX, self.OnChangeBuildingType, self.building_type)
        self.building_locationbui.Bind(wx.EVT_COMBOBOX, self.OnChangeBuildingLocation, self.building_locationbui)
        self.building_chancebui.Bind(wx.EVT_TEXT, self.OnBuildingChance, self.building_chancebui)
        self.building_build_time.Bind(wx.EVT_TEXT, self.OnBuildingBuildTime, self.building_build_time)
        self.building_extension.Bind(wx.EVT_CHECKBOX, self.OnBuildingExtension, self.building_extension)
        self.building_enables_pax.Bind(wx.EVT_CHECKBOX, self.OnBuildingEnableFlags, self.building_enables_pax)
        self.building_enables_post.Bind(wx.EVT_CHECKBOX, self.OnBuildingEnableFlags, self.building_enables_post)
        self.building_enables_ware.Bind(wx.EVT_CHECKBOX, self.OnBuildingEnableFlags, self.building_enables_ware)




        # Factory options box -----------------------------------------------------------------------------------------------
        # Make an array to hold pointers to everything in this box (for enabling/disabling)
        self.factory_controls = []
        self.s_factory_box = wx.StaticBox(self, -1, gt("Factory Options:"))
        self.factory_controls.append(self.s_factory_box)
        self.s_factory = wx.StaticBoxSizer(self.s_factory_box, wx.VERTICAL)

        self.factory_location_options_untrans = ["","Land","City", "Water"]
        self.factory_location_options = ["",gt("Land"),gt("City"), gt("Water")]


        # Factory location
        self.factory_locationfac_label = wx.StaticText(self, -1, gt("facLocation:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_locationfac_label)
        self.factory_locationfac = wx.ComboBox(self, -1, "", (-1, -1), (-1, -1), self.factory_location_options, wx.CB_READONLY)
        self.factory_locationfac.SetToolTipString(gt("ttfacLocation"))
        self.factory_controls.append(self.factory_locationfac)
        # Factory chance
        self.factory_chancefac_label = wx.StaticText(self, -1, gt("facChance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_chancefac_label)
        self.factory_chancefac = masked.TextCtrl(self, -1, value="", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,100)
                                            )
        self.factory_chancefac.SetToolTipString(gt("ttfacChance"))
        self.factory_controls.append(self.factory_chancefac)
        # Factory productivity
        self.factory_productivity_label = wx.StaticText(self, -1, gt("Productivity:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_productivity_label)
        self.factory_productivity = masked.TextCtrl(self, -1, value="", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                            )
        self.factory_productivity.SetToolTipString(gt("ttProductivity"))
        self.factory_controls.append(self.factory_productivity)
        # Factory range
        self.factory_range_label = wx.StaticText(self, -1, "+/-", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_range_label)
        self.factory_range = masked.TextCtrl(self, -1, value="", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                            )
        self.factory_range.SetToolTipString(gt("ttRange"))
        self.factory_controls.append(self.factory_range)
        # Factory mapcolour
        self.factory_mapcolour_label = wx.StaticText(self, -1, gt("Map Colour:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_mapcolour_label)
        self.factory_mapcolour = masked.TextCtrl(self, -1, value="", size=(50,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,255)
                                            )
        self.factory_mapcolour.SetToolTipString(gt("ttMap Colour"))
        self.factory_controls.append(self.factory_mapcolour)
        self.factory_mapcolour_display = wx.StaticText(self, -1, "", (-1,-1),(30,21),wx.SIMPLE_BORDER)
##        self.factory_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.factory_mapcolour.GetValue()))))
        self.factory_mapcolour_display.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.factory_mapcolour_display.SetToolTipString(gt("ttMap Colour Display"))
        self.factory_controls.append(self.factory_mapcolour_display)


        # Input list
        self.factory_input_label = wx.StaticText(self, -1, gt("Input Goods:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_input_label)
        self.factory_input = wx.ListBox(self, -1, (-1,-1), (1, -1), "", wx.LB_SINGLE)
        self.factory_input.SetToolTipString(gt("ttInput Goods:"))
        self.factory_controls.append(self.factory_input)
        self.factory_input_add = wx.Button(self, -1, "+", (-1,-1), (-1,16), wx.BU_EXACTFIT)
        self.factory_input_add.SetToolTipString(gt("ttAdd input good"))
        self.factory_controls.append(self.factory_input_add)
        self.factory_input_remove = wx.Button(self, -1, "-", (-1,-1), (-1,16), wx.BU_EXACTFIT)
        self.factory_input_remove.SetToolTipString(gt("ttRemove input good"))
        self.factory_controls.append(self.factory_input_remove)
        self.input_controls_adv = []
        self.input_controls_adv.append(self.factory_input_remove)
        self.factory_input_up = wx.BitmapButton(self, -1, self.imres.up, (-1,-1), (-1,16))
        self.factory_input_up.SetToolTipString(gt("ttMove input good up"))
        self.factory_controls.append(self.factory_input_up)
        self.input_controls_adv.append(self.factory_input_up)
        self.factory_input_down = wx.BitmapButton(self, -1, self.imres.down, (-1,-1), (-1,16))
        self.factory_input_down.SetToolTipString(gt("ttMove input good down"))
        self.factory_controls.append(self.factory_input_down)
        self.input_controls_adv.append(self.factory_input_down)

        # Output list
        self.factory_output_label = wx.StaticText(self, -1, gt("Output Goods:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_output_label)
        self.factory_output = wx.ListBox(self, -1, (-1,-1), (1, -1), "", wx.LB_SINGLE)
        self.factory_output.SetToolTipString(gt("ttOutput Goods:"))
        self.factory_controls.append(self.factory_output)
        self.factory_output_add = wx.Button(self, -1, "+", (-1,-1), (-1,16), wx.BU_EXACTFIT)
        self.factory_output_add.SetToolTipString(gt("ttAdd output good"))
        self.factory_controls.append(self.factory_output_add)
        self.factory_output_remove = wx.Button(self, -1, "-", (-1,-1), (-1,16), wx.BU_EXACTFIT)
        self.factory_output_remove.SetToolTipString(gt("ttRemove output good"))
        self.factory_controls.append(self.factory_output_remove)
        self.output_controls_adv = []
        self.output_controls_adv.append(self.factory_output_remove)
        self.factory_output_up = wx.BitmapButton(self, -1, self.imres.up, (-1,-1), (-1,16))
        self.factory_output_up.SetToolTipString(gt("ttMove output good up"))
        self.factory_controls.append(self.factory_output_up)
        self.output_controls_adv.append(self.factory_output_up)
        self.factory_output_down = wx.BitmapButton(self, -1, self.imres.down, (-1,-1), (-1,16))
        self.factory_output_down.SetToolTipString(gt("ttMove output good down"))
        self.factory_controls.append(self.factory_output_down)
        self.output_controls_adv.append(self.factory_output_down)


        # Input/Output edit controls
        self.factory_edit_label = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_edit_label)
        # Good name
        self.factory_edit_good_label = wx.StaticText(self, -1, gt("good Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_edit_good_label)
        self.factory_edit_good = wx.TextCtrl(self, -1, value="", size=(-1,-1))
        self.factory_edit_good.SetToolTipString(gt("ttgood Name:"))
        self.factory_controls.append(self.factory_edit_good)
        self.inout_controls = []
        self.inout_controls.append(self.factory_edit_good)
        # Good capacity
        self.factory_edit_capacity_label = wx.StaticText(self, -1, gt("good Capacity:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_edit_capacity_label)
        self.factory_edit_capacity = masked.TextCtrl(self, -1, value="0", size=(-1,-1),
                                                formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,99999)
                                                )
        self.factory_edit_capacity.SetToolTipString(gt("ttgood Capacity:"))
        self.factory_controls.append(self.factory_edit_capacity)
        self.inout_controls.append(self.factory_edit_capacity)
        # Good factor
        self.factory_edit_factor_label = wx.StaticText(self, -1, gt("good Factor:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_edit_factor_label)
        self.factory_edit_factor = masked.TextCtrl(self, -1, value="0", size=(-1,-1),
                                                formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,99999)
                                                )
        self.factory_edit_factor.SetToolTipString(gt("ttgood Factor:"))
        self.factory_controls.append(self.factory_edit_factor)
        self.inout_controls.append(self.factory_edit_factor)
        # Good suppliers
        self.factory_edit_suppliers_label = wx.StaticText(self, -1, gt("good Suppliers:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.factory_controls.append(self.factory_edit_suppliers_label)
        self.factory_edit_suppliers = masked.TextCtrl(self, -1, value="0", size=(-1,-1),
                                                    formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,999)
                                                    )
        self.factory_edit_suppliers.SetToolTipString(gt("ttgood Suppliers:"))
        self.factory_controls.append(self.factory_edit_suppliers)
        self.inout_controls.append(self.factory_edit_suppliers)

        self.s_factory_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_factory_flex.AddGrowableCol(1,0)

        # Add things to sizers
        self.s_factory_flex.Add(self.factory_locationfac_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex.Add(self.factory_locationfac, 1, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex.Add(self.factory_chancefac_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex.Add(self.factory_chancefac, 1, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex.Add(self.factory_productivity_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_prodrange = wx.BoxSizer(wx.HORIZONTAL)
        self.s_factory_prodrange.Add(self.factory_productivity, 1, wx.EXPAND|wx.TOP|wx.LEFT, 0)
        self.s_factory_prodrange.Add(self.factory_range_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_prodrange.Add(self.factory_range, 1, wx.EXPAND|wx.TOP|wx.LEFT, 0)
        self.s_factory_flex.Add(self.s_factory_prodrange, 1, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex.Add(self.factory_mapcolour_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_mapcolour = wx.BoxSizer(wx.HORIZONTAL)
        self.s_factory_mapcolour.Add(self.factory_mapcolour, 1, wx.EXPAND|wx.TOP|wx.LEFT, 0)
        self.s_factory_mapcolour.Add(self.factory_mapcolour_display, 0, wx.TOP|wx.LEFT, 0)
        self.s_factory_flex.Add(self.s_factory_mapcolour, 1, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_inout = wx.FlexGridSizer(0,2,0,0)
        self.s_factory_inout.AddGrowableCol(0,0)
        self.s_factory_inout.AddGrowableCol(1,0)
        self.s_factory_inout.Add(self.factory_input_label, 0, wx.TOP, 0)
        self.s_factory_inout.Add(self.factory_output_label, 0, wx.TOP, 0)

        self.s_factory_inout.Add(self.factory_input, 0, wx.EXPAND|wx.TOP, 2)
        self.s_factory_inout.Add(self.factory_output, 0, wx.EXPAND|wx.TOP, 2)

        self.s_factory_inputcontrols = wx.BoxSizer(wx.HORIZONTAL)
        self.s_factory_inputcontrols.Add(self.factory_input_add, 1, wx.LEFT, 0)
        self.s_factory_inputcontrols.Add(self.factory_input_remove, 1, wx.LEFT, 0)
        self.s_factory_inputcontrols.Add(self.factory_input_up, 1, wx.LEFT, 0)
        self.s_factory_inputcontrols.Add(self.factory_input_down, 1, wx.RIGHT, 0)
        self.s_factory_inout.Add(self.s_factory_inputcontrols, 0, wx.EXPAND|wx.TOP, 2)

        self.s_factory_outputcontrols = wx.BoxSizer(wx.HORIZONTAL)
        self.s_factory_outputcontrols.Add(self.factory_output_add, 1, wx.LEFT, 0)
        self.s_factory_outputcontrols.Add(self.factory_output_remove, 1, wx.LEFT, 0)
        self.s_factory_outputcontrols.Add(self.factory_output_up, 1, wx.LEFT, 0)
        self.s_factory_outputcontrols.Add(self.factory_output_down, 1, wx.RIGHT, 0)
        self.s_factory_inout.Add(self.s_factory_outputcontrols, 0, wx.EXPAND|wx.TOP, 2)

        self.s_factory_flex_bottom = wx.FlexGridSizer(0,2,0,0)
        self.s_factory_flex_bottom.AddGrowableCol(1,0)

        self.s_factory_flex_bottom.Add(self.factory_edit_good_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex_bottom.Add(self.factory_edit_good, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex_bottom.Add(self.factory_edit_capacity_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex_bottom.Add(self.factory_edit_capacity, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex_bottom.Add(self.factory_edit_factor_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex_bottom.Add(self.factory_edit_factor, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        self.s_factory_flex_bottom.Add(self.factory_edit_suppliers_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_factory_flex_bottom.Add(self.factory_edit_suppliers, 0, wx.EXPAND|wx.TOP|wx.LEFT, 2)

        # Finally add that sizer to the box sizer
        self.s_factory.Add(self.s_factory_flex, 1, wx.EXPAND|wx.TOP, 0)
        self.s_factory.Add(self.s_factory_inout, 1, wx.EXPAND|wx.TOP, 2)
        self.s_factory.Add(self.s_factory_flex_bottom, 1, wx.EXPAND|wx.TOP, 2)

        # Factory things bind to events
        # Factory global options events
        self.factory_locationfac.Bind(wx.EVT_COMBOBOX, self.OnFactoryLocation, self.factory_locationfac)
        self.factory_chancefac.Bind(wx.EVT_TEXT, self.OnFactoryChance, self.factory_chancefac)
        self.factory_productivity.Bind(wx.EVT_TEXT, self.OnFactoryProductivity, self.factory_productivity)
        self.factory_range.Bind(wx.EVT_TEXT, self.OnFactoryRange, self.factory_range)
        self.factory_mapcolour.Bind(wx.EVT_TEXT, self.OnFactoryMapcolourText, self.factory_mapcolour)
        self.factory_mapcolour_display.Bind(wx.EVT_LEFT_DOWN, self.OnFactoryMapcolourClick, self.factory_mapcolour_display)
        # Input list events
        self.factory_input.Bind(wx.EVT_LISTBOX, self.OnFactoryInputListboxSelect, self.factory_input)
        self.factory_input_add.Bind(wx.EVT_BUTTON, self.OnFactoryInputListboxAdd, self.factory_input_add)
        self.factory_input_remove.Bind(wx.EVT_BUTTON, self.OnFactoryInputListboxRemove, self.factory_input_remove)
        self.factory_input_up.Bind(wx.EVT_BUTTON, self.OnFactoryInputListboxUp, self.factory_input_up)
        self.factory_input_down.Bind(wx.EVT_BUTTON, self.OnFactoryInputListboxDown, self.factory_input_down)
        # Output list events
        self.factory_output.Bind(wx.EVT_LISTBOX, self.OnFactoryOutputListboxSelect, self.factory_output)
        self.factory_output_add.Bind(wx.EVT_BUTTON, self.OnFactoryOutputListboxAdd, self.factory_output_add)
        self.factory_output_remove.Bind(wx.EVT_BUTTON, self.OnFactoryOutputListboxRemove, self.factory_output_remove)
        self.factory_output_up.Bind(wx.EVT_BUTTON, self.OnFactoryOutputListboxUp, self.factory_output_up)
        self.factory_output_down.Bind(wx.EVT_BUTTON, self.OnFactoryOutputListboxDown, self.factory_output_down)
        # Input/Output edit control events
        self.factory_edit_good.Bind(wx.EVT_TEXT, self.OnFactoryEditGood, self.factory_edit_good)
        self.factory_edit_capacity.Bind(wx.EVT_TEXT, self.OnFactoryEditCapacity, self.factory_edit_capacity)
        self.factory_edit_factor.Bind(wx.EVT_TEXT, self.OnFactoryEditFactor, self.factory_edit_factor)
        self.factory_edit_suppliers.Bind(wx.EVT_TEXT, self.OnFactoryEditSuppliers, self.factory_edit_suppliers)


        # Additional options box --------------------------------------------------------------------------------------------
        self.s_additional_box = wx.StaticBox(self, -1, gt("Additional Options:"))
        self.s_additional = wx.StaticBoxSizer(self.s_additional_box, wx.VERTICAL)

        self.additional_ops = wx.TextCtrl(self, -1, "", (-1,-1),(-1,150), wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_RICH)
        self.additional_ops.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.additional_ops.SetToolTipString(gt("ttAdditional Options:"))

        self.s_additional.Add(self.additional_ops, 1, wx.EXPAND|wx.TOP|wx.LEFT, 0)

        self.additional_ops.Bind(wx.EVT_TEXT, self.OnAdditionalOptions, self.additional_ops)


        if type == 0:
            # If type is 0, then layout for the split panel
            self.s_panel.Add(self.select_obj_type, 0, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER, 4)
            self.s_panel.Add(self.s_global, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 4)
            self.s_panel.Add(self.s_climates, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 4)
            self.s_panel.Add(self.s_building, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 4)
            self.s_panel.Add(self.s_factory, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER, 4)
            self.s_panel.Add(self.s_additional, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER, 4)
##        elif type == 1:
            # If type is 1, then layout for the dialog

        # Layout sizers
        self.SetSizer(self.s_panel)
        self.Layout()

    def InitPanel(self):
        """Initialise the dat panel, call on first creation of the panel"""
        self.active = self.GetGrandParent().GetParent().active
        self.ActivateDatPanel(1)

        self.SetupScrolling()
        self.options = self.GetGrandParent().GetParent().options
        if self.options.sidebar_minwidths[self.placenum] == -1:
            self.options.sidebar_minwidths[self.placenum] = self.s_panel.GetSize().GetWidth()
        if self.options.sidebar_widths[self.placenum] == -1:
            self.options.sidebar_widths[self.placenum] = self.s_panel.GetSize().GetWidth()

        self.panel_height = self.s_panel.GetSize().GetHeight()

    # Global Options Functions
    def OnChangeName(self,e):
        """On Text change in the "Name" field"""
        if self.global_name.IsModified():
            self.active.datfile.obj_name = self.global_name.GetValue()
        app.debug_frame.WriteLine("Datfile: Name = %s"%self.active.datfile.obj_name)
    def OnChangeCopyright(self,e):
        """On Text change in the "Copyright" field"""
        if self.global_copyright.IsModified():
            self.active.datfile.obj_copyright = self.global_copyright.GetValue()
        app.debug_frame.WriteLine("Datfile: Copyright = %s"%self.active.datfile.obj_copyright)
    def OnChangeIntroMonth(self,e):
        """On Selection change in the "IntroMonth" field"""
        # Value in combobox needs to be translated into an int value
        self.active.datfile.obj_intromonth = self.tc_month_choices.index(self.global_intro_month.GetValue())
        app.debug_frame.WriteLine("Datfile: Intromonth = %i"%self.active.datfile.obj_intromonth)
    def OnChangeIntroYear(self,e):
        """On Text change in the "IntroYear" field"""
        if self.global_intro_year.IsModified():
            self.active.datfile.obj_introyear = int(self.global_intro_year.GetValue())
        app.debug_frame.WriteLine("Datfile: Introyear = %i"%self.active.datfile.obj_introyear)
    def OnChangeRetireMonth(self,e):
        """On Selection change in the "RetireMonth" field"""
        # Value in combobox needs to be translated into an int value
        self.active.datfile.obj_retiremonth = self.tc_month_choices.index(self.global_retire_month.GetValue())
        app.debug_frame.WriteLine("Datfile: Retiremonth = %i"%self.active.datfile.obj_retiremonth)
    def OnChangeRetireYear(self,e):
        """On Text change in the "RetireYear" field"""
        if self.global_retire_year.IsModified():
            self.active.datfile.obj_retireyear = int(self.global_retire_year.GetValue())
        app.debug_frame.WriteLine("Datfile: Retireyear = %i"%self.active.datfile.obj_retireyear)
    def OnChangeLevel(self,e):
        """On Text change in the "Level" field"""
        if self.global_level.IsModified():
            if self.global_level.GetValue() in ["", "     "]:
                self.active.datfile.obj_level = 0
            else:
                self.active.datfile.obj_level = int(self.global_level.GetValue())
        self.LevelInfoTextChange()
        app.debug_frame.WriteLine("Datfile: Level = %i"%self.active.datfile.obj_level)
    def OnChangeNoInfo(self,e):
        """On NoInfo checkbox toggle"""
        self.active.datfile.obj_noinfo = self.global_noinfo.GetValue()
        app.debug_frame.WriteLine("Datfile: Noinfo = %i"%self.active.datfile.obj_noinfo)
    def OnChangeNoConstruction(self,e):
        """On NoConstruction checkbox toggle"""
        self.active.datfile.obj_noconstruction = self.global_noconstruction.GetValue()
        app.debug_frame.WriteLine("Datfile: Noconstruction = %i"%self.active.datfile.obj_noconstruction)
    def OnChangeDrawGround(self,e):
        """On DrawGround checkbox toggle"""
        self.active.datfile.obj_drawground = self.global_needsground.GetValue()
        app.debug_frame.WriteLine("Datfile: DrawGround = %i"%self.active.datfile.obj_drawground)

    # Climate Options Functions
    def OnChangeClimates(self,e):
        """On check/uncheck of any of the climate checkboxes"""
        a = e.GetId() - 2000
        self.active.datfile.obj_climates[a] = self.climates_controls[a].GetValue()
        app.debug_frame.WriteLine("Datfile: Climates = " + str(self.active.datfile.obj_climates))

    # Building Options Functions
    def OnChangeBuildingType(self,e):
        """On Selection change in the Building Type field"""
        self.active.datfile.obj_bui_type = self.building_type_choices.index(self.building_type.GetValue())
        self.BuildingTypeDisable()
        self.LevelInfoTextChange()
        app.debug_frame.WriteLine("Datfile: BuiType = %i"%self.active.datfile.obj_bui_type)
    def OnChangeBuildingLocation(self,e):
        """On Selection change in the Building Location field"""
        self.active.datfile.obj_bui_location = self.building_location_options.index(self.building_locationbui.GetValue())
        self.BuildingTypeDisable()
        app.debug_frame.WriteLine("Datfile: BuiLocation = %i"%self.active.datfile.obj_bui_location)
    def OnBuildingChance(self,e):
        """On Text change in the Building Chance field"""
        if self.building_chancebui.IsModified():
            self.active.datfile.obj_bui_chance = int(self.building_chancebui.GetValue())
        app.debug_frame.WriteLine("Datfile: BuiChance = %i"%self.active.datfile.obj_bui_chance)
    def OnBuildingBuildTime(self,e):
        """On Text change in the Building Build Time field"""
        if self.building_build_time.IsModified():
            self.active.datfile.obj_bui_buildtime = int(self.building_build_time.GetValue())
        app.debug_frame.WriteLine("Datfile: BuiChance = %i"%self.active.datfile.obj_bui_buildtime)
    def OnBuildingExtension(self,e):
        """On ExtensionBuilding checkbox toggle"""
        self.active.datfile.obj_bui_extension = self.building_extension.GetValue()
        app.debug_frame.WriteLine("Datfile: BuiExtension = %i"%self.active.datfile.obj_bui_extension)
    def OnBuildingEnableFlags(self,e):
        """On toggle of the "enables" flag checkboxes"""
        a = e.GetId() - 2100
        self.active.datfile.obj_bui_enableflags[a] = self.building_flags[a].GetValue()
        app.debug_frame.WriteLine("Datfile: BuildingFlags = " + str(self.active.datfile.obj_bui_enableflags))

    # Factory Options Functions
    # Factory edit control events
    def OnFactoryLocation(self,e):
        """On selection of an item in the factory location combobox"""
        self.active.datfile.obj_fac_location = self.factory_location_options.index(self.factory_locationfac.GetValue())
        app.debug_frame.WriteLine("Datfile: FactoryLocation = %i"%self.active.datfile.obj_fac_location)
    def OnFactoryChance(self,e):
        """On text entry in the factory chance box"""
        if self.factory_chancefac.IsModified():
            if self.factory_chancefac.GetValue() in ["", "   "]:
                self.active.datfile.obj_fac_chance = 0
            else:
                self.active.datfile.obj_fac_chance = int(self.factory_chancefac.GetValue())
        app.debug_frame.WriteLine("Datfile: FactoryChance = %i"%self.active.datfile.obj_fac_chance)
    def OnFactoryProductivity(self,e):
        """On text entry in the factory productivity box"""
        if self.factory_productivity.IsModified():
            if self.factory_productivity.GetValue() in ["", "     "]:
                self.active.datfile.obj_fac_productivity = 0
            else:
                self.active.datfile.obj_fac_productivity = int(self.factory_productivity.GetValue())
        app.debug_frame.WriteLine("Datfile: FactoryProductivity = %i"%self.active.datfile.obj_fac_productivity)
    def OnFactoryRange(self,e):
        """On text entry in the factory range box"""
        if self.factory_range.IsModified():
            if self.factory_range.GetValue() in ["", "     "]:
                self.active.datfile.obj_fac_range = 0
            else:
                self.active.datfile.obj_fac_range = int(self.factory_range.GetValue())
        app.debug_frame.WriteLine("Datfile: FactoryRange = %i"%self.active.datfile.obj_fac_range)
    def OnFactoryMapcolourText(self,e):
        """On text entry to the map colour picker box"""
        if self.factory_mapcolour.IsModified():
            if self.factory_mapcolour.GetValue() in ["", "   "]:
                self.active.datfile.obj_fac_mapcolour = 0
            else:
                self.active.datfile.obj_fac_mapcolour = int(self.factory_mapcolour.GetValue())
        app.debug_frame.WriteLine("Datfile: FactoryMapColour = %i"%self.active.datfile.obj_fac_mapcolour)
    def OnFactoryMapcolourClick(self,e):
        """Open the colour picker dialog box"""

    # Input/Output listbox events

    def InputListDisplay(self, redraw=1):
        """Display the updated inputs list"""
        selected = self.active.datfile.obj_active_good_selection
        # Now set the output goods box to not have anything selected
        self.factory_output.SetSelection(wx.NOT_FOUND)
        if redraw == 1:
            # By default redraw the entire list, but sometimes we don't want to
            self.UpdateInputList()
            # Set the active selection
            if selected == -1:
                self.factory_input.SetSelection(wx.NOT_FOUND)
            else:
                self.factory_input.SetSelection(selected)
        # Now update the input fields
        if selected == -1:
            for x in range(len(self.inout_controls)):
                for y in range(len(self.inout_controls)):
                    self.inout_controls[y].Enable(False)
                self.inout_controls[x].SetValue("")
        else:
            for x in range(len(self.inout_controls)):
                self.inout_controls[x].Enable(True)
            self.factory_edit_good.SetValue(self.active.datfile.obj_fac_inputs[selected].name)
            self.factory_edit_capacity.SetValue(str(self.active.datfile.obj_fac_inputs[selected].capacity))
            self.factory_edit_factor.SetValue(str(self.active.datfile.obj_fac_inputs[selected].factor))
            self.factory_edit_suppliers.SetValue(str(self.active.datfile.obj_fac_inputs[selected].suppliers))

    def OutputListDisplay(self,redraw=1):
        """Display the updated outputs list"""
        selected = self.active.datfile.obj_active_good_selection
        # Now set the input goods box to not have anything selected
        self.factory_input.SetSelection(wx.NOT_FOUND)
        if redraw == 1:
            self.UpdateOutputList()
            # Set the active selection
            if selected == -1:
                self.factory_output.SetSelection(wx.NOT_FOUND)
            else:
                self.factory_output.SetSelection(selected)
        # Now update the output fields
        if selected == -1:
            for x in range(len(self.inout_controls)):
                for y in range(len(self.inout_controls)):
                    self.inout_controls[y].Enable(False)
                self.inout_controls[x].SetValue("")
        else:
            for x in range(len(self.inout_controls)-1):
                self.inout_controls[x].Enable(True)
            self.inout_controls[len(self.inout_controls)-1].Enable(False)
            self.factory_edit_good.SetValue(self.active.datfile.obj_fac_outputs[selected].name)
            self.factory_edit_capacity.SetValue(str(self.active.datfile.obj_fac_outputs[selected].capacity))
            self.factory_edit_factor.SetValue(str(self.active.datfile.obj_fac_outputs[selected].factor))
            self.factory_edit_suppliers.SetValue("")

    def UpdateInputList(self):
        """Update the input list"""
        # Set the items in the list & display them
        display_list = []
        for x in range(len(self.active.datfile.obj_fac_inputs)):
            display_list.append("Good #%i:%s"%(x,self.active.datfile.obj_fac_inputs[x].name))
        self.factory_input.Set(display_list)
        self.factory_input.SetSelection(self.active.datfile.obj_active_good_selection)
    def UpdateOutputList(self):
        """Update the output list"""
        # Set the items in the list & display them
        display_list = []
        for x in range(len(self.active.datfile.obj_fac_outputs)):
            display_list.append("Good #%i:%s"%(x,self.active.datfile.obj_fac_outputs[x].name))
        self.factory_output.Set(display_list)
        self.factory_output.SetSelection(self.active.datfile.obj_active_good_selection)

    def OnFactoryInputListboxSelect(self,e):
        """On selection of an item in the input list"""
        # Active good setting, 0 = input, 1 = output
        self.active.datfile.obj_active_good = 0
        selected = self.factory_input.GetSelection()
        if selected == wx.NOT_FOUND:
            self.active.datfile.obj_active_good_selection = -1
        else:
            self.active.datfile.obj_active_good_selection = selected
        self.InputListDisplay(0)
    def OnFactoryOutputListboxSelect(self,e):
        """On selection of an item in the output list"""
        # Active good setting, 0 = input, 1 = output
        self.active.datfile.obj_active_good = 1
        selected = self.factory_output.GetSelection()
        if selected == wx.NOT_FOUND:
            self.active.datfile.obj_active_good_selection = -1
        else:
            self.active.datfile.obj_active_good_selection = selected
        self.OutputListDisplay(0)


    def OnFactoryInputListboxAdd(self,e):
        """Add an item to the factory input list & re-display the box"""
        if self.factory_input.GetSelection() == wx.NOT_FOUND:
            self.active.datfile.obj_fac_inputs.append(Good("blah"))
            self.active.datfile.obj_active_good_selection = len(self.active.datfile.obj_fac_inputs) - 1
        else:
            selected = self.factory_input.GetSelection() + 1
            self.active.datfile.obj_fac_inputs.insert(selected, Good("meh"))
            self.active.datfile.obj_active_good_selection = selected
        for x in range(len(self.input_controls_adv)):
            self.input_controls_adv[x].Enable(True)
        self.InputListDisplay()
        app.debug_frame.WriteLine("Datfile: InputGood Add")

    def OnFactoryInputListboxRemove(self,e):
        """Remove an item from the factory input list & re-display the box"""
        selected = self.factory_input.GetSelection()
        # If other list selected when remove good clicked, then remove the last one
        if selected == wx.NOT_FOUND:
            selected = len(self.active.datfile.obj_fac_inputs) - 1
        self.active.datfile.obj_fac_inputs.pop(selected)
        if len(self.active.datfile.obj_fac_inputs) - 1 < selected:
            selected -= 1
        if len(self.active.datfile.obj_fac_inputs) == 0:
            # If nothing left in this box disable adv. controls
            for x in range(len(self.input_controls_adv)):
                self.input_controls_adv[x].Enable(False)
            # Check if other box has anything in it, and if so switch to that
            self.active.datfile.obj_active_good_selection = selected
            self.InputListDisplay()
            if len(self.active.datfile.obj_fac_outputs) != 0:
                selected = len(self.active.datfile.obj_fac_outputs) - 1
                self.active.datfile.obj_active_good = 1
                self.active.datfile.obj_active_good_selection = selected
                self.OutputListDisplay()
        else:
            self.active.datfile.obj_active_good_selection = selected
            self.InputListDisplay()
    def OnFactoryOutputListboxRemove(self,e):
        """Remove an item from the factory output list & re-display the box"""
        selected = self.factory_output.GetSelection()
        # If other list selected when remove good clicked, then remove the last one
        if selected == wx.NOT_FOUND:
            selected = len(self.active.datfile.obj_fac_outputs) - 1
        self.active.datfile.obj_fac_outputs.pop(selected)
        if len(self.active.datfile.obj_fac_outputs) - 1 < selected:
            selected -= 1
        if len(self.active.datfile.obj_fac_outputs) == 0:
            # If nothing left in this box disable adv. controls
            for x in range(len(self.output_controls_adv)):
                self.output_controls_adv[x].Enable(False)
            # Check if other box has anything in it, and if so switch to that
            self.active.datfile.obj_active_good_selection = selected
            self.OutputListDisplay()
            if len(self.active.datfile.obj_fac_inputs) != 0:
                selected = len(self.active.datfile.obj_fac_inputs) - 1
                self.active.datfile.obj_active_good = 0
                self.active.datfile.obj_active_good_selection = selected
                self.InputListDisplay()
        else:
            self.active.datfile.obj_active_good_selection = selected
            self.OutputListDisplay()

    def OnFactoryInputListboxUp(self,e):
        """"""
    def OnFactoryInputListboxDown(self,e):
        """"""


    def OnFactoryOutputListboxAdd(self,e):
        """Add an item to the factory output list & re-display the box"""
        if self.factory_output.GetSelection() == wx.NOT_FOUND:
            self.active.datfile.obj_fac_outputs.append(Good("blah"))
            self.active.datfile.obj_active_good_selection = len(self.active.datfile.obj_fac_outputs) - 1
        else:
            selected = self.factory_output.GetSelection() + 1
            self.active.datfile.obj_fac_outputs.insert(selected, Good("meh"))
            self.active.datfile.obj_active_good_selection = selected
        for x in range(len(self.output_controls_adv)):
            self.output_controls_adv[x].Enable(True)
        self.OutputListDisplay()
        app.debug_frame.WriteLine("Datfile: InputGood Add")


    def OnFactoryOutputListboxUp(self,e):
        """"""
    def OnFactoryOutputListboxDown(self,e):
        """"""

    # Input/Output edit control events
    def OnFactoryEditGood(self,e):
        """On change of the Good name box"""
        if self.factory_edit_good.IsModified():
            if self.active.datfile.obj_active_good == 0:
                self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].name = self.factory_edit_good.GetValue()
                self.UpdateInputList()
            else:
                self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].name = self.factory_edit_good.GetValue()
                self.UpdateOutputList()
        app.debug_frame.WriteLine("Datfile: FactoryEditGood")
    def OnFactoryEditCapacity(self,e):
        """On change of the Edit Capacity text box"""
        if self.factory_edit_capacity.IsModified():
            if self.factory_edit_capacity.GetValue() in ["", "     "]:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].capacity = 0
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].capacity = 0
                    self.UpdateOutputList()
            else:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].capacity = int(self.factory_edit_capacity.GetValue())
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].capacity = int(self.factory_edit_capacity.GetValue())
                    self.UpdateOutputList()
        app.debug_frame.WriteLine("Datfile: FactoryEditCapacity")
    def OnFactoryEditFactor(self,e):
        """On change of the Edit Factor text box"""
        if self.factory_edit_factor.IsModified():
            if self.factory_edit_factor.GetValue() in ["", "     "]:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].factor = 0
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].factor = 0
                    self.UpdateOutputList()
            else:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].factor = int(self.factory_edit_factor.GetValue())
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].factor = int(self.factory_edit_factor.GetValue())
                    self.UpdateOutputList()
        app.debug_frame.WriteLine("Datfile: FactoryEditFactor")
    def OnFactoryEditSuppliers(self,e):
        """On change of the Edit Suppliers text box"""
        if self.factory_edit_suppliers.IsModified():
            if self.factory_edit_suppliers.GetValue() in ["", "   "]:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].suppliers = 0
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].suppliers = 0
                    self.UpdateOutputList()
            else:
                if self.active.datfile.obj_active_good == 0:
                    self.active.datfile.obj_fac_inputs[self.active.datfile.obj_active_good_selection].suppliers = int(self.factory_edit_suppliers.GetValue())
                    self.UpdateInputList()
                else:
                    self.active.datfile.obj_fac_outputs[self.active.datfile.obj_active_good_selection].suppliers = int(self.factory_edit_suppliers.GetValue())
                    self.UpdateOutputList()
        app.debug_frame.WriteLine("Datfile: FactoryEditSuppliers")

    # Additional Options Functions
    def OnAdditionalOptions(self,e):
        """Saves the text in the additional options box when it changes"""
        self.active.datfile.obj_additional_ops = self.additional_ops.GetValue()
        app.debug_frame.WriteLine("Datfile: AdditionalOps Changed")


    def BuildingTypeDisable(self):
        """Handle disabling/enabling things to do with building type"""
        if self.active.datfile.obj_bui_type in [8,9,10]:
            # If hall/post/shed set & disable extension building flag
            self.building_extension.SetValue(1)
        else:
            self.building_extension.Enable(True)
            self.building_extension.SetValue(self.active.datfile.obj_bui_extension)
            self.building_extension.Enable(False)
        if self.active.datfile.obj_bui_type in [0,11,12,13,14,15]:
            # Disable all (none, res/com/ind, any/misc)
            self.building_locationbui_label.Enable(False)
            self.building_locationbui.Enable(False)
            self.building_chancebui_label.Enable(False)
            self.building_chancebui.Enable(False)
            self.building_build_time_label.Enable(False)
            self.building_build_time.Enable(False)
            self.building_enables_label.Enable(False)
            self.building_extension.Enable(False)
            self.building_enables_pax.Enable(False)
            self.building_enables_post.Enable(False)
            self.building_enables_ware.Enable(False)
        elif self.active.datfile.obj_bui_type in [1,2,3,4,5,6,7,8,9,10]:
            # Disable for station
            self.building_locationbui_label.Enable(False)
            self.building_locationbui.Enable(False)
            self.building_chancebui_label.Enable(False)
            self.building_chancebui.Enable(False)
            self.building_build_time_label.Enable(False)
            self.building_build_time.Enable(False)
            self.building_enables_label.Enable(True)
            if self.active.datfile.obj_bui_type in [8,9,10]:
                self.building_extension.Enable(False)
            else:
                self.building_extension.Enable(True)
            self.building_enables_pax.Enable(True)
            self.building_enables_post.Enable(True)
            self.building_enables_ware.Enable(True)
        elif self.active.datfile.obj_bui_type == 16:
            # Disable for monument
            self.building_locationbui_label.Enable(False)
            self.building_locationbui.Enable(False)
            self.building_chancebui_label.Enable(True)
            self.building_chancebui.Enable(True)
            self.building_build_time_label.Enable(False)
            self.building_build_time.Enable(False)
            self.building_enables_label.Enable(False)
            self.building_extension.Enable(False)
            self.building_enables_pax.Enable(False)
            self.building_enables_post.Enable(False)
            self.building_enables_ware.Enable(False)
        elif self.active.datfile.obj_bui_type == 17:
            # Disable for curiosity
            self.building_locationbui_label.Enable(True)
            self.building_locationbui.Enable(True)
            self.building_chancebui_label.Enable(True)
            self.building_chancebui.Enable(True)
            if self.active.datfile.obj_bui_location == 2:
                self.building_build_time_label.Enable(True)
                self.building_build_time.Enable(True)
            else:
                self.building_build_time_label.Enable(False)
                self.building_build_time.Enable(False)
            self.building_enables_label.Enable(False)
            self.building_extension.Enable(False)
            self.building_enables_pax.Enable(False)
            self.building_enables_post.Enable(False)
            self.building_enables_ware.Enable(False)
        elif self.active.datfile.obj_bui_type in [18,19]:
            # Disable for town hall/HQ
            self.building_locationbui_label.Enable(False)
            self.building_locationbui.Enable(False)
            self.building_chancebui_label.Enable(False)
            self.building_chancebui.Enable(False)
            self.building_build_time_label.Enable(True)
            self.building_build_time.Enable(True)
            self.building_enables_label.Enable(False)
            self.building_extension.Enable(False)
            self.building_enables_pax.Enable(False)
            self.building_enables_post.Enable(False)
            self.building_enables_ware.Enable(False)


    def LevelInfoTextChange(self):
        """Display the level info hint"""
        # First check if anything in level box
        if self.active.datfile.obj_level == 0:
            self.global_level_info.SetLabel(gt("Level not set"))
            self.global_level_info2.SetLabel("")
        else:
            # Check if it's a factory or not
            if self.active.datfile.obj == 0:
                # Check what kind of building and adjust accordingly
                if self.active.datfile.obj_bui_type == 0:
                    self.global_level_info.SetLabel(gt("Type not set"))
                    self.global_level_info2.SetLabel("")
                elif self.active.datfile.obj_bui_type in [1,2,3,4,5,6,7]:
                    self.global_level_info.SetLabel(gt("Capacity: %i")%(self.active.datfile.obj_level * 32))
                    self.global_level_info2.SetLabel("")
                elif self.active.datfile.obj_bui_type in [8,9,10]:
                    self.global_level_info.SetLabel(gt("Capacity: %i")%(self.active.datfile.obj_level))
                    self.global_level_info2.SetLabel("")
                elif self.active.datfile.obj_bui_type == 11:
                    self.global_level_info.SetLabel(gt("Passenger level: %i")%(self.active.datfile.obj_level - 1))
                    self.global_level_info2.SetLabel(gt("Mail level: %i")%(self.active.datfile.obj_level - 1))
                elif self.active.datfile.obj_bui_type == 12:
                    self.global_level_info.SetLabel(gt("Passenger level: %i")%(self.active.datfile.obj_level - 1))
                    self.global_level_info2.SetLabel(gt("Mail level: %i")%((self.active.datfile.obj_level - 1) * 2))
                elif self.active.datfile.obj_bui_type == 13:
                    self.global_level_info.SetLabel(gt("Passenger level: %i")%(self.active.datfile.obj_level - 1))
                    self.global_level_info2.SetLabel(gt("Mail level: %i")%((self.active.datfile.obj_level - 1) / 2))
                elif self.active.datfile.obj_bui_type in [14,15]:
                    self.global_level_info.SetLabel(gt("Level not supported"))
                    self.global_level_info2.SetLabel(gt("for this object type"))
                elif self.active.datfile.obj_bui_type in [16,17]:
                    self.global_level_info.SetLabel(gt("Passenger level: %i")%(self.active.datfile.obj_level))
                    self.global_level_info2.SetLabel(gt("Mail level: %i")%(self.active.datfile.obj_level))
                elif self.active.datfile.obj_bui_type in [18,19]:
                    self.global_level_info.SetLabel(gt("Upgrade Stage: %i")%(self.active.datfile.obj_level))
                    self.global_level_info2.SetLabel("")
            elif self.active.datfile.obj == 1:
                self.global_level_info.SetLabel(gt("facPassenger level: %i")%(self.active.datfile.obj_level - 1))
                self.global_level_info2.SetLabel(gt("facMail level: %i")%((self.active.datfile.obj_level - 1) / 3))
            else:
                self.global_level_info.SetLabel(gt("n/a"))
                self.global_level_info2.SetLabel("")

    def OnSelectObjType(self,e):
        """Event for changing the object type"""
        self.active.datfile.obj = self.select_obj_type.GetSelection()
        self.ActivateDatPanel()

    def ActivateDatPanel(self, init=0):
        """Loads values into the dat panel fields,
        called after anything changes"""
        # Object type
        self.select_obj_type.SetSelection(self.active.datfile.obj)
        if self.active.datfile.obj == 0:
            for x in range(len(self.global_controls)):
                self.global_controls[x].Enable(True)
                self.global_controls[x].Show(True)
            for x in range(len(self.climates_controls)):
                self.climates_controls[x].Enable(True)
                self.climates_controls[x].Show(True)
            for x in range(len(self.factory_controls)):
                self.factory_controls[x].Enable(False)
                self.factory_controls[x].Show(False)
            for x in range(len(self.building_controls)):
                self.building_controls[x].Enable(True)
                self.building_controls[x].Show(True)
        elif self.active.datfile.obj == 1:
            for x in range(len(self.global_controls)):
                self.global_controls[x].Enable(True)
                self.global_controls[x].Show(True)
            for x in range(len(self.climates_controls)):
                self.climates_controls[x].Enable(True)
                self.climates_controls[x].Show(True)
            for x in range(len(self.factory_controls)):
                self.factory_controls[x].Enable(True)
                self.factory_controls[x].Show(True)
            for x in range(len(self.building_controls)):
                self.building_controls[x].Enable(False)
                self.building_controls[x].Show(False)
        elif self.active.datfile.obj == 2:
            for x in range(len(self.global_controls)):
                self.global_controls[x].Enable(False)
                self.global_controls[x].Show(False)
            for x in range(len(self.climates_controls)):
                self.climates_controls[x].Enable(False)
                self.climates_controls[x].Show(False)
            for x in range(len(self.factory_controls)):
                self.factory_controls[x].Enable(False)
                self.factory_controls[x].Show(False)
            for x in range(len(self.building_controls)):
                self.building_controls[x].Enable(False)
                self.building_controls[x].Show(False)

        # Climates boxes
        for x in range(len(self.active.datfile.obj_climates)):
            self.climates_controls[x].SetValue(self.active.datfile.obj_climates[x])

        if init == 1:
            # Set values for the global options pane
            self.global_name.SetValue(self.active.datfile.obj_name)
            self.global_copyright.SetValue(self.active.datfile.obj_copyright)
            self.global_intro_month.SetValue(self.tc_month_choices[self.active.datfile.obj_intromonth])
            # If value = 0, then set to ""
            if self.active.datfile.obj_introyear == 0:
                self.global_intro_year.SetValue("")
            else:
                self.global_intro_year.SetValue(str(self.active.datfile.obj_introyear))
            self.global_retire_month.SetValue(self.tc_month_choices[self.active.datfile.obj_retiremonth])
            # If value = 0, then set to ""
            if self.active.datfile.obj_retireyear == 0:
                self.global_retire_year.SetValue("")
            else:
                self.global_retire_year.SetValue(str(self.active.datfile.obj_retireyear))
            # If value = 0, then set to ""
            if self.active.datfile.obj_level == 0:
                self.global_level.SetValue("")
            else:
                self.global_level.SetValue(str(self.active.datfile.obj_level))
            self.global_noinfo.SetValue(self.active.datfile.obj_noinfo)
            self.global_noconstruction.SetValue(self.active.datfile.obj_noconstruction)
            self.global_needsground.SetValue(self.active.datfile.obj_drawground)
            # Factory stuff
            self.factory_locationfac.SetValue(self.factory_location_options[self.active.datfile.obj_fac_location])
            if self.active.datfile.obj_fac_chance == 0:
                self.factory_chancefac.SetValue("")
            else:
                self.factory_chancefac.SetValue(str(self.active.datfile.obj_fac_chance))
            if self.active.datfile.obj_fac_productivity == 0:
                self.factory_productivity.SetValue("")
            else:
                self.factory_productivity.SetValue(str(self.active.datfile.obj_fac_productivity))
            if self.active.datfile.obj_fac_range == 0:
                self.factory_range.SetValue("")
            else:
                self.factory_range.SetValue(str(self.active.datfile.obj_fac_range))
            if self.active.datfile.obj_fac_mapcolour == 0:
                self.factory_mapcolour.SetValue("")
            else:
                self.factory_mapcolour.SetValue(str(self.active.datfile.obj_fac_mapcolour))
            self.InputListDisplay()
            self.OutputListDisplay()
            # Additional options box
            self.additional_ops.SetValue(self.active.datfile.obj_additional_ops)
        self.BuildingTypeDisable()
        self.LevelInfoTextChange()
        # Finally re-do the layout (as things may have changed)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.Layout()




class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), (700,600),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        # Init stuff
        self.imres = tc.ImRes()

        # All other windows are children of this main window (dialogs, workspaces, tools etc.)
        # On initialisation some basic things are produced (toolbars etc.), the configuration
        # of these can be saved in a config file or something like that

        # Toolbar goes here

        # Now the panel which will contain the project
        panel = wx.Panel(self, -1, (-1,-1), (500,500))

        self.tc_frame_boxsizer = wx.BoxSizer(wx.VERTICAL)

        # Sizers are set up thus:
        # Panel is divided vertically into three, s_panel_top, s_panel_middle and s_panel_bottom
        # s_panel_top has the global menu bar in it
        # s_panel_middle has the DC and toolbar, and is divided into two:
            # s_panel_mid_left, s_panel_mid_right
            # left has the DC and toolbars, right has the main toolbar
            # s_panel_ml_top, s_panel_ml_middle, s_panel_ml_bottom:
                # top has the frame controls
                # middle has the splitter window, left part is the DC, right is the tool pane:
                    # DC is the device context for output display
                    # Tool pane is user-configurable
                # bottom has the specific image source controls
        # s_panel_bottom has the global pathname controls (and other things eventually)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        # First three subdivisions
        self.s_panel_top = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_middle = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_bottom = wx.BoxSizer(wx.HORIZONTAL)
        # Middle part further subdivided
        self.s_panel_mid_left = wx.BoxSizer(wx.VERTICAL)
        self.s_panel_mid_right = wx.BoxSizer(wx.VERTICAL)
        # Then the left hand bit of that is divided
        self.s_panel_ml_top = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_ml_middle = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_ml_bottom = wx.FlexGridSizer(0,6,0,0)

        # List of label names for the side panes
        self.splitter_panels_labels = [gt("Frames"), gt("Dat Edit"), gt("Makeobj"),gt("Smoke"), gt("Icon"), gt("Log")]

        # Make the splitter window, which acts as a parent to the frame controller and
        # to the Image Window (DC)
        self.splitter = wx.SplitterWindow(panel, -1, (-1,-1), (-1,-1), wx.SP_LIVE_UPDATE|wx.SP_3D)
        self.splitter_panels = []
        #                                       (parent window, "id" - this is an absolute id to
        #                                                              identify the window in the
        #                                                              program options (width))
        self.splitter_panels.append(FramesPanel(self.splitter, 0))
        self.splitter_panels.append(DatPanel(self.splitter, 1))
        self.splitter_panels.append(MakeobjPanel(self.splitter, 2))
        self.splitter_panels.append(SmokePanel(self.splitter, 3))
        self.splitter_panels.append(IconPanel(self.splitter, 4))
        self.splitter_panels.append(LogPanel(self.splitter, 5))
        # Log panel is always the last one
        self.log = self.splitter_panels[-1]

        for x in range(len(self.splitter_panels)):
            self.splitter_panels[x].Show(False)

        # Make the Image Window (DC)
        self.display = ImageWindow(self.splitter)

        # Min frame size, may need changing to work dynamically
        self.splitter.SetMinimumPaneSize(60)
        # Set sash gravity, make only the left pane resize
        self.splitter.SetSashGravity(1.0)


        # Now create all the GUI objects
        # First for the top toolbar (needs adding!!!)                                                   <---------NEEDS CODE ADD-------


        # Next the upper DC controls
        self.frame_select_label = wx.StaticText(panel, -1, (gt("Frame %i of %i (%s / %s / %s)") % (1,1,gt("BackImage"),gt("Summer"),gt("North"))), (-1, -1), (-1, -1), wx.ALIGN_LEFT)

        self.frame_select_back_im = wx.StaticBitmap(panel, -1, self.imres.back)
        self.frame_select_back_im.SetToolTipString(gt("ttframeselectBack"))
        self.frame_select_back = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.RB_GROUP|wx.ALIGN_RIGHT)
        self.frame_select_back.SetToolTipString(gt("ttframeselectBack"))
        self.frame_select_front_im = wx.StaticBitmap(panel, -1, self.imres.front)
        self.frame_select_front_im.SetToolTipString(gt("ttframeselectFront"))
        self.frame_select_front = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.frame_select_front.SetToolTipString(gt("ttframeselectFront"))
        self.frame_select_front.Enable(0)

        self.frame_select_summer_im = wx.StaticBitmap(panel, -1, self.imres.summer)
        self.frame_select_summer_im.SetToolTipString(gt("ttframeselectSummer"))
        self.frame_select_summer = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.RB_GROUP|wx.ALIGN_RIGHT)
        self.frame_select_summer.SetToolTipString(gt("ttframeselectSummer"))
        self.frame_select_winter_im = wx.StaticBitmap(panel, -1, self.imres.winter)
        self.frame_select_winter_im.SetToolTipString(gt("ttframeselectWinter"))
        self.frame_select_winter = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.frame_select_winter.SetToolTipString(gt("ttframeselectWinter"))
        self.frame_select_winter.Enable(0)

        self.frame_select_n_im = wx.StaticBitmap(panel, -1, self.imres.north)
        self.frame_select_n_im.SetToolTipString(gt("ttframeselectN"))
        self.frame_select_n = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.RB_GROUP|wx.ALIGN_RIGHT)
        self.frame_select_n.SetToolTipString(gt("ttframeselectN"))

        self.frame_select_e_im = wx.StaticBitmap(panel, -1, self.imres.east)
        self.frame_select_e_im.SetToolTipString(gt("ttframeselectE"))
        self.frame_select_e = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.frame_select_e.SetToolTipString(gt("ttframeselectE"))
        self.frame_select_e.Enable(0)

        self.frame_select_s_im = wx.StaticBitmap(panel, -1, self.imres.south)
        self.frame_select_s_im.SetToolTipString(gt("ttframeselectS"))
        self.frame_select_s = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.frame_select_s.SetToolTipString(gt("ttframeselectS"))
        self.frame_select_s.Enable(0)

        self.frame_select_w_im = wx.StaticBitmap(panel, -1, self.imres.west)
        self.frame_select_w_im.SetToolTipString(gt("ttframeselectW"))
        self.frame_select_w = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.frame_select_w.SetToolTipString(gt("ttframeselectW"))
        self.frame_select_w.Enable(0)

        self.hack2 = wx.RadioButton(panel, -1, "", (-1,-1), (-1,-1), wx.RB_GROUP|wx.ALIGN_RIGHT)
        self.hack2.Show(False)
        # Bind them to events
        self.frame_select_back.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_back)
        self.frame_select_front.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_front)
        self.frame_select_summer.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_summer)
        self.frame_select_winter.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_winter)
        self.frame_select_n.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_n)
        self.frame_select_e.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_e)
        self.frame_select_s.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_s)
        self.frame_select_w.Bind(wx.EVT_RADIOBUTTON, self.OnViewsChange, self.frame_select_w)

        # Add them all to the sizer
        self.s_panel_ml_top.Add(self.frame_select_label, 1, wx.ALIGN_CENTER_VERTICAL, 2)

        self.s_panel_ml_top.Add(self.frame_select_back, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_back_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)
        self.s_panel_ml_top.Add(self.frame_select_front, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_front_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 16)

        self.s_panel_ml_top.Add(self.frame_select_summer, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_summer_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)
        self.s_panel_ml_top.Add(self.frame_select_winter, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_winter_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 16)

        self.s_panel_ml_top.Add(self.frame_select_n, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_n_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)
        self.s_panel_ml_top.Add(self.frame_select_e, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_e_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)
        self.s_panel_ml_top.Add(self.frame_select_s, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_s_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)
        self.s_panel_ml_top.Add(self.frame_select_w, 0, wx.ALIGN_RIGHT|wx.RIGHT, 2)
        self.s_panel_ml_top.Add(self.frame_select_w_im, 0, wx.ALIGN_RIGHT|wx.RIGHT, 4)


        # Then add the splitter window with the DC and frames display in it
        self.s_panel_ml_middle.Add(self.splitter, 1, wx.BOTTOM|wx.EXPAND, 4)


        # Next the lower DC controls
        self.impath_entry_label = wx.StaticText(panel, -1, gt("Source:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.impath_entry_box = wx.TextCtrl(panel, -1, value="", style=wx.TE_READONLY)
        self.impath_entry_box.SetToolTipString(gt("ttinputpath"))
        self.impath_entry_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.impath_entry_filebrowse = wx.Button(panel, -1, label=gt("Browse..."))
        self.impath_entry_filebrowse.SetToolTipString(gt("ttbrowseinputfile"))
        self.impath_entry_reloadfile = wx.BitmapButton(panel, -1, size=(25,-1), bitmap=self.imres.reload)
        self.impath_entry_reloadfile.SetToolTipString(gt("ttreloadinputfile"))
        self.impath_entry_sameforall = wx.BitmapButton(panel, -1, size=(25,-1), bitmap=self.imres.sameforall)
        self.impath_entry_sameforall.SetToolTipString(gt("ttsamefileforall"))
        # Add them to sizer...
        self.s_panel_ml_bottom.Add(self.impath_entry_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_ml_bottom.Add(self.impath_entry_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_ml_bottom.Add(self.impath_entry_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_ml_bottom.Add(self.impath_entry_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_ml_bottom.Add(self.impath_entry_sameforall, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_ml_bottom.AddGrowableCol(1, 4)
        # Bind them to events
        self.impath_entry_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseSource, self.impath_entry_filebrowse)
        self.impath_entry_reloadfile.Bind(wx.EVT_BUTTON, self.OnReloadImage, self.impath_entry_reloadfile)
        self.impath_entry_sameforall.Bind(wx.EVT_BUTTON, self.OnLoadImageForAll, self.impath_entry_sameforall)



        # Now the right-hand toolbar
        # pakSize choice box
        self.rightbar_paksize_label = wx.StaticText(panel, -1, gt("paksize:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_paksize = wx.ComboBox(panel, -1, DEFAULT_PAKSIZE, (-1, -1), (54, -1), choicelist_paksize, wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.rightbar_paksize.SetToolTipString(gt("ttpaksize:"))
        # Views choice box
        self.rightbar_views_label = wx.StaticText(panel, -1, gt("Views:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_views = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), ["1","2","4"], wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.rightbar_views.SetToolTipString(gt("ttViews:"))
        # View options
        self.rightbar_views_winter = wx.CheckBox(panel, -1, gt("Winter"), (-1,-1), (-1,-1))
        self.rightbar_views_front = wx.CheckBox(panel, -1, gt("Front"), (-1,-1), (-1,-1))
        # x dimensions choice box        
        self.rightbar_xdims_label = wx.StaticText(panel, -1, gt("x dimension:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_xdims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.rightbar_xdims.SetToolTipString(gt("ttx dimension:"))
        # y dimensions choice box        
        self.rightbar_ydims_label = wx.StaticText(panel, -1, "y dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_ydims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.rightbar_ydims.SetToolTipString(gt("tty dimension:"))
        # z dimensions choice box        
        self.rightbar_zdims_label = wx.StaticText(panel, -1, "z dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_zdims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims_z, wx.CB_READONLY)
        self.rightbar_zdims.SetToolTipString(gt("ttz dimension:"))
        # Auto button        
        self.rightbar_auto = wx.Button(panel, -1, gt("Auto"), (-1,-1), (-1,-1), wx.BU_EXACTFIT)
        self.rightbar_auto.SetToolTipString(gt("ttAuto"))
        # Offset control
        self.rightbar_offset_label = wx.StaticText(panel, -1, gt("Offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_offset_selector = wx.CheckBox(panel, -1, gt("Fine"), (-1,-1), (-1,-1))
        self.rightbar_offset_selector.SetToolTipString(gt("ttOffsetSelector"))
        self.rightbar_button_up = wx.BitmapButton(panel, -1, self.imres.up2, (-1,-1), (18,18))
        self.rightbar_button_up.SetToolTipString(gt("ttOffsetUp"))
        self.rightbar_button_left = wx.BitmapButton(panel, -1, self.imres.left2, (-1,-1), (18,18))
        self.rightbar_button_left.SetToolTipString(gt("ttOffsetLeft"))
        self.rightbar_button_reset = wx.BitmapButton(panel, -1, self.imres.center, (-1,-1), (18,18))
        self.rightbar_button_reset.SetToolTipString(gt("ttOffsetReset"))
        self.rightbar_button_right = wx.BitmapButton(panel, -1, self.imres.right2, (-1,-1), (18,18))
        self.rightbar_button_right.SetToolTipString(gt("ttOffsetRight"))
        self.rightbar_button_down = wx.BitmapButton(panel, -1, self.imres.down2, (-1,-1), (18,18))
        self.rightbar_button_down.SetToolTipString(gt("ttOffsetDown"))
        # Display controls
        self.rightbar_displayops_label = wx.StaticText(panel, -1, gt("Display:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.rightbar_displayops_mask = wx.CheckBox(panel, -1, gt("Mask"), (-1,-1), (-1,-1))
        self.rightbar_displayops_mask.SetToolTipString(gt("ttDisplayMask"))

        self.rightbar_displayops_smoke = wx.CheckBox(panel, -1, gt("Smoke"), (-1,-1), (-1,-1))
        self.rightbar_displayops_smoke.SetToolTipString(gt("ttDisplaySmoke"))

        self.rightbar_displayops_toggle = wx.CheckBox(panel, -1, gt("Panel"), (-1,-1), (-1,-1))
        self.rightbar_displayops_toggle.SetToolTipString(gt("ttDisplaySidePanel"))
        self.rightbar_displayops_toggle.SetValue(1)

        y = 0
        self.rightbar_displayops = []
        for x in range(len(self.splitter_panels)):
            if y == 0:
                group = wx.RB_GROUP
            else:
                y = Null
            self.rightbar_displayops.append(wx.RadioButton(panel, 1000 + x, self.splitter_panels_labels[x], (-1,-1), (-1,-1), y))


        self.hack1 = wx.RadioButton(panel, -1, gt("Log"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.hack1.Show(False)

        # Add them to sizers...
        # Dimensions controls
        self.s_panel_mid_right.Add(self.rightbar_paksize_label, 0, wx.TOP|wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_paksize, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 2)
        self.s_panel_mid_right.Add(self.rightbar_views_label, 0, wx.TOP|wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_views, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 2)

        self.s_panel_mid_right.Add(self.rightbar_views_winter, 0, wx.LEFT|wx.TOP, 2)
        self.s_panel_mid_right.Add(self.rightbar_views_front, 0, wx.LEFT|wx.TOP, 2)

        self.s_panel_mid_right.Add(self.rightbar_xdims_label, 0, wx.TOP|wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_xdims, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 2)
        self.s_panel_mid_right.Add(self.rightbar_ydims_label, 0, wx.TOP|wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_ydims, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 2)
        self.s_panel_mid_right.Add(self.rightbar_zdims_label, 0, wx.TOP|wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_zdims, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER, 2)
        self.s_panel_mid_right.Add(self.rightbar_auto, 0, wx.TOP|wx.ALIGN_CENTER|wx.BOTTOM, 2)
        self.s_panel_mid_right.Add(wx.StaticLine(panel,-1,(-1,-1),(-1,-1),style=wx.LI_HORIZONTAL|wx.EXPAND),0,wx.BOTTOM|wx.EXPAND|wx.TOP,border=5)
        # Offset controls
        self.s_panel_mid_right.Add(self.rightbar_offset_label, 0, wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_offset_selector, 0, wx.LEFT|wx.TOP, 2)
        self.s_panel_mid_right.Add(self.rightbar_button_up, 0, wx.ALIGN_CENTER|wx.TOP, 3)
        self.s_panel_mid_right_offset = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_mid_right_offset.Add(self.rightbar_button_left, 0, wx.ALIGN_CENTER)
        self.s_panel_mid_right_offset.Add(self.rightbar_button_reset, 0, wx.ALIGN_CENTER)
        self.s_panel_mid_right_offset.Add(self.rightbar_button_right, 0, wx.ALIGN_CENTER)
        self.s_panel_mid_right.Add(self.s_panel_mid_right_offset, 0, wx.ALIGN_CENTER)
        self.s_panel_mid_right.Add(self.rightbar_button_down, 0, wx.ALIGN_CENTER)
        self.s_panel_mid_right.Add(wx.StaticLine(panel,-1,(-1,-1),(-1,-1),style=wx.LI_HORIZONTAL|wx.EXPAND),0,wx.BOTTOM|wx.EXPAND|wx.TOP,border=5)
        # Display controls
        self.s_panel_mid_right.Add(self.rightbar_displayops_label, 0, wx.LEFT, 2)
        self.s_panel_mid_right.Add(self.rightbar_displayops_mask, 0, wx.LEFT|wx.TOP, 2)
        self.s_panel_mid_right.Add(self.rightbar_displayops_smoke, 0, wx.LEFT|wx.TOP, 2)
        self.s_panel_mid_right.Add(self.rightbar_displayops_toggle, 0, wx.LEFT|wx.TOP, 2)
        for x in range(len(self.splitter_panels)):
            self.s_panel_mid_right.Add(self.rightbar_displayops[x], 0, wx.LEFT|wx.TOP, 2)

        # Bind them to events
        self.rightbar_paksize.Bind(wx.EVT_COMBOBOX, self.OnPaksizeChange, self.rightbar_paksize)
        self.rightbar_views.Bind(wx.EVT_COMBOBOX, self.OnViewsChange, self.rightbar_views)

        self.rightbar_views_winter.Bind(wx.EVT_CHECKBOX, self.OnViewsChange, self.rightbar_views_winter)
        self.rightbar_views_front.Bind(wx.EVT_CHECKBOX, self.OnViewsChange, self.rightbar_views_front)

        self.rightbar_xdims.Bind(wx.EVT_COMBOBOX, self.OnXDimsChange, self.rightbar_xdims)
        self.rightbar_ydims.Bind(wx.EVT_COMBOBOX, self.OnYDimsChange, self.rightbar_ydims)
        self.rightbar_zdims.Bind(wx.EVT_COMBOBOX, self.OnZDimsChange, self.rightbar_zdims)
        self.rightbar_auto.Bind(wx.EVT_BUTTON, self.OnAutoButton, self.rightbar_auto)
        self.rightbar_offset_selector.Bind(wx.EVT_CHECKBOX, self.OnOffsetToggle, self.rightbar_offset_selector)
        self.rightbar_button_up.Bind(wx.EVT_BUTTON, self.OnOffsetUp, self.rightbar_button_up)
        self.rightbar_button_left.Bind(wx.EVT_BUTTON, self.OnOffsetLeft, self.rightbar_button_left)
        self.rightbar_button_reset.Bind(wx.EVT_BUTTON, self.OnOffsetReset, self.rightbar_button_reset)
        self.rightbar_button_right.Bind(wx.EVT_BUTTON, self.OnOffsetRight, self.rightbar_button_right)
        self.rightbar_button_down.Bind(wx.EVT_BUTTON, self.OnOffsetDown, self.rightbar_button_down)

        self.rightbar_displayops_mask.Bind(wx.EVT_CHECKBOX, self.OnDisplayMaskToggle, self.rightbar_displayops_mask)
        self.rightbar_displayops_smoke.Bind(wx.EVT_CHECKBOX, self.OnDisplaySmokeToggle, self.rightbar_displayops_smoke)

        self.rightbar_displayops_toggle.Bind(wx.EVT_CHECKBOX, self.OnDisplayFrameToggleCheck, self.rightbar_displayops_toggle)

        for x in range(len(self.splitter_panels)):
            self.rightbar_displayops[x].Bind(wx.EVT_RADIOBUTTON, self.OnDisplayFrameChange, self.rightbar_displayops[x])

        # Add all the sizers to each other...
        # First the left-hand divided area with the DC
        self.s_panel_mid_left.Add(self.s_panel_ml_top,0,wx.EXPAND|wx.ALL, 4)
        self.s_panel_mid_left.Add(self.s_panel_ml_middle,1,wx.EXPAND|wx.RIGHT, 0)
        self.s_panel_mid_left.Add(self.s_panel_ml_bottom,0,wx.EXPAND|wx.RIGHT, 0)
        # Then the middle slice of the panel
        self.s_panel_middle.Add(self.s_panel_mid_left,1,wx.EXPAND|wx.RIGHT, 0)
        self.s_panel_middle.Add(self.s_panel_mid_right,0,wx.LEFT, 2)
        # Then everything to the main panel sizer
        self.s_panel.Add(self.s_panel_top,1,wx.EXPAND|wx.RIGHT, 0)
        self.s_panel.Add(self.s_panel_middle,1,wx.EXPAND|wx.RIGHT, 0)
        self.s_panel.Add(self.s_panel_bottom,1,wx.EXPAND|wx.RIGHT, 0)

        #Layout sizers
        panel.SetSizer(self.s_panel)
        panel.SetAutoLayout(1)
        panel.Layout()

        # Finally, create the menu
        self.MakeMenus()



##-------------- Init Misc

    def MakeMenus(self):
        self.MainMenu = wx.MenuBar()
        self.AddMenus(self.MainMenu)
        self.SetMenuBar(self.MainMenu)

##-------------- Init Subwindows

    # Sub-panel init is done via a function in the App class

##-------------- Init Menus

    # Append to this function to add more menus
    def AddMenus(self, menu):
        self.AddFileMenu(menu)
        self.AddToolsMenu(menu)
        self.AddHelpMenu(menu)

    def AddMenuItem(self, menu, itemText, itemDescription, itemHandler, enabled=1):
        menuId = wx.NewId()
        menu.Append(menuId, itemText, itemDescription)
        self.Bind(wx.EVT_MENU, itemHandler, id=menuId)
        if enabled == 0:
            menu.Enable(menuId, 0)
        return menuId

    def AddFileMenu(self, menu):
        fileMenu = wx.Menu()
        self.AddMenuItem(fileMenu, '&New Project\tCtrl-N', 'New Project', self.OnNewProject)
        self.AddMenuItem(fileMenu, '&Open Project\tCtrl-O', 'Open Project', self.OnOpenProject)
        self.AddMenuItem(fileMenu, '&Close Project', 'Close Project', self.OnCloseProject)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, '&Save Project\tCtrl-S', 'Save Project', self.OnSaveProject)
        self.AddMenuItem(fileMenu, 'Save Project &As\tCtrl-A', 'Save Project As',self.OnSaveProjectAs)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, '&Export source\tCtrl-E', 'Export source files for Makeobj', self.OnExportSource)
        self.AddMenuItem(fileMenu, 'Export Dat &file only', 'Export dat file', self.OnSaveProject)
        self.AddMenuItem(fileMenu, 'Ex&port .pak\tCtrl-K', 'Export project as .pak file', self.OnSaveProject)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, 'E&xit\tAlt-Q', 'Exit', self.OnExit)
        menu.Append(fileMenu, 'File')

    def AddToolsMenu(self,menu):
        toolsMenu = wx.Menu()
        self.AddMenuItem(toolsMenu, '.&dat file options\tCtrl-D', 'Edit .dat file options', self.OnDatEdit)
        self.AddMenuItem(toolsMenu, '&Smoke options\tCtrl-M', 'Add or edit a smoke object associated with this project', self.OnSmokeEdit, 0)
        toolsMenu.AppendSeparator()
        self.AddMenuItem(toolsMenu, '&Preferences\tCtrl-P', 'Change program preferences', self.OnPreferences)
        menu.Append(toolsMenu, 'Tools')

    def AddHelpMenu(self,menu):
        helpMenu = wx.Menu()
        self.AddMenuItem(helpMenu, 'Help Topics\tCtrl-H', '', self.OnHelp, 0)
        helpMenu.AppendSeparator()
        self.AddMenuItem(helpMenu, '&About TileCutter', 'Information about this program', self.OnAbout)
        menu.Append(helpMenu, 'Help')

##-------------- Event Handlers

    # All event handlers which deal with project info should call
    # functions in a seperate project class or the project intermediary
    # class.

    # GUI behaviour functions
    # These change other bits of the GUI based on user interaction
    
    # GUI event handlers
    # Events for the basic dimension and view controls
    def OnPaksizeChange(self,e):
        """When the paksize is changed"""
        app.debug_frame.WriteLine("Paksize changed to %s"%self.rightbar_paksize.GetValue())
        self.active.info.paksize = int(self.rightbar_paksize.GetValue())
        self.ActivateProject()
        self.DrawImage()

    def OnViewsChange(self,e):
        """When the number of views is changed"""
        app.debug_frame.WriteLine("Views Change -> Dir: " + self.rightbar_views.GetValue() + ", Win: " + str(self.rightbar_views_winter.GetValue()) + ", Frnt: " + str(self.rightbar_views_front.GetValue()))
        # Check what's ticked within these buttons, and write to the active project
        # Then call ActivateProject
        if self.frame_select_back.GetValue() == 1:
            if self.frame_select_summer.GetValue() == 1:
                self.active.activeimage[2] = 0
            else:
                self.active.activeimage[2] = 1
        else:
            if self.frame_select_summer.GetValue() == 1:
                self.active.activeimage[2] = 2
            else:
                self.active.activeimage[2] = 3
        if self.frame_select_n.GetValue() == 1:
            self.active.activeimage[1] = 0
        if self.frame_select_e.GetValue() == 1:
            self.active.activeimage[1] = 1
        if self.frame_select_s.GetValue() == 1:
            self.active.activeimage[1] = 2
        if self.frame_select_w.GetValue() == 1:
            self.active.activeimage[1] = 3

        # First check if the winter image is enabled
        self.active.info.winter = self.rightbar_views_winter.GetValue()
        # Then check the front/back image
        self.active.info.frontimage = self.rightbar_views_front.GetValue()
        # Now check the directions
        if self.rightbar_views.GetValue() == "1":
            self.active.info.views = 1
        elif self.rightbar_views.GetValue() == "2":
            self.active.info.views = 2
        else:
            self.active.info.views = 4
        self.ActivateProject()
        self.DrawImage()
        app.debug_frame.WriteLine("Views Change -> Dir: " + str(self.active.info.views) + ", Win: " + str(self.active.info.winter) + ", Frnt: " + str(self.active.info.frontimage))

    def OnXDimsChange(self,e):
        """When the X dimensions are changed"""
        app.debug_frame.WriteLine("Xdims changed to %s"%self.rightbar_xdims.GetValue())
        self.active.info.xdims = int(self.rightbar_xdims.GetValue())
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()
    def OnYDimsChange(self,e):
        """When the Y dimensions are changed"""
        app.debug_frame.WriteLine("Ydims changed to %s"%self.rightbar_ydims.GetValue())
        self.active.info.ydims = int(self.rightbar_ydims.GetValue())
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()
    def OnZDimsChange(self,e):
        """When the Z dimensions (height) is changed"""
        app.debug_frame.WriteLine("Zdims changed to %s"%self.rightbar_zdims.GetValue())
        self.active.info.zdims = int(self.rightbar_zdims.GetValue())
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()

    def OnAutoButton(self,e):
        """When the Auto button is used"""
        app.debug_frame.WriteLine("Auto Button")

    # Events for the Offset controls
    def OnOffsetToggle(self,e):
        """On toggling of the "fine" offset switch"""
        app.debug_frame.WriteLine("Toggle Fine Mask -> " + str(self.rightbar_offset_selector.GetValue()))
        self.options.offset_fine = self.rightbar_offset_selector.GetValue()
        self.ActivateProject()
##        self.DrawImage()

    def OnOffsetUp(self,e):
        """On click of the offset move up button"""
        app.debug_frame.WriteLine("Offset Up")
        offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y
        # Any bounds checks should go here...
        if self.options.offset_fine == 0:
            offset_y -= self.active.info.paksize / 4
        else:
            offset_y -= 1
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y = offset_y
        self.ActivateProject()
        self.DrawImage()
    def OnOffsetDown(self,e):
        """On click of the offset move down button"""
        app.debug_frame.WriteLine("Offset Down")
        offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y
        # Any bounds checks should go here...
        if self.options.offset_fine == 0:
            offset_y += self.active.info.paksize / 4
        else:
            offset_y += 1
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y = offset_y
        self.ActivateProject()
        self.DrawImage()
    def OnOffsetLeft(self,e):
        """On click of the offset move left button"""
        app.debug_frame.WriteLine("Offset Left")
        offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
        # Any bounds checks should go here...
        if self.options.offset_fine == 0:
            offset_x -= self.active.info.paksize / 2
        else:
            offset_x -= 1
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x = offset_x
        self.ActivateProject()
        self.DrawImage()
    def OnOffsetRight(self,e):
        """On click of the offset move right button"""
        app.debug_frame.WriteLine("Offset Right")
        offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
        # Any bounds checks should go here...
        if self.options.offset_fine == 0:
            offset_x += self.active.info.paksize / 2
        else:
            offset_x += 1
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x = offset_x
        self.ActivateProject()
        self.DrawImage()
    def OnOffsetReset(self,e):
        """On click of the offset reset button"""
        app.debug_frame.WriteLine("Offset Reset")
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y = 0
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x = 0
        self.ActivateProject()
        self.DrawImage()


    def OnDisplayMaskToggle(self,e):
        """On toggle of the display mask"""
        app.debug_frame.WriteLine("Display Mask Toggle")
        self.options.show_mask = self.rightbar_displayops_mask.GetValue()
        self.ActivateProject()
        self.DrawImage()
    def OnDisplaySmokeToggle(self,e):
        """On toggle of the smoke preview display"""
        app.debug_frame.WriteLine("Smoke display toggle")
        self.options.show_smoke = self.rightbar_displayops_smoke.GetValue()
        self.ActivateProject()
        self.DrawImage()

    # Display of the side pane
    def OnDisplayFrameToggleCheck(self,e):
        """Activates the Debug pane"""
        self.options.sidepane_show = self.rightbar_displayops_toggle.GetValue()
        self.OnDisplayFramesToggle()

    def OnDisplayFrameChange(self,e):
        """When the radiobuttons are used to change which pane is displayed"""
        a = e.GetId() - 1000
        self.options.sidepane = a
        self.OnDisplayFramesToggle()

    def OnDisplayFramesToggle(self):
        """Turns the frames pane on or off"""
        app.debug_frame.WriteLine("Display Frames Toggle")

        # Now needs a way to detmine which pane to show!
        if self.options.sidepane_show == 0:
            if self.splitter.IsSplit() == 1:
                # First take the width value and save it, so that the program remembers
                # the user's size settings...
                self.options.sidebar_widths[self.options.sidepane] = self.splitter.GetWindow2().GetSize().GetWidth()
                self.splitter.Unsplit()
            else:
                self.splitter.Initialize(self.display)
        else:
            if self.splitter.IsSplit() == 0:
                # If the height of the viewpane panel is smaller than the height of the
                # panel to be displayed in it, we must increase the width of the panel
                # by the width of a scrollbar (to allow for the scrollbar)
                if self.s_panel_ml_middle.GetSize().GetHeight() < self.splitter_panels[self.options.sidepane].panel_height:
                    self.splitter.SplitVertically(self.display, self.splitter_panels[self.options.sidepane], 0 - SCROLLBAR_WIDTH - self.options.sidebar_widths[self.options.sidepane])
                    self.splitter.SetMinimumPaneSize(abs(self.options.sidebar_minwidths[self.options.sidepane] + SCROLLBAR_WIDTH))
                else:
                    self.splitter.SplitVertically(self.display, self.splitter_panels[self.options.sidepane], 0 - self.options.sidebar_widths[self.options.sidepane])
                    self.splitter.SetMinimumPaneSize(abs(self.options.sidebar_minwidths[self.options.sidepane]))
            else:
                window = self.splitter.GetWindow2()
                # First take the width value and save it, so that the program remembers
                # the user's size settings...
                self.options.sidebar_widths[window.placenum] = window.GetSize().GetWidth()
                # Then replace the split window
                self.splitter.ReplaceWindow(window, self.splitter_panels[self.options.sidepane])

                if self.s_panel_ml_middle.GetSize().GetHeight() < self.splitter_panels[self.options.sidepane].panel_height:
                    self.splitter.SetSashPosition(0 - SCROLLBAR_WIDTH - self.options.sidebar_widths[self.options.sidepane])
                    self.splitter.SetMinimumPaneSize(abs(self.options.sidebar_minwidths[self.options.sidepane] + SCROLLBAR_WIDTH))
                else:
                    self.splitter.SetSashPosition(0 - self.options.sidebar_widths[self.options.sidepane])
                    self.splitter.SetMinimumPaneSize(abs(self.options.sidebar_minwidths[self.options.sidepane]))

                window.Show(False)
            self.splitter_panels[self.options.sidepane].Show(True)
        self.ActivateProject()


    # Events for the source browse bar
    def OnBrowseSource(self,e):
        """On click of the source image browse button"""
        app.debug_frame.WriteLine("Browse Source Click")
        dlg = wx.FileDialog(self, gt("Choose a Source Image file..."), "", "", "PNG files (*.png)|*.png|Other Image files (*.bmp, *.gif, *.jpg)|*.bmp;*.gif;*.jpg", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]] = ProjectImage(dlg.GetPath())
        dlg.Destroy()
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()

    def OnChangeSourceText(self,e):
        """On manual edit of the source text box"""
    def OnReloadImage(self,e):
        """On click of the reload this image button"""
        app.debug_frame.WriteLine("Reload Image Click")
        self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].Reload()
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()

    def OnLoadImageForAll(self,e):
        """On click of the load this image for all views button"""
        app.debug_frame.WriteLine("Load Image For All Click")
        # Involves setting this image to be the image for all of the directions and
        # season images for the current frame
        path = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].path
        for x in range(4):
            for y in range(4):
                self.active.frame[self.active.activeimage[0]].direction[x].image[y] = ProjectImage(path)
        self.active.temp.update_dims = 1
        self.ActivateProject()
        self.DrawImage()


    # Menu event handlers
    def OnNewProject(self,e):
        """Creates a new project"""
        app.debug_frame.WriteLine("Menu: File -> New Project")
        app.NewProject()
    def OnOpenProject(self,e):
        """Opens a project"""
        app.debug_frame.WriteLine("Menu: File -> Open Project")
        # Prompt for a filename, load the project using UnPickle, then call
        # app.LoadProject to initialise it
        self.OpenProject()
    def OnCloseProject(self,e):
        """Checks to see if project has changed, if so prompt to save, else close"""
        app.debug_frame.WriteLine("Menu: File -> Close Project")
        self.CloseProject()
    def OnSaveProject(self,e):
        """Save the project, if not saved before prompt for filename etc."""
        app.debug_frame.WriteLine("Menu: File -> Save project")
        self.SaveProject()
    def OnSaveProjectAs(self,e):
        """Save the project with filename prompt"""
        app.debug_frame.WriteLine("Menu: File -> Save project As")
        self.SaveProject(1)
    def OnExit(self,e):
        """Close the application, prompt to save open projects first"""
        app.debug_frame.WriteLine("Menu: File -> Exit Program")
        app.ExitProgram(1)

    def OnExportSource(self,e):
        """Export the project source"""
        Export(self)
        app.debug_frame.WriteLine("Menu: File -> Export Source")

    def OpenProject(self):
        """Opens a project from a saved file"""
        loadname = wx.FileDialog(self,gt("Choose a file to open..."),self.active.info.savepath,"",
                                 "Project files (*.tcp)|*.tcp",wx.OPEN|wx.FILE_MUST_EXIST)
        if loadname.ShowModal() == wx.ID_OK:
            # OK was pressed, continue loading this file
            filename = loadname.GetFilename()
            loadpath = loadname.GetDirectory()
            loadname.Destroy()
        else:
            # Else cancel was pressed, abort loading
            return 0
        filein = file(os.path.join(loadpath,filename),"rb")
        stringin = filein.read()
        filein.close()
        project_data = self.UnPickleProject(stringin)
        app.LoadProject(project_data)

    def SaveProject(self, saveas=0):
        """Saves the project to disk"""
        if self.active.info.filename == "":
            saveas = 1
        if saveas == 1:
            savename = wx.FileDialog(self,gt("Choose a file to save to..."),self.active.info.savepath,self.active.info.filename,
                                     "Project files (*.tcp)|*.tcp",wx.SAVE|wx.OVERWRITE_PROMPT)
            if savename.ShowModal() == wx.ID_OK:
                # OK was pressed, continue saving with new filename
                self.active.info.filename = savename.GetFilename()
                self.active.info.savepath = savename.GetDirectory()
                savename.Destroy()
            else:
                # Else cancel was pressed, abort saving
                return 0
        stringout, hash = self.PickleProject()
        self.active.temp.project_hash = hash
        fileout = file(os.path.join(self.active.info.savepath,self.active.info.filename),"wb")
        fileout.write(stringout)
        fileout.close()

    def CloseProject(self):
        """Closes a project, prompting to save first if it has been changed"""
        if self.CompareHash(self.PickleProject()[1]):
            app.CloseProject()
        else:
            # Project has changed, prompt to save
            if self.SaveChangesDialog() == 1:
                app.CloseProject()

    def SaveChangesDialog(self):
        """Prompt user to save changes"""
        savechanges = wx.MessageDialog(self,gt("Project has changed, do you wish to save your changes?"),gt("Save changes?"),
                                       wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
        saveval = savechanges.ShowModal()
        if saveval == wx.ID_YES:
            # Save
            self.SaveProject()
            return 1
        elif saveval == wx.ID_NO:
            # Don't save
            return 1
        else:
            # Cancel operation
            return 0

    def PickleProject(self):
        """Pickle the project and return a StringIO object and a hash"""
        # Produce a stringIO object to write the pickle output to
        stringio = StringIO.StringIO()

        # Firstly we have to set the images to be null so it will save
        # properly...
        frames = []
        for f in range(len(self.active.frame)):
            directions = []
            for d in range(len(self.active.frame[0].direction)):
                images = []
                for i in range(len(self.active.frame[0].direction[0].image)):
                    images.append(self.active.frame[f].direction[d].image[i].image)
                    self.active.frame[f].direction[d].image[i].image = 0
                directions.append(images)
            frames.append(directions)
        # And the image in the smoke fork
        smokeimage = []
        smokeimage.append(self.active.smoke.image)
        self.active.smoke.image = 0

        # Now do the same for the project_temp stuff - none of this needs to be
        # pickled and any changes here don't need to be saved
        temp = self.active.temp
        self.active.temp = 0

        # Write the current project to the StringIO using pickle
        cPickle.dump(self.active, stringio, -1)

        # Put the temp stuff back again
        self.active.temp = temp

        # Put the images back again
        for f in range(len(self.active.frame)):
            for d in range(len(self.active.frame[0].direction)):
                for i in range(len(self.active.frame[0].direction[0].image)):
                    self.active.frame[f].direction[d].image[i].image = frames[f][d][i]
        # And the smoke image
        self.active.smoke.image = smokeimage[0]

        # Convert to a string
        string = stringio.getvalue()
        stringio.close()
        # Make a hash object
        md5hash = hashlib.md5()
        md5hash.update(string)
        # Calculate a hash of this save
        hash = md5hash.digest()
        # Return the values
        return (string, hash)

    def UnPickleProject(self, string):
        """Take a StringIO object and return a project object"""
        stringio = StringIO.StringIO(string)
        project = cPickle.load(stringio)

        # Initialise the temporary project stuff
        project.temp = ProjectTemp()

        return project

    def CompareHash(self, hash1, hash2=-1):
        """Compare two hashes (second is by default this project's old hash) and
        return true if they match"""
        if hash2 == -1:
            hash2 = self.active.temp.project_hash
        if hash1 == hash2:
            app.debug_frame.WriteLine("Hash equality")
            return True
        else:
            app.debug_frame.WriteLine("Hash inequality")
            return False
    # Save Project -> If project has a name, save it using that name, else
    #                 prompt for a save file name and then save using that
    # Close Project -> If project has been altered (compare hash to last
    #                  time saved hash) prompt to save changes, else pop
    #                  project from the projects list
    # Load Project -> Load a project from file (prompt for file) and then
    #                 call the LoadProject function of the App
    # Exit Program -> Go through all active projects, prompt to save them,
    #                 and then close them using the ProjectClose function


    def OnDatEdit(self,e):
        """Open .dat editor"""
    def OnSmokeEdit(self,e):
        """Open smoke editor"""
    def OnFrames(self,e):
        """Open frame selector/editor"""
    def OnPreferences(self,e):
        """Open preferences window"""

    def OnHelp(self,e):
        """Open the help dialog"""
    def OnAbout(self,e):
        """Open the about dialog"""

    def InitProject(self, projectnumber):
        """Initiates a project to allow it to become active, should be called whenever
        a project becomes active (or is created)"""
        # First make this project the active one
        self.active = app.projects[projectnumber]
        self.display.active = self.active

        for f in range(len(self.active.frame)):
            for d in range(len(self.active.frame[f].direction)):
                for i in range(len(self.active.frame[f].direction[d].image)):
                    self.active.frame[f].direction[d].image[i].Reload()

        # Activate child windows
        # Every child window (panel) has an InitPanel() function,
        # which allows it to inherit links to the active project
        # and initialise and such-like. Additionally each child panel
        # should gain a link back to the log window, and have an
        # overall update function (which may need to call container
        # update functions as required...)
        for x in range(len(self.splitter_panels)):
            self.splitter_panels[x].InitPanel()

        # Now we must load this project's info and make it active
        # To do this we call each window's own ActivateProject function
        # These functions load information from the active project into the
        # window's controls
        self.ActivateProject()
        self.DrawImage()
        self.OnDisplayFramesToggle()

    def InitProgramOps(self):
        """Initiates certain program options"""
        self.options = app.options

    def DrawImage(self, image=0):
        """Draws the image with any necessary options to the viewing pane
        ActivateProject should usually be called before this to ensure display
        of the correct image. "image" is a three-tuple of the image that should
        be displayed (this is usually the active image, but why not make it flexible..."""
        if image == 0:
            image = self.active.activeimage
        im = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].image

        # Any display overlay (cutting mask etc.) should now be drawn onto the copy of
        # the output image

        # Previously the image itself was modified prior to display,
        # in future the image will be pasted as-is, with the cutting
        # mask drawn on top directly. This should be more flexible

        # Reverse dims if east/west
        if self.active.activeimage[1] in [0,2]:
            x = self.active.info.xdims
            y = self.active.info.ydims
        else:
            y = self.active.info.xdims
            x = self.active.info.ydims
        z = self.active.info.zdims
        p = self.active.info.paksize
        w = (x + y) * (p/2)
        h = ((x + y) * (p/4)) + (p/2) + ((z - 1) * p)

        offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
        offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y

        if self.options.show_mask == 1:
            # Create the mask
            mask = self.DrawGrid((x,y,z),p,(w,h))

        if self.options.show_smoke == 1:
            # Create the smoke image object
            smoke = Image.new("RGBA",(p,p), color=(231,255,255,0))
            smoke1 = self.active.smoke.image
            smoke.paste(smoke1.crop((self.active.smoke.offset_x,self.active.smoke.offset_y,self.active.smoke.offset_x + p,self.active.smoke.offset_y + p)),(0,0))
            # Horrible hack...
            ss = smoke.load()
            for xxx in range(p):
                for yyy in range(p):
                    if ss[xxx,yyy] == (231,255,255,255):
                        ss[xxx,yyy] = (231,255,255,0)

        # While in theory smoke could be placed anywhere, in reality it is unlikely
        # that the user will want to place it outside the bounds of the image, thus
        # the smoke will not affect the display position of the rest of the image
        # (and so with excessive offset could dissapear off the edge of the image)
        # Some sort of code should be added in future to prevent/cater for this!            <-----------------CODE ADD NEEDED!--------


        # Image can be any arbitrary size, represented by image_width/image_height
        image_width, image_height = im.size
        # Mask size can be any size, larger or smaller than image, determined by a
        # simple formula based on x/y/z dims
        mask_width = (x + y) * (p/2)
        mask_height = ((x + y) * (p/4)) + (p/2) + ((z - 1) * p)
        # Smoke size is always p
        smoke_width = p
        smoke_height = p

        app.debug_frame.WriteLine("image width: %i height: %i \nmask width: %i height: %i"%(image_width,image_height,mask_width,mask_height))
        app.debug_frame.WriteLine("smoke width: %i height: %i"%(smoke_width,smoke_height))


        # Smoke location determined by tile + arb offset
        # Smoke position relative to (0,0) on the mask (add in any arbitrary positioning info here!)
        smoke2mask_offset_x = ((self.active.smoke.p_smoke_tile_y-1) * (p/2)) - ((self.active.smoke.p_smoke_tile_x-1) * (p/2)) + self.active.smoke.p_smoke_offset_x + (x * (p/2))
        smoke2mask_offset_y = ((self.active.smoke.p_smoke_tile_y-1) * (p/4)) + ((self.active.smoke.p_smoke_tile_x-1) * (p/4)) + self.active.smoke.p_smoke_offset_y
        # Mask location determined by global offset (relative to image)
        # and smoke position
        # mask_offset = global_offset + image_offset
        mask2image_offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
        mask2image_offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y
        # Image location determined by offsets of mask and smoke
        # Image (0,0) is origin for all offsets!
        # smoke2mask should be zero at (1,1)
        # Image offset should also take into account the difference in size between the mask
        # and the image base, if the mask is smaller than the base image then that difference
        # needs to be deducted from the offset when the mask is right of (0,0)                          <-----NEEDS CHANGE---------
        image_offset_x = mask2image_offset_x + smoke2mask_offset_x
        image_offset_y = mask2image_offset_y + smoke2mask_offset_y

        app.debug_frame.WriteLine("smoke2mask x: %i y: %i"%(smoke2mask_offset_x,smoke2mask_offset_y))
        app.debug_frame.WriteLine("mask2image x: %i y: %i"%(mask2image_offset_x,mask2image_offset_y))
        app.debug_frame.WriteLine("imageoffset x: %i y: %i"%(image_offset_x,image_offset_y))

        # Now for actual positioning
        # Nothing will ever in practice have a -ve offset to the screen

        # Image offset is sum of mask & smoke offsets if these are -ve overall,
        # else it's just 0 and everything else is offsetted.
        if image_offset_x < 0:
            im_off_x = abs(image_offset_x)
        else:
            im_off_x = 0
        if image_offset_y < 0:
            im_off_y = abs(image_offset_y)
        else:
            im_off_y = 0

        # Breaks when:
        # Smoke left of mask, mask right of image
        # 

        if mask2image_offset_x < 0:
            # mask left of image
            if smoke2mask_offset_x < 0:
                # smoke left of mask
                smoke_off_x = 0
                mask_off_x = abs(smoke2mask_offset_x)
            else:
                # smoke right of mask   not working!
                smoke_off_x = abs(smoke2mask_offset_x)
                mask_off_x = 0
                # Special case
                image_offset_x = abs(mask2image_offset_x)
                im_off_x = abs(image_offset_x)
        else:
            # mask right of image
            if smoke2mask_offset_x < 0:
                # smoke left of mask        <--------------------- problem area
                smoke_off_x = abs(smoke2mask_offset_x)
                mask_off_x = abs(mask2image_offset_x)
            else:
                # smoke right of mask
                smoke_off_x = abs(mask2image_offset_x) + abs(smoke2mask_offset_x)
                mask_off_x = abs(mask2image_offset_x)

        if mask2image_offset_y < 0:
            # mask above image
            if smoke2mask_offset_y < 0:
                # smoke above mask
                smoke_off_y = 0
                mask_off_y = abs(smoke2mask_offset_y)
            else:
                # smoke below mask
                smoke_off_y = abs(smoke2mask_offset_y)
                mask_off_y = 0
                # Special case
                image_offset_y = abs(mask2image_offset_y)
                im_off_y = abs(image_offset_y)
        else:
            # mask below image
            if smoke2mask_offset_y < 0:
                # smoke above mask
                if smoke2mask_offset_y + mask2image_offset_y < 0:
                    # if smoke above image
                    smoke_off_y = 0
                    mask_off_y = abs(smoke2mask_offset_y)
                else:
                    # if smoke also below image
                    smoke_off_y = abs(mask2image_offset_y) - abs(smoke2mask_offset_y)
                    mask_off_y = abs(mask2image_offset_y)
            else:
                # smoke below mask
                smoke_off_y = abs(mask2image_offset_y) + abs(smoke2mask_offset_y)
                mask_off_y = abs(mask2image_offset_y)

        # Create the wxImage and PILImage for the output
        outimage = wx.EmptyImage(max(smoke_width,mask_width,image_width)+abs(image_offset_x), max(smoke_height,mask_height,image_height)+abs(image_offset_y))
        img = Image.new("RGBA", (max(smoke_width,mask_width,image_width)+abs(image_offset_x), max(smoke_height,mask_height,image_height)+abs(image_offset_y)), color=(231,255,255,0))

        # Paste the base image into the output
        img.paste(im,(im_off_x,im_off_y))

        if self.options.show_mask == 1:
            # Paste the mask into the output
            img.paste(mask,(mask_off_x,mask_off_y),mask)
        if self.options.show_smoke == 1:
            # Paste the smoke into the output
            img.paste(smoke,(smoke_off_x,smoke_off_y),smoke)
        # Convert from PIL to wxImage
        outimage.SetData(img.convert("RGB").tostring())
        # Convert from Image to bitmap
        outimage = outimage.ConvertToBitmap()

        # Display the bitmap on the DC
        self.display.bmp = outimage
        self.display.DrawBitmap(1)

##        # Mask will always be at either 0,0 or some positive (absolute) offset
##        # When the offset is negative, the image must be offset by that amount
##        abs_offx = abs(offset_x)
##        abs_offy = abs(offset_y)
##        if offset_x < 0:
##            # If the offset is less than 0, then both image and mask need to be moved
##            image_offset_x = abs_offx
##            mask_offset_x = 0
##        else:
##            image_offset_x = 0
##            mask_offset_x = abs_offx
##        if offset_y < 0:
##            # If the offset is less than 0, then both image and mask need to be moved
##            image_offset_y = abs_offy
##            mask_offset_y = 0
##        else:
##            image_offset_y = 0
##            mask_offset_y = abs_offy

    def DrawGrid(self, dims, p, imdims):
        """Draw the grid overlay image to be stuck on top of image in the display pane"""
        # What we're doing here is producing an image with a background transparency
        # This is then drawn on top of the image itself in the viewpane
        # The position and dimensions of the grid are determined by the xdims, ydims,
        # zdims and the x and y offsets for the image.

        active_image = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]]

        xd,yd,zd = dims
        w,h = imdims

        offx = 0
        offy = 0

        # Now create an image of sufficient size
        # Size will be given as:
        im = Image.new("RGBA", (w,h), color=(231,255,255,0))

        # Now draw onto that image what needs to be drawn
        # (Here we can in future use a custom cutting mask to do the drawing
        # and thus produce more complex stuff, for now we'll just to this simply)
        draw = ImageDraw.Draw(im)

        ## Begin old code ------------------
        draw.line(((offx),(h - (yd * (p/4)) - offy),(offx + (yd * (p/2)) + 1),(h - offy)),fill="rgb(255,0,0)")  #Draw left hand bottom line
        draw.line(((offx + (yd * (p/2)) - 1),(h - offy),(w),(h - (xd * (p/4)) - offy) - 1),fill="rgb(255,0,0)") #Draw right hand bottom line
        for a in range(0,xd):                                                                                   #Draw left hand lines at top
            aa = w - ((a + 1) * (p/2)) - ((yd) * p/2)
            bb = ((a) * (p/4))
            draw.line((aa,bb,(aa + (p/2)),bb),fill="rgb(255,0,0)")
            draw.line((aa,bb,aa,(bb + p/4)),fill="rgb(255,0,0)")
        for a in range(0,yd):                                                                                   #Draw right hand lines at top
            aa = ((a + 1) * (p/2)) + ((xd) * p/2) - (p/2)
            bb = ((a) * (p/4))
            draw.line(((aa - 1 + offx),bb,(aa + (p/2) - 1 + offx),bb),fill="rgb(255,0,0)")
            draw.line(((aa + (p/2) - 1 + offx),bb,(aa + (p/2) - 1 + offx),(bb + p/4)),fill="rgb(255,0,0)")

        aa = w - ((xd) * (p/2)) - ((yd) * p/2)
        bb = ((xd) * (p/4))
        draw.line(((aa),(bb),(aa),(h - (yd * (p/4)) - offy)),fill="rgb(255,0,0)")       #Extend left hand line to base

        bb = ((yd) * (p/4))
        draw.line(((w-1),(bb),(w-1),(h - (xd * (p/4)) - offy)),fill="rgb(255,0,0)")     #Extend right hand line to base
        
        del draw
        ## End old code ------------------

        # Mask Codes (bitwise):
        #   0[1]: Do not output this tile
        #   1: Top left Triangle
        #   2: Top right Triangle
        #   3: Bottom left Triangle
        #   4: Bottom Right Triangle
        #   5: Top left Box
        #   6: Top right Box
        #   7: Bottom left Box
        #   8: Bottom right Box

        xx, yy = self.active.temp.iso_pos

        tile_im = Mask(self, p, active_image.mask[0][xx][yy], (0,255,255,128), (0,0,0,0))
        xpos = (xd*(p/2)) - (xx * (p/2)) + (yy * (p/2)) - p/2
        ypos = (xx * (p/4)) + (yy * (p/4)) + ((zd-1) * p)
        if xx != -1:
            if yy != -1:
                im.paste(tile_im,(xpos,ypos),tile_im)

        return im

    def ActivateProject(self):
        """Loads info from the active project (self.active) and updates everything
        in the window to reflect this"""
        # First, check the view and change the controls accordingly
        # NOTE: Must check anything which could affect which image is displayed
        # BEFORE the image displayer is called, otherwise it could show the wrong thing!
        app.debug_frame.WriteLine(str(self.active.activeimage))
        # First check if the winter image is enabled
        if self.active.info.winter == 1:
            self.rightbar_views_winter.SetValue(True)
            self.frame_select_winter.Enable()
        else:
            self.rightbar_views_winter.SetValue(False)
            self.frame_select_winter.Disable()
            if self.frame_select_winter.GetValue() == 1:
                self.frame_select_winter.SetValue(0)
                self.frame_select_summer.SetValue(1)
                # Active image thus changes...
                if self.active.activeimage[2] == 3:     # If Winter/Front change to Summer/Front
                    self.active.activeimage[2] = 2
                elif self.active.activeimage[2] == 1:   # If Winter/Back change to Summer/Back
                    self.active.activeimage[2] = 0
        # Then check the front/back image
        if self.active.info.frontimage == 1:
            self.rightbar_views_front.SetValue(True)
            self.frame_select_front.Enable()
        else:
            self.rightbar_views_front.SetValue(False)
            self.frame_select_front.Disable()
            if self.frame_select_front.GetValue() == 1:
                self.frame_select_front.SetValue(0)
                self.frame_select_back.SetValue(1)
                # Active image thus changes...
                if self.active.activeimage[2] == 3:     # If Winter/Front change to Winter/Back
                    self.active.activeimage[2] = 1
                elif self.active.activeimage[2] == 2:   # If Summer/Front change to Summer/Back
                    self.active.activeimage[2] = 0
        # Now check the directions
        if self.active.info.views == 1:
            self.rightbar_views.SetValue("1")
            self.frame_select_n.Enable()
            self.frame_select_e.Disable()
            self.frame_select_s.Disable()
            self.frame_select_w.Disable()
            self.frame_select_n.SetValue(True)
            self.frame_select_e.SetValue(False)
            self.frame_select_s.SetValue(False)
            self.frame_select_w.SetValue(False)
            self.active.activeimage[1] = 0
        elif self.active.info.views == 2:
            self.rightbar_views.SetValue("2")
            self.frame_select_n.Enable()
            self.frame_select_e.Enable()
            self.frame_select_s.Disable()
            self.frame_select_w.Disable()
            if self.active.activeimage[1] == 2 or self.active.activeimage[1] == 3:
                self.frame_select_n.SetValue(False)
                self.frame_select_e.SetValue(True)
                self.frame_select_s.SetValue(False)
                self.frame_select_w.SetValue(False)
                self.active.activeimage[1] = 1
        else:
            self.rightbar_views.SetValue("4")
            self.frame_select_n.Enable()
            self.frame_select_e.Enable()
            self.frame_select_s.Enable()
            self.frame_select_w.Enable()
        # Now change the controls for these on the side panel...
        self.rightbar_views
        self.rightbar_views_winter
        self.rightbar_views_front

        # Offset controls
        if self.options.offset_fine == 0:
            # Change the arrows of the buttons to be double arrows
            self.rightbar_button_up.SetBitmapLabel(self.imres.up2)
            self.rightbar_button_down.SetBitmapLabel(self.imres.down2)
            self.rightbar_button_left.SetBitmapLabel(self.imres.left2)
            self.rightbar_button_right.SetBitmapLabel(self.imres.right2)
        else:
            # Change the arrows of the buttons to be single arrows
            self.rightbar_button_up.SetBitmapLabel(self.imres.up)
            self.rightbar_button_down.SetBitmapLabel(self.imres.down)
            self.rightbar_button_left.SetBitmapLabel(self.imres.left)
            self.rightbar_button_right.SetBitmapLabel(self.imres.right)

        self.rightbar_offset_selector.SetValue(self.options.offset_fine)

        # Display options things
        self.rightbar_displayops_mask.SetValue(self.options.show_mask)
        self.rightbar_displayops_smoke.SetValue(self.options.show_smoke)

        self.rightbar_paksize.SetValue(str(self.active.info.paksize))

        # Side pane related things
        self.rightbar_displayops[self.options.sidepane].SetValue(True)
        self.rightbar_displayops_toggle.SetValue(self.options.sidepane_show)

        # Project dimensions
        # On project dimensions change, if not using a custom mask
        # we should update the masks of all the frames to reflect the
        # new dimensions. Remembering that the dimensions are reversed
        # for the east & west views
        self.rightbar_xdims.SetValue(str(self.active.info.xdims))
        self.rightbar_ydims.SetValue(str(self.active.info.ydims))
        self.rightbar_zdims.SetValue(str(self.active.info.zdims))
        if self.active.info.custom_mask == 0 and self.active.temp.update_dims == 1:
            self.active.temp.update_dims = 0
            # Update all the frame(s) mask info
            self.MakeDefaultMask()
            app.debug_frame.WriteLine("MAKE MASK")

        # Load the path of the currently viewed image
        self.impath_entry_box.SetValue(self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].path)

        # Update the display of which frame this is
        self.frame_select_label.SetLabel(gt("Frame %i of %i (%s)") % (self.active.activeimage[0]+1,len(self.active.frame),self.GetImageStats()))

    def GetImageStats(self):
        if self.active.activeimage[1] == 0:
            direction = gt("North")
        elif self.active.activeimage[1] == 1:
            direction = gt("East")
        elif self.active.activeimage[1] == 2:
            direction = gt("South")
        else:
            direction = gt("West")
        if self.active.activeimage[2] == 0:
            season = gt("Summer")
            image = gt("BackImage")
        elif self.active.activeimage[2] == 1:
            season = gt("Winter")
            image = gt("BackImage")
        elif self.active.activeimage[2] == 2:
            season = gt("Summer")
            image = gt("FrontImage")
        else:
            season = gt("Winter")
            image = gt("FrontImage")
        return (image + " / " + season + " / " + direction)

    def MakeDefaultMask(self):
        """Generate default cutting masks for all of the frames"""
        for f in range(len(self.active.frame)):
            for d in range(4):
                for i in range(4):
                    thisimage = self.active.frame[f].direction[d].image[i]
                    for z in range(self.active.info.zdims):
                        if d in [0,2]:
                            xx = self.active.info.xdims
                            yy = self.active.info.ydims
                        else:
                            xx = self.active.info.ydims
                            yy = self.active.info.xdims
                        for x in range(xx):
                            for y in range(yy):
                                # If this is the bottom layer
                                if z == 0:
                                    # And it's the top-right edge
                                    if x == 0:
                                        # If it's the very top middle square
                                        if y == 0:
                                            # Mask for top-middle
                                            thisimage.mask[z][x][y] = [0,0,0,1,1,0,0,0,0]
                                        else:
                                            # Mask for top-right
                                            thisimage.mask[z][x][y] = [0,1,0,1,1,1,0,0,0]
                                    else:
                                        # If this isn't the top-right edge
                                        if y == 0:
                                            # If it's the top-left edge, but not the top-middle
                                            thisimage.mask[z][x][y] = [0,0,1,1,1,0,1,0,0]
                                        else:
                                            # Else use the standard mask
                                            thisimage.mask[z][x][y] = [0,1,1,1,1,1,1,0,0]
                                # If this isn't the bottom layer
                                else:
                                    # And it's the top-right edge
                                    if x == 0:
                                        # If it's the very top middle square
                                        if y == 0:
                                            # Mask for top-middle
                                            thisimage.mask[z][x][y] = [0,0,0,0,0,0,0,0,0]
                                        else:
                                            # Mask for top-right
                                            thisimage.mask[z][x][y] = [0,0,0,0,0,1,0,1,0]
                                    else:
                                        # If this isn't the top-right edge
                                        if y == 0:
                                            # If it's the top-left edge, but not the top-middle
                                            thisimage.mask[z][x][y] = [0,0,0,0,0,0,1,0,1]
                                        else:
                                            # Else don't output this tile
                                            thisimage.mask[z][x][y] = [1,0,0,0,0,1,1,1,1]

class MyApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def OnInit(self):
        # Anything that needs to happen before the creation of the frame
        # should happen here
        self.active_project_number = 0

        self.projects = []
        self.options = ProgramOptions()
        
        self.debug_frame = DebugFrame(None, -1, "Debugging")
        if debug == 1:
            self.debug_frame.Show(True)

        # Create the main window frame
        self.frame = MainWindow(None, -1, "TileCutter v.%s"%VERSION_NUMBER)
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        # When the frame is closed (and returns) the program will exit,
        # any exiting stuff should thus go here.

        return True

    def ExitProgram(self, code):
        """Exits the program"""
        self.debug_frame.Close(True)
        self.frame.Close(True)

    def NewProject(self):
        """initialises a new project"""
        self.projects.append(ProjectData())
        self.active_project_number = len(self.projects)-1
        self.frame.InitProject(self.active_project_number)
        # Set the hash of the new project
        self.frame.active.temp.project_hash = self.frame.PickleProject()[1]

    def LoadProject(self, loaded_project):
        """Loads a project into the list of projects, takes a project object"""
        self.projects.append(loaded_project)
        self.active_project_number = len(self.projects)-1
        self.frame.InitProject(self.active_project_number)

    def CloseProject(self, to_close=-1):
        """Closes the currently active project"""
        if to_close == -1:
            close_project_number = self.active_project_number
        else:
            close_project_number = to_close
        self.projects.pop(close_project_number)
        if len(self.projects) == 0:
            # Create a new project
            self.NewProject()
        else:
            self.active_project_number = len(self.projects)-1
            self.frame.InitProject(self.active_project_number)

    def LoadProgramOps(self):
        self.frame.InitProgramOps()

if __name__ == '__main__':
    makeobj = Makeobj()
    app = MyApp(0)
    app.LoadProgramOps()
    app.NewProject()
    app.MainLoop()

