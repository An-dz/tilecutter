# coding: UTF-8
#
# TileCutter Cutting Engine
#

# Copyright © 2008-2012 Timothy Baldock. All Rights Reserved.


import wx
import sys, os, string, tempfile
import pickle, copy, math, io

import logger
debug = logger.Log()

import config
config = config.Config()

import subprocess

class TCMasks:
    """Generates and contains cutting masks for various paksizes"""
    # Whenever a TCMask is made, it checks if that paksize of masks has been generated
    # and if not makes them
    masksets = {}
    def __init__(self, paksize):
        if paksize not in TCMasks.masksets:
            # Generate new masks
            TCMasks.masksets[paksize] = TCMaskSet(paksize)
            debug("TCMasks - Generated new TCMaskSet for paksize: %s" % paksize)
        self.mask = TCMasks.masksets[paksize]

class TCMaskSet:
    """A set of cutting masks, 1bit bitmaps"""
    def __init__(self, p):
        self.masks = {}
        # -1 -> Nothing (fully masked)
        a = self.init_new_mask(p)
        self.fill_left(a)
        self.fill_right(a)
        #a.SaveFile("mask_-1.png", wx.BITMAP_TYPE_PNG)
        self.masks[-1] = a.ConvertToBitmap()

        # 0 -> Tile only
        a = self.init_new_mask(p)
        self.fill_bottom_triangles(a)
        self.fill_top_left(a)
        self.fill_top_right(a)
        #a.SaveFile("mask_00.png", wx.BITMAP_TYPE_PNG)
        self.masks[0] = a.ConvertToBitmap()

        # 1 -> Tile and top-right
        a = self.init_new_mask(p)
        self.fill_bottom_triangles(a)
        self.fill_top_left(a)
        #a.SaveFile("mask_01.png", wx.BITMAP_TYPE_PNG)
        self.masks[1] = a.ConvertToBitmap()

        # 2 -> Tile and top-left
        a = self.init_new_mask(p)
        self.fill_bottom_triangles(a)
        self.fill_top_right(a)
        #a.SaveFile("mask_02.png", wx.BITMAP_TYPE_PNG)
        self.masks[2] = a.ConvertToBitmap()

        # 3 -> Tile and all top
        a = self.init_new_mask(p)
        self.fill_bottom_triangles(a)
        #a.SaveFile("mask_03.png", wx.BITMAP_TYPE_PNG)
        self.masks[3] = a.ConvertToBitmap()

        # 4 -> Right side only
        a = self.init_new_mask(p)
        self.fill_left(a)
        #a.SaveFile("mask_04.png", wx.BITMAP_TYPE_PNG)
        self.masks[4] = a.ConvertToBitmap()

        # 5 -> Left side only
        a = self.init_new_mask(p)
        self.fill_right(a)
        #a.SaveFile("mask_05.png", wx.BITMAP_TYPE_PNG)
        self.masks[5] = a.ConvertToBitmap()

        # 6 -> Everything (no mask)
        a = self.init_new_mask(p)
        #a.SaveFile("mask_06.png", wx.BITMAP_TYPE_PNG)
        self.masks[6] = a.ConvertToBitmap()

    def init_new_mask(self, p):
        """Create a blank new cutting mask"""
        a = wx.Image(p, p)
        for i in range(p):
            for j in range(p):
                a.SetRGB(i, j, 255, 255, 255)

        return a

    def fill_bottom_triangles(self, b):
        """Fill in the bottom left and right triangles for a cutting mask"""
        p = b.GetWidth()

        for y in range(0, p/4):
            for x in range(0, y * 2):
                b.SetRGB(x, p/2 + p/4 + y, 0, 0, 0)

        for y in range(0, p/4):
            for x in range(p - y * 2, p):
                b.SetRGB(x, p/2 + p/4 + y, 0, 0, 0)

        return b
        
    def fill_left(self, b):
        """Fill in the entire left half"""
        p = b.GetWidth()
 
        for y in range(0, p):
            for x in range(0, p/2):
                b.SetRGB(x, y, 0, 0, 0)

        return b

    def fill_right(self, b):
        """Fill in the entire right half"""
        p = b.GetWidth()
 
        for y in range(0, p):
            for x in range(p/2, p):
                b.SetRGB(x, y, 0, 0, 0)

        return b

    def fill_top_left(self, b):
        """Fill top-left section of a cutting mask"""
        p = b.GetWidth()
        for y in range(0, p/4):
            for x in range(0, y * 2):
                b.SetRGB(x, p/2 + p/4 - y, 0, 0, 0)
 
        for y in range(0, p/2 + 1):
            for x in range(0, p/2):
                b.SetRGB(x, y, 0, 0, 0)

        return b

    def fill_top_right(self, b):
        """Fill top-right section of a cutting mask"""
        p = b.GetWidth()
        for y in range(0, p/4):
            for x in range(p - y * 2, p):
                b.SetRGB(x, p/2 + p/4 - y, 0, 0, 0)
 
        for y in range(0, p/2 + 1):
            for x in range(p/2, p):
                b.SetRGB(x, y, 0, 0, 0)

        return b

    def __getitem__(self, key):
        return wx.Mask(self.masks[key])

