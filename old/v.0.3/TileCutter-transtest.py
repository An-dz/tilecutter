    
# Hack to make PIL work with py2exe
import Image
import PngImagePlugin
import JpegImagePlugin
import GifImagePlugin
import BmpImagePlugin
Image._initialized=2

import ImageDraw
import ImageWin
import os
import wx
import wx.lib.masked as masked
import wx.lib.scrolledpanel as scrolled
import wx.lib.hyperlink as hl
import sys
import pickle
import copy

ID_ABOUT=1101
ID_OPEN=1102
ID_EXIT=1110
ID_INPUT=7001
ID_OUTPUT=7002
ID_EDIT_GOOD = 7003
ID_EDIT_CAP = 7004
ID_EDIT_FAC = 7005
ID_EDIT_SUP = 7006

MAX_FRAMES = 64
VERSION_NUMBER = "0.3d"
PATH_TO_PAL_FILE = "simud80.pal"
DEFAULT_PAKSIZE = "64"

##path_to_pal = PATH_TO_PAL_FILE

#sys.stderr.write("a")

fsock = open('error.log', 'w')
sys.stderr = fsock

def MakeIcon(self, img):
    """
    The various platforms have different requirements for the
    icon size...
    """
    if "wxMSW" in wx.PlatformInfo:
        img = img.Scale(16, 16)
    elif "wxGTK" in wx.PlatformInfo:
        img = img.Scale(22, 22)
    # wxMac can be any size upto 128x128, so leave the source img alone....
    icon = wx.IconFromBitmap(img.ConvertToBitmap() )
    return icon


#language = ""
#firstrun = 0

def relative(p1, p2):
    """Take two absolute paths and return a relative path between them"""
    p1 = os.path.abspath(p1)
    p2 = os.path.abspath(p2)
    cp = os.path.commonprefix([p1,p2])
    i = len(cp)
    #check for path separator or empty on both:
    if not (p1[i:i+1] in '/\\' and p2[i:i+1] in '/\\'):
        cp = os.path.dirname(cp)
    up = p1.count(os.path.sep, len(cp)+1)
    return up*('..%s'%os.path.sep) + p2[len(cp)+1:]

def Write_Config(language):
    file = open("tilecutter.cfg", "w")
    file.write("language=\n" + language + "\n")
##    file.write("path_to_pal=\n" + path_to_pal + "\n") 
    file.close()

def Read_Config():
    #Read from the config file, if no config file exists, create one
    if os.access("tilecutter.cfg", os.F_OK):
        file = open("tilecutter.cfg", "r")
        p = file.readlines()
        file.close()
##        for i in range(len(p)):
##            if p[i] == "path_to_pal=\n":
##                path_to_pal = p[i + 1][:2]

        for i in range(len(p)):
            #if p[i] == "firstrun=\n":
            #    firstrun = int(p[i + 1][:-1])
            #    if firstrun == 1:
            #        return ("", 1)      #If set for first run, return 1 to initiate config
            if p[i] == "language=\n":
                lan = p[i + 1][:2]
                #Check that the language code given in the config file is valid!
                options = []
                if os.access("language/", os.F_OK):
                    listing = []
                    listing = os.listdir("language/")  #Get a list of the contents of the languages subfolder
                    for i in range(len(listing)):
                        if listing[i][-4:] == ".tab":
                            if listing[i][:3] == "tc-":
                                options.append(listing[i][3:5])     #Add the language code to the list of ones to display
                    if options.count(lan) != 0:
                        return (lan, 0)         #If the language code is valid, return it for use
                    else:
                        return ("", 1)          #Otherwise, we need a new config file
                else:
                    sys.stderr.write("ERROR: Unable to open the language directory - please check your installation!")
                    return ("", -1)
            else:
                return ("", 1)
    else:
        return ("", 1)
        #language = "en"
    

translation = []
choicelist_paksize = []
choicelist_dims = []
choicelist_dims_z = []
choicelist_anim = []
tc_month_choices = []


def Load_Translation(code):
    """Loads a translation file into memory, takes a two-letter country code as input"""
    file = open(("language\\tc-" + code + ".tab"), "r")
    p = file.readlines()
    file.close
    translation = []
    for i in range(len(p)):
        if p[i][0] != "#":          #If the first character of a line is "#" it's a comment, so don't read it into the main file
            if p[i] == "\n" or p[i] == "":
                translation.append("")          #If line empty (just a newline, or completely blank) add a blank entry
            elif p[i][-1] == "\n":
                translation.append(p[i][:-1])   #If line ends in a newline, strip the newline and add it
            else:
                translation.append(p[i])        #If line has no newline, just add it
            #sys.stderr.write(p[i])
    return translation


def gt(string):
    """Return a translated string for the input string if available, else just return the same"""
    string = string.encode("utf-8")
    if translation.count("~" + string) == 0:
        x = string
    elif translation.count("~" + string) > 0:
        if translation[(translation.index("~" + string) + 1)] == "":
            x = string
        else:
            x = unicode(translation[(translation.index("~" + string) + 1)], "utf-8")
    return x




class frame_props:
    """All the properties of a frame, created as a subclass of frame"""
    abs_path = ""
    rel_path = ""
    #filename = ""
    image = 0
    xdims = 1
    ydims = 1
    zdims = 1
    offsetx = 0
    offsety = 0
class smoke:
    """Details pertaining to any smoke object associated with a project"""  #Needs implementing later
    abs_path = ""
    rel_path = ""
    filename = ""
    smokename = ""
class output:
    """Details of the output options for a project"""
    abs_path_dat = ""
    abs_path_png = ""
class good:
    """An entry in either the input or output goods list,
    always used as a subclass of datoptions"""
    type = ""
    val = 0
    name = ""
    capacity = ""
    factor = ""
    supplier = ""
class dat:
    """All .dat file options for a project, these are loaded into
    the .dat file edit dialog"""
    obj = 0   #"b" (building) = 0, "f" (factory) = 1 or "o" (misc) = 2
    #Global
    name = ""   #Any
    copyright = ""
    in_month = 0
    in_year = ""
    out_month = 0
    out_year = ""
    level = ""
    noinfo = 0
    nocon = 0
    #Building
    type = 0
    location_b = ""
    chance_b = ""
    build_time = ""
    extension = 0
    pax = 0
    post = 0
    ware = 0
    #Factory
    location_f = ""
    chance_f = ""
    prod = ""
    range = ""
    colour = ""
    # Needs Ground - whether the ground should be drawn under the building or not
    needs_ground = 0
    #Additional options
    add = ""
    # Input/Output goods
    inputgoods = []
    outputgoods = []
    # Climates, array of the climates this building will appear in
    # rocky, tundra, temperate, mediterran, desert, arctic, tropic, water
    climates = []

class tc_frame:
    """Contains 4 sub-options for each possible view of a given frame"""
    def __init__(self):
        self.north = frame_props()
        self.east = frame_props()
        self.south = frame_props()
        self.west = frame_props()
    north = ""
    east = ""
    south = ""
    west = ""
class tc_project:
    """The overall project object, containing all details of the project"""
    frame = []
    #frame.append(frame_props())
    smoke = smoke()
    output = output()
    dat = dat()
    paksize = "64"
    views = "1"
    abs_path = ""
    rel_path = ""
    filename = ""
        
#project = tc.project() #Project is the overall container for all project data, it contains several other types of object
                        #defined in the tc class above. Loading/saving a project involves loading or saving a project
                        #object (through pickling).
                        #This is now initialised in the main window init function


def LoadPal(palname=PATH_TO_PAL_FILE):
    """Loads a pal file as a list of rgb values"""
    f = open(palname, "r")
    p = f.readlines()
    f.close
    pal = []
    for i in range(1,257):
        pal.append(p[i][:-1])
    return pal

def GetPalEntry(pal, i):
    """Given a palette object and a reference number, this function
    returns a tuple with the rgb value of that entry in the palette"""
    if pal[i][1] == " ":
        r = pal[i][0:1]
        if pal[i][3] == " ":
            g = pal[i][2:3]
            b = pal[i][4:]
        elif pal[i][4] == " ":
            g = pal[i][2:4]
            b = pal[i][5:]
        else:
            g = pal[i][2:5]
            b = pal[i][6:]
    elif pal[i][2] == " ":
        r = pal[i][0:2]
        if pal[i][4] == " ":
            g = pal[i][3:4]
            b = pal[i][5:]
        elif pal[i][5] == " ":
            g = pal[i][3:5]
            b = pal[i][6:]
        else:
            g = pal[i][3:6]
            b = pal[i][7:]
    else:
        r = pal[i][0:3]
        if pal[i][5] == " ":
            g = pal[i][4:5]
            b = pal[i][6:]
        elif pal[i][6] == " ":
            g = pal[i][4:6]
            b = pal[i][7:]
        else:
            g = pal[i][4:7]
            b = pal[i][8:]
    return (int(r),int(g),int(b))

def DrawIcon(icon):
    """Draws one of a number of icons used in the program
       Valid arguments are: summer, winter"""
    if icon == "summer":
        b = wx.Image("summer-icon.png")
    elif icon == "winter":
        b = wx.Image("winter-icon.png")

    b.SetMaskFromImage(b,255,255,255)        
    bmp = b.ConvertToBitmap()
    return bmp

def DrawArrow(direction, double=0):
    """Draws an arrow in the specified direction for use on buttons
    valid values: up, down, left, right"""
    if direction == "up":
        if double == 0:
            b = wx.EmptyImage(7, 4)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,j,255,255,255)
                    b.SetRGB((6 - i),j,255,255,255)
        else:
            b = wx.EmptyImage(7, 8)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,j,255,255,255)
                    b.SetRGB((6 - i),j,255,255,255)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,j+4,255,255,255)
                    b.SetRGB((6 - i),j+4,255,255,255)

    if direction == "down":
        if double == 0:
            b = wx.EmptyImage(7, 4)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,(3 - j),255,255,255)
                    b.SetRGB((6 - i),(3 - j),255,255,255)
        else:
            b = wx.EmptyImage(7, 8)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,(3 - j),255,255,255)
                    b.SetRGB((6 - i),(3 - j),255,255,255)
            for i in range(3):
                for j in range((3 - i)):
                    b.SetRGB(i,(3 - j)+4,255,255,255)
                    b.SetRGB((6 - i),(3 - j)+4,255,255,255)

    if direction == "left":
        if double == 0:
            b = wx.EmptyImage(4, 7)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB(i,j,255,255,255)
                    b.SetRGB(i,(6 - j),255,255,255)
        else:
            b = wx.EmptyImage(8, 7)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB(i,j,255,255,255)
                    b.SetRGB(i,(6 - j),255,255,255)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB(i+4,j,255,255,255)
                    b.SetRGB(i+4,(6 - j),255,255,255)
    if direction == "right":
        if double == 0:
            b = wx.EmptyImage(4, 7)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB((3 - i),j,255,255,255)
                    b.SetRGB((3 - i),(6 - j),255,255,255)
        else:
            b = wx.EmptyImage(8, 7)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB((3 - i),j,255,255,255)
                    b.SetRGB((3 - i),(6 - j),255,255,255)
            for i in range(6):
                for j in range((3 - i)):
                    b.SetRGB((3 - i)+4,j,255,255,255)
                    b.SetRGB((3 - i)+4,(6 - j),255,255,255)

    if direction == "empty":
        b = wx.EmptyImage(1, 1)
        b.SetRGB(0,0,231,255,255)
    b.SetMaskFromImage(b,255,255,255)        
    bmp = b.ConvertToBitmap()
    return bmp

def ShowImage(showimg, b):
    """Shows the image in the display port: (image to display, port to use)"""
    outimage = wx.EmptyImage(showimg.size[0], showimg.size[1])  #create a new wx.image
    outimage.SetData(showimg.convert("RGB").tostring())         #convert PIL image to RGB bitmap, then append into new wx.image
    outimage = outimage.ConvertToBitmap()                       #finally convert to wx.bitmap for display

    frame.tc_display_panel.bmp = outimage
    frame.tc_display_panel.DrawBitmap(1)


    return outimage     #return not required

def NewImage(dimensions=(1,1)):
    """Create a new image with dimensions"""
    om = Image.new("RGB", dimensions, color=(231,255,255))
    return om

#Analyse image, args:
#                   dims - (-1,-1,-1) means run detection, assume square, else is (x,y,z) coords
#                   off - means offset for detection from top-left corner, default nothing
#                   dir - direction, "N","E","S","W" - possibly redundant?
#                   frame - frame # of image - Again, possibly redundant, doesn't actually affect this (yet...)
def Analyse(current,p,dims=(-1,-1,-1),off=(0,0),dir="",frame=0,showgrid=1):
    """Resizes an image to be a multiple of the paksize, and optionally
    draws a grid on the image demonstrating the cutting margins.
    Args: image, pakSize, dims=(x,y,z), off=(x,y), dir, frame"""
    xd, yd, zd = dims
    xoff, yoff = off
    image = current.image
    w, h = image.size

    hOut = h    
    if xd == -1:
        a = divmod(w, p)                # a = width - offset divided by paksize, divisor and remainder
        if a[1] == 0:
            wOut = xoff + (a[0] * p)
            xdn = a[0]                  # xdn (xdims new) = number of tiles wide
            ydn = a[0]                  # ydn = number of tiles wide (assumes square building)
        else:
            wOut = xoff + (a[0] * p) + p
            xdn = a[0] + 1              # xdn (xdims new) = number of tiles wide plus one for adjustment
            ydn = a[0] + 1              # ydn = number of tiles wide (assumes square building) plus one for adjustment
    else:
        xdn = xd
        ydn = yd
        wOut = xoff + ((xdn + ydn) * (p / 2))
        if wOut < w:
            wOut = w
        
    
    gamma = ((xdn + ydn) * (p / 4)) - (p / 2)    # gamma = base offset for vertical adjustment (tiles underneath everything)
    if zd == -1:
        if gamma >= (h - yoff):
            hOut = gamma + p
            zdn = 1
        else:
            b = divmod((h - gamma), p)
            if b[1] == 0:
                hOut = yoff + (b[0] * p) + gamma
                zdn = b[0]
            else:
                hOut = yoff + (b[0] * p) + p + gamma
                zdn = b[0] + 1
    else:
        zdn = zd
        hOut = yoff + gamma + (zdn * p)
#        if hOut < h:
#            hOut = h

    imOut = NewImage((wOut,hOut))
#    imOut = Image.new("RGB", (wOut, hOut))
#    image.crop((0,0,w,h))
    imOut.paste(image, (0,(hOut - image.size[1])))

    if showgrid == 1:
        dimsOut = xdn,ydn,zdn
        DrawGrid(imOut,p,dimsOut,off)

    if xd == -1 or yd == -1 or zd == -1:    #If any of these are -1, we're using the auto feature, so don't update current
        return (xdn, ydn, zdn)              #Just return the values found
    else:
        current.xdims = xdn
        current.ydims = ydn     #With these enabled, auto will not appear on the comboboxes
        current.zdims = zdn

        current.offsetx = xoff
        current.offsety = yoff
    
        return imOut    #Return the image to display, original image is stored in current.image


def DrawGrid(image,p,dims,off):
    offx, offy = off
    xd, yd, zd = dims
    zd = zd
    w = offx + ((xd + yd) * (p / 2))
    h = image.size[1]
    
    draw = ImageDraw.Draw(image)    #make a context to draw to out of the image

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

#    imOut = image
    return image



#Catch-all tile copy routine, can be used for anything
#   p - paksize
#   imgIn - base image to copy from
#   imgOut - output image to copy to
#   fromXY -  x, y and z coords of the tile to copy (works out position from these)
#   toXY - x and y coords of the square in the output image to copy to
#   dims - dimensions of the image in tiles (x,y,z)
#   off - offset values
#
def CopyXY(p, imgIn, imgOut, fromXY=(0,0,0), toXY=(0,0), dims=(-1,-1,-1), off=(0,0), mask=0):
    """Copies part of an image to another"""
    if mask != 0:               #Mask of 0 implies that the tile should not be cut...
        x, y, z = fromXY
        dimx, dimy, dimz = dims
        offx, offy = off

        fDimX = (dimx * (p/2)) - (x * (p/2)) + (y * (p/2)) - (p/2)  #looks ok
        
        #fDimY = ((dimx + dimy) * (p/4)) + ((x + y) * (p/4)) - (p/2) + (z * p) - 1
        fDimY = ((dimz * p) - ((z + 1) * p)) + (x * p/4) + (y * p/4) - 1
        left = fDimX + offx
        upper = fDimY
        #upper = fDimY - offy
        right = left + p
        lower = upper + p
        imgCopy = imgIn.crop((left, upper, right, lower))
        if mask != 7:           #Mask of 7 is effectively no mask so skip to save time
            imgPaste = MaskXY(p, imgCopy, mask)
        else:
            imgPaste = imgCopy
        upper = toXY[0] * p
        left = toXY[1] * p
        imgOut.paste(imgCopy, (upper, left))

def MaskXY(p, im, mask):
    draw = ImageDraw.Draw(im)   #make a context to draw to out of the image
    
    if mask == 1:               #Mask 1 (tile only)
        draw.rectangle(((0,0),(p,(p/2))), fill=(231,255,255))                               #Draw top box
        draw.polygon([(0, p/2), (p/2, p/2), (0, p/2 + p/4)], fill=(231,255,255))            #Draw top left triangle
        draw.polygon([(p/2-1, p/2), (p-1, p/2), (p-1, p/2 + p/4)], fill=(231,255,255))      #Draw top right triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 2:
        draw.rectangle(((p/2, 0),(p, p/2)), fill=(231,255,255))                             #Draw top box (right)
        draw.polygon([(p/2-1, p/2), (p-1, p/2), (p-1, p/2 + p/4)], fill=(231,255,255))      #Draw top right triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 3:
        draw.rectangle(((0,0),(p/2-1, p/2)), fill=(231,255,255))                              #Draw top box (left)
        draw.polygon([(0, p/2), (p/2, p/2), (0, p/2 + p/4)], fill=(231,255,255))            #Draw top left triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 4:
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 5:
        draw.rectangle(((p/2, 0),(p, p)), fill=(231,255,255))                             #Draw right hand box
    elif mask == 6:
        draw.rectangle(((0, 0),(p/2, p)), fill=(231,255,255))                             #Draw left hand box
    # If mask is 7, do nothing
    del draw

def MakeMatrix(num_frames, zdims, xdims, ydims):
    """Makes a standard cutting matrix for a building view with auto-generated masking - this is a temporary function"""
    matrix = []
    for f in range(int(num_frames)):                     #For each frame in this direction
        for z in range(int(zdims)):                          #For each height level
            for x in range(int(xdims)):                          #For each x value
                for y in range(int(ydims)):                          #For each y value
                    if z == 0:                                      #If this is the bottom layer...
                        if x == 0:                                      #And this is the top-right edge...
                            if y == 0:
                                mask = 4                                    #Mask for top-middle
                            else:
                                mask = 3                                    #Otherwise mask for top-right
                        elif y == 0:                                    #if this is the top-left edge...
                            mask = 2                                        #Mask for top-left
                        else: mask = 1                                  #Otherwise standard mask...
                    else:                                           #Otherwise, if this is not the bottom layer...
                        if x == 0:                                      #And this is the top-right edge...
                            if y == 0:
                                mask = 7                                    #Mask for top-middle
                            else:
                                mask = 6                                    #Otherwise mask for top-right
                        elif y == 0:                                    #If this is the top-left edge
                            mask = 5                                        #Mask for top-left
                        else: mask = 0                  #Otherwise do not cut this tile

                        
                    matrix.append((f, z, x, y, mask))
    return matrix;

