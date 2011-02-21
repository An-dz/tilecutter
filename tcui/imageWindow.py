# coding: UTF-8
#
# TileCutter User Interface Module - imageWindow
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.

import os, wx, imres, tcui, tc

# Utility functions
import translator
gt = translator.Translator()
_gt = gt.loop

import config
config = config.Config()

import logger
debug = logger.Log()

from tc import Paths

class imageWindow(wx.ScrolledWindow):
    """Window onto which bitmaps may be drawn, background colour is set by bgcolor
    Also contains the image path entry box and associated controls"""
    bmp = []
    def __init__(self, parent, panel, app, parent_sizer, bgcolor, id=wx.ID_ANY, size=wx.DefaultSize, extended=0):
        self.bgcolor = bgcolor
        self.app = app
        self.panel = panel
        self.parent = parent
        wx.ScrolledWindow.__init__(self, panel, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        # Make controls for the image path entry box
        self.s_panel_flex = wx.FlexGridSizer(0,5,0,0)
            # Make controls
        # tcproject image class does some additional checking on the path to source images
        # which break this control
        self.control_imagepath = tcui.FileControl(self.panel, app, self.s_panel_flex, parent.get_active_image_path,
                                                  _gt("Source image location:"), _gt("tt_image_file_location"),
                                                  _gt("Choose an image file to open..."), "PNG files (*.png)|*.png",
                                                  _gt("Browse..."), _gt("tt_browse_input_file"), parent.get_active_savefile_path,
                                                  wx.FD_OPEN|wx.FD_FILE_MUST_EXIST, self.refresh_if_valid)

        self.impath_entry_reloadfile = wx.Button(self.panel, wx.ID_ANY)
        self.impath_entry_reloadfile.Bind(wx.EVT_BUTTON, self.OnReloadImage, self.impath_entry_reloadfile)

        # Add them to sizer...
        self.s_panel_flex.Add(self.impath_entry_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 3)
        self.s_panel_flex.AddGrowableCol(1)
        # Bind them to events
        # Add element to its parent sizer
        parent_sizer.Add(self.s_panel_flex, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.ALL, 4)

        self.s_panel_imagewindow = wx.BoxSizer(wx.HORIZONTAL)           # Right side (bottom part for the image window
        self.s_panel_imagewindow.Add(self, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 0)

        parent_sizer.Add(self.s_panel_imagewindow,1,wx.EXPAND, 0)

        self.lines = []
        self.x = self.y = 0
        self.drawing = False

        self.SetVirtualSize((1, 1))
        self.SetScrollRate(20,20)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

##        if extended == 1:
##            #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)
##            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
##            self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
##            self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
##            self.Bind(wx.EVT_MOTION, self.OnMotion)

        #Need to make intelligent buffer bitmap sizing work!
        self.buffer = wx.EmptyBitmap(4000,2500)
        self.lastisopos = (-1,-1)
        self.isopos = (-1,-1)

        self.lastpath = ""  # Stores the last path entered, to check for differences
        self.translate()    # Load the initial translation

    # Device Context events and methods
    def OnPaint(self, e):
        """Event handler for scrolled window repaint requests"""
        if self.IsDoubleBuffered():
            wx.PaintDC(self)
        else:
            wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.control_imagepath.translate()
        self.impath_entry_reloadfile.SetLabel(gt("Reload Image"))
        self.impath_entry_reloadfile.SetToolTipString(gt("tt_reload_input_file"))

    # Update refreshes both textbox (if it's changed) and the device context
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        self.control_imagepath.update()
        self.refresh_screen()

    def refresh_if_valid(self):
        """Called when child impath entry box text changes
        Only updates the displayed image if a new valid file has been entered"""
        debug("valid: %s, path: %s" % (self.app.activeproject.activeImage().valid_path(),self.app.activeproject.activeImage().path()))
        if self.app.activeproject.activeImage().valid_path() == self.app.activeproject.activeImage().path():
            # If valid_path and path are same, then refresh screen
            self.refresh_screen()

    def refresh_screen(self):
        """Refresh the screen display"""
        debug("imageWindow - refresh_screen")
        # Redraw the active image in the window, with mask etc.
        bitmap = self.app.activeproject.activeImage().bitmap()

        # Setup image properties for mask generation
        # If direction is 1 or 3, then reverse x/y to take account of irregular buildings
        if self.app.activeproject.active.direction in [1,3]:
            x = self.app.activeproject.y()
            y = self.app.activeproject.x()
        else:
            x = self.app.activeproject.x()
            y = self.app.activeproject.y()
        z = self.app.activeproject.z()
        p = self.app.activeproject.paksize()
        p2 = p/2
        p4 = p/4
        mask_offset_x, mask_offset_y = self.app.activeproject.offset()
        mask_width = (x + y) * p2
        mask_height = (x + y) * p4 + p2 + (z - 1) * p
        mask_width_off = mask_width + abs(mask_offset_x)
        mask_height_off = mask_height + abs(mask_offset_y)

        # Calculate the vertical and horizontal offsets (from the top-left of the screen) of the image bitmap
        # The origin for the cutting mask is the bottom-left corner of this bitmap

        # If xoffset -ve, draw bitmap that amount to the right, if xoffset +ve, align to left (value 0)
        if mask_offset_x < 0:
            bmp_offset_x = abs(mask_offset_x)
        else:
            bmp_offset_x = 0
        # If the bitmap's height is less than the mask (taking -ve offset into account) then need to move bitmap down by
        # the overlap
        if bitmap.GetHeight() < mask_height + mask_offset_y:
            bmp_offset_y = (mask_height + mask_offset_y) - bitmap.GetHeight()
        else:
            bmp_offset_y = 0


        # Set the size of the scrolled window to the size of the output
        # Height - will be either height of bitmap, or calculated height of mask (whichever is greater)
        # Width, same thing
        # -ve offset values for mask should count as positive for this calculation!
        self.SetVirtualSize((max(bitmap.GetWidth(),mask_width_off), max(bitmap.GetHeight(),mask_height_off)))

        if self.IsDoubleBuffered():
            dc = wx.ClientDC(self)
            self.PrepareDC(dc)            
        else:
            cdc = wx.ClientDC(self)
            self.PrepareDC(cdc)            
            dc = wx.BufferedDC(cdc, self.buffer)

        # Setup default brushes
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.SetPen(wx.Pen((255,0,0)))
##        dc.SetPen(wx.Pen(config.transparent))
        
        dc.SetBrush(wx.Brush((0,128,0)))
        dc.SetBrush(wx.Brush(config.transparent))
        # Clear ready for drawing
        dc.Clear()

        # Test rectangle to indicate virtual size area of DC (shows extent of mask at present however)
##        dc.DrawRectangle(bmp_offset_x,bitmap.GetHeight() + bmp_offset_y, mask_width_off, -mask_height_off)

        # Draw the bitmap
        dc.DrawBitmap(bitmap, bmp_offset_x, bmp_offset_y, True)

        # Then draw the mask
            # Draw x-dimension lines, top bits first
        for xx in range(1,x+1):
            # Find screen position for this tile
            pos = self.tileToScreen((xx, 1, 1), (x,y,z), (mask_offset_x,mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            if xx == x:
                # Draw vertical line all the way from the bottom of the tile to the top
                dc.DrawLine(pos[0],pos[1]-p4,           pos[0],pos[1]-p*z)
            else:
                # Draw vertical line only in the top quarter for tiles not at the edge
                dc.DrawLine(pos[0],pos[1]-p*z+p4,       pos[0],pos[1]-p*z)
            # Draw this tile's horizontal line section
            dc.DrawLine(pos[0],pos[1]-p*z,              pos[0]+p2,pos[1]-p*z)
            # Draw this tile's diagonal line section (bottom-right for x, bottom-left for y
            pos = self.tileToScreen((xx, y, 1), (x,y,z), (mask_offset_x,mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            dc.DrawLine(pos[0] + p-1,pos[1] - p4, pos[0]+p2-1,pos[1])
        for yy in range(1,y+1):
            pos = self.tileToScreen((1, yy, 1), (x,y,z), (mask_offset_x,mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            if yy == y:
                # -1's in the x values correct for line-drawing oddness here (line needs to be drawn at position 64, not 65 (1+psize)
                dc.DrawLine(pos[0]+(p-1),pos[1]-p4,     pos[0]+(p-1),pos[1]-p*z)
            else:
                dc.DrawLine(pos[0]+(p-1),pos[1]-p*z+p4, pos[0]+(p-1),pos[1]-p*z)
            dc.DrawLine(pos[0]+(p-1),pos[1]-p*z,        pos[0]+(p2-1),pos[1]-p*z)
            # Then the bottom ones
            pos = self.tileToScreen((x, yy, 1), (x,y,z), (mask_offset_x,mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            dc.DrawLine(pos[0],pos[1] - p4, pos[0]+p2,pos[1])

    # Take tile coords and convert into screen coords
    # This function is replicated in tc, and references to it should be made there!
    def tileToScreen(self, pos, dims, off, p, screen_height=None):
        """Take tile coords and convert to screen coords
        by default converts into bottom-left screen coords, but with height attribute supplied converts to top-left
        returns the bottom-left position of the tile on the screen"""
        offx, offy = off
        if offx < 0:
            offx = 0
        xpos, ypos, zpos = pos
        xdims, ydims, zdims = dims
        xx = ((ypos - xpos) + (xdims - 1)) * (p/2) + offx
        yy = ((xdims - xpos) + (ydims - ypos)) * (p/4) + ((zpos - 1) * p) + offy
        if screen_height != None:
            yy = screen_height - yy
        return (xx,yy)

    def OnReloadImage(self,e):
        """When reload image button clicked"""
        debug("Reload active image...")
        self.app.activeproject.activeImage().reloadImage()
        self.update()

