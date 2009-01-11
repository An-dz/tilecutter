# TC Backend functions

import wx
import sys, os
import pickle, copy

from debug import DebugFrame as debug

TRANSPARENT = (231,255,255)

class TCMasks:
    """Generates and contains cutting masks for various paksizes"""
    # Whenever a TCMask is made, it checks if that paksize of masks has been generated
    # and if not makes them
    masksets = {}
    def __init__(self, paksize):
        if not TCMasks.masksets.has_key(paksize):
            # Generate new masks
            TCMasks.masksets[paksize] = TCMaskSet(paksize)
            debug("TCMasks - Generated new TCMaskSet for paksize: %s" % paksize)
        self.mask = TCMasks.masksets[paksize]

class TCMaskSet:
    """A set of cutting masks, 1bit bitmaps"""
    def __init__(self, p):
        # -1 -> Nothing (fully masked)
        # 0 -> Tile only
        # 1 -> Tile and top-right
        # 2 -> Tile and top-left
        # 3 -> Tile and all top
        # 4 -> Right side only
        # 5 -> Left side only
        # 6 -> Everything (no mask)
        self.masks = {}
        self.masks[-1] = self.makeMaskFromPoints([], p)
        self.masks[0] = self.makeMaskFromPoints(
            [(p/2,p),(0,p/4+p/2),(p/2-1,p/2+1),(p/2,p/2+1),(p-1,p/4+p/2),(p/2,p-1)], p)
        self.masks[1] = self.makeMaskFromPoints(
            [(p/2,p),(0,p/4+p/2),(p/2-1,p/2+1),(p/2,p/2+1),(p/2,0),(p-1,0),(p-1,p/4+p/2),(p/2,p-1)], p)
        self.masks[2] = self.makeMaskFromPoints(
            [(p/2,p),(0,p/4+p/2),(0,0),(p/2-1,0),(p/2-1,p/2+1),(p/2,p/2+1),(p-1,p/4+p/2),(p/2,p-1)], p)
        self.masks[3] = self.makeMaskFromPoints(
            [(p/2,p),(0,p/4+p/2),(0,0),(p-1,0),(p-1,p/4+p/2),(p/2,p-1)], p)
        self.masks[4] = self.makeMaskFromPoints(
            [(p-1,0),(p-1,p-1),(p/2,p-1),(p/2,0)], p)
        self.masks[5] = self.makeMaskFromPoints(
            [(0,0),(p/2-1,0),(p/2-1,p-1),(0,p-1)], p)
        self.masks[6] = self.makeMaskFromPoints(
            [(0,0),(p-1,0),(p-1,p-1),(0,p-1)], p)

    def makeMaskFromPoints(self, points, p):
        """Make a mask from a sequence of points"""
        # Init the DC, for monochrome bitmap/mask white pen/brush draws the bits which are see-through
        dc = wx.MemoryDC()
        dc.SetPen(wx.WHITE_PEN)
        dc.SetBrush(wx.WHITE_BRUSH)
        b = wx.EmptyBitmap(p,p)
        dc.SelectObject(b)
        dc.DrawPolygon(points)
        dc.SelectObject(wx.NullBitmap)
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
    source_bitmap = wx.EmptyBitmap(max_width, max_height)
    tdc = wx.MemoryDC()
    tdc.SelectObject(source_bitmap)
    tdc.SetPen(wx.Pen(TRANSPARENT, 1, wx.SOLID))
    tdc.SetBrush(wx.Brush(TRANSPARENT, wx.SOLID))
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

                zarray.append(submap)
            yarray.append(zarray)
        output_array.append(yarray)
    debug("e_c: Build output array complete, exiting")
    return output_array

def Export(self, export_dat=1, export_png=1):
    """Exports the cut png image and dat file"""

    output_png = "test-output.png"
    output_dat = "test-output.dat"
    dat_to_png = "test-output"

    # Firstly find the path from dat file to png
    # Check that both of these are filled out, if png only then
    # don't export the dat file and throw Warning
    # If dat only then export the dat only, and throw Warning
    # If neither, than stop with Error
    p = self.active.info.paksize

    x_dims = self.active.info.xdims
    y_dims = self.active.info.ydims
    z_dims = self.active.info.zdims
    view_dims = self.active.info.views
    winter_dims = self.active.info.winter
    front_dims = self.active.info.frontimage
    frame_dims = len(self.active.frame)

    unit = (xdims,ydims*zdims)

    width = view_dims * (unit[0] + unit[0]*winter_dims)
    height = frame_dims * (unit[1] + unit[1]*front_dims)

    # Create the wxImage and PILImage for the output
    img = Image.new("RGBA", (width*p,height*p), color=(231,255,255,0))

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

    for f in range(len(self.active.frame)):
        for d in range(self.active.info.views):
            for i in ii:
                # Make a temp image to copy from
                im = self.active.frame[f].direction[d].image[i].image
                # If offset is negative...
                if self.active.frame[f].direction[d] in [0,2]:
                    # Normal dimensions
                    xx = len(self.active.info.xdims)
                    yy = len(self.active.info.ydims)
                else:
                    # Reverse dimensions
                    xx = len(self.active.info.ydims)
                    yy = len(self.active.info.xdims)
                zz = self.active.info.zdims
                w = (xx + yy) * (p/2)
                h = ((xx + yy) * (p/4)) + (p/2) + ((zz - 1) * p)
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
                tempimg = Image.new("RGB", (max([w,im.size[0]])+abs_offx, max([h,im.size[1]])+abs_offy), color=(231,255,255,0))
                # And paste this image into it at the right spot
                # Paste the base image into the output
                tempimg.paste(im,(image_offset_x,image_offset_y))

                # Now copy from and mask each bit of the image
                for z in range(zz):
                    for x in range(xx):
                        for y in range(yy):
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

                            img.paste(tempim,(xpos,ypos,xpos+p,ypos+p))
                            
                            # Masking routine goes here...

    img.save("test.png")

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

def ExportSmoke(self):
    """Exports a smoke object"""

def ExportCursor(self):
    """Exports the cursor/icon for a building"""


