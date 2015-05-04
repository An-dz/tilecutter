# TC Backend functions

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
import pickle, copy

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


class tc:
    """This class contains all the core TileCutter functionality, image manipulation,
    exporting, masking etc."""

# Load some image rescources (icons etc.)
class ImRes:
    def __init__(self):
        self.summer_im = wx.Image("icons/summer-icon.png")
        self.summer_im.SetMaskFromImage(self.summer_im,231,255,255)
        self.summer = self.summer_im.ConvertToBitmap()

        self.winter_im = wx.Image("icons/winter-icon.png")
        self.winter_im.SetMaskFromImage(self.winter_im,231,255,255)
        self.winter = self.winter_im.ConvertToBitmap()

        self.front_im = wx.Image("icons/frontimage-icon.png")
        self.front_im.SetMaskFromImage(self.front_im,231,255,255)
        self.front = self.front_im.ConvertToBitmap()

        self.back_im = wx.Image("icons/backimage-icon.png")
        self.back_im.SetMaskFromImage(self.back_im,231,255,255)
        self.back = self.back_im.ConvertToBitmap()

        self.north_im = wx.Image("icons/north-icon.png")
        self.north_im.SetMaskFromImage(self.north_im,231,255,255)
        self.north = self.north_im.ConvertToBitmap()

        self.east_im = wx.Image("icons/east-icon.png")
        self.east_im.SetMaskFromImage(self.east_im,231,255,255)
        self.east = self.east_im.ConvertToBitmap()

        self.south_im = wx.Image("icons/south-icon.png")
        self.south_im.SetMaskFromImage(self.south_im,231,255,255)
        self.south = self.south_im.ConvertToBitmap()

        self.west_im = wx.Image("icons/west-icon.png")
        self.west_im.SetMaskFromImage(self.west_im,231,255,255)
        self.west = self.west_im.ConvertToBitmap()

        self.reload_im = wx.Image("icons/reloadfile-icon.png")
        self.reload_im.SetMaskFromImage(self.reload_im,231,255,255)
        self.reload = self.reload_im.ConvertToBitmap()

        self.sameforall_im = wx.Image("icons/sameforall-icon.png")
        self.sameforall_im.SetMaskFromImage(self.sameforall_im,231,255,255)
        self.sameforall = self.sameforall_im.ConvertToBitmap()

        self.center_im = wx.Image("icons/center-icon.png")
        self.center_im.SetMaskFromImage(self.center_im,231,255,255)
        self.center = self.center_im.ConvertToBitmap()

        self.x = wx.Image("icons/up-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.up = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/up2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.up2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.down = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.down2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/left-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.left = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/left2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.left2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/right-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.right = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/right2-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.right2 = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/up-right-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.upright = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down-right-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.downright = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/up-left-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.upleft = self.x.ConvertToBitmap()

        self.x = wx.Image("icons/down-left-icon.png")
        self.x.SetMaskFromImage(self.x,231,255,255)
        self.downleft = self.x.ConvertToBitmap()













    