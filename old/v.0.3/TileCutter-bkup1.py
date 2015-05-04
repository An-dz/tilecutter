import Image, ImageDraw
import ImageWin
import os
import wx
import wx.lib.masked as masked
import wx.lib.scrolledpanel as scrolled
import wx.lib.hyperlink as hl
import sys
import pickle
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
VERSION_NUMBER = "0.3a"

#sys.stderr.write("a")


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

translation = Load_Translation("xx")
choicelist_paksize = ["16","32","48","64","80","96","112","128","144","160","176","192","208","224","240"]
choicelist_dims = [gt("auto"),"1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
choicelist_dims_z = [gt("auto"),"1","2","3","4"]
choicelist_anim = ["0",]
tc_month_choices = [gt("January"),gt("February"),gt("March"),gt("April"),gt("May"),gt("June"),
                    gt("July"),gt("August"),gt("September"),gt("October"),gt("November"),gt("December")]



class frame_props:
    """All the properties of a frame, created as a subclass of frame"""
    abs_path = ""
    rel_path = ""
    filename = ""
    image = 0
    xdims = -1
    ydims = -1
    zdims = -1
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
    rel_path_dat = ""
    abs_path_png = ""
    rel_path_png = ""
    path_dat_to_png = ""
    dat_filename = ""
    png_filename = ""
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
    in_month = ""
    in_year = ""
    out_month = ""
    out_year = ""
    level = ""
    noinfo = 0
    nocon = 0
    #Building
    type = ""
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
    inputgoods = []
    outputgoods = []
    #Additional options
    add = ""
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
    dat =  dat()
    paksize = "64"
    views = "1"
    abs_path = ""
    rel_path = ""
    filename = ""
        
#project = tc.project() #Project is the overall container for all project data, it contains several other types of object
                        #defined in the tc class above. Loading/saving a project involves loading or saving a project
                        #object (through pickling).
                        #This is now initialised in the main window init function


def LoadPal(palname="simud80.pal"):
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


def DrawArrow(direction):
    """Draws an arrow in the specified direction for use on buttons
    valid values: up, down, left, right"""
    if direction == "up":
        b = wx.EmptyImage(7, 4)
        for i in range(3):
            for j in range((3 - i)):
                b.SetRGB(i,j,255,255,255)
                b.SetRGB((6 - i),j,255,255,255)
    if direction == "down":
        b = wx.EmptyImage(7, 4)
        for i in range(3):
            for j in range((3 - i)):
                b.SetRGB(i,(3 - j),255,255,255)
                b.SetRGB((6 - i),(3 - j),255,255,255)
    if direction == "left":
        b = wx.EmptyImage(4, 7)
        for i in range(6):
            for j in range((3 - i)):
                b.SetRGB(i,j,255,255,255)
                b.SetRGB(i,(6 - j),255,255,255)
    if direction == "right":
        b = wx.EmptyImage(4, 7)
        for i in range(6):
            for j in range((3 - i)):
                b.SetRGB((3 - i),j,255,255,255)
                b.SetRGB((3 - i),(6 - j),255,255,255)
    if direction == "empty":
        b = wx.EmptyImage(1, 1)
        b.SetRGB(0,0,233,255,255)
    b.SetMaskFromImage(b,255,255,255)        
    bmp = b.ConvertToBitmap()
    return bmp

def ShowImage(showimg, b):
    """Shows the image in the display port: (image to display, port to use)"""
    outimage = wx.EmptyImage(showimg.size[0], showimg.size[1])  #create a new wx.image
    outimage.SetData(showimg.convert("RGB").tostring())     #convert PIL image to RGB bitmap, then append into new wx.image
    outimage = outimage.ConvertToBitmap()   #finally convert to wx.bitmap for display

    frame.tc_display_panel.DrawBitmap(outimage)


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

    #current.xdims = xd
    #current.ydims = yd     #With these enabled, auto will appear on the comboboxes
    #current.zdims = zd
    
    current.xdims = xdn
    current.ydims = ydn     #With these enabled, auto will not appear on the comboboxes
    current.zdims = zdn

    current.offsetx = xoff
    current.offsety = yoff
    
    #sys.stderr.write("X: " + str(current.xdims) + " Y: " + str(current.ydims) + " Z: " + str(current.zdims)
                     #+ " OffX: " + str(current.offsetx) + " OffY: " + str(current.offsety))
    
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
        draw.rectangle(((0,0),(p,(p/2))), fill=(233,255,255))                               #Draw top box
        draw.polygon([(0, p/2), (p/2, p/2), (0, p/2 + p/4)], fill=(231,255,255))            #Draw top left triangle
        draw.polygon([(p/2-1, p/2), (p-1, p/2), (p-1, p/2 + p/4)], fill=(231,255,255))      #Draw top right triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 2:
        draw.rectangle(((p/2, 0),(p, p/2)), fill=(233,255,255))                             #Draw top box (right)
        draw.polygon([(p/2-1, p/2), (p-1, p/2), (p-1, p/2 + p/4)], fill=(231,255,255))      #Draw top right triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 3:
        draw.rectangle(((0,0),(p/2-1, p/2)), fill=(233,255,255))                              #Draw top box (left)
        draw.polygon([(0, p/2), (p/2, p/2), (0, p/2 + p/4)], fill=(231,255,255))            #Draw top left triangle
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    elif mask == 4:
        draw.polygon([(0, p/2 + p/4+1), (0, p+1), (p/2, p+1)], fill=(231,255,255))          #Draw bottom left triangle
        draw.polygon([(p/2-1, p+1), (p+1, p+1), (p+1, p/2 + p/4)], fill=(231,255,255))      #Draw bottom right triangle
    del draw

def MakeMatrix(num_frames, zdims, xdims, ydims):
    """Makes a standard cutting matrix for a building view with auto-generated masking - this is a temporary function"""
    matrix = []
    for f in range(num_frames):                     #For each frame in this direction
        for z in range(zdims):                          #For each height level
            for x in range(xdims):                          #For each x value
                for y in range(ydims):                          #For each y value
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

def Export(makepak=0):
    """Exports a .png and .dat of the project, optionally runs makeobj to create a pak file"""
    north_matrix = []
    east_matrix = []
    south_matrix = []
    west_matrix = []    #Create lists for the direction matrixes
    #Next, use values of the project to generate the matrix tuples
    #xdims = frame.project.frame[0].north.xdims
    #ydims = frame.project.frame[0].north.ydims
    #zdims = frame.project.frame[0].north.zdims
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
    datfile = open("test.dat", "w")
    
    datfile.write("#\n# File created with TileCutter version " + VERSION_NUMBER +
                  "\n# For more information see http://simutrans.entropy.me.uk/tilecutter/\n#\n")
    if frame.project.dat.obj != 2:
        if frame.project.dat.obj == 0:
            datfile.write("Obj=building\n")
        else:
            datfile.write("Obj=factory\n")
        datfile.write("name=" + frame.project.dat.name + "\n")
        datfile.write("copyright=" + frame.project.dat.copyright + "\n")
        datfile.write("intro_year=" + frame.project.dat.in_year + "\n")
        
        
        datfile.write("intro_month=" + str(tc_month_choices.index(frame.project.dat.in_month) + 1) + "\n")
        datfile.write("retire_year=" + frame.project.dat.out_year + "\n")
        datfile.write("retire_month=" + str(tc_month_choices.index(frame.project.dat.out_month) + 1) + "\n")
        datfile.write("level=" + frame.project.dat.level + "\n")

        datfile.write("NoInfo=" + str(int(frame.project.dat.noinfo)) + "\n")
        datfile.write("NoConstruction=" + str(int(frame.project.dat.nocon)) + "\n")
        
        if frame.project.dat.obj == 0:
            #Write a building dat file
            type = frame.project.dat.type
            #Write types...
            if type == "":
                datfile.write("type=" + frame.project.dat.type + "\n")
            if type == gt("Carstop"):
                datfile.write("type=carstop\n")
            if type == gt("Busstop"):
                datfile.write("type=busstop\n")
            if type == gt("Station"):
                datfile.write("type=station\n")
            if type == gt("Monorailstop"):
                datfile.write("type=monorailstop\n")
            if type == gt("Harbour"):
                datfile.write("type=harbour\n")
            if type == gt("Wharf"):
                datfile.write("type=wharf\n")
            if type == gt("Airport"):
                datfile.write("type=airport\n")
            if type == gt("hall"):
                datfile.write("type=hall\n")
            if type == gt("post"):
                datfile.write("type=post\n")
            if type == gt("shed"):
                datfile.write("type=shed\n")

            #Write other stuff for stations...
            if type == gt("Carstop") or type == gt("Busstop") or type == gt("Station") or type == gt("Monorailstop") or type == gt("Harbour") or type == gt("Wharf") or type == gt("Airport") or type == gt("hall") or type == gt("post") or type == gt("shed"):
                datfile.write("extension_building=" + str(int(frame.project.dat.extension)) + "\n")
                datfile.write("enables_pax=" + str(int(frame.project.dat.pax)) + "\n")
                datfile.write("enables_post=" + str(int(frame.project.dat.post)) + "\n")
                datfile.write("enables_ware=" + str(int(frame.project.dat.ware)) + "\n")

            if type == gt("Residential"):
                datfile.write("type=res\n")
            if type == gt("Commercial"):
                datfile.write("type=com\n")
            if type == gt("Industrial"):
                datfile.write("type=ind\n")

            if type == gt("any"):
                datfile.write("type=any\n")
            if type == gt("misc"):
                datfile.write("type=misc\n")

            #Write other stuff for Monument/Curiosity/Town Hall
            if type == gt("Monument"):
                datfile.write("type=mon\n")
                datfile.write("chance=" + frame.project.dat.chance_b + "\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
            if type == gt("Curiosity"):
                datfile.write("type=cur\n")
                datfile.write("location=" + frame.project.dat.location_b + "\n")
                datfile.write("chance=" + frame.project.dat.chance_b + "\n")
            if type == gt("Town Hall"):
                datfile.write("type=tow\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
            if type == gt("Headquarters"):
                datfile.write("type=hq\n")
                datfile.write("build_time=" + frame.project.dat.build_time + "\n")
                
        else:
            #Write a factory dat file
            datfile.write("Location=" + frame.project.dat.location_f + "\n")
            datfile.write("chance=" + frame.project.dat.chance_f + "\n")
            datfile.write("Productivity=" + frame.project.dat.prod + "\n")
            datfile.write("Range=" + frame.project.dat.range + "\n")
            datfile.write("MapColor=" + frame.project.dat.colour + "\n")
            #Do input/output goods next...
            for a in range(len(frame.project.dat.inputgoods)):
                datfile.write("InputGood[" + str(a) + "]=" + frame.project.dat.inputgoods[a].name + "\n")
                datfile.write("InputCapacity[" + str(a) + "]=" + frame.project.dat.inputgoods[a].capacity + "\n")
                datfile.write("InputFactor[" + str(a) + "]=" + frame.project.dat.inputgoods[a].factor + "\n")
                datfile.write("InputSupplier[" + str(a) + "]=" + frame.project.dat.inputgoods[a].supplier + "\n")
            for a in range(len(frame.project.dat.outputgoods)):
                datfile.write("OutputGood[" + str(a) + "]=" + frame.project.dat.outputgoods[a].name + "\n")
                datfile.write("OutputCapacity[" + str(a) + "]=" + frame.project.dat.outputgoods[a].capacity + "\n")
                datfile.write("OutputFactor[" + str(a) + "]=" + frame.project.dat.outputgoods[a].factor + "\n")

            #Needs smoke stuff added here when smoke implemented!!

        datfile.write(frame.project.dat.add + "\n")
    else:
        #Write a misc dat file
        datfile.write(frame.project.dat.add + "\n")
    
    #Make an image to output to
    imout = NewImage(((width_out * int(frame.project.paksize)), (height_out * int(frame.project.paksize))))
    
    #Now that we have a cutting matrix, we can proceed to the cutting routine
    views_int = int(frame.project.views)

    #Write dims information to .dat file...
    datfile.write("Dims=" + str(xdimsN) + "," + str(ydimsN) + "," + frame.project.views + "\n")

    
    for f in range(num_frames):
        
        if views_int >= 1:     #If one direction
            #For north direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].north, int(frame.project.paksize), (xdimsN, ydimsN, zdimsN),
                         (frame.project.frame[f].north.offsetx, frame.project.frame[f].north.offsety), showgrid=0)

            for i in range((f * len(north_matrix)), ((f + 1) * len(north_matrix))):     #For all the tiles in a given frame
            
                CopyXY(int(frame.project.paksize), im, imout, (north_matrix[i][2], north_matrix[i][3], north_matrix[i][1]),
                        ((north_matrix[i][3]), (north_matrix[i][2] + (xdimsN * north_matrix[i][1]))),
                       (xdimsN, ydimsN, zdimsN), (frame.project.frame[f].north.offsetx, frame.project.frame[f].north.offsety),
                       north_matrix[i][4])
        if views_int >= 2:                              #Do east as well
            #For east direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].east, int(frame.project.paksize), (xdimsE, ydimsE, zdimsE),
                         (frame.project.frame[f].east.offsetx, frame.project.frame[f].east.offsety), showgrid=0)

            for i in range((f * len(east_matrix)), ((f + 1) * len(east_matrix))):     #For all the tiles in a given frame
            
                CopyXY(int(frame.project.paksize), im, imout, (east_matrix[i][2], east_matrix[i][3], east_matrix[i][1]),
                        ((east_matrix[i][3] + (ydimsN)), (east_matrix[i][2] + (xdimsE * east_matrix[i][1]))),
                       (xdimsE, ydimsE, zdimsE), (frame.project.frame[f].east.offsetx, frame.project.frame[f].east.offsety),
                       east_matrix[i][4])
        if views_int == 4:                              #Do south and west also
            #For south direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].south, int(frame.project.paksize), (xdimsS, ydimsS, zdimsS),
                         (frame.project.frame[f].south.offsetx, frame.project.frame[f].south.offsety), showgrid=0)

            for i in range((f * len(south_matrix)), ((f + 1) * len(south_matrix))):     #For all the tiles in a given frame
            
                CopyXY(int(frame.project.paksize), im, imout, (south_matrix[i][2], south_matrix[i][3], south_matrix[i][1]),
                        ((south_matrix[i][3] + (ydimsN + ydimsE)), (south_matrix[i][2] + (xdimsS * south_matrix[i][1]))),
                       (xdimsS, ydimsS, zdimsS), (frame.project.frame[f].south.offsetx, frame.project.frame[f].south.offsety),
                       south_matrix[i][4])
            #For west direction, produce an image to cut from using the Analyse function
            im = Analyse(frame.project.frame[f].west, int(frame.project.paksize), (xdimsW, ydimsW, zdimsW),
                         (frame.project.frame[f].west.offsetx, frame.project.frame[f].west.offsety), showgrid=0)

            for i in range((f * len(west_matrix)), ((f + 1) * len(west_matrix))):     #For all the tiles in a given frame
            
                CopyXY(int(frame.project.paksize), im, imout, (west_matrix[i][2], west_matrix[i][3], west_matrix[i][1]),
                        ((west_matrix[i][3] + (ydimsN + ydimsE + ydimsS)), (west_matrix[i][2] + (xdimsW * west_matrix[i][1]))),
                       (xdimsW, ydimsW, zdimsW), (frame.project.frame[f].west.offsetx, frame.project.frame[f].west.offsety),
                       west_matrix[i][4])

    imout.save("output-test.png")

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

        self.tc_colour_box = wx.StaticBox(self, -1, "Pick a colour:")   #Box containing all global options

        self.tc_colour_sizer = wx.StaticBoxSizer(self.tc_colour_box)    #Sizer for the static box ^
        self.tc_colour_sizer2 =  wx.BoxSizer(wx.VERTICAL)               #Container for control_sizer and sizer_flex
        self.tc_colour_control_sizer = wx.BoxSizer(wx.HORIZONTAL)       #Sizer for the control buttons at the bottom
        self.tc_colour_sizer_flex = wx.FlexGridSizer(16,16,0,0)         #Flex grid for the palette colour boxes

        self.tc_colour_display = wx.StaticText(self, -1, "", (-1,-1),(50,40),
                                               wx.SIMPLE_BORDER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL
                                               )        #Displays the currently selected palette colour
        self.tc_colour_sel_button = wx.Button(self, wx.ID_OK, label="Use this colour")  #OK button
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