def Export(args=0):
    """Exports a .png and .dat of the project, optionally runs makeobj to create a pak file"""
    makepak = 0
    makedat = 0
    if args == 1:
        makepak = 1
    elif args == 2:
        makedat = 1
    north_matrix = []
    east_matrix = []
    south_matrix = []
    west_matrix = []    #Create lists for the direction matrixes
    #Next, use values of the project to generate the matrix tuples
    num_frames = len(frame.project.frame)
    
    #Get dimensions to use... Dims from frame #0 used
    xdimsN = frame.project.frame[0].north.xdims
    ydimsN = frame.project.frame[0].north.ydims
    zdimsN = frame.project.frame[0].north.zdims
    xdimsE = frame.project.frame[0].east.xdims
    ydimsE = frame.project.frame[0].east.ydims
    zdimsE = frame.project.frame[0].east.zdims
    xdimsS = frame.project.frame[0].south.xdims
    ydimsS = frame.project.frame[0].south.ydims
    zdimsS = frame.project.frame[0].south.zdims
    xdimsW = frame.project.frame[0].west.xdims
    ydimsW = frame.project.frame[0].west.ydims
    zdimsW = frame.project.frame[0].west.zdims
    
    #Tuple structure...
    #   (Frame #, z, x, y, mask)
    #   If mask set to 0, do not cut this tile
    #Now build the standard cutting mask from the frame values
    north_matrix = MakeMatrix(num_frames, zdimsN, xdimsN, ydimsN)
    east_matrix = MakeMatrix(num_frames, zdimsE, xdimsE, ydimsE)
    south_matrix = MakeMatrix(num_frames, zdimsS, xdimsS, ydimsS)
    west_matrix = MakeMatrix(num_frames, zdimsW, xdimsW, ydimsW)
            
    #sys.stderr.write(str(north_matrix))
    #sys.stderr.write("\n")
    #sys.stderr.write("z: " + str(zdims) + " x: " + str(xdims) + " y: " + str(ydims))

    #Make output image, 2 kinds, optimized for space (needs to be done!) and debugging, which is layed out strictly
    #Debugging layout -> 4 columns, north, east, south, west
                    #Width of column = direction ydims
                    #Height of column = direction xdims * direction zdims
                    #Width of overall image = Ny + Ey + Sy + Wy
                    #Height of overall image = biggest out of Dx * Dz
    #Compressed layout -> Only cut tiles outputted, in the smallest and squarest possible space, not designed to be human readable
                    #Find total number of output tiles (tiles which are cut)
                    #Organise them somehow into the smallest space

    #Produce image width, just y values added together (also determine if directions to be used!)
    #Produce image heights (one for each direction) then determine which is biggest and use that for output
    if frame.project.views == "1":
        #Width...
        if ydimsN > 0:
            width_out = ydimsN
        else:
            sys.stderr.write("ERROR: Incorrectly set ydimsN in output function")
        #Height...
        if xdimsN > 0:
            if zdimsN > 0:
                height_out = zdimsN * xdimsN
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsN in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsN in output function")
    elif frame.project.views == "2":
        #Width...
        if ydimsN > 0:
            if ydimsE > 0:
                width_out = ydimsN + ydimsE
            else:
                sys.stderr.write("ERROR: Incorrectly set ydimsE in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set ydimsN in output function")
        #Height...
        if xdimsN > 0:
            if zdimsN > 0:
                height_outN = zdimsN * xdimsN
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsN in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsN in output function")
        if xdimsE > 0:
            if zdimsE > 0:
                height_outE = zdimsE * xdimsE
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsE in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsE in output function")
        #Determine which height is bigger
        heights = []
        heights.append(height_outN)
        heights.append(height_outE)
        height_out = max(heights)
            
    elif frame.project.views == "4":
        #Width...
        if ydimsN > 0:
            if ydimsE > 0:
                if ydimsS > 0:
                    if ydimsW > 0:
                        width_out = ydimsN + ydimsE + ydimsS + ydimsW
                    else:
                        sys.stderr.write("ERROR: Incorrectly set ydimsW in output function")
                else:
                    sys.stderr.write("ERROR: Incorrectly set ydimsS in output function")
            else:
                sys.stderr.write("ERROR: Incorrectly set ydimsE in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set ydimsN in output function")
        #Height...
        if xdimsN > 0:
            if zdimsN > 0:
                height_outN = zdimsN * xdimsN
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsN in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsN in output function")
        if xdimsE > 0:
            if zdimsE > 0:
                height_outE = zdimsE * xdimsE
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsE in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsE in output function")
        if xdimsS > 0:
            if zdimsS > 0:
                height_outS = zdimsS * xdimsS
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsS in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsS in output function")
        if xdimsW > 0:
            if zdimsW > 0:
                height_outW = zdimsW * xdimsW
            else:
                sys.stderr.write("ERROR: Incorrectly set zdimsW in output function")
        else:
            sys.stderr.write("ERROR: Incorrectly set xdimsW in output function")
        #Determine which height is bigger
        heights = []
        heights.append(height_outN)
        heights.append(height_outE)
        heights.append(height_outS)
        heights.append(height_outW)
        height_out = max(heights)

    else:
        sys.stderr.write("ERROR: Incorrectly set Project Views in output function")

    #Do .dat file output...
    #Output all the bits of the dat file before the image data
    #All dat file entries should end with a newline

    # First, check to see if a file with this name already exists
    if os.access(frame.project.output.abs_path_dat, os.F_OK) == 1:
        old_datfile = open(frame.project.output.abs_path_dat, "r")
        old_datfile_data = old_datfile.read()
        old_datfile.close()

        # If an old file exists, write it to a backup file
        path_1 = os.path.split(frame.project.output.abs_path_dat)
        new_path = path_1[0] + os.path.sep + "backup-" + path_1[1]
        old_datfile = open(new_path, "w")
        old_datfile.write(old_datfile_data)
        old_datfile.close()
##        sys.stderr.write("VALUE: " + new_path)

    datfile = open(frame.project.output.abs_path_dat, "w")
    
    datfile.write("#\n# File created with TileCutter version " + VERSION_NUMBER +
                  "\n# For more information see http://simutrans.entropy.me.uk/tilecutter/\n#\n")
    if frame.project.dat.obj != 2:
        if frame.project.dat.obj == 0:
            datfile.write("Obj=building\n")
        else:
            datfile.write("Obj=factory\n")
        if frame.project.dat.name == "":
            datfile.write("name=default_name\n")
        else:
            datfile.write("name=" + frame.project.dat.name + "\n")

        if frame.project.dat.copyright != "":
            datfile.write("copyright=" + frame.project.dat.copyright + "\n")

        if frame.project.dat.in_year != "":     #If intro year not set to nothing, output it
            datfile.write("intro_year=" + frame.project.dat.in_year + "\n")
            if frame.project.dat.in_month > 0:  #Only output a month if year is output and month value is set
                datfile.write("intro_month=" + str(frame.project.dat.in_month) + "\n")
                              
        if frame.project.dat.out_year != "":    #Same as for intro year
            datfile.write("retire_year=" + frame.project.dat.out_year + "\n")
            if frame.project.dat.out_month > 0: #Same as for intro year
                datfile.write("retire_month=" + str(frame.project.dat.out_month) + "\n")
                              
        if frame.project.dat.level != "":
            datfile.write("level=" + frame.project.dat.level + "\n")

        if frame.project.dat.noinfo == 1 or frame.project.dat.noinfo == "1":
            datfile.write("NoInfo=1\n")
        if frame.project.dat.nocon == 1 or frame.project.dat.nocon == "1":
            datfile.write("NoConstruction=1\n")
        if frame.project.dat.needs_ground == 1 or frame.project.dat.needs_ground == "1":
            datfile.write("needs_ground=1\n")

        # Write climates output
        if frame.project.dat.climates != []:
            out_clim = "climates=" + frame.project.dat.climates[0]
            for k in range(1, len(frame.project.dat.climates)):
                out_clim = out_clim + "," + frame.project.dat.climates[k]
            datfile.write(out_clim + "\n")

        if frame.project.dat.obj == 0:
            #Write a building dat file
            type = frame.project.dat.type
            #Write types...
            if type == 0: #type undefined
                datfile.write("#Warning - no building type defined for obj=building!\n")
            if type == 1:   #type carstop
                datfile.write("type=carstop\n")
            if type == 2:   #type busstop
                datfile.write("type=busstop\n")
            if type == 3:   #type station
                datfile.write("type=station\n")
            if type == 4:   #type monorailstop
                datfile.write("type=monorailstop\n")
            if type == 5:   #type harbour
                datfile.write("type=harbour\n")
            if type == 6:   #type wharf
                datfile.write("type=wharf\n")
            if type == 7:   #type airport
                datfile.write("type=airport\n")
            if type == 8:   #type hall
                datfile.write("type=hall\n")
            if type == 9:   #type post
                datfile.write("type=post\n")
            if type == 10:  #type shed
                datfile.write("type=shed\n")

            #Write other stuff for stations...
            if type > 0 and type < 11:
                if frame.project.dat.extension == 1 or frame.project.dat.extension == "1":
                    datfile.write("extension_building=1\n")
                if frame.project.dat.pax == 1 or frame.project.dat.pax == "1":
                    datfile.write("enables_pax=1\n")
                if frame.project.dat.post == 1 or frame.project.dat.post == "1":
                    datfile.write("enables_post=1\n")
                if frame.project.dat.ware == 1 or frame.project.dat.ware == "1":
                    datfile.write("enables_ware=1\n")

            if type == 11:  #type res
                datfile.write("type=res\n")
            if type == 12:  #type com
                datfile.write("type=com\n")
            if type == 13:  #type ind
                datfile.write("type=ind\n")

            if type == 14:  #type any
                datfile.write("type=any\n")
            if type == 15:  #type misc
                datfile.write("type=misc\n")

            #Write other stuff for Monument/Curiosity/Town Hall
            if type == 16:  #type mon
                datfile.write("type=mon\n")
                datfile.write("chance=" + frame.project.dat.chance_b + "\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
            if type == 17:  #type cur
                datfile.write("type=cur\n")
                datfile.write("location=" + frame.project.dat.location_b + "\n")
                datfile.write("chance=" + frame.project.dat.chance_b + "\n")
            if type == 18:  #type tow
                datfile.write("type=tow\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
            if type == 19:  #type hq
                datfile.write("type=hq\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
                
        else:
            #Write a factory dat file
            if frame.project.dat.location_f != "":
                datfile.write("Location=" + frame.project.dat.location_f + "\n")
            if frame.project.dat.chance_f != "":
                datfile.write("chance=" + frame.project.dat.chance_f + "\n")
            if frame.project.dat.prod != "":
                datfile.write("Productivity=" + frame.project.dat.prod + "\n")
            if frame.project.dat.range != "":
                datfile.write("Range=" + frame.project.dat.range + "\n")
            if frame.project.dat.colour != "":
                datfile.write("MapColor=" + frame.project.dat.colour + "\n")
                
            #Do input/output goods next...
            for a in range(len(frame.project.dat.inputgoods)):
                if frame.project.dat.inputgoods[a].name != "":  #input good must have a name
                    datfile.write("InputGood[" + str(a) + "]=" + frame.project.dat.inputgoods[a].name + "\n")
                    if frame.project.dat.inputgoods[a].capacity != "":
                        datfile.write("InputCapacity[" + str(a) + "]=" + frame.project.dat.inputgoods[a].capacity + "\n")
                    if frame.project.dat.inputgoods[a].factor != "":
                        datfile.write("InputFactor[" + str(a) + "]=" + frame.project.dat.inputgoods[a].factor + "\n")
                    if frame.project.dat.inputgoods[a].supplier != "":
                        datfile.write("InputSupplier[" + str(a) + "]=" + frame.project.dat.inputgoods[a].supplier + "\n")
            for a in range(len(frame.project.dat.outputgoods)):
                if frame.project.dat.outputgoods[a].name != "":     #Output good must have a name
                    datfile.write("OutputGood[" + str(a) + "]=" + frame.project.dat.outputgoods[a].name + "\n")
                    if frame.project.dat.outputgoods[a].capacity != "":
                        datfile.write("OutputCapacity[" + str(a) + "]=" + frame.project.dat.outputgoods[a].capacity + "\n")
                    if frame.project.dat.outputgoods[a].factor != "":
                        datfile.write("OutputFactor[" + str(a) + "]=" + frame.project.dat.outputgoods[a].factor + "\n")

            #Needs smoke stuff added here when smoke implemented!!
        if frame.project.dat.add != "" and frame.project.dat.add != "\n":
            if frame.project.dat.add[-1] == "\n":
                datfile.write(frame.project.dat.add)
            else:
                datfile.write(frame.project.dat.add + "\n")
    else:
        #Write a misc dat file
        if frame.project.dat.add != "":
            if frame.project.dat.add[-1] == "\n":
                datfile.write(frame.project.dat.add)
            else:
                datfile.write(frame.project.dat.add + "\n")
        else:
            datfile.write("#Warning - Object type set to \"other\", \nbut nothing specified in the \"any\" field!\n")
    #Make an image to output to
    imout = NewImage(((width_out * int(frame.project.paksize)), (height_out * int(frame.project.paksize))))
    
    #Now that we have a cutting matrix, we can proceed to the cutting routine
    views_int = int(frame.project.views)

    #Write dims information to .dat file...
    datfile.write("Dims=" + str(xdimsN) + "," + str(ydimsN) + "," + frame.project.views + "\n")

    #Get the relative path between the location of the dat file and the location of the png file
    dat_to_png = relative(frame.project.output.abs_path_dat, frame.project.output.abs_path_png)
    dat_to_png = os.path.splitext(dat_to_png)[0]
    for f in range(num_frames):
        
        if views_int >= 1:     #If one direction
            #For north direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].north, int(frame.project.paksize), (xdimsN, ydimsN, zdimsN),
                         (frame.project.frame[f].north.offsetx, frame.project.frame[f].north.offsety), showgrid=0)

            for i in range((f * len(north_matrix)), ((f + 1) * len(north_matrix))):     #For all the tiles in a given frame
                
                #(Frame #, z, x, y, mask)
                if north_matrix[i][4] != 0:     #If mask = 0, then this doesn't need an entry in the dat file
                    datfile.write("BackImage[%i][%i][%i][%i][%i]=%s.%i.%i\n" % (0, north_matrix[i][2], north_matrix[i][3], north_matrix[i][1],
                                                                                north_matrix[i][0], dat_to_png,
                                                                                (north_matrix[i][2] + (xdimsN * north_matrix[i][1])),
                                                                                north_matrix[i][3]))
                CopyXY(int(frame.project.paksize), im, imout, (north_matrix[i][2], north_matrix[i][3], north_matrix[i][1]),
                        ((north_matrix[i][3]), (north_matrix[i][2] + (xdimsN * north_matrix[i][1]))),
                       (xdimsN, ydimsN, zdimsN), (frame.project.frame[f].north.offsetx, frame.project.frame[f].north.offsety),
                       north_matrix[i][4])
        if views_int >= 2:                              #Do east as well
            #For east direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].east, int(frame.project.paksize), (xdimsE, ydimsE, zdimsE),
                         (frame.project.frame[f].east.offsetx, frame.project.frame[f].east.offsety), showgrid=0)

            for i in range((f * len(east_matrix)), ((f + 1) * len(east_matrix))):     #For all the tiles in a given frame

                #(Frame #, z, x, y, mask)
                if east_matrix[i][4] != 0:     #If mask = 0, then this doesn't need an entry in the dat file
                    datfile.write("BackImage[%i][%i][%i][%i][%i]=%s.%i.%i\n" % (0, east_matrix[i][2], east_matrix[i][3], east_matrix[i][1],
                                                                                east_matrix[i][0], dat_to_png,
                                                                                (east_matrix[i][2] + (xdimsE * east_matrix[i][1])),
                                                                                east_matrix[i][3]))
                CopyXY(int(frame.project.paksize), im, imout, (east_matrix[i][2], east_matrix[i][3], east_matrix[i][1]),
                        ((east_matrix[i][3] + (ydimsN)), (east_matrix[i][2] + (xdimsE * east_matrix[i][1]))),
                       (xdimsE, ydimsE, zdimsE), (frame.project.frame[f].east.offsetx, frame.project.frame[f].east.offsety),
                       east_matrix[i][4])
        if views_int == 4:                              #Do south and west also
            #For south direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].south, int(frame.project.paksize), (xdimsS, ydimsS, zdimsS),
                         (frame.project.frame[f].south.offsetx, frame.project.frame[f].south.offsety), showgrid=0)

            for i in range((f * len(south_matrix)), ((f + 1) * len(south_matrix))):     #For all the tiles in a given frame

                #(Frame #, z, x, y, mask)
                if south_matrix[i][4] != 0:     #If mask = 0, then this doesn't need an entry in the dat file
                    datfile.write("BackImage[%i][%i][%i][%i][%i]=%s.%i.%i\n" % (0, south_matrix[i][2], south_matrix[i][3], south_matrix[i][1],
                                                                                south_matrix[i][0], dat_to_png,
                                                                                (south_matrix[i][2] + (xdimsS * south_matrix[i][1])),
                                                                                south_matrix[i][3]))
                CopyXY(int(frame.project.paksize), im, imout, (south_matrix[i][2], south_matrix[i][3], south_matrix[i][1]),
                        ((south_matrix[i][3] + (ydimsN + ydimsE)), (south_matrix[i][2] + (xdimsS * south_matrix[i][1]))),
                       (xdimsS, ydimsS, zdimsS), (frame.project.frame[f].south.offsetx, frame.project.frame[f].south.offsety),
                       south_matrix[i][4])
            #For west direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].west, int(frame.project.paksize), (xdimsW, ydimsW, zdimsW),
                         (frame.project.frame[f].west.offsetx, frame.project.frame[f].west.offsety), showgrid=0)

            for i in range((f * len(west_matrix)), ((f + 1) * len(west_matrix))):     #For all the tiles in a given frame

                #(Frame #, z, x, y, mask)
                if west_matrix[i][4] != 0:     #If mask = 0, then this doesn't need an entry in the dat file
                    datfile.write("BackImage[%i][%i][%i][%i][%i]=%s.%i.%i\n" % (0, west_matrix[i][2], west_matrix[i][3], west_matrix[i][1],
                                                                                west_matrix[i][0], dat_to_png,
                                                                                (west_matrix[i][2] + (xdimsW * west_matrix[i][1])),
                                                                                west_matrix[i][3]))
                CopyXY(int(frame.project.paksize), im, imout, (west_matrix[i][2], west_matrix[i][3], west_matrix[i][1]),
                        ((west_matrix[i][3] + (ydimsN + ydimsE + ydimsS)), (west_matrix[i][2] + (xdimsW * west_matrix[i][1]))),
                       (xdimsW, ydimsW, zdimsW), (frame.project.frame[f].west.offsetx, frame.project.frame[f].west.offsety),
                       west_matrix[i][4])

    #Save completed image to file
    if makedat == 0:
        imout.save(frame.project.output.abs_path_png)

    #Finally, write ending bar and close .dat file
    datfile.write("--------------------")
    datfile.close()


    
    #If output filenames not present, prompt for them...
    #If output files exist, prompt to overwrite (unless auto-overwrite enabled)
    #If no custom cutting matrix supplied, generate the cutting matrix from dims values
    #Generation should use the first frame (keyframe) values for x, y and z
    #Needs to generate a matrix for each direction
        #Cutting matrix is an array, with x,y,z coords for frame and view
    #Determine size of output image from cutting matrix stats
    #Create output image...
    #For all frames... For all views... For all z... For all x... For all y...
        #Use cutting matrix to copy and paste a square
        #Use cutting matrix mask info to mask this square
        #Use cutting matrix info to generate a .dat file image array entry for this file, and write it to the .dat output
    #Repeat for all cutting matrix entries...
    #Finally, write all the other .dat file information, then write the .dat output
    #Then write the image to a file


#----------------------------------------------Colour select Dialogue----------------------------------------------------


class ColourDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        self.value = 0
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        self.tc_colour_box = wx.StaticBox(self, -1, gt("Pick a colour:"))   #Box containing all global options

        self.tc_colour_sizer = wx.StaticBoxSizer(self.tc_colour_box)    #Sizer for the static box ^
        self.tc_colour_sizer2 = wx.BoxSizer(wx.VERTICAL)                #Container for control_sizer and sizer_flex
        self.tc_colour_control_sizer = wx.BoxSizer(wx.HORIZONTAL)       #Sizer for the control buttons at the bottom
        self.tc_colour_sizer_flex = wx.FlexGridSizer(16,16,0,0)         #Flex grid for the palette colour boxes

        self.tc_colour_display = wx.StaticText(self, -1, "", (-1,-1),(50,40),
                                               wx.SIMPLE_BORDER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL
                                               )        #Displays the currently selected palette colour
        self.tc_colour_sel_button = wx.Button(self, wx.ID_OK, label=gt("Use this colour"))  #OK button
        self.tc_colour_minus = wx.Button(self, -1, label="-", size=(19,19))             #Reduce colour number button
        self.tc_colour_disp_number = masked.TextCtrl(self, -1, value="0",
                                                     formatcodes="F0R",fillChar=" ", mask="###", validRequired=1, validRange=(0,255)
                                                     )  #Displays the currently selected palette entry number
        self.tc_colour_plus = wx.Button(self, -1, label="+", size=(19,19))              #Increase colour number button

        def On_pick(e):     #Event triggered when a colour is clicked on in the palette
            a = e.GetEventObject()
            self.tc_colour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(a.GetId()) - 3000)))
            self.tc_colour_display.ClearBackground()
            self.tc_colour_disp_number.SetValue(str(int(a.GetId()) - 3000))
            parent.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(a.GetId()) - 3000)))
            parent.tc_mapcolour_display.ClearBackground()
            parent.tc_mapcolour.SetValue(str(int(a.GetId()) - 3000))
            #self.tc_colour_display.SetLabel(a.GetLabel())
        def On_minus(e):    #Event for the reduce mapcolour value button
            if int(self.tc_colour_disp_number.GetValue()) > 0:
                self.tc_colour_disp_number.SetValue(str(int(self.tc_colour_disp_number.GetValue()) - 1))
                self.tc_colour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
                self.tc_colour_display.ClearBackground()
                parent.tc_mapcolour.SetValue(str(int(self.tc_colour_disp_number.GetValue())))
                parent.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
                parent.tc_mapcolour_display.ClearBackground()
        def On_plus(e):     #Event for the increase mapcolour value button
            if int(self.tc_colour_disp_number.GetValue()) < 255:
                self.tc_colour_disp_number.SetValue(str(int(self.tc_colour_disp_number.GetValue()) + 1))
                self.tc_colour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
                self.tc_colour_display.ClearBackground()
                parent.tc_mapcolour.SetValue(str(int(self.tc_colour_disp_number.GetValue())))
                parent.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
                parent.tc_mapcolour_display.ClearBackground()
        def On_textchange(e):   #Event triggered when the palette entry text changes
            self.tc_colour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
            self.tc_colour_display.ClearBackground()
            parent.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_colour_disp_number.GetValue()))))
            parent.tc_mapcolour_display.ClearBackground()
            parent.tc_mapcolour.SetValue(str(int(self.tc_colour_disp_number.GetValue())))

        self.tc_colours = []        #Array of colour squares in the palette
        for i in range(0,16):
            for j in range(0,16):