# Take tile coords and convert into screen coords
def tile_to_screen(pos, dims, off, p, screen_height=None):
    """Take tile coords and convert to screen coords
    by default converts into bottom-left screen coords,
    but with height attribute supplied converts to top-left
    returns the bottom-left position of the tile on the screen"""
    offx, offy = off
    if offx < 0:
        offx = 0
    xpos, ypos, zpos = pos          # x, y and z position
    xdims, ydims, zdims = dims      # Total size of x, y and z
    xx = (xdims - 1 - xpos + ypos) * p/2 + offx
    # Gives top-left position of subsection
    yy = ((xdims - xpos) + (ydims - ypos)) * (p/4) + (zpos * p) + offy + p/2
    if screen_height != None:
        yy = screen_height - yy
    return (xx,yy)


class Makeobj:
    """Interface class to Makeobj"""
    def __init__(self, path_to_makeobj):
        """Takes absolute path to makeobj and returns a makeobj control object"""
        self.path_to_makeobj = path_to_makeobj
    def pak(self, paksize, path_to_pak, path_to_dat):
        """Calls makeobj with appropriate arguments for generating a pakfile"""
        # path_to_makeobj pak[paksize] path_to_pak path_to_dat
        # Paths to pak and dat are absolute paths (or relative to makeobj)
        args = [self.path_to_makeobj, "pak%s" % paksize, path_to_pak, path_to_dat]
        # Need to convert to system encoding on Windows as CMD interpreter can't do unicode
        for n, arg in enumerate(args):
            if isinstance(arg, str):
                args[n] = arg.encode(sys.getfilesystemencoding())
        debug("Activating Makeobj with arguments: %s" % str(args))
        process = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        process.wait()
        # Write out makeobj log information to main log
        output = process.communicate()
        if output[0] != "":
            debug(output[0])
        if output[1] != "":
            debug(output[1])
        debug("Makeobj output complete")

class Paths(object):
    """Advanced path manipulation functions"""
    # splitPath     breaks a string up into path components
    # joinPaths     joins two paths together, taking end components (filenames etc.) into account
    # existingPath  returns the largest section of a path which exists on the filesystem
    # comparePaths  produces a relative path from two absolute ones
    def splitPath(self, p1, p2=None):
        """Split a path into an array, index[0] being the first path section, index[len-1] being the last
        Optionally takes a second path which is joined with the first for existence checks, to allow for
        checking existence of relative paths"""
        if os.path.split(p1)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p1)[0])[1] != "":
                p1 = os.path.split(p1)[0]
        a = []
        if p2 == None:
            p2 = ""
        while os.path.split(p1)[1] != "":
            n = os.path.split(p1)
            # Add at front, text,   offset,             length,     exists or not,      File or Directory?