#----------------------------------------------Dat File edit Dialogue----------------------------------------------------

class DatDialog(wx.Dialog):
    def __init__(self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        tc_obj_choices = [gt("Building"), gt("Factory"), gt("Other")]
        tc_type_choices = [gt("Carstop"),gt("Busstop"),gt("Station"),gt("Monorailstop"),gt("Harbour"),gt("Wharf"),gt("Airport"),
                           gt("Monument"),gt("Curiosity"),gt("Town Hall"),gt("Residential"),gt("Commercial"),gt("Industrial"),
                           gt("Headquarters"),gt("hall"),gt("post"),gt("shed"),gt("any"),gt("misc")]
        #Global options--------------------------------------------------------------------------------------------------
        self.tc_global_box = wx.StaticBox(self, -1, gt("Global Options:"))   #Box containing all global options
        self.tc_obj = wx.RadioBox(self, 5500,  gt("Object Type:"), (-1,-1),(-1,-1), tc_obj_choices, 1, style=wx.RA_SPECIFY_ROWS)
        
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
            else:           #Disable all elements of main panel for "other" option
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


        wx.EVT_RADIOBOX(self, 5500, On_tc_obj)

        self.tc_name_label = wx.StaticText(self, -1, gt("Name:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_name = wx.TextCtrl(self, 5501, value="", size=(114,-1))                                             #Name
        self.tc_copyright_label = wx.StaticText(self, -1, gt("Copyright:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_copyright = wx.TextCtrl(self, 5502, value="", size=(114,-1))                                        #Copyright
        self.tc_intro_year_label = wx.StaticText(self, -1, gt("Introduced:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_intro_month = wx.ComboBox(self, 5504, "", (-1, -1), (76, -1), tc_month_choices, wx.CB_READONLY)     #Intro month
        self.tc_intro_year = wx.TextCtrl(self, 5503, value="", size=(36,-1))                                        #Intro Year
        self.tc_retire_year_label = wx.StaticText(self, -1, gt("Retires:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_retire_month = wx.ComboBox(self, 5506, "", (-1, -1), (76, -1), tc_month_choices, wx.CB_READONLY)    #Retire month
        self.tc_retire_year = wx.TextCtrl(self, 5505, value="", size=(36,-1))                                       #Retire year
        self.tc_level_label = wx.StaticText(self, -1, gt("Level:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_level = wx.TextCtrl(self, 5507, value="")                                                           #Level
        self.tc_noinfo = wx.CheckBox(self, -1, gt("No info"))                                                           #Do not show factory info
        self.tc_noconstruction = wx.CheckBox(self, -1, gt("No Construction"))                                           #No construction site
        


        self.tc_global_sizer = wx.StaticBoxSizer(self.tc_global_box, wx.HORIZONTAL)
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

        self.tc_global_sizer_flex.Add(self.tc_noinfo, 0, wx.TOP|wx.LEFT, 4)
        self.tc_global_sizer_flex.Add(self.tc_noconstruction, 0, wx.TOP|wx.LEFT, 4)


        self.tc_global_sizer.Add(self.tc_global_sizer_flex, 0, wx.TOP|wx.LEFT, 0)





        #Building options (ID order 5700+)--------------------------------------------------------------------------------------------------
        self.tc_building_box = wx.StaticBox(self, -1, gt("Building Options:"))   #Box containing all building options

        self.tc_type_label = wx.StaticText(self, -1, gt("Type:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_type = wx.ComboBox(self, 5700, "", (-1, -1), (-1, -1), tc_type_choices, wx.CB_READONLY)         #Type of building

        def On_tc_type(e):
            if self.tc_type.GetValue() == "":
                DisableBuilding(0)      #Disable all
            #Stations
            elif self.tc_type.GetValue() == gt("Carstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Busstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Station"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Monorailstop"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Harbour"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Wharf"):
                DisableBuilding(1)      #Disable for station
            elif self.tc_type.GetValue() == gt("Airport"):
                DisableBuilding(1)      #Disable for station
            #Monument/Curiosity/Town Hall
            elif self.tc_type.GetValue() == gt("Monument"):
                DisableBuilding(2)      #Disable for monument (same as curiosity except location)
            elif self.tc_type.GetValue() == gt("Curiosity"):
                DisableBuilding(3)      #Disable for curiosity (only thing which uses location)
            elif self.tc_type.GetValue() == gt("Town Hall"):
                DisableBuilding(4)      #Disable for town hall (only build time)
            #Res/Com/Ind (disable all)
            elif self.tc_type.GetValue() == gt("Residential"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("Commercial"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("Industrial"):
                DisableBuilding(0)      #Disable all
            elif self.tc_type.GetValue() == gt("Headquarters"):
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
        
        self.tc_locationbui_label = wx.StaticText(self, -1, gt("Location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_locationbui = wx.ComboBox(self, 5702, "", (-1, -1), (-1, -1), ["Land","City"], wx.CB_READONLY)  #Location (building)
        self.tc_chancebui_label = wx.StaticText(self, -1, gt("Chance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_chancebui = wx.TextCtrl(self, 5703, value="", size=(50,-1))                                     #Chance (building)
        self.tc_build_time_label = wx.StaticText(self, -1, gt("Build Time:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_build_time = wx.TextCtrl(self, 5704, value="", size=(50,-1))                                    #Build time
        self.tc_extension_label = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_extension = wx.CheckBox(self, -1, gt("Is Extension Building"))                                      #Extension building flag
        self.tc_enables_label = wx.StaticText(self, -1, gt("Enables:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_enables_pax = wx.CheckBox(self, -1, gt("Passengers"))                                               #Enables passengers
        self.tc_enables_post = wx.CheckBox(self, -1, gt("Mail"))                                                    #Enables mail
        self.tc_enables_ware = wx.CheckBox(self, -1, gt("Goods"))                                                   #Enables goods

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


        self.tc_locationfac_label = wx.StaticText(self, -1, gt("Location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_locationfac = wx.ComboBox(self, 5600, "", (-1, -1), (-1, -1), ["Land","City","Water"], wx.CB_READONLY)  #Location (factory)
        self.tc_chancefac_label = wx.StaticText(self, -1, gt("Chance:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_chancefac = masked.TextCtrl(self, 5601, value="0", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,100)
                                            )                                                                           #Chance (factory)
        self.tc_productivity_label = wx.StaticText(self, -1, gt("Productivity:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_productivity = masked.TextCtrl(self, 5602, value="0", size=(44,-1),
                                            formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                            )                                                                           #Productivity
        self.tc_range_label = wx.StaticText(self, -1, "±", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_range = masked.TextCtrl(self, 5603, value="0", size=(44,-1),
                                        formatcodes="S",fillChar=" ", mask="#####", validRequired=1, validRange=(0,65535)
                                        )                                                                               #Range
        self.tc_mapcolour_label = wx.StaticText(self, -1, gt("Map Colour:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_mapcolour = masked.TextCtrl(self, 5604, value="0", size=(50,-1),
                                            formatcodes="S",fillChar=" ", mask="###", validRequired=1, validRange=(0,255)
                                            )                                                                           #Map Colour Entry
        self.tc_mapcolour_display = wx.StaticText(self, 5605, "", (-1,-1),(30,21),wx.SIMPLE_BORDER)            #Map Colour display
        self.tc_mapcolour_display.SetBackgroundColour(GetPalEntry(frame.pal, (int(self.tc_mapcolour.GetValue()))))
        self.tc_mapcolour_display.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
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
                            self.tc_io_edit_label.SetLabel(gt("Input Good #") + str(inputgoods[a].val))
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
                            self.tc_io_edit_label.SetLabel(gt("Output Good #") + str(outputgoods[a].val))
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
            frame.project.dat.in_month = self.tc_intro_month.GetValue()
            frame.project.dat.in_year = self.tc_intro_year.GetValue()
            frame.project.dat.out_month = self.tc_retire_month.GetValue()
            frame.project.dat.out_year = self.tc_retire_year.GetValue()
            frame.project.dat.level = self.tc_level.GetValue()
            frame.project.dat.noinfo = self.tc_noinfo.GetValue()
            frame.project.dat.nocon = self.tc_noconstruction.GetValue()
            frame.project.dat.type = self.tc_type.GetValue()
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
            self.tc_intro_month.SetValue(datoptions.in_month)
            self.tc_intro_year.SetValue(datoptions.in_year)
            self.tc_retire_month.SetValue(datoptions.out_month)
            self.tc_retire_year.SetValue(datoptions.out_year)
            self.tc_level.SetValue(datoptions.level)
            self.tc_noinfo.SetValue(datoptions.noinfo)
            self.tc_noconstruction.SetValue(datoptions.nocon)
            self.tc_type.SetValue(datoptions.type)
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

    
#----------------------------------------------About Dialogue----------------------------------------------------

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
        btn.SetHelpText(gt("ttCloseAbout"))
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

        self.SetVirtualSize((1000, 1000))
        self.SetScrollRate(20,20)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        # since we're not buffering in this case, we have to
        # paint the whole window, potentially very time consuming.
        self.DrawBitmap(self.bmp)

    def DoDrawing(self, dc):
        dc.SetBrush(wx.LIGHT_GREY_BRUSH)
        dc.SetPen(wx.Pen('BLUE', 4))
        dc.DrawRectangle(15, 15, 50, 50)

    def DrawBitmap(self, bitmap):
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        self.bmp = bitmap
        self.SetVirtualSize((bitmap.GetWidth(), bitmap.GetHeight()))
        dc.Clear()
        dc.DrawBitmap(bitmap, 0, 0, True)
        #mask = wx.Mask(bitmap, wx.BLUE)
        #bmp.SetMask(mask)
        #self.bmp = bmp

#----------------------------------------------Main Window----------------------------------------------------

class MainWindow(wx.Frame):

    Xdimsval = "auto"
    Ydimsval = "auto"
    Zdimsval = "auto"
    offsetX = 0
    offsetY = 0

    inputgoods = []
    inputgoods.append(good())
    inputgoods[0].type = "i"
    inputgoods[0].val = 0
    inputgoods[0].name = "alpha"
    inputgoods.append(good())
    inputgoods[1].type = "i"
    inputgoods[1].val = 1
    inputgoods[1].name = "beta"

    outputgoods = []

    project = tc_project()
    project.frame.append(tc_frame())
    project.dat.obj = 1
    project.dat.name = "My Building"   #Any
    project.dat.copyright = "Timothy Baldock"
    project.dat.in_month = "January"
    project.dat.in_year = "1990"
    project.dat.out_month = "December"
    project.dat.out_year = "2010"
    project.dat.level = "13"
    project.dat.noinfo = 1
    project.dat.nocon = 1
    #Building
    project.dat.type = "Station"
    project.dat.location_b = "Land"
    project.dat.chance_b = "12"
    project.dat.build_time = "1222"
    project.dat.extension = 1
    project.dat.pax = 1
    project.dat.post = 1
    project.dat.ware = 1
    #Factory
    project.dat.location_f = "land"
    project.dat.chance_f = "100"
    project.dat.prod = "1222"
    project.dat.range = "122"
    project.dat.colour = "123"
    project.dat.inputgoods = inputgoods
    project.dat.outputgoods = outputgoods
    project.dat.add = "Somestuff=image.0.0\nSomeotherstuff=image.0.0\n"

    current = []
    old_f = 0
    old_direction = ""

    

    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), (500,500),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        #Startup functions...
        self.pal = LoadPal()
        #self.project.frame[0].north.image = wx.EmptyImage(1,1)
        #self.project.frame[0].east.image = wx.EmptyImage(1,1)
        #self.project.frame[0].south.image = wx.EmptyImage(1,1)
        #self.project.frame[0].west.image = wx.EmptyImage(1,1)

        
        #Frame box, containing the currently being worked on frame
        self.tc_frame_box = wx.StaticBox(self, -1, "")               #Box containing the current frame
        self.tc_frame_box_sizer = wx.StaticBoxSizer(self.tc_frame_box, wx.VERTICAL)
        #Frame contents
        #Frame itself, containing the image
        self.tc_display_panel = ImageWindow(self)
        self.tc_display_panel.SetBackgroundColour((233,255,255))
        #Top frame controls, direction selection
        self.tc_frame_label = wx.StaticText(self, -1, (gt("FrameNumberDisplay") % (1,1,"North")), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_frame_filebrowse_n = wx.ToggleButton(self, -1, gt("N"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_e = wx.ToggleButton(self, -1, gt("E"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_s = wx.ToggleButton(self, -1, gt("S"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        self.tc_frame_filebrowse_w = wx.ToggleButton(self, -1, gt("W"), (-1,-1), (24,18), wx.ALIGN_RIGHT)
        #self.tc_frame_filebrowse_n.Enable()
        self.tc_frame_filebrowse_n.SetValue(1)
        self.tc_frame_filebrowse_e.Disable()
        self.tc_frame_filebrowse_s.Disable()
        self.tc_frame_filebrowse_w.Disable()
        #Bottom frame controls - file selection
        self.tc_frame_path_label = wx.StaticText(self, -1, gt("Source:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_frame_path = wx.TextCtrl(self, -1, value="", style=wx.TE_READONLY)                        #Current frame's path
        self.tc_frame_filename_label = wx.StaticText(self, -1, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_frame_filename = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)                    #Current frame's filename
        self.tc_frame_filename.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.tc_frame_filebrowse = wx.Button(self, -1, label=gt("Browse..."))           #Change current frame's filename (browse)


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
        self.tc_display_panel_file_sizer.Add(self.tc_frame_filename_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_filename, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 0)
        self.tc_display_panel_file_sizer.Add(self.tc_frame_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.tc_display_panel_file_sizer.AddGrowableCol(1, 4)
        self.tc_display_panel_file_sizer.AddGrowableCol(3, 2)
        self.tc_frame_box_sizer.Add(self.tc_display_panel, 1, wx.BOTTOM|wx.EXPAND, 4)
        self.tc_frame_box_sizer.Add(self.tc_display_panel_file_sizer, 0, wx.BOTTOM|wx.EXPAND, 2)



        #Dimension box, containing controls over image dimensions & display
        self.tc_size_box = wx.StaticBox(self, -1, "")               #Box containing the dimension controls
        self.tc_size_box_sizer = wx.StaticBoxSizer(self.tc_size_box, wx.VERTICAL)
        #Right hand panel
        #pakSize choice box
        
        self.tc_choice_paksize_label = wx.StaticText(self, -1, gt("paksize:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_paksize = wx.ComboBox(self, -1, "64", (-1, -1), (54, -1), choicelist_paksize, wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.tc_choice_paksize.SetToolTipString(gt("ttpaksize:"))
        #Views choice box
        self.tc_choice_views_label = wx.StaticText(self, -1, gt("Views:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_views = wx.ComboBox(self, -1, "1", (-1, -1), (54, -1), ["1","2","4"], wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.tc_choice_views.SetToolTipString(gt("ttViews:"))
        #x dimensions choice box        
        self.tc_choice_xdims_label = wx.StaticText(self, -1, gt("x dimension:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_xdims = wx.ComboBox(self, -1, gt("auto"), (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.tc_choice_xdims.SetToolTipString(gt("ttx dimension:"))
        #y dimensions choice box        
        self.tc_choice_ydims_label = wx.StaticText(self, -1, "y dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_ydims = wx.ComboBox(self, -1, gt("auto"), (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.tc_choice_ydims.SetToolTipString(gt("tty dimension:"))
        #z dimensions choice box        
        self.tc_choice_zdims_label = wx.StaticText(self, -1, "z dimension:", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_choice_zdims = wx.ComboBox(self, -1, gt("auto"), (-1, -1), (54, -1), choicelist_dims_z, wx.CB_READONLY)
        self.tc_choice_zdims.SetToolTipString(gt("ttz dimension:"))
        #Offset control
        self.tc_offset_label = wx.StaticText(self, -1, gt("Offset:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_offset_button_up = wx.BitmapButton(self, -1, DrawArrow("up"), (-1,-1), (18,18))
        self.tc_offset_button_up.SetToolTipString(gt("ttOffsetUp"))
        self.tc_offset_button_left = wx.BitmapButton(self, -1, DrawArrow("left"), (-1,-1), (18,18))
        self.tc_offset_button_left.SetToolTipString(gt("ttOffsetLeft"))
        self.tc_offset_button_right = wx.BitmapButton(self, -1, DrawArrow("right"), (-1,-1), (18,18))
        self.tc_offset_button_right.SetToolTipString(gt("ttOffsetRight"))
        self.tc_offset_button_down = wx.BitmapButton(self, -1, DrawArrow("down"), (-1,-1), (18,18))
        self.tc_offset_button_down.SetToolTipString(gt("ttOffsetDown"))
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
        #Add offset controls
        self.tc_size_box_sizer.Add(self.tc_offset_label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.TOP, 5)
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
            self.tc_frame_filename.SetValue(self.current.filename)
            if a == 0:  #Usually this should be set first, so that the other values update only afterwards
                im = Analyse(self.current, int(self.project.paksize), GetXYZdims(1), (self.current.offsetx,self.current.offsety))
                ShowImage(im, self.tc_display_panel)
            
            if self.current.xdims == -1:
                self.tc_choice_xdims.SetValue(gt("auto"))
            else:
                self.tc_choice_xdims.SetValue(str(self.current.xdims))
            if self.current.ydims == -1:
                self.tc_choice_ydims.SetValue(gt("auto"))
            else:
                self.tc_choice_ydims.SetValue(str(self.current.ydims))
            if self.current.zdims == -1:
                self.tc_choice_zdims.SetValue(gt("auto"))
            else:
                self.tc_choice_zdims.SetValue(str(self.current.zdims))

            if a == 1:  #But when initialising a frame for the first time, do this second
                im = Analyse(self.current, int(self.project.paksize), GetXYZdims(1), (self.current.offsetx,self.current.offsety))
                ShowImage(im, self.tc_display_panel)

            #self.tc_frame_label.SetLabel(gt("Frame") + " " + str((self.old_f + 1)) + " " + gt("of") + " " + str(len(self.project.frame))
            #                             + " (" + GetLongDirection(self.old_direction) + "):")
            self.tc_frame_label.SetLabel(gt("FrameNumberDisplay") % ((self.old_f + 1), len(self.project.frame), GetLongDirection(self.old_direction)))
            
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

            if self.current.image == 0:
                if self.current.filename == "":
                    self.current.image = NewImage()
                else:
                    self.current.image = (Image.open(self.current.abs_path + "\\" + self.current.filename))
                

            self.old_f = f
            self.old_direction = direction                          #Set old values so that this frame can later be saved

            if p == 0 or p == 2:
                Set_frame_values(1)
                

        def On_browse_input(e):
            
            """Changes the location of the source file for the current frame"""
            dlg = wx.FileDialog(self, gt("Choose a Source file..."), "", "", gt("FiletypesImport"), wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.current.filename = dlg.GetFilename()
                self.current.abs_path = dlg.GetDirectory()
                self.current.image = (Image.open(self.current.abs_path + "\\" + self.current.filename))
            dlg.Destroy()
            Set_frame_values()
            
        self.tc_frame_filebrowse.Bind(wx.EVT_BUTTON, On_browse_input, self.tc_frame_filebrowse)


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

        def OnCombo_Xdims(e):
            """On selection of new item in the Xdims combo box"""
            a = self.tc_choice_xdims.GetValue()    # a = xdims value 1-16
            b = self.tc_choice_ydims.GetValue()    # b = ydims value 1-16
            c = self.tc_choice_zdims.GetValue()    # c = zdims value 1-4

            if a == gt("auto"):
                self.tc_choice_ydims.SetValue(gt("auto"))
                xx = -1
                yy = -1
            else:
                if b == gt("auto"):
                    self.tc_choice_ydims.SetValue(a)
                    yy = int(a)
                    xx = int(a)
                else:
                    xx = int(a)
                    yy = int(b)
            if c == gt("auto"):
                zz = -1
            else:
                zz = int(c)
            Set_frame_values()
            
        def OnCombo_Ydims(e):
            """On selection of new item in the Ydims combo box"""
            a = self.tc_choice_xdims.GetValue()    # a = xdims value 1-16
            b = self.tc_choice_ydims.GetValue()    # b = ydims value 1-16
            c = self.tc_choice_zdims.GetValue()    # c = zdims value 1-4

            if b == gt("auto"):
                self.tc_choice_xdims.SetValue(gt("auto"))
                xx = -1
                yy = -1
            else:
                if a == gt("auto"):
                    self.tc_choice_xdims.SetValue(b)
                    xx = int(b)
                    yy = int(b)
                else:
                    xx = int(a)
                    yy = int(b)
            if c == gt("auto"):
                zz = -1
            else:
                zz = int(c)
            Set_frame_values()
            
        def OnCombo_Zdims(e):
            """On selection of new item in the Zdims combo box"""
            Set_frame_values()

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

        # Functions for the offset buttons        
        def OnClickOffUp(e):
            """On click of the offset increase button"""
            self.current.offsety = self.current.offsety + 1
            Set_frame_values()
        def OnClickOffLeft(e):
            """On click of the offset increase button"""
            if self.current.offsetx > 0:
                self.current.offsetx = self.current.offsetx - 1
                Set_frame_values()
        def OnClickOffRight(e):
            """On click of the offset increase button"""
            self.current.offsetx = self.current.offsetx + 1
            Set_frame_values()
        def OnClickOffDown(e):
            """On click of the offset increase button"""
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

        self.tc_offset_button_up.Bind(wx.EVT_BUTTON, OnClickOffUp, self.tc_offset_button_up)
        self.tc_offset_button_left.Bind(wx.EVT_BUTTON, OnClickOffLeft, self.tc_offset_button_left)
        self.tc_offset_button_right.Bind(wx.EVT_BUTTON, OnClickOffRight, self.tc_offset_button_right)
        self.tc_offset_button_down.Bind(wx.EVT_BUTTON, OnClickOffDown, self.tc_offset_button_down)



        #Frame selection box, containing controls to select the frame and add/remove frames
        self.tc_frame_select_box = wx.StaticBox(self, -1, "")               #Box containing the frame selection controls
        self.tc_frame_select_box_sizer = wx.StaticBoxSizer(self.tc_frame_select_box, wx.VERTICAL)
        #Animation control
        self.tc_frame_select_items = []
        self.tc_frame_select_input_add = wx.Button(self, -1, "+", (-1,-1), (30,16))
        self.tc_frame_select_input_add.SetToolTipString(gt("ttAdd new frame"))
        self.tc_frame_select_input_remove = wx.Button(self, -1, "-", (-1,-1), (30,16))
        self.tc_frame_select_input_remove.SetToolTipString(gt("ttRemove selected frame"))
        self.tc_frame_select_input = wx.ListBox(self, -1, (-1,-1), (60, -1), self.tc_frame_select_items, wx.LB_SINGLE)
        self.tc_frame_select_input.SetToolTipString(gt("ttList of frames"))
        self.tc_frame_select_input_up = wx.BitmapButton(self, -1, DrawArrow("up"), (-1,-1), (30,16))
        self.tc_frame_select_input_up.SetToolTipString(gt("ttMove frame up"))
        self.tc_frame_select_input_down = wx.BitmapButton(self, -1, DrawArrow("down"), (-1,-1), (30,16))
        self.tc_frame_select_input_down.SetToolTipString(gt("ttMove frame down"))
        #Add this to its sizer...
        self.tc_frame_select_controls_top = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_frame_select_controls_top.Add(self.tc_frame_select_input_add, 0, wx.TOP, 0)
        self.tc_frame_select_controls_top.Add(self.tc_frame_select_input_remove, 0, wx.TOP, 0)
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_controls_top, 0, wx.TOP|wx.ALIGN_CENTER, 2)
        
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_input, 1, wx.TOP|wx.ALIGN_CENTER, 0)

        self.tc_frame_select_controls_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.tc_frame_select_controls_bottom.Add(self.tc_frame_select_input_up, 0, wx.TOP, 0)
        self.tc_frame_select_controls_bottom.Add(self.tc_frame_select_input_down, 0, wx.TOP, 0)
        self.tc_frame_select_box_sizer.Add(self.tc_frame_select_controls_bottom, 0, wx.TOP|wx.ALIGN_CENTER, 0)

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
                d_frames.append(gt("FrameDisplayFormat") % (a + 1))
            self.tc_frame_select_input.Set(d_frames)

        
        self.tc_frame_select_input.Bind(wx.EVT_LISTBOX, tc_frame_click, self.tc_frame_select_input)
        self.tc_frame_select_input_add.Bind(wx.EVT_BUTTON, tc_frame_add, self.tc_frame_select_input_add)
        self.tc_frame_select_input_remove.Bind(wx.EVT_BUTTON, tc_frame_remove, self.tc_frame_select_input_remove)
        self.tc_frame_select_input_up.Bind(wx.EVT_BUTTON, tc_frame_up, self.tc_frame_select_input_up)
        self.tc_frame_select_input_down.Bind(wx.EVT_BUTTON, tc_frame_down, self.tc_frame_select_input_down)


        #Bottom panel containing output paths and buttons
        self.tc_global_box = wx.StaticBox(self, -1, gt("Global Options:"))               #Box containing the global controls
        self.tc_global_box_sizer = wx.StaticBoxSizer(self.tc_global_box, wx.HORIZONTAL)
        #Output .png selection
        self.tc_global_imageout_path_label = wx.StaticText(self, -1, gt("Output .png:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_imageout_path = wx.TextCtrl(self, -1, value="")                      #Path display/edit
        self.tc_global_imageout_filename_label = wx.StaticText(self, -1, "\\", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_imageout_filename = wx.TextCtrl(self, -1, value="")                  #Filename display/edit
        self.tc_global_imageout_filebrowse = wx.Button(self, -1, label=gt("Browse..."))         #Change output image filename
        #Output .dat selection
        self.tc_global_datout_path_label = wx.StaticText(self, -1, gt("Output .dat:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_datout_path = wx.TextCtrl(self, -1, value="")                        #Path display/edit
        self.tc_global_datout_filename_label = wx.StaticText(self, -1, "\\", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.tc_global_datout_filename = wx.TextCtrl(self, -1, value="")                    #Filename display/edit
        self.tc_global_datout_filebrowse = wx.Button(self, -1, label=gt("Browse..."))           #Change output image filename
        #Add controls to the sizer...
        #Add output .png...
        self.tc_global_out_sizer = wx.FlexGridSizer(0,5,0,0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_path_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_path, 0, wx.EXPAND|wx.BOTTOM, 2)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_filename_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_filename, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_imageout_filebrowse, 0, wx.TOP, 0)
        #Add output .dat...
        self.tc_global_out_sizer.Add(self.tc_global_datout_path_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_datout_path, 0, wx.EXPAND|wx.BOTTOM, 2)
        self.tc_global_out_sizer.Add(self.tc_global_datout_filename_label, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_datout_filename, 0, wx.TOP, 0)
        self.tc_global_out_sizer.Add(self.tc_global_datout_filebrowse, 0, wx.TOP, 0)
        self.tc_global_out_sizer.AddGrowableCol(1)
        self.tc_global_box_sizer.Add(self.tc_global_out_sizer, 1, wx.TOP|wx.EXPAND, 0)
        

        #self.tc_global_box_sizer.Add(self.tc_frame_select_input, 1, wx.TOP, 0)


        self.SetBackgroundColour((212,208,200))

         
        #self.CreateStatusBar() # A StatusBar in the bottom of the window
        
        # Setting up the menu.
        filemenu= wx.Menu()
        #filemenu.Append(ID_ABOUT, "&About"," Information about this program")
        filemenu.Append(9101, "&New Project\tCtrl-N"," Information about this program")
        filemenu.Append(9102, "&Open Project\tCtrl-O"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(9103, "&Save Project\tCtrl-S"," Information about this program")
        filemenu.Append(9104, "Save Project &As...\tCtrl-A"," Information about this program")
        filemenu.AppendSeparator()
        filemenu.Append(9105, "&Export source\tCtrl-E"," Export project as source files for Makeobj")
        filemenu.Append(9106, "Ex&port .pak\tCtrl-K"," Export project as .pak file for the game")
        filemenu.AppendSeparator()
        filemenu.Append(9107,"E&xit\tCtrl-Q"," Terminate the program")

        def menu_file_saveas(e):
            """Set the file to save the project to"""
            dlg = wx.FileDialog(self, "Choose a file to save to...", "", "", "Project files (*.tcp)|*.tcp", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                self.project.filename = dlg.GetFilename()
                self.project.abs_path = dlg.GetDirectory()
            dlg.Destroy()
            tc_save_project()
        def menu_file_open(e):
            """Open the load file dialog"""
            dlg = wx.FileDialog(self, "Choose a file to load...", "", "", "Project files (*.tcp)|*.tcp", wx.OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                open_filename = dlg.GetFilename()
                open_path = dlg.GetDirectory()
            dlg.Destroy()
            tc_load_project((open_path + "\\" + open_filename))
            
        def menu_file_save(e):
            if self.project.filename == "":     #Needs addition of some kind of check to see if file has been changed
                menu_file_saveas(1)               #since last save
            else:
                tc_save_project()

        def tc_save_project():
            file = open((self.project.abs_path + "\\" + self.project.filename), "w")
            save = self.project
            
            for i in range(len(save.frame)):        #Set all image info to nothing, as image info doesn't need saving here
                save.frame[i].north.image = 0
                save.frame[i].east.image = 0
                save.frame[i].south.image = 0
                save.frame[i].west.image = 0

            pickle.dump(save, file)         #Dump all components to the file in order
            pickle.dump(save.frame, file)
            pickle.dump(save.smoke, file)
            pickle.dump(save.output, file)
            pickle.dump(save.dat, file)
            file.close()
        def tc_load_project(filename):
            """Loads a saved project from memory"""
            file = open(filename, "r")              
            self.project = pickle.load(file)
            self.project.frame = pickle.load(file)
            self.project.smoke = pickle.load(file)
            self.project.output = pickle.load(file)
            self.project.dat = pickle.load(file)
            file.close()
            tc_project_init()

        def menu_file_export_source(e):
            Export()

        #self.Bind(wx.EVT_MENU, self.menu_file_new, id=9101)
        self.Bind(wx.EVT_MENU, menu_file_open, id=9102)
        self.Bind(wx.EVT_MENU, menu_file_save, id=9103)
        self.Bind(wx.EVT_MENU, menu_file_saveas, id=9104)
        self.Bind(wx.EVT_MENU, menu_file_export_source, id=9105)
        #self.Bind(wx.EVT_MENU, self.menu_file_export_pak, id=9106)
        #self.Bind(wx.EVT_MENU, self.menu_file_exit, id=9107)

        recentmenu= wx.Menu()
        recentmenu.Append(-1, "Document #1"," Information about this program")
        recentmenu.Append(-1, "Document #2"," Information about this program")
        recentmenu.Append(-1, "Document #3"," Information about this program")
        recentmenu.Append(-1, "Document #4"," Information about this program")
        recentmenu.AppendSeparator()
        recentmenu.Append(-1, "&Clear this list"," Clear the cache of recent documents")

        toolsmenu= wx.Menu()
        toolsmenu.Append(9301, ".&dat file options\tCtrl-D"," Edit .dat file options")
        toolsmenu.Append(9302, "&Smoke options\tCtrl-M"," Add or edit a smoke object associated with this project")
        toolsmenu.Enable(9302, 0)
        toolsmenu.AppendSeparator()
        toolsmenu.Append(9303, "&Preferences\tCtrl-P"," Change program preferences")
        toolsmenu.Enable(9303, 0)

        def menu_tools_dat(e):
            """Open the dat edit dialog"""
            dlg = DatDialog(self, -1, "Edit .dat information", size=(-1, -1),
                            style=wx.DEFAULT_DIALOG_STYLE)
            dlg.ShowModal()
            dlg.Destroy()

        self.Bind(wx.EVT_MENU, menu_tools_dat, id=9301)
        #self.Bind(wx.EVT_MENU, self.menu_tools_smoke, id=9302)
        #self.Bind(wx.EVT_MENU, self.menu_file_exit, id=9303)


        helpmenu= wx.Menu()
        helpmenu.Append(9501, "Help Topics\tCtrl-H","")
        helpmenu.AppendSeparator()
        helpmenu.Append(9502, "&About TileCutter"," Information about this program")

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
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(recentmenu,"&Recent") # Adding the "recentmenu" to the MenuBar
        menuBar.Append(toolsmenu,"&Tools") # Adding the "toolsmenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the "helpmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.





        # Image panel
        
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.top_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_box_sizer_right = wx.BoxSizer(wx.VERTICAL)
        
        self.top_box_sizer.Add(self.tc_frame_box_sizer,1,wx.EXPAND|wx.RIGHT, 4)
        self.top_box_sizer_right.Add(self.tc_size_box_sizer,0,wx.ALL,border=0)
        self.top_box_sizer_right.Add(self.tc_frame_select_box_sizer,1,wx.EXPAND|wx.ALL,border=0)
        self.top_box_sizer.Add(self.top_box_sizer_right,0,wx.EXPAND)
        self.sizer.Add(self.top_box_sizer,1,wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,border=2)
        self.sizer.Add(self.tc_global_box_sizer,0,wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,border=2)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

        def tc_project_init():
            """This function should be called whenever a new function is loaded or created"""
            tc_display_frames(1)    #Display the frames from the new project in the frames list
            Set_Working(0, "N", 2)  #Set the working frame to the first one of the project, North direction
                                    #with flag set to 2, so that new current is initialised
            tc_highlight(0)


        #On first loading the program
        Set_Working(0, "N", 1)
        tc_display_frames(1)            #Show whatever frames there may be on loading...
        tc_highlight(0)
        self.Show(True)
    


    def OnExit(self,e):
        self.Close(True)  # Close the frame.
    def OnClickCutImage(self,e):
        """Commands to execute on clicking the Cut button"""
        
        
    def OnClickDatEdit(self,e):
        """Open the dat edit dialog"""
        dlg = DatDialog(self, -1, "Edit .dat information", size=(600, 450),
                        style=wx.DEFAULT_DIALOG_STYLE)
        dlg.ShowModal()
        dlg.Destroy()
    def OnClickBrowseInput(self,e):
        """ Open an input file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a Source file...", self.dirname, "", "*.png", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            f=open(os.path.join(self.dirname,self.filename),'r')
            self.control1.SetValue((dlg.GetDirectory() + "\\" + dlg.GetFilename()))
            self.control2.SetValue((dlg.GetDirectory() + "\\output-" + dlg.GetFilename()))
            f.close()
            self.alpha = (Image.open((self.dirname) + "\\" + (self.filename)))
            
            #Analyse(alpha, int(self.choice_paksize.GetValue()))     #All other values defaults (not set yet!)
            ShowImage(Analyse(self.alpha, int(self.choice_paksize.GetValue())), self.bitmap1)
        dlg.Destroy()


        
    def OnClickBrowseOutput(self,e):
        """ Open an output file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file to save to...", self.dirname, "", "*.png", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            f=open(os.path.join(self.dirname,self.filename),'r')
            self.control2.SetValue((dlg.GetDirectory() + "\\" + dlg.GetFilename()))
            f.close()
        dlg.Destroy()
    

app = wx.App()
frame = MainWindow(None, -1, "TileCutter v." + VERSION_NUMBER)              

app.MainLoop()