#                self.tc_colours.append(wx.StaticText(self, (3000 + (j + 16 * i)), (str((j + 16 * i))), (-1,-1),(22,18),    #Show numbers
                self.tc_colours.append(wx.StaticText(self, (3000 + (j + 16 * i)), "", (-1,-1),(22,18),                      #Hide numbers
                                                    wx.SIMPLE_BORDER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL))
                self.tc_colour_sizer_flex.Add(self.tc_colours[(j + 16 * i)], 0, wx.TOP|wx.LEFT, 0)
                
                self.tc_colours[(j + 16 * i)].Bind(wx.EVT_LEFT_DOWN, On_pick, self.tc_colours[(j + 16 * i)])
                self.tc_colours[(j + 16 * i)].SetBackgroundColour(GetPalEntry(frame.pal, (j + 16 * i)))
                self.tc_colours[(j + 16 * i)].ClearBackground()
        #Bind all functions
        self.tc_colour_minus.Bind(wx.EVT_BUTTON, On_minus, self.tc_colour_minus)
        self.tc_colour_plus.Bind(wx.EVT_BUTTON, On_plus, self.tc_colour_plus)
        self.tc_colour_disp_number.Bind(wx.EVT_TEXT, On_textchange, self.tc_colour_disp_number)
        #Do sizer stuff...
        self.tc_colour_control_sizer.Add(self.tc_colour_display, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_colour_control_sizer.Add(self.tc_colour_minus, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.tc_colour_control_sizer.Add(self.tc_colour_disp_number, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_colour_control_sizer.Add(self.tc_colour_plus, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_colour_control_sizer.Add(self.tc_colour_sel_button, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        self.tc_colour_sizer2.Add(self.tc_colour_sizer_flex, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_colour_sizer2.Add(self.tc_colour_control_sizer, 1, wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_colour_sizer.Add(self.tc_colour_sizer2, 0, wx.TOP|wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(self.tc_colour_sizer)
        #Init the colour display from the values in the parent window...
        self.tc_colour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(parent.tc_mapcolour.GetValue()))))
        self.tc_colour_display.ClearBackground()
        self.tc_colour_disp_number.SetValue(str(int(parent.tc_mapcolour.GetValue())))
        #Set default button and show the window...
        self.tc_colour_sel_button.SetDefault()
        self.tc_colour_sizer.Fit(self)
        self.ShowModal()

#----------------------------------------------Climates Dialogue----------------------------------------------------

class ClimateDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):

        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        # rocky,tundra,temperate,mediterran,desert,arctic,tropic,water

        def modify_list(e):
            a = e.GetEventObject()
            if int(a.GetId()) == 9991:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("rocky")
                else:
                    q = frame.project.dat.climates.index("rocky")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9992:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("tundra")
                else:
                    q = frame.project.dat.climates.index("tundra")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9993:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("temperate")
                else:
                    q = frame.project.dat.climates.index("temperate")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9994:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("mediterran")
                else:
                    q = frame.project.dat.climates.index("mediterran")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9995:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("desert")
                else:
                    q = frame.project.dat.climates.index("desert")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9996:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("arctic")
                else:
                    q = frame.project.dat.climates.index("arctic")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9997:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("tropic")
                else:
                    q = frame.project.dat.climates.index("tropic")
                    frame.project.dat.climates.pop(q)
            elif int(a.GetId()) == 9998:
                if a.GetValue() == 1:
                    frame.project.dat.climates.append("water")
                else:
                    q = frame.project.dat.climates.index("water")
                    frame.project.dat.climates.pop(q)


        self.tc_climate_rocky = wx.CheckBox(self, 9991, gt("rocky"), (-1,-1),(-1,-1))
        self.tc_climate_rocky.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_rocky)
        
        self.tc_climate_tundra = wx.CheckBox(self, 9992, gt("tundra"), (-1,-1),(-1,-1))
        self.tc_climate_tundra.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_tundra)
        
        self.tc_climate_temperate = wx.CheckBox(self, 9993, gt("temperate"), (-1,-1),(-1,-1))
        self.tc_climate_temperate.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_temperate)
        
        self.tc_climate_mediterran = wx.CheckBox(self, 9994, gt("mediterran"), (-1,-1),(-1,-1))
        self.tc_climate_mediterran.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_mediterran)
        
        self.tc_climate_desert = wx.CheckBox(self, 9995, gt("desert"), (-1,-1),(-1,-1))
        self.tc_climate_desert.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_desert)
        
        self.tc_climate_arctic = wx.CheckBox(self, 9996, gt("arctic"), (-1,-1),(-1,-1))
        self.tc_climate_arctic.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_arctic)
        
        self.tc_climate_tropic = wx.CheckBox(self, 9997, gt("tropic"), (-1,-1),(-1,-1))
        self.tc_climate_tropic.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_tropic)
        
        self.tc_climate_water = wx.CheckBox(self, 9998, gt("water"), (-1,-1),(-1,-1))
        self.tc_climate_water.Bind(wx.EVT_CHECKBOX, modify_list, self.tc_climate_water)
        
        if "rocky" in frame.project.dat.climates:
            self.tc_climate_rocky.SetValue(1)
        else:
            self.tc_climate_rocky.SetValue(0)
        if "tundra" in frame.project.dat.climates:
            self.tc_climate_tundra.SetValue(1)
        else:
            self.tc_climate_tundra.SetValue(0)
        if "temperate" in frame.project.dat.climates:
            self.tc_climate_temperate.SetValue(1)
        else:
            self.tc_climate_temperate.SetValue(0)
        if "mediterran" in frame.project.dat.climates:
            self.tc_climate_mediterran.SetValue(1)
        else:
            self.tc_climate_mediterran.SetValue(0)
        if "desert" in frame.project.dat.climates:
            self.tc_climate_desert.SetValue(1)
        else:
            self.tc_climate_desert.SetValue(0)
        if "arctic" in frame.project.dat.climates:
            self.tc_climate_arctic.SetValue(1)
        else:
            self.tc_climate_arctic.SetValue(0)
        if "tropic" in frame.project.dat.climates:
            self.tc_climate_tropic.SetValue(1)
        else:
            self.tc_climate_tropic.SetValue(0)
        if "water" in frame.project.dat.climates:
            self.tc_climate_water.SetValue(1)
        else:
            self.tc_climate_water.SetValue(0)

        self.tc_climate_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_climate_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.tc_climate_sizer.Add(self.tc_climate_rocky, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_tundra, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_temperate, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_mediterran, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_desert, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_arctic, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_tropic, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)
        self.tc_climate_sizer.Add(self.tc_climate_water, 1, wx.EXPAND|wx.TOP|wx.ALIGN_CENTER, 3)

        self.tc_climate_sizer2.Add(self.tc_climate_sizer, 0, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(self.tc_climate_sizer2)

        self.tc_climate_sizer2.Fit(self)

        self.ShowModal()

#----------------------------------------------Dat File edit Dialogue----------------------------------------------------

class DatDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        tc_obj_choices = [gt("Building"), gt("Factory"), gt("Other")]
#        tc_type_choices = [gt("Carstop"),gt("Busstop"),gt("Station"),gt("Monorailstop"),gt("Harbour"),gt("Wharf"),gt("Airport"),
#                           gt("Monument"),gt("Curiosity"),gt("Town Hall"),gt("Residential"),gt("Commercial"),gt("Industrial"),
#                           gt("Headquarters"),gt("hall"),gt("post"),gt("shed"),gt("any"),gt("misc")]
        #Global options--------------------------------------------------------------------------------------------------
        self.tc_global_box = wx.StaticBox(self, -1, gt("Global Options:"))   #Box containing all global options
        self.tc_obj = wx.RadioBox(self, 5500,  gt("Object Type:"), (-1,-1),(-1,-1), tc_obj_choices, 1, style=wx.RA_SPECIFY_ROWS)
        self.tc_obj.SetToolTipString(gt("ttObject Type"))

        def On_tc_obj(e):
            if self.tc_obj.GetSelection() == 0:
                DisablePanel(1)
                EnablePanel(0)
                EnablePanel(2)
                On_tc_type(self)
            elif self.tc_obj.GetSelection() == 1:
                DisablePanel(0)
                EnablePanel(1)
                EnablePanel(2)
            else:
                DisablePanel(0)
                DisablePanel(1)
                DisablePanel(2)
            On_level_textchange(e)
        def DisablePanel(a):
            if a == 0:      #If e = 0 disable all elements of Building Panel
                self.tc_building_box.Disable()
                self.tc_type_label.Disable()
                self.tc_type.Disable()
                self.tc_locationbui_label.Disable()
                self.tc_locationbui.Disable()
                self.tc_chancebui_label.Disable()
                self.tc_chancebui.Disable()
                self.tc_build_time_label.Disable()
                self.tc_build_time.Disable()
                self.tc_extension_label.Disable()
                self.tc_extension.Disable()
                self.tc_enables_label.Disable()
                self.tc_enables_pax.Disable()
                self.tc_enables_post.Disable()
                self.tc_enables_ware.Disable()
            elif a == 1:           #Otherwise, disable all elements of Factory Panel
                self.tc_factory_box.Disable()
                self.tc_locationfac_label.Disable()
                self.tc_locationfac.Disable()
                self.tc_chancefac_label.Disable()
                self.tc_chancefac.Disable()
                self.tc_productivity_label.Disable()
                self.tc_productivity.Disable()
                self.tc_range_label.Disable()
                self.tc_range.Disable()
                self.tc_mapcolour_label.Disable()
                self.tc_mapcolour.Disable()
                self.tc_mapcolour_display.Disable()
                self.tc_list_input_label.Disable()
                self.tc_list_input.Disable()
                self.tc_list_input_add.Disable()
                self.tc_list_input_remove.Disable()
                self.tc_list_input_up.Disable()
                self.tc_list_input_down.Disable()
                self.tc_list_output_label.Disable()
                self.tc_list_output.Disable()
                self.tc_list_output_add.Disable()
                self.tc_list_output_remove.Disable()
                self.tc_list_output_up.Disable()
                self.tc_list_output_down.Disable()
                self.tc_io_edit_label.Disable()
                #self.tc_io_edit_label2.Disable()
                self.tc_io_edit_good_label.Disable()
                self.tc_io_edit_good.Disable()
                self.tc_io_edit_capacity_label.Disable()
                self.tc_io_edit_capacity.Disable()
                self.tc_io_edit_factor_label.Disable()
                self.tc_io_edit_factor.Disable()
                self.tc_io_edit_suppliers_label.Disable()
                self.tc_io_edit_suppliers.Disable()
            else:           #Disable all elements of main panel for "other" option
                self.tc_global_box.Disable()
                self.tc_name_label.Disable()
                self.tc_name.Disable()
                self.tc_copyright_label.Disable()
                self.tc_copyright.Disable()
                self.tc_intro_year_label.Disable()
                self.tc_intro_month.Disable()
                self.tc_intro_year.Disable()
                self.tc_retire_year_label.Disable()
                self.tc_retire_month.Disable()
                self.tc_retire_year.Disable()
                self.tc_level_label.Disable()
                self.tc_level.Disable()
                self.tc_noinfo.Disable()
                self.tc_noconstruction.Disable()
                self.tc_needsground.Disable()
                self.tc_level_info_label.Disable()
                self.tc_level_info.Disable()

        def EnablePanel(a):
            if a == 0:       #If a = 0, enable all elements of Building Panel
                self.tc_building_box.Enable()
                self.tc_type_label.Enable()
                self.tc_type.Enable()
                self.tc_locationbui_label.Enable()
                self.tc_locationbui.Enable()
                self.tc_chancebui_label.Enable()
                self.tc_chancebui.Enable()
                self.tc_build_time_label.Enable()
                self.tc_build_time.Enable()
                self.tc_extension_label.Enable()
                self.tc_extension.Enable()
                self.tc_enables_label.Enable()
                self.tc_enables_pax.Enable()
                self.tc_enables_post.Enable()
                self.tc_enables_ware.Enable()
            elif a == 1:           #Otherwise, enable all elements of Factory Panel
                self.tc_factory_box.Enable()
                self.tc_locationfac_label.Enable()
                self.tc_locationfac.Enable()
                self.tc_chancefac_label.Enable()
                self.tc_chancefac.Enable()
                self.tc_productivity_label.Enable()
                self.tc_productivity.Enable()
                self.tc_range_label.Enable()
                self.tc_range.Enable()
                self.tc_mapcolour_label.Enable()
                self.tc_mapcolour.Enable()
                self.tc_mapcolour_display.Enable()
                self.tc_list_input_label.Enable()
                self.tc_list_input.Enable()
                self.tc_list_input_add.Enable()
                self.tc_list_input_remove.Enable()
                self.tc_list_input_up.Enable()
                self.tc_list_input_down.Enable()
                self.tc_list_output_label.Enable()
                self.tc_list_output.Enable()
                self.tc_list_output_add.Enable()
                self.tc_list_output_remove.Enable()
                self.tc_list_output_up.Enable()
                self.tc_list_output_down.Enable()
                self.tc_io_edit_label.Enable()
                #self.tc_io_edit_label2.Enable()
                self.tc_io_edit_good_label.Enable()
                self.tc_io_edit_good.Enable()
                self.tc_io_edit_capacity_label.Enable()
                self.tc_io_edit_capacity.Enable()
                self.tc_io_edit_factor_label.Enable()
                self.tc_io_edit_factor.Enable()
                self.tc_io_edit_suppliers_label.Enable()
                self.tc_io_edit_suppliers.Enable()
            else:           # Enable all elements of main panel for "other" option
                self.tc_global_box.Enable()
                self.tc_name_label.Enable()
                self.tc_name.Enable()
                self.tc_copyright_label.Enable()
                self.tc_copyright.Enable()
                self.tc_intro_year_label.Enable()
                self.tc_intro_month.Enable()
                self.tc_intro_year.Enable()
                self.tc_retire_year_label.Enable()
                self.tc_retire_month.Enable()
                self.tc_retire_year.Enable()
                self.tc_level_label.Enable()
                self.tc_level.Enable()
                self.tc_noinfo.Enable()
                self.tc_noconstruction.Enable()
                self.tc_needsground.Enable()
                self.tc_level_info_label.Enable()
                self.tc_level_info.Enable()


        wx.EVT_RADIOBOX(self, 5500, On_tc_obj)

        self.tc_name_label = wx.StaticText(self, -1, gt("Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_name = wx.TextCtrl(self, 5501, value="", size=(114,-1))                                             #Name
        self.tc_name.SetToolTipString(gt("ttName"))
        self.tc_copyright_label = wx.StaticText(self, -1, gt("Copyright:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_copyright = wx.TextCtrl(self, 5502, value="", size=(114,-1))                                        #Copyright
        self.tc_copyright.SetToolTipString(gt("ttCopyright"))
        self.tc_intro_year_label = wx.StaticText(self, -1, gt("Introduced:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_intro_month = wx.ComboBox(self, 5504, "", (-1, -1), (76, -1), tc_month_choices, wx.CB_READONLY)     #Intro month
        self.tc_intro_month.SetToolTipString(gt("ttIntroMonth"))
        #self.tc_intro_year = wx.TextCtrl(self, 5503, value="", size=(36,-1))                                        #Intro Year
        self.tc_intro_year = masked.TextCtrl(self, 5503, value="", size=(36,-1),
                                        formatcodes="S",fillChar=" ", mask="####", validRequired=1, validRange=(1,9999)
                                        )
        self.tc_intro_year.SetToolTipString(gt("ttIntroYear"))
        self.tc_retire_year_label = wx.StaticText(self, -1, gt("Retires:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_retire_month = wx.ComboBox(self, 5506, "", (-1, -1), (76, -1), tc_month_choices, wx.CB_READONLY)    #Retire month
        self.tc_retire_month.SetToolTipString(gt("ttRetiresMonth"))
        #self.tc_retire_year = wx.TextCtrl(self, 5505, value="", size=(36,-1))                                       #Retire year
        self.tc_retire_year = masked.TextCtrl(self, 5505, value="", size=(36,-1),
                                        formatcodes="S",fillChar=" ", mask="####", validRequired=1, validRange=(1,9999)
                                        )
        self.tc_retire_year.SetToolTipString(gt("ttRetiresYear"))
        self.tc_level_label = wx.StaticText(self, -1, gt("Level:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        #self.tc_level = wx.TextCtrl(self, 5507, value="")                                                           #Level
        self.tc_level = masked.TextCtrl(self, 5507, value="", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(1,99999)
                                        )
        self.tc_level.SetToolTipString(gt("ttLevel"))
        self.tc_level_info_label = wx.StaticText(self, -1, gt("Level Info:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_level_info = wx.StaticText(self, -1, "", (-1, -1), (-1, 15), wx.ALIGN_LEFT)
        self.tc_level_info2 = wx.StaticText(self, -1, "", (-1, -1), (-1, 15), wx.ALIGN_LEFT)

        self.tc_noinfo = wx.CheckBox(self, -1, gt("No info"))                                                           #Do not show factory info
        self.tc_noinfo.SetToolTipString(gt("ttNo info"))
        self.tc_noconstruction = wx.CheckBox(self, -1, gt("No Construction"))                                           #No construction site
        self.tc_noconstruction.SetToolTipString(gt("ttNo Construction"))

        self.tc_needsground = wx.CheckBox(self, -1, gt("Draw ground"))
        self.tc_needsground.SetToolTipString(gt("ttDraw Ground"))

        self.tc_global_sizer = wx.StaticBoxSizer(self.tc_global_box, wx.VERTICAL)
        self.tc_global_sizer_flex = wx.FlexGridSizer(0,2,0,0)

        #Global options added to global box
        self.tc_global_sizer_flex.Add(self.tc_name_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_global_sizer_flex.Add(self.tc_name, 0, wx.TOP|wx.LEFT, 2)
        self.tc_global_sizer_flex.Add(self.tc_copyright_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_global_sizer_flex.Add(self.tc_copyright, 0, wx.TOP|wx.LEFT, 2)
        #Intro year and month
        self.tc_global_sizer_flex.Add(self.tc_intro_year_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.sizer_intro = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_intro.Add(self.tc_intro_month, 0, wx.LEFT, 0)
        self.sizer_intro.Add(self.tc_intro_year, 0, wx.LEFT, 2)
        self.tc_global_sizer_flex.Add(self.sizer_intro, 0, wx.TOP|wx.LEFT, 2)
        #Retire year and month
        self.tc_global_sizer_flex.Add(self.tc_retire_year_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.sizer_retire = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_retire.Add(self.tc_retire_month, 0, wx.LEFT, 0)
        self.sizer_retire.Add(self.tc_retire_year, 0, wx.LEFT, 2)
        self.tc_global_sizer_flex.Add(self.sizer_retire, 0, wx.TOP|wx.LEFT, 2)

        
        self.tc_global_sizer_flex.Add(self.tc_level_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_global_sizer_flex.Add(self.tc_level, 0, wx.TOP|wx.LEFT, 2)

        self.tc_global_sizer_flex.Add(self.tc_level_info_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)

        self.tc_info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tc_info_sizer.Add(self.tc_level_info, 0, wx.TOP|wx.LEFT, 0)
        self.tc_info_sizer.Add(self.tc_level_info2, 0, wx.TOP|wx.LEFT, 0)

        self.tc_global_sizer_flex.Add(self.tc_info_sizer, 0, wx.TOP|wx.LEFT, 2)

        self.tc_global_sizer_flex.Add(self.tc_noinfo, 0, wx.TOP|wx.LEFT, 4)
        self.tc_global_sizer_flex.Add(self.tc_noconstruction, 0, wx.TOP|wx.LEFT, 4)


        self.tc_global_sizer.Add(self.tc_global_sizer_flex, 0, wx.TOP|wx.LEFT, 0)

        self.tc_global_sizer.Add(self.tc_needsground, 0, wx.TOP|wx.LEFT, 4)

        def On_level_textchange(e):
            """Takes care of the level indicator hint"""
            p = 0
            if self.tc_obj.GetSelection() == 0:     #If it's a building...
                if self.tc_level.GetValue() == "" or self.tc_level.GetValue() == "     ":   #First, check if there's anything in the level box
                    self.tc_level_info.SetLabel(gt("Level not set"))
                else:                                       #If there is, check if it's a factory, building or other
                
                    if self.tc_type.GetValue() == "":   #Check building types...
                        p = 0

                    elif self.tc_type.GetValue() == gt("carstop"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("busstop"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("station"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("monorailstop"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("harbour"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("wharf"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("airport"):
                        p = 1
                    #Monument/Curiosity/Town Hall
                    elif self.tc_type.GetValue() == gt("mon"):
                        p = 2
                    elif self.tc_type.GetValue() == gt("cur"):
                        p = 2
                    elif self.tc_type.GetValue() == gt("tow"):
                        p = 3   #Upgrade stage
                    #Res/Com/Ind (disable all)
                    elif self.tc_type.GetValue() == gt("res"):
                        p = 4
                    elif self.tc_type.GetValue() == gt("com"):
                        p = 5
                    elif self.tc_type.GetValue() == gt("ind"):
                        p = 6
                    elif self.tc_type.GetValue() == gt("hq"):
                        p = 3   #Upgrade stage
                    elif self.tc_type.GetValue() == gt("hall"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("post"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("shed"):
                        p = 1
                    elif self.tc_type.GetValue() == gt("any"):
                        p = -1
                    elif self.tc_type.GetValue() == gt("misc"):
                        p = -1

                    if p == 0:
                        self.tc_level_info.SetLabel(gt("Type not set"))
                        self.tc_level_info2.SetLabel("")
                    elif p == -1:
##                        self.tc_level_info.SetLabel(gt("Levela not supported\nfor this object type"))
                        self.tc_level_info.SetLabel(gt("Level not supported"))
                        self.tc_level_info2.SetLabel(gt("for this object type"))
                    elif p == 1:
                        self.tc_level_info.SetLabel(gt("Capacity: %s")%(int(self.tc_level.GetValue()) * 32))
                        self.tc_level_info2.SetLabel("")
                    elif p == 2:
                        self.tc_level_info.SetLabel(gt("moncurPassenger level: %s")%(int(self.tc_level.GetValue())))
                        self.tc_level_info2.SetLabel(gt("moncurMail level: %s")%(int(self.tc_level.GetValue())))
                    elif p == 3:
                        self.tc_level_info.SetLabel(gt("Upgrade Stage: %s")%(self.tc_level.GetValue()))
                        self.tc_level_info2.SetLabel("")
                    elif p == 4:
                        self.tc_level_info.SetLabel(gt("resPassenger level: %s")%(int(self.tc_level.GetValue()) - 1))
                        self.tc_level_info2.SetLabel(gt("resMail level: %s")%(int(self.tc_level.GetValue()) - 1))
                    elif p == 5:
                        self.tc_level_info.SetLabel(gt("comPassenger level: %s")%(int(self.tc_level.GetValue()) - 1))
                        self.tc_level_info2.SetLabel(gt("comMail level: %s")%((int(self.tc_level.GetValue()) - 1) * 2))
                    elif p == 6:
                        self.tc_level_info.SetLabel(gt("indPassenger level: %s")%(int(self.tc_level.GetValue()) - 1))
                        self.tc_level_info2.SetLabel(gt("indMail level: %s")%(int((int(self.tc_level.GetValue()) - 1) / 2)))
            elif self.tc_obj.GetSelection() == 1:   #If it's a factory
                if self.tc_level.GetValue() == "" or self.tc_level.GetValue() == "     ":   #First, check if there's anything in the level box
                    self.tc_level_info.SetLabel(gt("Level not set"))
                    self.tc_level_info2.SetLabel("")
                else:                                       #If there is, check if it's a factory, building or other
                    self.tc_level_info.SetLabel(gt("facPassenger level: %s")%(int(self.tc_level.GetValue()) - 1))
                    self.tc_level_info2.SetLabel(gt("facMail level: %s")%(int((int(self.tc_level.GetValue()) - 1) / 3)))
            else:                                   #If it's other
                self.tc_level_info.SetLabel(gt("n/a"))
                    

        self.tc_level.Bind(wx.EVT_TEXT, On_level_textchange, self.tc_level)



        #Building options (ID order 5700+)--------------------------------------------------------------------------------------------------
        self.tc_building_box = wx.StaticBox(self, -1, gt("Building Options:"))   #Box containing all building options

        self.tc_type_label = wx.StaticText(self, -1, gt("Type:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_type = wx.ComboBox(self, 5700, "", (-1, -1), (-1, -1), tc_type_choices, wx.CB_READONLY)         #Type of building
        self.tc_type.SetToolTipString(gt("ttType"))

        def On_tc_type(e):
            if self.tc_type.GetValue() == "":
                DisableBuilding(0)      #Disable all
            #Stations
            elif self.tc_type.GetValue() == gt("carstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("busstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("station"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("monorailstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("harbour"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("wharf"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("airport"):
                DisableBuilding(1)      #Disable for station
            #Monument/Curiosity/Town Hall
            elif self.tc_type.GetValue() == gt("mon"):
                DisableBuilding(2)      #Disable for monument (same as curiosity except location)
            elif self.tc_type.GetValue() == gt("cur"):
                DisableBuilding(3)      #Disable for curiosity (only thing which uses location)
            elif self.tc_type.GetValue() == gt("tow"):
                DisableBuilding(4)      #Disable for town hall (only build time)
            #Res/Com/Ind (disable all)
            elif self.tc_type.GetValue() == gt("res"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("com"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("ind"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("hq"):
                DisableBuilding(4)      #Disable for HQ (only build time)
            elif self.tc_type.GetValue() == gt("hall"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("post"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("shed"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("any"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("misc"):
                DisableBuilding(0)      #Disable all
            On_level_textchange(e)

        def DisableBuilding(a):
            if a == 0:                                  #Disable all
                self.tc_locationbui_label.Disable()
                self.tc_locationbui.Disable()
                self.tc_chancebui_label.Disable()
                self.tc_chancebui.Disable()
                self.tc_build_time_label.Disable()
                self.tc_build_time.Disable()
                self.tc_extension_label.Disable()
                self.tc_extension.Disable()
                self.tc_enables_label.Disable()
                self.tc_enables_pax.Disable()
                self.tc_enables_post.Disable()
                self.tc_enables_ware.Disable()
            if a == 1:                                  #Disable for station
                self.tc_locationbui_label.Disable()
                self.tc_locationbui.Disable()
                self.tc_chancebui_label.Disable()
                self.tc_chancebui.Disable()
                self.tc_build_time_label.Disable()
                self.tc_build_time.Disable()
                self.tc_extension_label.Enable()
                self.tc_extension.Enable()
                self.tc_enables_label.Enable()
                self.tc_enables_pax.Enable()
                self.tc_enables_post.Enable()
                self.tc_enables_ware.Enable()
            if a == 2:                                  #Disable for monument
                self.tc_locationbui_label.Disable()
                self.tc_locationbui.Disable()
                self.tc_chancebui_label.Enable()
                self.tc_chancebui.Enable()
                self.tc_build_time_label.Enable()
                self.tc_build_time.Enable()
                self.tc_extension_label.Disable()
                self.tc_extension.Disable()
                self.tc_enables_label.Disable()
                self.tc_enables_pax.Disable()
                self.tc_enables_post.Disable()
                self.tc_enables_ware.Disable()
            if a == 3:                                  #Disable for curiosity
                self.tc_locationbui_label.Enable()
                self.tc_locationbui.Enable()
                self.tc_chancebui_label.Enable()
                self.tc_chancebui.Enable()
                self.tc_build_time_label.Disable()
                self.tc_build_time.Disable()
                self.tc_extension_label.Disable()
                self.tc_extension.Disable()
                self.tc_enables_label.Disable()
                self.tc_enables_pax.Disable()
                self.tc_enables_post.Disable()
                self.tc_enables_ware.Disable()
            if a == 4:                                  #Disable for town hall/HQ (build time only)
                self.tc_locationbui_label.Disable()
                self.tc_locationbui.Disable()
                self.tc_chancebui_label.Disable()
                self.tc_chancebui.Disable()
                self.tc_build_time_label.Enable()
                self.tc_build_time.Enable()
                self.tc_extension_label.Disable()
                self.tc_extension.Disable()
                self.tc_enables_label.Disable()
                self.tc_enables_pax.Disable()
                self.tc_enables_post.Disable()
                self.tc_enables_ware.Disable()

    


        wx.EVT_COMBOBOX(self, 5700, On_tc_type)



        
        self.tc_locationbui_label = wx.StaticText(self, -1, gt("buiLocation:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_locationbui = wx.ComboBox(self, 5702, "", (-1, -1), (-1, -1), ["Land","City"], wx.CB_READONLY)  #Location (building)
        self.tc_locationbui.SetToolTipString(gt("ttbuiLocation"))
        self.tc_chancebui_label = wx.StaticText(self, -1, gt("buiChance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        #self.tc_chancebui = wx.TextCtrl(self, 5703, value="", size=(50,-1))                                     #Chance (building)
        self.tc_chancebui = masked.TextCtrl(self, 5703, value="0", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                        )
        self.tc_chancebui.SetToolTipString(gt("ttbuiChance"))
        self.tc_build_time_label = wx.StaticText(self, -1, gt("Build Time:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        #self.tc_build_time = wx.TextCtrl(self, 5704, value="", size=(50,-1))                                    #Build time
        self.tc_build_time = masked.TextCtrl(self, 5704, value="0", size=(70,-1),
                                        formatcodes="S",fillChar=" ", mask="########", validRequired=1, validRange=(0,16777216)
                                        )
        self.tc_build_time.SetToolTipString(gt("ttBuild Time"))
        self.tc_extension_label = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_extension = wx.CheckBox(self, -1, gt("Is Extension Building"))                                      #Extension building flag
        self.tc_extension.SetToolTipString(gt("ttIs Extension Building"))
        self.tc_enables_label = wx.StaticText(self, -1, gt("Enables:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_enables_pax = wx.CheckBox(self, -1, gt("EnablesPax"))                                               #Enables passengers
        self.tc_enables_pax.SetToolTipString(gt("ttEnablesPax"))
        self.tc_enables_post = wx.CheckBox(self, -1, gt("EnablesMail"))                                                    #Enables mail
        self.tc_enables_post.SetToolTipString(gt("ttEnablesMail"))
        self.tc_enables_ware = wx.CheckBox(self, -1, gt("EnablesGoods"))                                                   #Enables goods
        self.tc_enables_ware.SetToolTipString(gt("ttEnablesGoods"))

                # Needs addition of cursor/icon selection system!!!
                
        self.tc_building_sizer = wx.StaticBoxSizer(self.tc_building_box, wx.HORIZONTAL)
        self.tc_building_sizer_flex = wx.FlexGridSizer(0,2,0,0)

        #Building options added to building box
        self.tc_building_sizer_flex.Add(self.tc_type_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_building_sizer_flex.Add(self.tc_type, 0, wx.TOP|wx.LEFT, 2)
        self.tc_building_sizer_flex.Add(self.tc_locationbui_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_building_sizer_flex.Add(self.tc_locationbui, 0, wx.TOP|wx.LEFT, 2)
        self.tc_building_sizer_flex.Add(self.tc_chancebui_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_building_sizer_flex.Add(self.tc_chancebui, 0, wx.TOP|wx.LEFT, 2)
        self.tc_building_sizer_flex.Add(self.tc_build_time_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_building_sizer_flex.Add(self.tc_build_time, 0, wx.TOP|wx.LEFT|wx.BOTTOM, 2)
        self.tc_building_sizer_flex.Add(self.tc_extension_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_building_sizer_flex.Add(self.tc_extension, 0, wx.TOP|wx.LEFT|wx.BOTTOM, 2)
        #Enables options
        self.tc_building_sizer_flex.Add(self.tc_enables_label, 0, wx.LEFT, 2)
        self.sizer_enables = wx.BoxSizer(wx.VERTICAL)
        self.sizer_enables.Add(self.tc_enables_pax, 0, wx.LEFT, 0)
        self.sizer_enables.Add(self.tc_enables_post, 0, wx.LEFT, 0)
        self.sizer_enables.Add(self.tc_enables_ware, 0, wx.LEFT, 0)
        self.tc_building_sizer_flex.Add(self.sizer_enables, 0, wx.TOP|wx.LEFT, 2)


        self.tc_building_sizer.Add(self.tc_building_sizer_flex, 0, wx.TOP|wx.LEFT, 0)


        #Factory options (ID order 5600+)--------------------------------------------------------------------------------------------------
        self.tc_factory_box = wx.StaticBox(self, -1, gt("Factory Options:"))   #Box containing all global options


        self.tc_locationfac_label = wx.StaticText(self, -1, gt("facLocation:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_locationfac = wx.ComboBox(self, 5600, "", (-1, -1), (-1, -1), ["","Land","City","Water"], wx.CB_READONLY)  #Location (factory)
        self.tc_locationfac.SetToolTipString(gt("ttfacLocation"))
        self.tc_chancefac_label = wx.StaticText(self, -1, gt("facChance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_chancefac = masked.TextCtrl(self, 5601, value="0", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,100)
                                            )                                                                           #Chance (factory)
        self.tc_chancefac.SetToolTipString(gt("ttfacChance"))
        self.tc_productivity_label = wx.StaticText(self, -1, gt("Productivity:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_productivity = masked.TextCtrl(self, 5602, value="0", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                            )                                                                           #Productivity
        self.tc_productivity.SetToolTipString(gt("ttProductivity"))
        self.tc_range_label = wx.StaticText(self, -1, "±", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_range = masked.TextCtrl(self, 5603, value="0", size=(44,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                        )                                                                               #Range
        self.tc_mapcolour_label = wx.StaticText(self, -1, gt("Map Colour:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_mapcolour = masked.TextCtrl(self, 5604, value="0", size=(50,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,255)
                                            )                                                                           #Map Colour Entry
        self.tc_mapcolour.SetToolTipString(gt("ttMap Colour"))
        self.tc_mapcolour_display = wx.StaticText(self, 5605, "", (-1,-1),(30,21),wx.SIMPLE_BORDER)            #Map Colour display
        self.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_mapcolour.GetValue()))))
        self.tc_mapcolour_display.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.tc_mapcolour_display.SetToolTipString(gt("ttMap Colour Display"))

            #Add in smoke stuff later!!
        
        #Input List box & controls
        self.input_list_items = []
        self.tc_list_input_label = wx.StaticText(self, -1, gt("Input Goods:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_list_input = wx.ListBox(self, ID_INPUT, (-1,-1), (92, -1), self.input_list_items, wx.LB_SINGLE)
        self.tc_list_input.SetToolTipString(gt("ttInput Goods:"))
        self.tc_list_input_add = wx.Button(self, ID_INPUT, "+", (-1,-1), (22,16))
        self.tc_list_input_add.SetToolTipString(gt("ttAdd input good"))
        self.tc_list_input_remove = wx.Button(self, ID_INPUT, "-", (-1,-1), (22,16))
        self.tc_list_input_remove.SetToolTipString(gt("ttRemove input good"))
        self.tc_list_input_up = wx.BitmapButton(self, -1, DrawArrow("up"), (-1,-1), (22,16))
        self.tc_list_input_up.SetToolTipString(gt("ttMove input good up"))
        self.tc_list_input_down = wx.BitmapButton(self, -1, DrawArrow("down"), (-1,-1), (22,16))
        self.tc_list_input_down.SetToolTipString(gt("ttMove input good down"))

        #Output List box & controls
        self.output_list_items = []
        self.tc_list_output_label = wx.StaticText(self, -1, gt("Output Goods:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_list_output = wx.ListBox(self, ID_OUTPUT, (-1,-1), (92, -1), self.output_list_items, wx.LB_SINGLE)
        self.tc_list_output.SetToolTipString(gt("ttOutput Goods:"))
        self.tc_list_output_add = wx.Button(self, ID_OUTPUT, "+", (-1,-1), (22,16))
        self.tc_list_output_add.SetToolTipString(gt("ttAdd output good"))
        self.tc_list_output_remove = wx.Button(self, ID_OUTPUT, "-", (-1,-1), (22,16))
        self.tc_list_output_remove.SetToolTipString(gt("ttRemove output good"))
        self.tc_list_output_up = wx.BitmapButton(self, -1, DrawArrow("up"), (-1,-1), (22,16))
        self.tc_list_output_up.SetToolTipString(gt("ttMove output good up"))
        self.tc_list_output_down = wx.BitmapButton(self, -1, DrawArrow("down"), (-1,-1), (22,16))
        self.tc_list_output_down.SetToolTipString(gt("ttMove output good down"))

        #Input/Output edit controls
        self.tc_io_edit_label = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
#        self.tc_io_edit_label2 = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_io_edit_good_label = wx.StaticText(self, -1, gt("good Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_io_edit_good = wx.TextCtrl(self, ID_EDIT_GOOD, value="", size=(70,-1))            #Good name entry box
        self.tc_io_edit_good.SetToolTipString(gt("ttgood Name:"))
        self.tc_io_edit_capacity_label = wx.StaticText(self, -1, gt("good Capacity:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_io_edit_capacity = masked.TextCtrl(self, ID_EDIT_CAP, value="0", size=(50,-1),              #Capacity entry box
                                                formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,99999)
                                                )
        self.tc_io_edit_capacity.SetToolTipString(gt("ttgood Capacity:"))
        self.tc_io_edit_factor_label = wx.StaticText(self, -1, gt("good Factor:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_io_edit_factor = masked.TextCtrl(self, ID_EDIT_FAC, value="0", size=(50,-1),              #Factor entry box
                                                formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,99999)
                                                )
        self.tc_io_edit_factor.SetToolTipString(gt("ttgood Factor:"))
        self.tc_io_edit_suppliers_label = wx.StaticText(self, -1, gt("good Suppliers:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_io_edit_suppliers = masked.TextCtrl(self, ID_EDIT_SUP, value="0", size=(50,-1),              #Suppliers entry box
                                                    formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,999)
                                                    )
        self.tc_io_edit_suppliers.SetToolTipString(gt("ttgood Suppliers:"))
        
        self.tc_factory_line1 = wx.StaticLine(self, -1, (-1,-1), (-1,-1), wx.LI_HORIZONTAL)

        def On_textchange(e):
            if self.tc_mapcolour.GetValue() == "   ":
                self.tc_mapcolour.SetValue("0")
            else:
                self.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_mapcolour.GetValue()))))
                self.tc_mapcolour_display.ClearBackground()

        def On_mapcolour_select(e):
            dlg = ColourDialog(self, -1, gt("Mapcolour Palette"), size=(369, 380),
                            style=wx.DEFAULT_DIALOG_STYLE)
            
            dlg.Destroy()
            #self.tc_mapcolour_display.SetBackgroundColour((255,255,0))
            #self.tc_mapcolour_display.ClearBackground()
            #self.tc_mapcolour.SetValue("")

        self.tc_mapcolour_display.Bind(wx.EVT_LEFT_DOWN, On_mapcolour_select)
        self.tc_mapcolour.Bind(wx.EVT_TEXT, On_textchange, self.tc_mapcolour)

        self.tc_factory_sizer = wx.StaticBoxSizer(self.tc_factory_box, wx.VERTICAL)
        self.tc_factory_sizer_flex = wx.FlexGridSizer(0,4,2,2)
        self.tc_factory_sizer_io = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_input_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tc_output_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tc_io_edit_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tx_io_edit_flex_sizer = wx.FlexGridSizer(0,2,0,0)

        #Factory options added to upper factory box
        #Location
        self.tc_factory_sizer_flex.Add(self.tc_locationfac_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_factory_sizer_flex.Add(self.tc_locationfac, 0, wx.TOP|wx.LEFT, 2)
        #Productivity & Range
        self.tc_factory_sizer_flex.Add(self.tc_productivity_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.sizer_produc = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_produc.Add(self.tc_productivity, 0, wx.LEFT, 0)
        self.sizer_produc.Add(self.tc_range_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.sizer_produc.Add(self.tc_range, 0, wx.LEFT, 2)
        self.tc_factory_sizer_flex.Add(self.sizer_produc, 0, wx.TOP|wx.LEFT, 2)
        #Chance
        self.tc_factory_sizer_flex.Add(self.tc_chancefac_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_factory_sizer_flex.Add(self.tc_chancefac, 0, wx.LEFT, 2)
        #Map colour picker
        self.tc_factory_sizer_flex.Add(self.tc_mapcolour_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.sizer_colour = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_colour.Add(self.tc_mapcolour, 0, wx.LEFT, 0)
        self.sizer_colour.Add(self.tc_mapcolour_display, 0, wx.LEFT, 2)
        self.tc_factory_sizer_flex.Add(self.sizer_colour, 0, wx.LEFT, 2)

        self.tc_factory_sizer.Add(self.tc_factory_sizer_flex, 0, wx.TOP|wx.LEFT, 0)


        #Input stuff added to sizers...
        self.tc_input_sizer.Add(self.tc_list_input_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_input_sizer.Add(self.tc_list_input, 1, wx.LEFT, 2)
        self.tc_input_sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_input_sizer_buttons.Add(self.tc_list_input_add, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_input_sizer_buttons.Add(self.tc_list_input_remove, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_input_sizer_buttons.Add(self.tc_list_input_up, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_input_sizer_buttons.Add(self.tc_list_input_down, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_input_sizer.Add(self.tc_input_sizer_buttons, 0, wx.LEFT|wx.ALIGN_CENTER, 2)
        #Output stuff added to sizers...
        self.tc_output_sizer.Add(self.tc_list_output_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_output_sizer.Add(self.tc_list_output, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_output_sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_output_sizer_buttons.Add(self.tc_list_output_add, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_output_sizer_buttons.Add(self.tc_list_output_remove, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_output_sizer_buttons.Add(self.tc_list_output_up, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_output_sizer_buttons.Add(self.tc_list_output_down, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.tc_output_sizer.Add(self.tc_output_sizer_buttons, 0, wx.LEFT|wx.ALIGN_CENTER, 2)
        #Edit stuff added to sizers...
        self.tc_io_edit_sizer.Add(self.tc_io_edit_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_good_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_good, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_capacity_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_capacity, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_factor_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_factor, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_suppliers_label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tx_io_edit_flex_sizer.Add(self.tc_io_edit_suppliers, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_io_edit_sizer.Add(self.tx_io_edit_flex_sizer, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)

        def tc_unhighlight(io, num):
            """Removes highlighted items from other list
            io is the list to remove highlighting from, num is the item to deselect"""
            if io == "o":
                self.tc_list_input.Deselect(num)
            if io == "i":
                self.tc_list_output.Deselect(num)
        def tc_highlight(io, num):
            """Highlights item in a list
            io is the list to highlight, num is the item to select"""
            if io == "i":
                self.tc_list_input.SetSelection(num)
            if io == "o":
                self.tc_list_output.SetSelection(num)
        def tc_display_goods(e):
            """Displays the array of goods in the input/output lists"""
            input = []
            output = []
            for a in range(len(inputgoods)):
                if a < 10:
                    num = ("0" + str(inputgoods[a].val) + " - ")
                else:
                    num = (str(inputgoods[a].val) + " - ")
                input.append(num + inputgoods[a].name)
            for a in range(len(outputgoods)):
                if a < 10:
                    num = ("0" + str(outputgoods[a].val) + " - ")
                else:
                    num = (str(outputgoods[a].val) + " - ")
                output.append(num + outputgoods[a].name)
                #sys.stderr.write(goods[a].name + str(a))
            self.tc_list_input.Set(input)
            self.tc_list_output.Set(output)
        def tc_listbox_click(e):
            a = e.GetEventObject()
            if a.GetId() == ID_INPUT:
                sel = self.tc_list_input.GetSelection()    #Find which item is selected
                selo = self.tc_list_output.GetSelection()  #Find other
                selbox = "i"                                #Input box is clicked
                #sys.stderr.write(selo)
                if selo != wx.NOT_FOUND:
                    if sel != wx.NOT_FOUND:
                        tc_unhighlight("i", selo)
            else:
                sel = self.tc_list_output.GetSelection()   #Find which item is selected
                selo = self.tc_list_input.GetSelection()   #Find which item is selected in other list
                selbox = "o"                                #Output box is clicked
                #sys.stderr.write(selo)
                if selo != wx.NOT_FOUND:
                    if sel != wx.NOT_FOUND:
                        tc_unhighlight("o", selo)
            tc_list_edit_load(selbox, sel)
        def tc_list_edit_load(selbox, sel):
            if sel != wx.NOT_FOUND:
                if selbox == "i":
                    for a in range(len(inputgoods)):
                        if inputgoods[a].val == sel:
                            self.tc_io_edit_label.SetLabel(gt("Input Good #%s")%str(inputgoods[a].val))
                            self.tc_io_edit_good.SetValue(inputgoods[a].name)    #Then set all the edit values to the values of the entry
                            self.tc_io_edit_capacity.SetValue(inputgoods[a].capacity)
                            self.tc_io_edit_factor.SetValue(inputgoods[a].factor)
                            self.tc_io_edit_suppliers.SetValue(inputgoods[a].supplier)
                    self.tc_io_edit_label.Enable()
                    self.tc_io_edit_good_label.Enable()
                    self.tc_io_edit_good.Enable()
                    self.tc_io_edit_capacity_label.Enable()
                    self.tc_io_edit_capacity.Enable()
                    self.tc_io_edit_factor_label.Enable()
                    self.tc_io_edit_factor.Enable()
                    self.tc_io_edit_suppliers_label.Enable()
                    self.tc_io_edit_suppliers.Enable()
                elif selbox == "o":
                    for a in range(len(outputgoods)):
                        if outputgoods[a].val == sel:
                            self.tc_io_edit_label.SetLabel(gt("Output Good #%s")%str(outputgoods[a].val))
                            self.tc_io_edit_good.SetValue(outputgoods[a].name)    #Then set all the edit values to the values of the entry
                            self.tc_io_edit_capacity.SetValue(outputgoods[a].capacity)
                            self.tc_io_edit_factor.SetValue(outputgoods[a].factor)
                            self.tc_io_edit_suppliers.SetValue(outputgoods[a].supplier)
                    self.tc_io_edit_label.Enable()
                    self.tc_io_edit_good_label.Enable()
                    self.tc_io_edit_good.Enable()
                    self.tc_io_edit_capacity_label.Enable()
                    self.tc_io_edit_capacity.Enable()
                    self.tc_io_edit_factor_label.Enable()
                    self.tc_io_edit_factor.Enable()
                    self.tc_io_edit_suppliers_label.Enable()
                    self.tc_io_edit_suppliers.Enable()
                elif selbox == "n":
                    if self.tc_list_input.GetCount() == 0:
                        if self.tc_list_output.GetCount() == 0:         #If both lists empty, disable edit and display add message
                            self.tc_io_edit_label.SetLabel(gt("Please add a good..."))
                            self.tc_io_edit_good_label.Disable()
                            self.tc_io_edit_good.Disable()
                            self.tc_io_edit_good.SetValue("")
                            self.tc_io_edit_capacity_label.Disable()
                            self.tc_io_edit_capacity.Disable()
                            self.tc_io_edit_capacity.SetValue("0")
                            self.tc_io_edit_factor_label.Disable()
                            self.tc_io_edit_factor.Disable()
                            self.tc_io_edit_factor.SetValue("0")
                            self.tc_io_edit_suppliers_label.Disable()
                            self.tc_io_edit_suppliers.Disable()
                            self.tc_io_edit_suppliers.SetValue("0")
                        else:
                            tc_highlight("o", 0)
                            tc_list_edit_load("o", 0)               #Otherwise, switch focus to other list, and load first item
                    else:
                        tc_highlight("i", 0)
                        tc_list_edit_load("i", 0)

        def tc_listbox_add(e):
            """Event triggered when the add button under one of the lists is clicked"""
            a = e.GetEventObject()
            skip = 0
            input_num = 0
            output_num = 0
            if a.GetId() == ID_INPUT:
                selbox = "i"
                if self.tc_list_input.GetCount() == 16:
                    skip = 1
                else:
                    inputgoods.append(good())
                    inputgoods[(len(inputgoods) - 1)].type = "i"
                    valout = self.tc_list_input.GetCount()
                    inputgoods[(len(inputgoods) - 1)].val = valout
                    inputgoods[(len(inputgoods) - 1)].name = ""
                    inputgoods[(len(inputgoods) - 1)].capacity = "0"
                    inputgoods[(len(inputgoods) - 1)].factor = "0"
                    inputgoods[(len(inputgoods) - 1)].supplier = "0"
            else:
                selbox = "o"
                if self.tc_list_output.GetCount() == 16:
                    skip = 1
                else:
                    outputgoods.append(good())
                    outputgoods[(len(outputgoods) - 1)].type = "i"
                    valout = self.tc_list_output.GetCount()
                    outputgoods[(len(outputgoods) - 1)].val = valout
                    outputgoods[(len(outputgoods) - 1)].name = ""
                    outputgoods[(len(outputgoods) - 1)].capacity = "0"
                    outputgoods[(len(outputgoods) - 1)].factor = "0"
                    outputgoods[(len(outputgoods) - 1)].supplier = "0"
            if skip == 0:
                tc_display_goods(1)
                tc_highlight(selbox, valout)
                tc_list_edit_load(selbox, valout)
                #sys.stderr.write("(" + str(goods) + ")\n")
        def tc_listbox_remove(e):
            """Event triggered when the remove button under one of the lists is clicked"""
            a = e.GetEventObject()  #What list is this for?
            remove = 0
            length = 1
            skip = 0
            if a.GetId() == ID_INPUT:
                if self.tc_list_input.IsEmpty():
                    skip = 1
                else:
                    total = self.tc_list_input.GetSelection()
                    inputgoods.pop(total)
                    for a in range(self.tc_list_input.GetCount() - 1):
                        inputgoods[a].val = a
                    tc_display_goods(1)
                    if self.tc_list_input.GetCount() != 0:
                        if total > (self.tc_list_input.GetCount() - 1):
                            total = total - 1
                        tc_highlight("i", total)
                        tc_list_edit_load("i", total)
                    else:
                        tc_list_edit_load("n", total)  #If nothing left in the list, disable the edit box
            else:
                if self.tc_list_output.IsEmpty():
                    skip = 1
                else:
                    total = self.tc_list_output.GetSelection()
                    outputgoods.pop(total)
                    for a in range(self.tc_list_output.GetCount() - 1):
                        outputgoods[a].val = a
                    tc_display_goods(1)
                    if self.tc_list_output.GetCount() != 0:
                        if total > (self.tc_list_output.GetCount() - 1):
                            total = total - 1
                        tc_highlight("o", total)
                        tc_list_edit_load("o", total)
                    else:
                        tc_list_edit_load("n", total)  #If nothing left in the list, disable the edit box
        def tc_edit_text(e):
            """Event triggered when the edit box text is changed"""
            a = e.GetEventObject()  #What entry is this for?
            skip = 0
            if self.tc_list_input.GetSelection() == wx.NOT_FOUND:   #What box is currently selected?
                if self.tc_list_output.GetSelection() == wx.NOT_FOUND: #If both boxes are empty...
                    skip = 1
                else:
                    io = outputgoods
                    iot = "o"
                    num = self.tc_list_output.GetSelection()
            else:
                io = inputgoods
                iot = "i"
                num = self.tc_list_input.GetSelection()
            if skip == 0:
                if a.GetId() == ID_EDIT_GOOD:
                    #sys.stderr.write(str(num) + "\n")
                    io[num].name = self.tc_io_edit_good.GetValue()     #Do update of list when editing the name field
                    tc_display_goods(1)
                    tc_highlight(iot, num)
                if a.GetId() == ID_EDIT_CAP:
                    io[num].capacity = self.tc_io_edit_capacity.GetValue() #Update others transparently
                if a.GetId() == ID_EDIT_FAC:
                    io[num].factor = self.tc_io_edit_factor.GetValue()
                if a.GetId() == ID_EDIT_SUP:
                    io[num].supplier = self.tc_io_edit_suppliers.GetValue()
                    
        def On_close(e):
            frame.project.dat.obj = self.tc_obj.GetSelection()
            frame.project.dat.name = self.tc_name.GetValue()
            frame.project.dat.copyright = self.tc_copyright.GetValue()
            
            #Set month, 0 is blank, 1-12 are month names as defined in tc_month_choices
            frame.project.dat.in_month = self.tc_intro_month.GetSelection()
            frame.project.dat.out_month = self.tc_retire_month.GetSelection()
            
            #Set year, if this is blank then month won't be used for output dat
            frame.project.dat.in_year = self.tc_intro_year.GetValue()
            frame.project.dat.out_year = self.tc_retire_year.GetValue()
            
            frame.project.dat.level = self.tc_level.GetValue()
            frame.project.dat.noinfo = self.tc_noinfo.GetValue()
            frame.project.dat.nocon = self.tc_noconstruction.GetValue()
            frame.project.dat.needs_ground = self.tc_needsground.GetValue()
            
            #Set type by which option is set in the type box, this can be referenced against the list of tc_type choices
            #to find the output name
            frame.project.dat.type = self.tc_type.GetSelection()
            
            
            frame.project.dat.location_b = self.tc_locationbui.GetValue()
            frame.project.dat.chance_b = self.tc_chancebui.GetValue()
            frame.project.dat.build_time = self.tc_build_time.GetValue()
            frame.project.dat.extension = self.tc_extension.GetValue()
            frame.project.dat.pax = self.tc_enables_pax.GetValue()
            frame.project.dat.post = self.tc_enables_post.GetValue()
            frame.project.dat.ware = self.tc_enables_ware.GetValue()
            frame.project.dat.location_f = self.tc_locationfac.GetValue()
            frame.project.dat.chance_f = self.tc_chancefac.GetValue()
            frame.project.dat.prod = self.tc_productivity.GetValue()
            frame.project.dat.range = self.tc_range.GetValue()
            frame.project.dat.colour = self.tc_mapcolour.GetValue()
            frame.project.dat.add = self.tc_add_op.GetValue()
            self.Destroy()
        def On_init(datoptions):
            self.tc_obj.SetSelection(datoptions.obj)
            self.tc_name.SetValue(datoptions.name)
            self.tc_copyright.SetValue(datoptions.copyright)


            self.tc_intro_month.SetValue(tc_month_choices[datoptions.in_month])
            self.tc_intro_year.SetValue(datoptions.in_year)
            
            self.tc_retire_month.SetValue(tc_month_choices[datoptions.out_month])
            self.tc_retire_year.SetValue(datoptions.out_year)
            
            self.tc_level.SetValue(datoptions.level)
            self.tc_noinfo.SetValue(datoptions.noinfo)
            self.tc_noconstruction.SetValue(datoptions.nocon)
            
            self.tc_needsground.SetValue(frame.project.dat.needs_ground)

            #Set type
            self.tc_type.SetValue(tc_type_choices[datoptions.type])
            
            
            self.tc_locationbui.SetValue(datoptions.location_b)
            self.tc_chancebui.SetValue(datoptions.chance_b)
            self.tc_build_time.SetValue(datoptions.build_time)
            self.tc_extension.SetValue(datoptions.extension)
            self.tc_enables_pax.SetValue(datoptions.pax)
            self.tc_enables_post.SetValue(datoptions.post)
            self.tc_enables_ware.SetValue(datoptions.ware)
            self.tc_locationfac.SetValue(datoptions.location_f)
            self.tc_chancefac.SetValue(datoptions.chance_f)
            self.tc_productivity.SetValue(datoptions.prod)
            self.tc_range.SetValue(datoptions.range)
            self.tc_mapcolour.SetValue(datoptions.colour)
            self.tc_add_op.SetValue(datoptions.add)

        #self.tc_list_input_add.Bind(wx.EVT_BUTTON, tc_display_goods, self.tc_list_input_add)
        self.tc_list_input.Bind(wx.EVT_LISTBOX, tc_listbox_click, self.tc_list_input)
        self.tc_list_output.Bind(wx.EVT_LISTBOX, tc_listbox_click, self.tc_list_output)
        self.tc_list_input_add.Bind(wx.EVT_BUTTON, tc_listbox_add, self.tc_list_input_add)
        self.tc_list_output_add.Bind(wx.EVT_BUTTON, tc_listbox_add, self.tc_list_output_add)
        self.tc_list_input_remove.Bind(wx.EVT_BUTTON, tc_listbox_remove, self.tc_list_input_remove)
        self.tc_list_output_remove.Bind(wx.EVT_BUTTON, tc_listbox_remove, self.tc_list_output_remove)

        self.tc_io_edit_good.Bind(wx.EVT_TEXT, tc_edit_text, self.tc_io_edit_good)
        self.tc_io_edit_capacity.Bind(wx.EVT_TEXT, tc_edit_text, self.tc_io_edit_capacity)
        self.tc_io_edit_factor.Bind(wx.EVT_TEXT, tc_edit_text, self.tc_io_edit_factor)
        self.tc_io_edit_suppliers.Bind(wx.EVT_TEXT, tc_edit_text, self.tc_io_edit_suppliers)
        self.Bind(wx.EVT_CLOSE, On_close, self)
        self.close_button = wx.Button(self, -1, label=gt("&Save changes and close"))  #Close button
        self.close_button.Bind(wx.EVT_BUTTON, On_close, self.close_button)
        
        #Input/Output sizers added to lower factory box        
        self.tc_factory_sizer_io.Add(self.tc_input_sizer, 1, wx.LEFT|wx.ALIGN_TOP, 0)
        self.tc_factory_sizer_io.Add(self.tc_output_sizer, 1, wx.LEFT|wx.ALIGN_TOP, 0)
        self.tc_factory_sizer_io.Add(self.tc_io_edit_sizer, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
        
        self.tc_factory_sizer.Add(self.tc_factory_line1, 0, wx.TOP|wx.EXPAND, 6)
        self.tc_factory_sizer.Add(self.tc_factory_sizer_io, 1, wx.TOP, 2)

        #Additional options--------------------------------------------------------------------------------------------------
        self.tc_add_box = wx.StaticBox(self, -1, gt("Additional Options:"))#
        self.tc_add_box.SetToolTipString(gt("ttAdditional Options:"))
        self.tc_add_sizer = wx.StaticBoxSizer(self.tc_add_box, wx.VERTICAL)
                
        self.tc_add_op =  wx.TextCtrl(self, 6601, "", (-1,-1),(-1,-1), wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_RICH)     #Additional options
        self.tc_add_sizer.Add(self.tc_add_op, 1, wx.EXPAND|wx.ALL, 5)
        self.tc_add_op.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))

        #Put everything inside the window--------------------------------------------------------------------------------------------------
        self.border = wx.FlexGridSizer(2,2,0,0)

        self.everything = wx.BoxSizer(wx.VERTICAL)
        
        self.close_controls = wx.BoxSizer(wx.HORIZONTAL)
        self.close_controls.Add(self.close_button, 0, wx.ALIGN_RIGHT)
        
        self.grouper_1 = wx.BoxSizer(wx.VERTICAL)
        self.grouper_1.Add(self.tc_obj, 0, wx.EXPAND|wx.RIGHT|wx.BOTTOM, 5)
        self.grouper_1.Add(self.tc_global_sizer, 1, wx.EXPAND|wx.RIGHT, 5)
        
        self.border.Add(self.grouper_1, 0, wx.TOP|wx.LEFT, 5)        
        self.border.Add(self.tc_add_sizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        self.border.Add(self.tc_building_sizer, 1, wx.EXPAND|wx.ALL, 5)
        self.border.Add(self.tc_factory_sizer, 1, wx.EXPAND|wx.ALL, 5)

        self.everything.Add(self.border, 1, wx.EXPAND|wx.ALL, 0)
        self.everything.Add(self.close_controls, 0, wx.BOTTOM|wx.ALIGN_CENTER, 3)

        inputgoods = frame.project.dat.inputgoods
        outputgoods = frame.project.dat.outputgoods
        tc_display_goods(1)

        self.SetSizer(self.everything)
        self.everything.Fit(self)

        #Finally, initiate function to disable controls...
        On_tc_obj(self)
        On_tc_type(self)
        #And set all the starting values...
        On_init(frame.project.dat)
        On_tc_obj(1)

#----------------------------------------------Save Changes?? Dialog----------------------------------------------------

class PreferencesDialog(wx.Dialog):
    """Displays the preferences window, which lets you pick language, and set other options"""
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE):

        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        self.sizer = wx.BoxSizer(wx.VERTICAL)   #Main sizer

        #Language options        
        self.pref_language_box = wx.StaticBox(self, -1, gt("PrefsLanguage:"))    #Box containing language options
        self.pref_language_box_sizer = wx.StaticBoxSizer(self.pref_language_box, wx.VERTICAL)
        self.pref_language_top = wx.BoxSizer(wx.HORIZONTAL)
        
        def GetLanguageAttribs():
            #Get image and name for the translation
            #Translation image
            language, firstrun = Read_Config()
            if os.access("language/tc-" + language + ".png", os.F_OK):
                im = wx.Image("language/tc-" + language + ".png", wx.BITMAP_TYPE_PNG)
                bmp = im.ConvertToBitmap()
            else:
                if os.access("language/tc-xx.png", os.F_OK):
                    im = wx.Image("language/tc-xx.png", wx.BITMAP_TYPE_PNG)
                    bmp = im.ConvertToBitmap()
                else:
                    sys.stderr.write("ERROR: Unable to open the default language image - please check your installation!")
            #Translation name
            file = open(("language/tc-" + language + ".tab"), "r")
            p = file.readline()
            if p[-1] == "\n":
                p = p[:-1]
            q = unicode(p, "utf-8")
            file.close
            return (bmp, q)

        bmp, q = GetLanguageAttribs()
        self.pref_language_icon = wx.StaticBitmap(self, -1, bmp, (-1,-1), (-1,-1))
        self.pref_language_name = wx.StaticText(self, -1, q)
        self.pref_language_changebutton = wx.Button(self, -1, label=gt("ChangeLanguage..."))
        self.pref_language_warning = wx.StaticText(self, -1, gt("Note: Changing language requires restart"))

        self.pref_language_top.Add(self.pref_language_icon, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.pref_language_top.Add(self.pref_language_name, 1, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)             #Add first three bits to horizontal sizer
        self.pref_language_top.Add(self.pref_language_changebutton, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)

        self.pref_language_box_sizer.Add(self.pref_language_top, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)        #Add that sizer and the text to vertical box
        self.pref_language_box_sizer.Add(self.pref_language_warning, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        def OnClickLanguage(e):
            dlg = SelectLanguageDialog(self, -1, gt("Select Language"), size=(-1, -1),
                                 #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                                 style = wx.DEFAULT_DIALOG_STYLE
                                 )
            a = dlg.ShowModal() # Shows it & collects return information in "a"
            dlg.Destroy() # finally destroy it when finished.
            
            bmp, q = GetLanguageAttribs()
            self.pref_language_icon.SetBitmap(bmp)
            self.pref_language_name.SetLabel(q)

        self.pref_language_changebutton.Bind(wx.EVT_BUTTON, OnClickLanguage, self.pref_language_changebutton)

##.Disable()

        #Makeobj options
        self.pref_makeobj_box = wx.StaticBox(self, -1, gt("Makeobj:"))    #Box containing makeobj options
        self.pref_makeobj_box_sizer = wx.StaticBoxSizer(self.pref_makeobj_box, wx.VERTICAL)
        self.pref_makeobj_bottom = wx.BoxSizer(wx.HORIZONTAL)

        self.pref_makeobj_box.Disable()

        self.pref_makeobj_pathlabel = wx.StaticText(self, -1, gt("Path to makeobj:"))
        self.pref_makeobj_path = wx.TextCtrl(self, -1, value="")
        self.pref_makeobj_path.SetToolTipString(gt("ttPath to makeobj:"))
        self.pref_makeobj_browse = wx.Button(self, -1, label=gt("ChangeMakeobj..."))

        self.pref_makeobj_pathlabel.Disable()
        self.pref_makeobj_path.Disable()
        self.pref_makeobj_browse.Disable()

        self.pref_makeobj_bottom.Add(self.pref_makeobj_path, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        self.pref_makeobj_bottom.Add(self.pref_makeobj_browse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)

        self.pref_makeobj_box_sizer.Add(self.pref_makeobj_pathlabel, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 3)
        self.pref_makeobj_box_sizer.Add(self.pref_makeobj_bottom, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)


        #Palette options
        self.pref_palette_box = wx.StaticBox(self, -1, gt("Palette:"))    #Box containing language options
        self.pref_palette_box_sizer = wx.StaticBoxSizer(self.pref_palette_box, wx.VERTICAL)
        self.pref_palette_bottom = wx.BoxSizer(wx.HORIZONTAL)

        self.pref_palette_box.Disable()

        self.pref_palette_pathlabel = wx.StaticText(self, -1, gt("Path to palette file:"))
        self.pref_palette_path = wx.TextCtrl(self, -1, value=PATH_TO_PAL_FILE)
        self.pref_makeobj_path.SetToolTipString(gt("ttPath to palette:"))
        self.pref_palette_browse = wx.Button(self, -1, label=gt("palChange..."))
        self.pref_palette_default = wx.Button(self, -1, label=gt("palReset"))

        self.pref_palette_pathlabel.Disable()
        self.pref_palette_path.Disable()
        self.pref_makeobj_path.Disable()
        self.pref_palette_browse.Disable()
        self.pref_palette_default.Disable()

        self.pref_palette_bottom.Add(self.pref_palette_path, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        self.pref_palette_bottom.Add(self.pref_palette_browse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        self.pref_palette_bottom.Add(self.pref_palette_default, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 3)

        self.pref_palette_box_sizer.Add(self.pref_palette_pathlabel, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 3)
        self.pref_palette_box_sizer.Add(self.pref_palette_bottom, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        def OnClickPalDefault(e):
            self.pref_palette_path.SetValue(PATH_TO_PAL_FILE)
        def OnClickPalChange(e):
            dlg = wx.FileDialog(self, gt("Choose a file to save to .pal file to use..."), "", "", "Palette Files (*.pal)|*.pal", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                language, firstrun = Read_Config()
                frame.path_to_pal = dlg.GetPath()
                self.pref_palette_path.SetValue(frame.path_to_pal)
                # Now save this new preference
                Write_Config(language)
                dlg.Destroy()
                return 1
            else:
                dlg.Destroy()
                return 0

##        self.pref_palette_default.Bind(wx.EVT_BUTTON, OnClickPalDefault, self.pref_palette_default)
##        self.pref_palette_browse.Bind(wx.EVT_BUTTON, OnClickPalChange, self.pref_palette_browse)

        #Rest of the dialog
        self.ok_button = wx.Button(self, -1, label=gt("Ok"))

        def OnClickOk(e):
            self.EndModal(1)
        self.ok_button.Bind(wx.EVT_BUTTON, OnClickOk, self.ok_button)

        self.sizer.Add(self.pref_language_box_sizer, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        self.sizer.Add(self.pref_makeobj_box_sizer, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        self.sizer.Add(self.pref_palette_box_sizer, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP|wx.LEFT|wx.RIGHT, 5)
        self.sizer.Add(self.ok_button, 0, wx.ALIGN_LEFT|wx.ALL, 5)


        self.ok_button.SetDefault()
        self.SetSizer(self.sizer)
        self.sizer.SetMinSize((350,1))
        self.sizer.Fit(self)

#----------------------------------------------Save Changes?? Dialog----------------------------------------------------

class SaveChangesDialog(wx.Dialog):
    """Displays a prompt to choose to save changes, discard or cancel,
    returns 1 for save, 0 for discard, -1 for cancel"""
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
#        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        
        text = wx.StaticText(self, -1, gt("Document has been modified - do you wish to save your changes?"))
        
        yes_button = wx.Button(self, -1, label=gt("Yes"))
        no_button = wx.Button(self, -1, label=gt("No"))
        cancel_button = wx.Button(self, -1, label=gt("Cancel"))

        def OnClickYes(e):
            self.EndModal(1)
        def OnClickNo(e):
            self.EndModal(0)
        def OnClickCancel(e):
            self.EndModal(-1)


        yes_button.Bind(wx.EVT_BUTTON, OnClickYes, yes_button)
        no_button.Bind(wx.EVT_BUTTON, OnClickNo, no_button)
        cancel_button.Bind(wx.EVT_BUTTON, OnClickCancel, cancel_button)


        sizer.Add(text, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        sizer2.Add(yes_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        sizer2.Add(no_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        sizer2.Add(cancel_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        sizer.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        yes_button.SetDefault()
        self.SetSizer(sizer)

        sizer.Fit(self)



#----------------------------------------------About Dialog----------------------------------------------------

class AboutDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE):

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
#        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label1 = wx.StaticText(self, -1, "TileCutter v" + VERSION_NUMBER)
#
        para_1 = wx.StaticText(self, -1, gt("About Text1"))
        para_1.Wrap(300)
        para_2 = wx.StaticText(self, -1, gt("About Text2"))
        para_2.Wrap(300)
        para_3 = wx.StaticText(self, -1, gt("About Text3"))
        para_3.Wrap(300)

        sizer.Add(label1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        sizer.Add(para_1, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        sizer.Add(para_2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        sizer.Add(para_3, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        # Default Web links:
        self._hyper1 = hl.HyperLinkCtrl(self, wx.ID_ANY, "http://simutrans.entropy.me.uk/tilecutter/",
                                        URL="http://simutrans.entropy.me.uk/tilecutter/")
        sizer.Add(self._hyper1, 0, wx.ALL, 10)

        label3 = wx.StaticText(self, -1, gt("About EndText"))
        label3.Wrap(350)
        sizer.Add(label3, 0, wx.ALIGN_LEFT|wx.ALL, 5)


        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK, label=gt("CloseAbout"))
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

#----------------------------------------------Image area-----------------------------------------------------
BUFFERED = 0
class ImageWindow(wx.ScrolledWindow):
    bmp = []
    def __init__(self, parent, id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.bmp = DrawArrow("empty")
        self.lines = []
        self.x = self.y = 0
        #self.curLine = []
        self.drawing = False

        #self.SetBackgroundColour("WHITE")
        #self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        self.SetVirtualSize((1, 1))
        self.SetScrollRate(20,20)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)


        #Need to make intelligent buffer bitmap sizing work!
        
        self.buffer = wx.EmptyBitmap(4000,2500)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush((231,255,255)))
        dc.Clear()
        self.DrawBitmap(dc)
        
    def OnPaint(self, event):
        
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
        
        #dc = wx.PaintDC(self)
        #self.PrepareDC(dc)
        # since we're not buffering in this case, we have to
        # paint the whole window, potentially very time consuming.
        #self.DrawBitmap(1)

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
        dc.SetBackground(wx.Brush((231,255,255)))
        dc.Clear()
        dc.DrawBitmap(bitmap, 0, 0, True)


        #dc = wx.ClientDC(self)
        #self.PrepareDC(dc)
        #self.bmp = bitmap
        #self.SetVirtualSize((bitmap.GetWidth(), bitmap.GetHeight()))
        #dc.Clear()
        #dc.DrawBitmap(bitmap, 0, 0, True)
        #mask = wx.Mask(bitmap, wx.BLUE)
        #bmp.SetMask(mask)
        #self.bmp = bmp


#----------------------------------------------Main Window----------------------------------------------------

class MainWindow(wx.Frame):

    first_open = 1

    Xdimsval = "1"
    Ydimsval = "1"
    Zdimsval = "1"
    offsetX = 0
    offsetY = 0
    
    project = tc_project()
    project.frame.append(tc_frame())

    current = []
    old_f = 0
    old_direction = ""

    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), (700,600),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )



        
        #Startup functions...
        self.pal = LoadPal()
        
        panel = wx.Panel(self, -1, (-1,-1), (500,500))

        #Frame box, containing the currently being worked on frame
        #self.tc_frame_box = wx.StaticBox(panel, -1, "")               #Box containing the current frame
        #self.tc_frame_box_sizer = wx.StaticBoxSizer(self.tc_frame_box, wx.VERTICAL)
        self.tc_frame_box_sizer = wx.BoxSizer(wx.VERTICAL)
        #Frame contents
        #Frame itself, containing the image
        self.tc_display_panel = ImageWindow(panel)
        self.tc_display_panel.SetBackgroundColour((231,255,255))
        #Top frame controls, direction selection
        self.tc_frame_label = wx.StaticText(panel, -1, (gt("Frame %i of %i (%s)") % (1,1,gt("North"))), (-1, -1), (-1, -1), wx.ALIGN_LEFT)

##        self.tc_frame_filebrowse_summer = wx.RadioButton(panel, -1, "", (-1,-1), (0,0), wx.RB_GROUP|wx.ALIGN_RIGHT)
##        self.tc_frame_filebrowse_summericon = 
##        self.tc_frame_filebrowse_winter = wx.RadioButton(panel, -1, "", (-1,-1), (0,0), wx.RB_GROUP|wx.ALIGN_RIGHT)

        self.tc_frame_filebrowse_n = wx.ToggleButton(panel, -1, gt("N"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_e = wx.ToggleButton(panel, -1, gt("E"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_s = wx.ToggleButton(panel, -1, gt("S"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_w = wx.ToggleButton(panel, -1, gt("W"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_n.SetToolTipString(gt("ttdirectionselecterN"))
        self.tc_frame_filebrowse_s.SetToolTipString(gt("ttdirectionselecterS"))
        self.tc_frame_filebrowse_e.SetToolTipString(gt("ttdirectionselecterE"))
        self.tc_frame_filebrowse_w.SetToolTipString(gt("ttdirectionselecterW"))
        #self.tc_frame_filebrowse_n.Enable()
        self.tc_frame_filebrowse_n.SetValue(1)
        self.tc_frame_filebrowse_e.Disable()
        self.tc_frame_filebrowse_s.Disable()
        self.tc_frame_filebrowse_w.Disable()
        #Bottom frame controls - file selection
        self.tc_frame_path_label = wx.StaticText(panel, -1, gt("Source:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_frame_path = wx.TextCtrl(panel, -1, value="", style=wx.TE_READONLY)                        #Current frame's path
        self.tc_frame_path.SetToolTipString(gt("ttinputpath"))
        self.tc_frame_path.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.tc_frame_filebrowse = wx.Button(panel, -1, label=gt("Browse..."))           #Change current frame's filename (browse)
        self.tc_frame_filebrowse.SetToolTipString(gt("ttbrowseinputfile"))
        self.tc_frame_reloadfile = wx.Button(panel, -1, size=(25,-1), label=gt("R"))          #Reload current file
        self.tc_frame_reloadfile.SetToolTipString(gt("ttreloadinputfile"))

        self.tc_display_panel_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_display_panel_top_sizer.Add(self.tc_frame_label, 1, wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_display_panel_top_sizer.Add(self.tc_frame_filebrowse_n, 0, wx.ALIGN_RIGHT, 2)
        self.tc_display_panel_top_sizer.Add(self.tc_frame_filebrowse_e, 0, wx.ALIGN_RIGHT, 2)
        self.tc_display_panel_top_sizer.Add(self.tc_frame_filebrowse_s, 0, wx.ALIGN_RIGHT, 2)
        self.tc_display_panel_top_sizer.Add(self.tc_frame_filebrowse_w, 0, wx.ALIGN_RIGHT, 2)
        self.tc_frame_box_sizer.Add(self.tc_display_panel_top_sizer, 0, wx.BOTTOM|wx.EXPAND, 4)

        self.tc_display_panel_file_sizer = wx.FlexGridSizer(0,5,0,0)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_path_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_path, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.tc_display_panel_file_sizer.AddGrowableCol(1, 4)
        #self.tc_display_panel_file_sizer.AddGrowableCol(3, 2)
        self.tc_frame_box_sizer.Add(self.tc_display_panel, 1, wx.BOTTOM|wx.EXPAND, 4)
        self.tc_frame_box_sizer.Add(self.tc_display_panel_file_sizer, 0, wx.BOTTOM|wx.EXPAND, 2)



        #Dimension box, containing controls over image dimensions & display
        #self.tc_size_box = wx.StaticBox(panel, -1, "")               #Box containing the dimension controls
        #self.tc_size_box_sizer = wx.StaticBoxSizer(self.tc_size_box, wx.VERTICAL)
        self.tc_size_box_sizer = wx.BoxSizer(wx.VERTICAL)
        #Right hand panel
        #pakSize choice box
        
        self.tc_choice_paksize_label = wx.StaticText(panel, -1, gt("paksize:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_paksize = wx.ComboBox(panel, -1, DEFAULT_PAKSIZE, (-1, -1), (54, -1), choicelist_paksize, wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.tc_choice_paksize.SetToolTipString(gt("ttpaksize:"))
        #Views choice box
        self.tc_choice_views_label = wx.StaticText(panel, -1, gt("Views:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_views = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), ["1","2","4"], wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.tc_choice_views.SetToolTipString(gt("ttViews:"))
        #x dimensions choice box        
        self.tc_choice_xdims_label = wx.StaticText(panel, -1, gt("x dimension:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_xdims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.tc_choice_xdims.SetToolTipString(gt("ttx dimension:"))
        #y dimensions choice box        
        self.tc_choice_ydims_label = wx.StaticText(panel, -1, "y dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_ydims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.tc_choice_ydims.SetToolTipString(gt("tty dimension:"))
        #z dimensions choice box        
        self.tc_choice_zdims_label = wx.StaticText(panel, -1, "z dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_zdims = wx.ComboBox(panel, -1, "1", (-1, -1), (54, -1), choicelist_dims_z, wx.CB_READONLY)
        self.tc_choice_zdims.SetToolTipString(gt("ttz dimension:"))
        #Auto button        
        self.tc_choice_auto = wx.Button(panel, -1, gt("Auto"), (-1,-1), (-1,-1), wx.BU_EXACTFIT)  #Use the auto function to determine size
        self.tc_choice_auto.SetToolTipString(gt("ttAuto"))
        #Offset control
        self.tc_offset_label = wx.StaticText(panel, -1, gt("Offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_offset_button_up = wx.BitmapButton(panel, -1, DrawArrow("up",1), (-1,-1), (18,18))
        self.tc_offset_button_up.SetToolTipString(gt("ttOffsetUp"))
        self.tc_offset_button_left = wx.BitmapButton(panel, -1, DrawArrow("left",1), (-1,-1), (18,18))
        self.tc_offset_button_left.SetToolTipString(gt("ttOffsetLeft"))
        self.tc_offset_button_right = wx.BitmapButton(panel, -1, DrawArrow("right",1), (-1,-1), (18,18))
        self.tc_offset_button_right.SetToolTipString(gt("ttOffsetRight"))
        self.tc_offset_button_down = wx.BitmapButton(panel, -1, DrawArrow("down",1), (-1,-1), (18,18))
        self.tc_offset_button_down.SetToolTipString(gt("ttOffsetDown"))

        self.tc_offset_selector = wx.CheckBox(panel, -1, gt("Fine"), (-1,-1), (-1,-1))
        self.tc_offset_selector.SetToolTipString(gt("ttOffsetSelector"))
        
        #Add all this to the Dimension box
        #Add dimension controls
        self.tc_size_box_sizer.Add(self.tc_choice_paksize_label, 0, wx.TOP, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_paksize, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_views_label, 0, wx.TOP, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_views, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_xdims_label, 0, wx.TOP, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_xdims, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_ydims_label, 0, wx.TOP, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_ydims, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_zdims_label, 0, wx.TOP, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_zdims, 0, wx.TOP|wx.ALIGN_CENTER, 0)
        self.tc_size_box_sizer.Add(self.tc_choice_auto, 0, wx.TOP|wx.ALIGN_CENTER, 2)
        #Add offset controls
        self.tc_size_box_sizer.Add(self.tc_offset_label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
        self.tc_size_box_sizer.Add(self.tc_offset_selector, 0, wx.ALIGN_LEFT|wx.TOP, 3)
        self.tc_size_box_sizer.Add(self.tc_offset_button_up, 0, wx.ALIGN_CENTER|wx.TOP, 3)
        self.tc_size_box_offset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_size_box_offset_sizer.Add(self.tc_offset_button_left, 0, wx.ALIGN_CENTER|wx.RIGHT,border=9)
        self.tc_size_box_offset_sizer.Add(self.tc_offset_button_right, 0, wx.ALIGN_CENTER|wx.LEFT,border=9)
        self.tc_size_box_sizer.Add(self.tc_size_box_offset_sizer, 0, wx.ALIGN_CENTER)
        self.tc_size_box_sizer.Add(self.tc_offset_button_down, 0, wx.ALIGN_CENTER)

        def GetLongDirection(short):
            if short == "N":
                return gt("North")
            elif short == "E":
                return gt("East")
            elif short == "S":
                return gt("South")
            elif short == "W":
                return gt("West")

        def Set_frame_values(a=0):
            """When the selected frame or a value affecting the selected frame is changed,
            we must update the displayed values..."""
            self.tc_frame_path.SetValue(self.current.abs_path)
            
            if a == 0:  #Usually this should be set first, so that the other values update only afterwards
                im = Analyse(self.current, int(self.project.paksize), GetXYZdims(1), (self.current.offsetx,self.current.offsety))
                ShowImage(im, self.tc_display_panel)
            if a == 2:  #If this is 2, then a new file has been loaded, if this is the first file of a project then
                        #we should use auto-detection to find dimensions
                if self.first_open == 1:
                    dims_xyz = Set_XYZdims(2)  #Set the size values for other frames using special function of Set_XYZdims
                    #dims_xyz = Analyse(self.current, int(self.project.paksize), (-1,-1,-1), (self.current.offsetx,self.current.offsety))
                    im = Analyse(self.current, int(self.project.paksize), dims_xyz, (self.current.offsetx,self.current.offsety))
                    ShowImage(im, self.tc_display_panel)
                    self.first_open = 0
                else:
                    im = Analyse(self.current, int(self.project.paksize), GetXYZdims(1), (self.current.offsetx,self.current.offsety))
                    ShowImage(im, self.tc_display_panel)


            if self.current.xdims == -1:
                sys.stderr.write("tried to set xdims to -1 (37373)\n")
            else:
                self.tc_choice_xdims.SetValue(str(self.current.xdims))
            if self.current.ydims == -1:
                sys.stderr.write("tried to set xdims to -1 (37374)\n")
            else:
                self.tc_choice_ydims.SetValue(str(self.current.ydims))
            if self.current.zdims == -1:
                sys.stderr.write("tried to set xdims to -1 (37375)\n")
            else:
                self.tc_choice_zdims.SetValue(str(self.current.zdims))

            if a == 1:  #But when initialising a frame for the first time, do this second
                im = Analyse(self.current, int(self.project.paksize), GetXYZdims(1), (self.current.offsetx,self.current.offsety))
                ShowImage(im, self.tc_display_panel)

            #self.tc_frame_label.SetLabel(gt("Frame") + " " + str((self.old_f + 1)) + " " + gt("of") + " " + str(len(self.project.frame))
            #                             + " (" + GetLongDirection(self.old_direction) + "):")
            self.tc_frame_label.SetLabel(gt("Frame %i of %i (%s)") % ((self.old_f + 1), len(self.project.frame), GetLongDirection(self.old_direction)))
            
        def Set_Working(f, direction, p=0):  #Read/write current frame info to the project
            """Transfers values from the project to the current working frame,
            takes a frame number and a direction ("N","E","S","W") as arguments,
            passing the same frame as is currently open will save that frame's state to
            the project"""
            if p < 1:   #Set p to 2 if you're deleting a frame, to stop assignment
                if self.old_direction == "N":
                    self.project.frame[self.old_f].north = self.current
                elif self.old_direction == "E":
                    self.project.frame[self.old_f].east = self.current       #First copy current working to the project...
                elif self.old_direction == "S":
                    self.project.frame[self.old_f].south = self.current
                elif self.old_direction == "W":
                    self.project.frame[self.old_f].west = self.current

            if direction == "N":
                self.current = self.project.frame[f].north
            elif direction == "E":
                self.current = self.project.frame[f].east           #Then copy new working from project to current
            elif direction == "S":
                self.current = self.project.frame[f].south
            elif direction == "W":
                self.current = self.project.frame[f].west
                
            #sys.stderr.write("image:" + str(self.current.image) + "\n")
            if self.current.image == 0:
                if self.current.abs_path == "":
                    #sys.stderr.write("filename" + self.current.abs_path + "\n")
                    self.current.image = NewImage()
                else:
                    #sys.stderr.write("filename" + self.current.abs_path + "\n")
                    self.current.image = (Image.open(self.current.abs_path))
                

            self.old_f = f
            self.old_direction = direction                          #Set old values so that this frame can later be saved

            if p == 0 or p == 2:
                Set_frame_values(1)
                

        def On_browse_input(e):
            
            """Changes the location of the source file for the current frame"""
            dlg = wx.FileDialog(self, gt("Choose a Source file..."), "", "", "PNG files (*.png)|*.png|Other Image files (*.bmp, *.gif, *.jpg)|*.bmp;*.gif;*.jpg", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.current.abs_path = (dlg.GetPath())
                self.current.image = (Image.open(self.current.abs_path))
            dlg.Destroy()
            Set_frame_values(2)
        def On_reload_input(e):
            """Reloads the input file into memory"""
            self.current.image = (Image.open(self.current.abs_path))
            Set_frame_values(2)

        self.tc_frame_filebrowse.Bind(wx.EVT_BUTTON, On_browse_input, self.tc_frame_filebrowse)
        self.tc_frame_reloadfile.Bind(wx.EVT_BUTTON, On_reload_input, self.tc_frame_reloadfile)

        def Set_views():
            if self.tc_choice_views.GetValue() == "1":   #If one view selected, disable all other views
                frame.project.views = "1"   #Set number of views used in project file
                self.tc_frame_filebrowse_n.Enable()
                self.tc_frame_filebrowse_e.Disable()
                self.tc_frame_filebrowse_s.Disable()
                self.tc_frame_filebrowse_w.Disable()
                self.tc_frame_filebrowse_n.SetValue(1)
                self.tc_frame_filebrowse_e.SetValue(0)
                self.tc_frame_filebrowse_s.SetValue(0)
                self.tc_frame_filebrowse_w.SetValue(0)
                Set_Working(self.old_f, "N")
            elif self.tc_choice_views.GetValue() == "2": #If 2 views selected, disable other two
                frame.project.views = "2"   #Set number of views used in project file
                self.tc_frame_filebrowse_n.Enable()
                self.tc_frame_filebrowse_e.Enable()
                self.tc_frame_filebrowse_s.Disable()
                self.tc_frame_filebrowse_w.Disable()
                if self.tc_frame_filebrowse_s.GetValue() == 1 or self.tc_frame_filebrowse_w.GetValue() == 1:
                    self.tc_frame_filebrowse_n.SetValue(0)
                    self.tc_frame_filebrowse_e.SetValue(1)
                    self.tc_frame_filebrowse_s.SetValue(0)
                    self.tc_frame_filebrowse_w.SetValue(0)
                    Set_Working(self.old_f, "E")
            else:                   #Otherwise, enable all
                frame.project.views = "4"   #Set number of views used in project file
                self.tc_frame_filebrowse_n.Enable()
                self.tc_frame_filebrowse_e.Enable()
                self.tc_frame_filebrowse_s.Enable()
                self.tc_frame_filebrowse_w.Enable()
            

        def On_views(e):
            #a = e.GetEventObject()
            Set_views()
        def On_view_select(e):
            a = e.GetEventObject()
            self.tc_frame_filebrowse_n.SetValue(0)
            self.tc_frame_filebrowse_e.SetValue(0)
            self.tc_frame_filebrowse_s.SetValue(0)
            self.tc_frame_filebrowse_w.SetValue(0)
            if a.GetLabel() == gt("N"):
                self.tc_frame_filebrowse_n.SetValue(1)
                Set_Working(self.old_f, "N")
            elif a.GetLabel() == gt("E"):
                self.tc_frame_filebrowse_e.SetValue(1)
                Set_Working(self.old_f, "E")
            elif a.GetLabel() == gt("S"):
                self.tc_frame_filebrowse_s.SetValue(1)
                Set_Working(self.old_f, "S")
            else:
                self.tc_frame_filebrowse_w.SetValue(1)
                Set_Working(self.old_f, "W")

        def OnCombo_paksize(e):
            """On selection of an item in the paksize box"""
            self.project.paksize = self.tc_choice_paksize.GetValue()
            Set_frame_values()

        def Set_XYZdims(a=0):
            #Needs to be altered when multi-frame supported, so that frame zero's dims values used for all
            """Controls the dimensions for the project frames"""
            
            direction = self.old_direction
            if a == 0:
                z = self.tc_choice_zdims.GetValue()
                if direction == "N" or direction == "S":
                    x = self.tc_choice_xdims.GetValue()    # a = xdims value 1-16
                    y = self.tc_choice_ydims.GetValue()    # b = ydims value 1-16
                else:
                    y = self.tc_choice_xdims.GetValue()    # a = xdims value 1-16
                    x = self.tc_choice_ydims.GetValue()    # b = ydims value 1-16
            elif a == 1 or a == 2:  #Auto button has been used or first image has been added
                                    #call Analyse to guess dimensions and then apply to all directions
                x, y, z = Analyse(self.current, int(self.project.paksize), (-1,-1,-1), (self.current.offsetx,self.current.offsety))
                
            frame.project.frame[0].north.zdims = z
            frame.project.frame[0].north.xdims = x
            frame.project.frame[0].north.ydims = y
            
            frame.project.frame[0].east.zdims = z
            frame.project.frame[0].east.xdims = y
            frame.project.frame[0].east.ydims = x
            
            frame.project.frame[0].south.zdims = z
            frame.project.frame[0].south.xdims = x
            frame.project.frame[0].south.ydims = y
            
            frame.project.frame[0].west.zdims = z
            frame.project.frame[0].west.xdims = y
            frame.project.frame[0].west.ydims = x
            
            if a == 0:
                Set_frame_values()
            elif a == 1:
                Set_frame_values(1)
            elif a == 2:
                return (x, y, z)
            
        def OnAuto_XYZ(e):
            """On click of the automatic size detection button"""
            Set_XYZdims(1)
            
        def OnCombo_Xdims(e):
            """On selection of new item in the Xdims combo box"""
            Set_XYZdims()

        def OnCombo_Ydims(e):
            """On selection of new item in the Ydims combo box"""
            Set_XYZdims()

        def OnCombo_Zdims(e):
            """On selection of new item in the Zdims combo box"""
            Set_XYZdims()

        def GetXYZdims(e):
            """Returns the dimensions set in the program's GUI"""
            a = self.tc_choice_ydims.GetValue()
            b = self.tc_choice_xdims.GetValue()
            c = self.tc_choice_zdims.GetValue()
            if a == gt("auto"):
                yy = -1
                xx = -1
            else:
                yy = int(a)
                xx = int(b)
            if c == gt("auto"):
                zz = -1
            else:
                zz = int(c)
            g = xx,yy,zz
            return g

##        self.tc_offset_button_up = wx.BitmapButton(panel, -1, DrawArrow("up"), (-1,-1), (18,18))
##        self.tc_offset_button_up.SetToolTipString(gt("ttOffsetUp"))
##        self.tc_offset_button_left = wx.BitmapButton(panel, -1, DrawArrow("left"), (-1,-1), (18,18))
##        self.tc_offset_button_left.SetToolTipString(gt("ttOffsetLeft"))
##        self.tc_offset_button_right = wx.BitmapButton(panel, -1, DrawArrow("right"), (-1,-1), (18,18))
##        self.tc_offset_button_right.SetToolTipString(gt("ttOffsetRight"))
##        self.tc_offset_button_down = wx.BitmapButton(panel, -1, DrawArrow("down"), (-1,-1), (18,18))
##        self.tc_offset_button_down.SetToolTipString(gt("ttOffsetDown"))


        # Functions for the offset buttons
        def OnSelectFine(e):
            """On selection or deselection of the fine control checkbox"""
            if self.tc_offset_selector.GetValue() == 0:
                # Change the arrows of the buttons to be double arrows
                self.tc_offset_button_up.SetBitmapLabel(DrawArrow("up",1))
                self.tc_offset_button_down.SetBitmapLabel(DrawArrow("down",1))
                self.tc_offset_button_left.SetBitmapLabel(DrawArrow("left",1))
                self.tc_offset_button_right.SetBitmapLabel(DrawArrow("right",1))
            else:
                # Change the arrows of the buttons to be single arrows
                self.tc_offset_button_up.SetBitmapLabel(DrawArrow("up",0))
                self.tc_offset_button_down.SetBitmapLabel(DrawArrow("down",0))
                self.tc_offset_button_left.SetBitmapLabel(DrawArrow("left",0))
                self.tc_offset_button_right.SetBitmapLabel(DrawArrow("right",0))
        def OnClickOffUp(e):
            """On click of the offset increase button"""
            if self.tc_offset_selector.GetValue() == 1:
                self.current.offsety = self.current.offsety + 1
            else:
                self.current.offsety = self.current.offsety + int(self.project.paksize)
            Set_frame_values()
        def OnClickOffLeft(e):
            """On click of the offset increase button"""
            if self.tc_offset_selector.GetValue() == 0:
                if self.current.offsetx >= int(self.project.paksize):
                    self.current.offsetx = self.current.offsetx - int(self.project.paksize)
                    Set_frame_values()
                else:
                    self.current.offsetx = 0
                    Set_frame_values()
            else:
                if self.current.offsetx > 0:
                    self.current.offsetx = self.current.offsetx - 1
                    Set_frame_values()

        def OnClickOffRight(e):
            """On click of the offset increase button"""
            if self.tc_offset_selector.GetValue() == 1:
                self.current.offsetx = self.current.offsetx + 1
            else:
                self.current.offsetx = self.current.offsetx + int(self.project.paksize)
            Set_frame_values()
        def OnClickOffDown(e):
            """On click of the offset increase button"""
            if self.tc_offset_selector.GetValue() == 0:
                if self.current.offsety >= int(self.project.paksize):
                    self.current.offsety = self.current.offsety - int(self.project.paksize)
                    Set_frame_values()
                else:
                    self.current.offsety = 0
                    Set_frame_values()
            else:
                if self.current.offsety > 0:
                    self.current.offsety = self.current.offsety - 1
                    Set_frame_values()

        self.tc_choice_views.Bind(wx.EVT_COMBOBOX, On_views, self.tc_choice_views)
        self.tc_frame_filebrowse_n.Bind(wx.EVT_TOGGLEBUTTON, On_view_select, self.tc_frame_filebrowse_n)
        self.tc_frame_filebrowse_e.Bind(wx.EVT_TOGGLEBUTTON, On_view_select, self.tc_frame_filebrowse_e)
        self.tc_frame_filebrowse_s.Bind(wx.EVT_TOGGLEBUTTON, On_view_select, self.tc_frame_filebrowse_s)
        self.tc_frame_filebrowse_w.Bind(wx.EVT_TOGGLEBUTTON, On_view_select, self.tc_frame_filebrowse_w)
        self.tc_choice_paksize.Bind(wx.EVT_COMBOBOX, OnCombo_paksize, self.tc_choice_paksize)
        self.tc_choice_xdims.Bind(wx.EVT_COMBOBOX, OnCombo_Xdims, self.tc_choice_xdims)
        self.tc_choice_ydims.Bind(wx.EVT_COMBOBOX, OnCombo_Ydims, self.tc_choice_ydims)
        self.tc_choice_zdims.Bind(wx.EVT_COMBOBOX, OnCombo_Zdims, self.tc_choice_zdims)
        self.tc_choice_auto.Bind(wx.EVT_BUTTON, OnAuto_XYZ, self.tc_choice_auto)

        self.tc_offset_button_up.Bind(wx.EVT_BUTTON, OnClickOffUp, self.tc_offset_button_up)
        self.tc_offset_button_left.Bind(wx.EVT_BUTTON, OnClickOffLeft, self.tc_offset_button_left)
        self.tc_offset_button_right.Bind(wx.EVT_BUTTON, OnClickOffRight, self.tc_offset_button_right)
        self.tc_offset_button_down.Bind(wx.EVT_BUTTON, OnClickOffDown, self.tc_offset_button_down)

        self.tc_offset_selector.Bind(wx.EVT_CHECKBOX, OnSelectFine, self.tc_offset_selector)

        #Frame selection box, containing controls to select the frame and add/remove frames
        #self.tc_frame_select_box = wx.StaticBox(panel, -1, "")               #Box containing the frame selection controls
        #self.tc_frame_select_box_sizer = wx.StaticBoxSizer(self.tc_frame_select_box, wx.VERTICAL)
        self.tc_frame_select_box_sizer = wx.BoxSizer(wx.VERTICAL)
        #Animation control
        self.tc_frame_select_items = []
        self.tc_frame_select_label = wx.StaticText(panel, -1, gt("Frames:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_frame_select_input_add = wx.Button(panel, -1, "+", (-1,-1), (30,16))
        self.tc_frame_select_input_add.SetToolTipString(gt("ttAdd new frame"))
        self.tc_frame_select_input_remove = wx.Button(panel, -1, "-", (-1,-1), (30,16))
        self.tc_frame_select_input_remove.SetToolTipString(gt("ttRemove selected frame"))
        self.tc_frame_select_input = wx.ListBox(panel, -1, (-1,-1), (60, -1), self.tc_frame_select_items, wx.LB_SINGLE)
        self.tc_frame_select_input.SetToolTipString(gt("ttList of frames"))
        self.tc_frame_select_input_up = wx.BitmapButton(panel, -1, DrawArrow("up"), (-1,-1), (30,16))
        self.tc_frame_select_input_up.SetToolTipString(gt("ttMove frame up"))
        self.tc_frame_select_input_down = wx.BitmapButton(panel, -1, DrawArrow("down"), (-1,-1), (30,16))
        self.tc_frame_select_input_down.SetToolTipString(gt("ttMove frame down"))
        #Add this to its sizer...
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_label, 0, wx.TOP|wx.ALIGN_LEFT, 0)
        self.tc_frame_select_controls_top = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_frame_select_controls_top.Add(self.tc_frame_select_input_add, 0, wx.TOP, 0)
        self.tc_frame_select_controls_top.Add(self.tc_frame_select_input_remove, 0, wx.TOP, 0)
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_controls_top, 0, wx.TOP|wx.ALIGN_CENTER, 2)
        
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_input, 1, wx.TOP|wx.ALIGN_CENTER, 0)

        self.tc_frame_select_controls_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_frame_select_controls_bottom.Add(self.tc_frame_select_input_up, 0, wx.TOP, 0)
        self.tc_frame_select_controls_bottom.Add(self.tc_frame_select_input_down, 0, wx.TOP, 0)
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_controls_bottom, 0, wx.BOTTOM|wx.ALIGN_CENTER, 30)


        self.tc_frame_select_label.Disable()
        self.tc_frame_select_input_add.Disable()
        self.tc_frame_select_input_remove.Disable()
        self.tc_frame_select_input.Disable()
        self.tc_frame_select_input_up.Disable()
        self.tc_frame_select_input_down.Disable()

        def tc_highlight(num):
            """Highlights item in a list
            io is the list to highlight, num is the item to select"""
            self.tc_frame_select_input.SetSelection(num)
        def tc_frame_click(e):
            """Event triggered when a frame list item is clicked on
            Load all details of that frame into the current frame,
            which is then displayed by another function"""
            skip = 0
            selected = self.tc_frame_select_input.GetSelection()
            if selected == -1:
                skip = 1
            else:
                Set_Working(selected, self.old_direction)
            
        def tc_frame_up(e):
            """Event triggered when the move frame up button is clicked"""
            skip = 0
            selected = self.tc_frame_select_input.GetSelection()
            if selected == -1:  #If nothing selected, do nothing
                skip = 1
            elif selected == 0: #If the first frame is selected, also do nothing
                skip = 1
            else:               #Otherwise, move the frame up
                f = self.project.frame.pop(selected)
                self.project.frame.insert((selected - 1), f)
                #tc_display_frames(1)
                tc_highlight(selected - 1)
                self.old_f = (selected - 1)
                Set_Working(selected - 1, self.old_direction, 0)
        def tc_frame_down(e):
            """Event triggered when the move frame down button is clicked"""
            skip = 0
            selected = self.tc_frame_select_input.GetSelection()
            if selected == -1:  #If nothing selected, do nothing
                skip = 1
            elif selected == (len(self.project.frame) - 1): #If last frame selected, do nothing
                skip = 1
            else:   #Otherwise, move the frame down
                f = self.project.frame.pop(selected)
                self.project.frame.insert((selected + 1), f)
                #tc_display_frames(1)
                tc_highlight(selected + 1)
                self.old_f = (selected + 1)
                Set_Working(selected + 1, self.old_direction, 0)
        def tc_frame_add(e):
            """Event triggered when the add frame button is clicked"""
            skip = 0
            if len(self.project.frame) == MAX_FRAMES:   #Do nothing if there are already max number of frames
                skip = 1
            else:
                selected = self.tc_frame_select_input.GetSelection()
                if selected == -1:      #If nothing selected, add a frame to the end and select it
                    self.project.frame.append(tc_frame())
                    tc_display_frames(1)
                    tc_highlight(len(self.project.frame) - 1)
                    Set_Working((len(self.project.frame) - 1), "N")
                elif selected == (len(self.project.frame) - 1): #If the last frame is selected, add to the end
                    self.project.frame.append(tc_frame())
                    tc_display_frames(1)
                    tc_highlight(len(self.project.frame) - 1)
                    Set_Working((len(self.project.frame) - 1), "N")
                else:           #Otherwise, add a frame after the current one and select it
                    self.project.frame.insert((selected + 1),tc_frame())
                    tc_display_frames(1)
                    tc_highlight(selected + 1)
                    Set_Working(selected + 1, "N")
        def tc_frame_remove(e):
            """Event triggered when the remove frame button is clicked"""
            remove = 0
            length = 1
            skip = 0
            if len(self.project.frame) == 1:    #If only one item in list, do nothing (can't remove last frame)
                skip = 1
            else:
                selected = self.tc_frame_select_input.GetSelection()
                if selected == -1:      #If nothing selected, don't remove anything
                    skip = 1
                elif selected == (len(self.project.frame) - 1): #If the last item selected, remove and highlight new last
                    self.project.frame.pop(selected)
                    tc_display_frames(1)
                    tc_highlight(selected - 1)
                    Set_Working(selected - 1, "N", 2)
                else:                   #Otherwise, remove the current item and highlight the next one
                    self.project.frame.pop(selected)
                    tc_display_frames(1)
                    tc_highlight(selected)
                    Set_Working(selected, "N", 2)
        def tc_display_frames(e):
            """Displays the array of frames in the frame list"""
            d_frames = []
            for a in range(len(self.project.frame)):
                d_frames.append(gt("F - %i") % (a + 1))
            self.tc_frame_select_input.Set(d_frames)

        
        self.tc_frame_select_input.Bind(wx.EVT_LISTBOX, tc_frame_click, self.tc_frame_select_input)
        self.tc_frame_select_input_add.Bind(wx.EVT_BUTTON, tc_frame_add, self.tc_frame_select_input_add)
        self.tc_frame_select_input_remove.Bind(wx.EVT_BUTTON, tc_frame_remove, self.tc_frame_select_input_remove)
        self.tc_frame_select_input_up.Bind(wx.EVT_BUTTON, tc_frame_up, self.tc_frame_select_input_up)
        self.tc_frame_select_input_down.Bind(wx.EVT_BUTTON, tc_frame_down, self.tc_frame_select_input_down)


        #Bottom panel containing output paths and buttons
        #self.tc_global_box = wx.StaticBox(panel, -1, gt("Global Options:"))               #Box containing the global controls
        #self.tc_global_box_sizer = wx.StaticBoxSizer(self.tc_global_box, wx.HORIZONTAL)
        self.tc_global_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #Output .png selection
        self.tc_global_imageout_path_label = wx.StaticText(panel, -1, gt("Output .png:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_imageout_path = wx.TextCtrl(panel, -1, value="")                      #Path display/edit
        self.tc_global_imageout_path.SetToolTipString(gt("ttOutputPNG"))
        self.tc_global_imageout_filebrowse = wx.Button(panel, -1, label=gt("Browse..."))         #Change output image filename
        #Output .dat selection
        self.tc_global_datout_path_label = wx.StaticText(panel, -1, gt("Output .dat:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_datout_path = wx.TextCtrl(panel, -1, value="")                        #Path display/edit
        self.tc_global_datout_path.SetToolTipString(gt("ttOutputDAT"))
        self.tc_global_datout_filebrowse = wx.Button(panel, -1, label=gt("Browse..."))           #Change output image filename
        #Add controls to the sizer...
        #Add output .png...
        self.tc_global_out_sizer = wx.FlexGridSizer(0,3,0,0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_path_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_path, 0, wx.EXPAND|wx.BOTTOM, 2)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_filebrowse, 0, wx.TOP, 0)
        #Add output .dat...
        self.tc_global_out_sizer.Add(self.tc_global_datout_path_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_datout_path, 0, wx.EXPAND|wx.BOTTOM, 2)
        self.tc_global_out_sizer.Add(self.tc_global_datout_filebrowse, 0, wx.TOP, 0)
        self.tc_global_out_sizer.AddGrowableCol(1)
        self.tc_global_box_sizer.Add(self.tc_global_out_sizer, 1, wx.TOP|wx.EXPAND, 0)
        
        def On_browse_output_dat(e):
            
            """Changes the location of the output dat file"""
            dlg = wx.FileDialog(self, gt("Choose a location to output the dat file"), "", "",
                                "DAT files (*.dat)|*.dat", wx.SAVE)
            dlg.SetFilename("*.dat")
            if dlg.ShowModal() == wx.ID_OK:
                frame.project.output.abs_path_dat = (dlg.GetPath())
                self.tc_global_datout_path.SetValue(frame.project.output.abs_path_dat)

            dlg.Destroy()
            
        def On_browse_output_png(e):
            
            """Changes the location of the output png file"""
            dlg = wx.FileDialog(self, gt("Choose a location to output the png file"), "", "",
                                "PNG files (*.png)|*.png", wx.SAVE)
            dlg.SetFilename("*.png")
            if dlg.ShowModal() == wx.ID_OK:
                frame.project.output.abs_path_png = (dlg.GetPath())
                self.tc_global_imageout_path.SetValue(frame.project.output.abs_path_png)

            dlg.Destroy()

        self.tc_global_imageout_filebrowse.Bind(wx.EVT_BUTTON, On_browse_output_png, self.tc_global_imageout_filebrowse)
        self.tc_global_datout_filebrowse.Bind(wx.EVT_BUTTON, On_browse_output_dat, self.tc_global_datout_filebrowse)


        #self.CreateStatusBar() # A StatusBar in the bottom of the window
        
        # Setting up the menu.
        filemenu= wx.Menu()
        #filemenu.Append(ID_ABOUT, "&About"," Information about this program")
        filemenu.Append(9101, gt("&New Project\tCtrl-N")," Information about this program")
        filemenu.Append(9102, gt("&Open Project\tCtrl-O")," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(9103, gt("&Save Project\tCtrl-S")," Information about this program")
        filemenu.Append(9104, gt("Save Project &As...\tCtrl-A")," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(9105, gt("&Export source\tCtrl-E")," Export project as source files for Makeobj")
        filemenu.Append(9108, gt("Export Dat &file only")," Export dat file for this project")
        filemenu.Append(9106, gt("Ex&port .pak\tCtrl-K")," Export project as .pak file for the game")
        filemenu.Enable(9106, 0)
        filemenu.AppendSeparator()
        filemenu.Append(9107, gt("E&xit\tCtrl-Q")," Terminate the program")

        def menu_file_saveas(e):
            """Event triggered by the save as command in the menu"""
            tc_save_project_dialog()
        def menu_file_save(e):
            if self.project.filename == "":     #Needs addition of some kind of check to see if file has been changed
                menu_file_saveas(1)               #since last save
            else:
                tc_save_project()
        def tc_save_project_dialog():
            dlg = wx.FileDialog(self, gt("Choose a file to save to..."), "", "", "Project files (*.tcp)|*.tcp", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.project.filename = dlg.GetFilename()
                self.project.abs_path = dlg.GetDirectory()
                tc_save_project()
                dlg.Destroy()
                return 1
            else:
                dlg.Destroy()
                return 0
            
            
        def menu_file_new(e):
            """Create a new project"""
            if tc_kill_project() == 1:
                init_project()

        def menu_file_exit(e):
            if tc_kill_project() == 1:
                self.Close()

        def menu_file_open(e):
            """Open the load file dialog"""
            #sys.stderr.write("open")
            if tc_kill_project() == 1:
                dlg = wx.FileDialog(self, gt("Choose a file to load..."), "", "", "Project files (*.tcp)|*.tcp", wx.OPEN)
                if dlg.ShowModal() == wx.ID_OK:
                    tc_load_project((dlg.GetPath()))
                dlg.Destroy()
                
        def init_project():
            """Initialises a new project, resetting all values and cleaning up everything"""
            #Make a new project array
            self.project.frame = []
            self.project.smoke = smoke()
            self.project.output = output()
            self.project.dat = dat()
            self.project.paksize = "64"
            self.project.views = "1"
            self.project.abs_path = ""
            self.project.rel_path = ""
            self.project.filename = ""

            self.project.frame.append(tc_frame())

            #Initialise current working information
            self.current = []
            self.old_f = 0
            self.old_direction = ""

            Set_Working(0, "N", 2)
            Set_Working(self.old_f, "N")
            tc_display_frames(1)
            tc_highlight(0)
            self.first_open = 1

        def tc_kill_project():
            """Function called whenever a project file is potentially going to be closed
            checks if the project file has been saved, and if not prompts to save it
            returns a value based on what happened, 1 is success (continue),
            -1 is failure (abort whatever was being done)"""
            x = 0
            #First determine if there is actually an open project at all
            #Do this by comparing to the output of a "null" project (one which has been initialised
            #in its default state)
            
            
            #Next determine if the project has changed since the last save
            #First, check to see if the project *has* an old save, if it does not
            #Then set changed to be 1, otherwise, compare with the old save as above,
            #If any changes detected, set changed to 1
            project_changed = 1
            #if project_changed == 1:
            dlg = SaveChangesDialog(self, -1, gt("Save changes?"), size=(350, 200),
                                 #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                                 style = wx.DEFAULT_DIALOG_STYLE
                                 )
            a = dlg.ShowModal() # Shows it
            dlg.Destroy() # finally destroy it when finished.

            if a == 1:    #If return is 1, then save project
                if self.project.filename == "":
                    x = tc_save_project_dialog()  #Show the save-as dialogue to get a filename
                else:
                    tc_save_project()   #Otherwise, just save the project...
                    x = 1               #And return ok
            elif a == 0:  #If return is 0, discard changes (i.e. don't save but return 1 for continue anyway)
                x = 1
            else: #Otherwise, cancel whatever was being done
                x = -1      #And return cancel code
                
            return x


        
        def tc_save_project():
            file = open((self.project.abs_path + "\\" + self.project.filename), "w")
            save = self.project
            bckN = []
            bckE = []
            bckS = []
            bckW = []
            for i in range(len(save.frame)):        #Set all image info to nothing, as image info doesn't need saving here
                bckN.append(save.frame[i].north.image)
                save.frame[i].north.image = 0
                bckE.append(save.frame[i].north.image)
                save.frame[i].east.image = 0
                bckS.append(save.frame[i].north.image)
                save.frame[i].south.image = 0
                bckW.append(save.frame[i].north.image)
                save.frame[i].west.image = 0

            pickle.dump(save, file)         #Dump all components to the file in order
            pickle.dump(save.frame, file)
            pickle.dump(save.smoke, file)
            pickle.dump(save.output, file)
            pickle.dump(save.dat, file)
            pickle.dump(save.dat.inputgoods, file)
            pickle.dump(save.dat.outputgoods, file)
            pickle.dump(save.dat.climates, file)
            file.close()
            
            for i in range(len(save.frame)):        #Return all image info to what it was before
                save.frame[i].north.image = bckN[i]
                bckN[i] = 0
                save.frame[i].east.image = bckE[i]
                bckE[i] = 0
                save.frame[i].south.image = bckS[i]
                bckS[i] = 0
                save.frame[i].west.image = bckW[i]
                bckW[i] = 0

        def tc_load_project(filename):
            """Loads a saved project from memory"""
            file = open(filename, "r")              
            self.project = pickle.load(file)
            self.project.frame = pickle.load(file)
            self.project.smoke = pickle.load(file)
            self.project.output = pickle.load(file)
            self.project.dat = pickle.load(file)
            self.project.dat.inputgoods = pickle.load(file)
            self.project.dat.outputgoods = pickle.load(file)
            self.project.dat.climates = pickle.load(file)

            file.close()

            #self.current.filename

            tc_display_frames(1)    #Display the frames from the new project in the frames list
            Set_Working(0, "N", 2)  #Set the working frame to the first one of the project, North direction
                                    #with flag set to 2, so that new current is initialised
            tc_highlight(0)
            self.tc_global_imageout_path.SetValue(frame.project.output.abs_path_png)
            self.tc_global_datout_path.SetValue(frame.project.output.abs_path_dat)
            self.first_open = 0

        def menu_file_export_source(e):
            Export()
        def menu_file_export_datonly(e):
            Export(2)

        self.Bind(wx.EVT_MENU, menu_file_new, id=9101)
        self.Bind(wx.EVT_MENU, menu_file_open, id=9102)
        self.Bind(wx.EVT_MENU, menu_file_save, id=9103)
        self.Bind(wx.EVT_MENU, menu_file_saveas, id=9104)
        self.Bind(wx.EVT_MENU, menu_file_export_source, id=9105)
        self.Bind(wx.EVT_MENU, menu_file_export_datonly, id=9108)
        #self.Bind(wx.EVT_MENU, self.menu_file_export_pak, id=9106)
        self.Bind(wx.EVT_MENU, menu_file_exit, id=9107)

        recentmenu= wx.Menu()
        
        recentmenu.Append(-1, "Document #1"," Information about this program")
        recentmenu.Append(-1, "Document #2"," Information about this program")
        recentmenu.Append(-1, "Document #3"," Information about this program")
        recentmenu.Append(-1, "Document #4"," Information about this program")
        recentmenu.AppendSeparator()
        recentmenu.Append(-1, "&Clear this list"," Clear the cache of recent documents")

        toolsmenu= wx.Menu()
        toolsmenu.Append(9301, gt(".&dat file options\tCtrl-D")," Edit .dat file options")
        toolsmenu.Append(9302, gt("&Smoke options\tCtrl-M")," Add or edit a smoke object associated with this project")
        toolsmenu.Append(9304, gt("&Climates\tCtrl-C")," Change the climates this building should appear in")
        toolsmenu.Enable(9302, 0)
        toolsmenu.AppendSeparator()
        toolsmenu.Append(9303, gt("&Preferences\tCtrl-P")," Change program preferences")
        #toolsmenu.Enable(9303, 0)

        def menu_tools_dat(e):
            """Open the dat edit dialog"""
            dlg = DatDialog(self, -1, gt("Edit .dat information"), size=(-1, -1),
                            style=wx.DEFAULT_DIALOG_STYLE)
            dlg.ShowModal()
            dlg.Destroy()

        def menu_climates_select(e):
            """Open the dat edit dialog"""
            dlg = ClimateDialog(self, -1, gt("Choose climates"), size=(-1, -1),
                            style=wx.DEFAULT_DIALOG_STYLE)
            #dlg.ShowModal()
            dlg.Destroy()

        def menu_language_select(e):
            dlg = SelectLanguageDialog(self, -1, gt("Select Language"), size=(350, 200),
                                 #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                                 style = wx.DEFAULT_DIALOG_STYLE
                                 )
            a = dlg.ShowModal() # Shows it
            dlg.Destroy() # finally destroy it when finished.
            
        def menu_preferences(e):
            dlg = PreferencesDialog(self, -1, gt("Preferences"), size=(-1, -1),
                                 #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                                 style = wx.DEFAULT_DIALOG_STYLE
                                 )
            a = dlg.ShowModal() # Shows it & collects return information in "a"
            dlg.Destroy() # finally destroy it when finished.

        self.Bind(wx.EVT_MENU, menu_tools_dat, id=9301)
        self.Bind(wx.EVT_MENU, menu_climates_select, id=9304)
        self.Bind(wx.EVT_MENU, menu_language_select, id=9302)
        self.Bind(wx.EVT_MENU, menu_preferences, id=9303)


        helpmenu= wx.Menu()
        helpmenu.Append(9501, gt("Help Topics\tCtrl-H"),"")
        helpmenu.Enable(9501, 0)
        helpmenu.AppendSeparator()
        helpmenu.Append(9502, gt("&About TileCutter")," Information about this program")

        def menu_help_about(e):
            dlg = AboutDialog(self, -1, gt("About TileCutter"), size=(350, 200),
                             #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                             style = wx.DEFAULT_DIALOG_STYLE
                             )
            dlg.ShowModal() # Shows it
            dlg.Destroy() # finally destroy it when finished.

        self.Bind(wx.EVT_MENU, menu_help_about, id=9502)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,gt("&File")) # Adding the "filemenu" to the MenuBar
        menuBar.Append(recentmenu,gt("&Recent")) # Adding the "recentmenu" to the MenuBar
        menuBar.Append(toolsmenu,gt("&Tools")) # Adding the "toolsmenu" to the MenuBar
        menuBar.Append(helpmenu,gt("&Help")) # Adding the "helpmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        menuBar.EnableTop(1, 0)


        # Image panel
        
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.top_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_box_sizer_right = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer.Add(wx.StaticLine(panel,-1,(-1,-1),(100,-1),style=wx.LI_HORIZONTAL|wx.EXPAND),0,wx.BOTTOM|wx.EXPAND,border=5)

        self.top_box_sizer.Add(self.tc_frame_box_sizer,1,wx.EXPAND|wx.RIGHT, 4)
        self.top_box_sizer_right.Add(self.tc_size_box_sizer,0,wx.ALL,border=0)
        self.top_box_sizer_right.Add(self.tc_frame_select_box_sizer,1,wx.EXPAND|wx.ALL,border=0)
        self.top_box_sizer.Add(self.top_box_sizer_right,0,wx.EXPAND)
        #self.sizer.Add(panel,1,wx.EXPAND,border=0)
        self.sizer.Add(self.top_box_sizer,1,wx.LEFT|wx.RIGHT|wx.EXPAND,border=2)
        
        self.sizer.Add(wx.StaticLine(panel,-1,(-1,-1),(100,-1),style=wx.LI_HORIZONTAL|wx.EXPAND),0,wx.TOP|wx.EXPAND,border=5)

        self.sizer.Add(self.tc_global_box_sizer,0,wx.ALL|wx.EXPAND,border=5)

        #Layout sizers
        panel.SetSizer(self.sizer)
        panel.SetAutoLayout(1)
        panel.Layout()



        #On first loading the program
        Set_Working(0, "N", 1)
        tc_display_frames(1)            #Show whatever frames there may be on loading...
        tc_highlight(0)
        self.Show(True)
    
    def tc_project_init(e):
        """Initiator function"""
        frame.Set_Working(0, "N", 2)
        frame.Set_Working(self.old_f, "N")


    def OnExit(self,e):
        self.Close(True)  # Close the frame.


#----------------------------------------------Select language Dialog----------------------------------------------------

class SelectLanguageDialog(wx.Dialog):
    """Displays a list of languages available to the program for the user to choose from,
    returns a two-letter language code from the selection"""
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE, firstrun=0):
        
        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI dialog using the Create
        # method.
        pre = wx.PreDialog()
#        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)
        
        self.options = []
        lan = ""
        if os.access("language/", os.F_OK):
            listing = []
            listing = os.listdir("language/")  #Get a list of the contents of the languages subfolder
            for i in range(len(listing)):
                if listing[i][-4:] == ".tab":
                    if listing[i][:3] == "tc-":
                        self.options.append(listing[i][3:5])     #Add the language code to the list of ones to display
        else:
            sys.stderr.write("ERROR: Unable to open the language directory - please check your installation!")
            #return -1

        # Now continue with the normal construction of the dialog
        # contents
        NumCols = 2
        if len(self.options) > 5:
            NumCols = 4
        elif len(self.options) > 10:
            NumCols = 6
        self.sizer = wx.FlexGridSizer(0, NumCols, 0, 0)

        self.lan_images = []
        self.lan_options = []
        #lan_texts = []
        if firstrun != 1:
            self.text2 = wx.StaticText(self, -1, gt("Note: You must restart the program for your changes to take effect!"))
            #text2.Wrap(300)

        def on_toggle(e):
            a = e.GetEventObject()
            for i in range(len(self.options)):
                self.lan_options[i].SetValue(0)
            a.SetValue(1)

        for i in range(len(self.options)):
            if os.access("language/tc-" + self.options[i] + ".png", os.F_OK):
                im = wx.Image("language/tc-" + self.options[i] + ".png", wx.BITMAP_TYPE_PNG)
                bmp = im.ConvertToBitmap()
            else:
                if os.access("language/tc-xx.png", os.F_OK):
                    im = wx.Image("language/tc-xx.png", wx.BITMAP_TYPE_PNG)
                    bmp = im.ConvertToBitmap()
                else:
                    sys.stderr.write("ERROR: Unable to open the default language image - please check your installation!")
                    #return -1
                    
            file = open(("language/tc-" + self.options[i] + ".tab"), "r")
            p = file.readline()
            if p[-1] == "\n":
                p = p[:-1]
            q = unicode(p, "utf-8")
            file.close

            self.lan_images.append(wx.StaticBitmap(self, -1, bmp, (-1,-1), (-1,-1)))
            self.lan_options.append(wx.RadioButton(self, -1, q, (-1,-1), (-1,-1), style=wx.RB_SINGLE))
            self.sizer.Add(self.lan_images[i], 0, wx.ALIGN_CENTER|wx.TOP, 2)
            self.sizer.Add(self.lan_options[i], 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.LEFT, 2)
            self.lan_options[i].Bind(wx.EVT_RADIOBUTTON, on_toggle, self.lan_options[i])


        def OnClickOk(e):
            if firstrun:
                for i in range(len(self.options)):
                    if self.lan_options[i].GetValue() == 1:
                        lan = self.options[i]
                        fsock.write("language 1: " + lan)
                parent.lang = lan
                self.EndModal(1)
            else:
                for i in range(len(self.options)):
                    if self.lan_options[i].GetValue() == 1:
                        lan = self.options[i]
                Write_Config(lan)
                self.EndModal(1)

        def OnClickCancel(e):
            self.EndModal(0)
            
        if firstrun:
            self.ok_button = wx.Button(self, -1, label="&Select")
        else:
            self.ok_button = wx.Button(self, -1, label=gt("Select"))
            self.cancel_button = wx.Button(self, -1, label=gt("Cancel"))
            self.cancel_button.Bind(wx.EVT_BUTTON, OnClickCancel, self.cancel_button)


        self.ok_button.Bind(wx.EVT_BUTTON, OnClickOk, self.ok_button)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2 = wx.BoxSizer(wx.VERTICAL)

        if firstrun != 1:
            self.sizer2.Add(self.text2, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        self.sizer2.Add(self.sizer, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        
        self.line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        self.sizer2.Add(self.line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP|wx.LEFT, 5)

        self.button_sizer.Add(self.ok_button, 0, wx.ALIGN_RIGHT)

        if firstrun != 1:
            self.button_sizer.Add(self.cancel_button, 0, wx.ALIGN_RIGHT|wx.LEFT, 5)

        self.sizer2.Add(self.button_sizer, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

        self.ok_button.SetDefault()
        self.SetSizer(self.sizer2)
        self.sizer2.Fit(self)
        


#----------------------------------------------Initialisation Window----------------------------------------------------

class InitWindow(wx.Frame):
    """This window is shown first if this is the first time running the program,
    it allows setting of some critical options"""
    lang = ""
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), (500,500),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        dlg = SelectLanguageDialog(self, -1, "Select Language", size=(350, 200),
                                    #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                                    style = wx.DEFAULT_DIALOG_STYLE, firstrun=1)
        
        a = dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.
        firstrun = 0
        fsock.write("\nlanguage 3: " + self.lang)

        Write_Config(self.lang)
        #translation = Load_Translation(self.lang)
        #language = self.lang
        self.Close()



language, firstrun = Read_Config()

app = wx.App()

icon = wx.Icon("tilecutter.ico", wx.BITMAP_TYPE_ICO, 16, 16)

if firstrun == 1:
    init_window = InitWindow(None, -1, "TileCutter initialisation")
    init_window.SetIcon(icon)
    language, firstrun = Read_Config()


translation = Load_Translation(language)

fsock.write("\nlanguage 4: " + language)

choicelist_paksize = ["16","32","48","64","80","96","112","128","144","160","176","192","208","224","240"]
choicelist_dims = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
choicelist_dims_z = ["1","2","3","4"]
choicelist_anim = ["0",]
tc_month_choices = ["",gt("January"),gt("Febuary"),gt("March"),gt("April"),gt("May"),gt("June"),
                    gt("July"),gt("August"),gt("September"),gt("October"),gt("November"),gt("December")]
tc_type_choices = ["", gt("carstop"),gt("busstop"),gt("station"),gt("monorailstop"),gt("harbour"),gt("wharf"),gt("airport"),
                   gt("hall"),gt("post"),gt("shed"),
                   gt("res"),gt("com"),gt("ind"),
                   gt("any"),gt("misc"),
                   gt("mon"),gt("cur"),gt("tow"),gt("hq")]

frame = MainWindow(None, -1, "TileCutter v." + VERSION_NUMBER)

frame.SetIcon(icon)

app.MainLoop()