##            debug(u"path1: %s, path2: %s" % (p1, p2))
##            debug(u"exists? %s, %s" % (self.joinPaths(p2, p1), os.path.exists(self.joinPaths(p2, p1))))
            a.insert(0,    [n[1],  len(p1)-len(n[1]),   len(n[1]),  os.path.exists(self.joinPaths(p2, p1))])#, existsAsType(p)])
            p1 = n[0]
        return a

    def join_paths(self, p1, p2):
        """Join two paths together accounting for end cases on first path"""
        # If path is a file, or end section of path is file-like (e.g. has an extension)
        if os.path.isfile(p1) or os.path.splitext(p1)[1] != "" and not os.path.isdir(p1):
            # Split off end section
            p1 = os.path.split(p1)[0]
        p3 = os.path.join(p1, p2)
        if os.path.isfile(p3) or os.path.splitext(p3)[1] != "" and not os.path.isdir(p3):
            return p3
        else:
            return os.path.join(p3, "")

    def joinPaths(self, p1, p2):
        """Join p2 to p1, accounting for end cases (is directory, is file etc.)"""
        return self.join_paths(p1, p2)

    def existingPath(self, p):
        """Take a path and return the largest section of this path that exists
        on the filesystem"""
        if os.path.split(p)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p)[0])[1] != "":
                p = os.path.split(p)[0]
        while not os.path.exists(p):
            p = os.path.split(p)[0]
        return p

    def is_input_file(self, path):
        """Checks if file's extension is in the list of allowed input extensions"""
        if os.path.splitext(path)[1] in config.valid_image_extensions:
            return True
        else:
            return False

    def compare_paths(self, p1, p2):
        """Return either a relative path from p1 to p2, or p1 if no relative path exists"""
        # Check that p2 is not an empty string, or None, and that drive letters match
        if p2 == None or p2 == "" or os.path.splitdrive(p1)[0] != os.path.splitdrive(p2)[0]:
            return p1
        p1s = self.splitPath(os.path.normpath(p1))
        p2s = self.splitPath(os.path.normpath(p2))
        k = 0
        while p1s[k][0] == p2s[k][0]:
            k += 1
        # Number of /../'s is length of p2s minus k (number of sections which match, but remember this will be one more
        # than the number which match, which is what we want as the length is one more than we need anyway
        p3 = ""
        # If p2's last component is a file, need to subtract one more to give correct path
        e = 1
        for a in range(len(p2s)-k-e):
            p3 = os.path.join(p3, "..")
        # Then just add on all of the remaining parts of p1s past the sections which match
        for a in range(k,len(p1s)):
            p3 = os.path.join(p3, p1s[a][0])
        return p3

    def comparePaths(self, p1, p2):
        """Compare two absolute paths, returning either a relative path from p1 to p2, or p1 if no relative path exists"""
        return self.compare_paths(p1, p2)

    def win_to_unix(self, path):
        """Convert windows style path blah\meh to unix style blah/meh"""
        return path.replace("\\", "/")
    
def export_writer(project, pak_output=False, return_dat=False, write_dat=True):
    """Write a project's dat and png files"""
    # Runs after export_cutter has been called for all active images in the project,
    # uses information generated by it to output files ready for makeobj compilation
    paths = Paths()
    dat_path = paths.join_paths(project.save_location(), project.datfile_location())
    png_path = paths.join_paths(project.save_location(), project.pngfile_location())
    pak_path = paths.join_paths(project.save_location(), project.pakfile_location())
    debug("e_w: export_writer init")
    debug("e_w: Writing .png to file: %s" % png_path)
    if project.datfile_write():
        debug("e_w: Writing .dat info to file: %s" % dat_path)
    else:
        debug("e_w: Writing .dat info to console")

    # Get path from dat file location to png file location
    dat_to_png = os.path.splitext(paths.compare_paths(png_path, dat_path))[0]
    debug("e_w: Path from .dat to .png is: %s" % dat_to_png)

    # First calculate the size of output image required, this depends on a number of factors
    # - Dimensions of the image, x*y images for first layer + (x+y-1)*(z-1) images for higher layers
    # - Number of views, 1-4
    # - Number of seasons, 1-2
    # - Whether there is a frontimage, 1-2
    # - Number of frames (this will always be 1 in the current version)
    #       However, it's likely animation will be implemented such that it's possible for only the front
    #       image to be animated, and for animation to be selected for views, seasons etc. on a case-by-case
    #       basis, so don't assume it'll be so simple
    # So:
    # dims * views * seasons * images ( * frames )
    # The root of this number is then found, and rounding that up gives the side length for the output image

    p = project.paksize()
    xdims = project.x()
    ydims = project.y()
    zdims = project.z()
    layers = project.frontimage() + 1       # +1 as this value is stored as an 0 or 1, we need 1 or 2
    views = project.directions()
    seasons = project.winter() + 1          # +1 as this value is stored as an 0 or 1, we need 1 or 2

    debug("e_w: Outputting using paksize: %s" % p)
    debug("e_w: Outputting %s front/backimages" % layers)
    debug("e_w: Outputting %s views" % views)
    debug("e_w: Outputting %s seasons" % seasons)
    debug("e_w: Outputting dims: x:%s, y:%s, z:%s" % (xdims, ydims, zdims))

    # Calculate dimensions of output image
    dims = xdims*ydims + (xdims+ydims-1)*(zdims-1)
    totalimages = dims * layers * views * seasons
    side = int(math.ceil(math.sqrt(totalimages)))

    debug("e_w: Outputting %s images total, output size %sx%sp (%sx%spx)" % (totalimages, side, side, side*p, side*p))

    # Init output bitmap and dc for drawing into it
    output_bitmap = wx.Bitmap(side*p, side*p)
    outdc = wx.MemoryDC()
    outdc.SelectObject(output_bitmap)
    outdc.SetBackground(wx.Brush(config.transparent))
    outdc.Clear()

    # A list can now be produced of all images to be output
    # project[view][season][frame][layer][xdim][ydim][zdim] = [bitmap, (xposout, yposout)]
    output_list = []
    for d in range(views):
        for s in range(seasons):
            for f in range(1):              # Change for multi-frame
                for l in range(layers):
                    if d in [1,3]:          # Reverse x and y dims for rotation views
                        xx = ydims
                        yy = xdims
                    else:
                        xx = xdims
                        yy = ydims
                    for x in range(xx):
                        for y in range(yy):
                            for z in range(zdims):
                                # No need to write out middle bits of higher levels
                                if (z > 0 and (x == 0 or y == 0)) or z == 0:
#                                    output_list.append([project[d][s][f][l][x][y][z], {"d":d,"s":s,"f":f,"l":l,"x":x,"y":y,"z":z}, None])
                                    output_list.append([project.get_cut_image(d, s, f, l, x, y, z), {"d":d,"s":s,"f":f,"l":l,"x":x,"y":y,"z":z}, None])

    # Now that a list of component images has been generated, output these in sequence
    x = 0
    y = 0
    for k in output_list:
        outdc.DrawBitmap(k[0], x*p, y*p, True)
        # Makeobj references the image array by row,column, e.g. y,x, so switch these
        k[2] = (y,x)
        x += 1
        if x == side:
            x = 0
            y += 1
    # Select bitmap out of dc ready for saving
    outdc.SelectObject(wx.NullBitmap)

    # output_bitmap now contains the image array
    debug("e_w: Image output complete")


    output_text = io.StringIO()
    # Test text
    output_text.write(project.dat_lump() + "\n")
    # dims=East-West, North-south, Views
    output_text.write("dims=%s,%s,%s\n" % (ydims, xdims, views))
    for k in output_list:
        # (d,s,f,l,x,y,z)
        j = k[1]
        if j["l"] == 0:
            imtext = "BackImage"
        else:
            imtext = "FrontImage"
        # imtext[direction][x][y][z][frame][season]=filename.xpos.ypos
        output_text.write("%s[%s][%s][%s][%s][%s][%s]=%s.%s.%s\n" % (
            imtext, j["d"], j["x"], j["y"], j["z"], j["f"], j["s"], paths.win_to_unix(dat_to_png), k[2][0], k[2][1]))
    dat_text = output_text.getvalue()

    # Write out to files if required
    if write_dat:
        debug("e_w: Writing out .dat file to %s" % dat_path)
        # Check that each component in dat_path exists, create directories if needed
        if not os.path.isdir(os.path.split(dat_path)[0]):
            os.makedirs(os.path.split(dat_path)[0])
        f = open(dat_path, "w")
    else:
        debug("e_w: Writing out .dat file to temporary file")
        tempfile.tempdir = os.path.split(dat_path)[0]
        f = tempfile.NamedTemporaryFile("w", suffix=".tmp", delete=False)
        dat_path = f.name

    # Write .dat file
    f.write(dat_text)
    f.close()

    # Check that each component in png_path exists, create directories if needed
    if not os.path.isdir(os.path.split(png_path)[0]):
        os.makedirs(os.path.split(png_path)[0])

    # Write out .png file
    output_bitmap.SaveFile(png_path, wx.BITMAP_TYPE_PNG)

    if pak_output:
        # Output .pak file using makeobj if required
        debug("e_w: Use makeobj to output pak file")
        path_to_makeobj = paths.join_paths(os.getcwd(), config.path_to_makeobj)
        makeobj = Makeobj(path_to_makeobj)
        print(repr(pak_path))
        print(repr(dat_path))
        makeobj.pak(project.paksize(), paths.win_to_unix(pak_path), paths.win_to_unix(dat_path))

    # Delete temporary file if needed
    if not write_dat:
        debug("e_w: deleting temporary file used: %s" % dat_path)
        os.remove(dat_path)

    # Log .dat file generated
    debug("e_w: .dat file text is:")
    debug(dat_text)
    # Return dat file text (e.g. for output within the program in a dialog box etc.)
    if return_dat:
        return dat_text
    else:
        return True

def export_cutter(bitmap, dims, offset, p):
    """Takes a bitmap and dimensions, and returns an array of masked bitmaps"""
    debug("e_c: export_cutter init")
    debug("e_c: Passed in bitmap of size (x, y): (%s, %s)" % (bitmap.GetWidth(), bitmap.GetHeight()))
    debug("e_c: Dims (x, y, z, d): %s" % str(dims))
    debug("e_c: Offset (offx, offy): %s" % str(offset))

    # To account for irregularly shaped buildings, the values of x and y dims
    # need to be swapped where dims[3] (view#) is in [1,3]
    if dims[3] in [1,3]:
        dims = (dims[1],dims[0],dims[2])
    else:
        dims = (dims[0],dims[1],dims[2])

    # Based on the paksize of the project, cut it into little bits which are stored in an array
    # ready for the next stage of the process
    # Use wx.Bitmap.GetSubBitmap to grab the correct paksize section, then set the Bitmap's mask to
    # the appropriate masking image which is generated automatically for each paksize the first time
    # the mask provider function is called with that particular paksize

    # Init mask provider
    masks = TCMasks(p)

    debug("e_c: Building output array...")
    output_array = []
    # Must ensure that the source bitmap is large enough so that all subbitmap operations succeed
    # Extend to the right and up
    # Max height will be offy + (dimsx+dimsy)*p/4 + p/2 + p*(dimsz-1)
    # Max width will be offx + (dimsx+dimsy)*p/2
    max_width = offset[0] + (dims[0]+dims[1])*(p/2)
    max_height = offset[1] + (dims[0]+dims[1])*(p/4) + p/2 + p*(dims[2]-1)
    if max_width < bitmap.GetWidth():
        max_width = bitmap.GetWidth()
    if max_height < bitmap.GetHeight():
        max_height = bitmap.GetHeight()
    source_bitmap = wx.Bitmap(max_width, max_height)
    tdc = wx.MemoryDC()
    tdc.SelectObject(source_bitmap)
    tdc.SetPen(wx.Pen(config.transparent, 1, wx.SOLID))
    tdc.SetBrush(wx.Brush(config.transparent, wx.SOLID))
    tdc.DrawRectangle(0,0,max_width, max_height)
    tdc.DrawBitmap(bitmap, 0, max_height - bitmap.GetHeight())
    tdc.SelectObject(wx.NullBitmap)
    
    for x in range(dims[0]):
        yarray = []
        for y in range(dims[1]):
            zarray = []
            for z in range(dims[2]):
                pos = tile_to_screen((x,y,z), dims, offset, p, source_bitmap.GetHeight())
                submap = source_bitmap.GetSubBitmap((pos[0], pos[1], p,p))
                if z == 0:
                    if x == 0 and y == 0:
                        submap.SetMask(masks.mask[3])
                    elif x == 0 and y != 0:
                        submap.SetMask(masks.mask[1])
                    elif x != 0 and y == 0:
                        submap.SetMask(masks.mask[2])
                    else:
                        submap.SetMask(masks.mask[0])
                else:
                    if x == 0 and y == 0:
                        submap.SetMask(masks.mask[6])
                    elif x == 0 and y != 0:
                        submap.SetMask(masks.mask[4])
                    elif x != 0 and y == 0:
                        submap.SetMask(masks.mask[5])
                    else:
                        submap.SetMask(masks.mask[-1])

##                tdc = wx.MemoryDC()
##                kk = wx.EmptyBitmap(p,p)
##                tdc.SelectObject(kk)
##                tdc.DrawBitmap(submap, 0, 0, True)
##                tdc.SelectObject(wx.NullBitmap)
##                tdc = 0
##                kk.SaveFile("test_%s%s%s.png" % (x,y, z), wx.BITMAP_TYPE_PNG)
##                kk = 0

                # submap = Bitmap+Mask, Second variable stores location of this tile within
                #                       the output image as a tuple
                zarray.append(submap)
            yarray.append(zarray)
        output_array.append(yarray)
    debug("e_c: Build output array complete, exiting")
    return output_array



