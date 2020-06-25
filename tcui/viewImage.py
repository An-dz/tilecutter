# TileCutter User Interface Module
#        Image/Editor view

import logging
import wx
import config, tcui
config = config.Config()


class ViewImage(wx.Panel):
    """Window onto which bitmaps may be drawn, background colour is set by bgcolor
    Also contains the image path entry box and associated controls"""
    bmp = []

    def __init__(self, parent, app, bgcolor, extended=0):
        logging.info("Create image display area")

        wx.Panel.__init__(self, parent=parent.panel, id=wx.ID_ANY)
        self.bgcolor = bgcolor
        self.app = app
        self.parent = parent
        self.scrolledwindow = wx.ScrolledWindow(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)

        # Required for wx.AutoBufferedPaintDC to work
        self.scrolledwindow.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.control_imagepath = tcui.ControlImageFile(self, app)

        # Add all items to panel's sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control_imagepath, 0, wx.EXPAND | wx.ALL, 4)
        self.sizer.Add(self.scrolledwindow,    1, wx.EXPAND,          0)

        self.SetSizer(self.sizer)

        self.lines = []
        self.x = self.y = 0
        self.drawing = False

        self.scrolledwindow.SetVirtualSize((1, 1))
        self.scrolledwindow.SetScrollRate(20, 20)
        self.scrolledwindow.Bind(wx.EVT_PAINT, self.OnPaint, self.scrolledwindow)

        ## if extended == 1:
        ##     #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)
        ##     self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        ##     self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        ##     self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        ##     self.Bind(wx.EVT_MOTION, self.OnMotion)

        # Need to make intelligent buffer bitmap sizing work!
        self.buffer = wx.Bitmap(4000, 2500)
        self.lastisopos = (-1, -1)
        self.isopos     = (-1, -1)

        self.lastpath = ""  # Stores the last path entered, to check for differences
        self.translate()    # Load the initial translation

        # Transparent grid background
        self.transparent_bg = wx.Bitmap(16, 16)
        tdc = wx.MemoryDC()
        tdc.SelectObject(self.transparent_bg)
        tdc.SetBackground(wx.Brush(config.transparent_bg[0]))
        tdc.Clear()
        tdc.SetPen(wx.Pen(config.transparent_bg[1]))
        tdc.SetBrush(wx.Brush(config.transparent_bg[1]))
        tdc.DrawRectangle(0, 0,  8,  8)
        tdc.DrawRectangle(8, 8, 15, 15)
        tdc.SelectObject(wx.NullBitmap)

    # Device Context events and methods
    def OnPaint(self, e):
        """Event handler for scrolled window repaint requests"""
        logging.info("Painting")
        dc = wx.AutoBufferedPaintDC(self.scrolledwindow)
        self.refresh_screen(dc)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("Translate UI")
        self.control_imagepath.translate()

    # Update refreshes both textbox (if it's changed) and the device context
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        logging.info("Update controls and context")
        self.control_imagepath.update()
        self.scrolledwindow.Refresh()

    def refresh_if_valid(self):
        """Called when child in path entry box text changes
        Only updates the displayed image if a new valid file has been entered"""
        ## logging.debug("valid: %s, path: %s" % (self.app.activeproject.active_image().valid_path(), self.app.activeproject.active_image().path()))
        ## if self.app.activeproject.active_image().valid_path() == self.app.activeproject.active_image().path():
        ##     # If valid_path and path are same, then refresh screen
        ##     self.Refresh()
        # Always refresh the screen to show either blank/noimage graphic or the valid graphic
        logging.info("new image path: %s, calling Refresh()" % self.app.activeproject.active_image_path())
        self.app.activeproject.reload_active_image()
        self.scrolledwindow.Refresh()

    def refresh_screen(self, dc):
        """Refresh the screen display"""
        logging.info("Update view")

        # Redraw the active image in the window, with mask etc.
        bitmap = self.app.activeproject.get_active_bitmap()
        transparency = self.app.activeproject.transparency()

        # Setup image properties for mask generation
        # If direction is 1 or 3, then reverse x/y to take account of irregular buildings
        if self.app.activeproject.direction() in [1, 3]:
            x = self.app.activeproject.y()
            y = self.app.activeproject.x()
        else:
            x = self.app.activeproject.x()
            y = self.app.activeproject.y()

        z = self.app.activeproject.z()
        p = self.app.activeproject.paksize()
        p2 = p / 2
        p4 = p / 4
        mask_offset_x, mask_offset_y = self.app.activeproject.active_offset()
        mask_width  = (x + y) * p2
        mask_height = (x + y) * p4 + p2 + (z - 1) * p
        mask_width_off  = mask_width  + abs(mask_offset_x)
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
        self.scrolledwindow.SetVirtualSize((max(bitmap.GetWidth(), mask_width_off), max(bitmap.GetHeight(), mask_height_off)))

        ## if self.IsDoubleBuffered():
        ##     dc = pdc
        ## else:
        ##     #cdc = wx.ClientDC(self)
        ##     dc = wx.BufferedDC(pdc, self.buffer)

        self.scrolledwindow.DoPrepareDC(dc)

        # Setup default brushes
        dc.SetBackground(wx.Brush(self.bgcolor))
        # Clear ready for drawing
        dc.Clear()

        # Transparent grid background
        if transparency:
            dc.SetPen(wx.Pen((0, 0, 0), style=wx.PENSTYLE_TRANSPARENT))
            dc.SetBrush(wx.Brush(self.transparent_bg))
        else:
            dc.SetPen(wx.Pen(self.bgcolor))
            dc.SetBrush(wx.Brush(self.bgcolor))

        w, h = self.scrolledwindow.GetVirtualSize()
        # +50 because I have no idea how to get the "real virtual" size
        dc.DrawRectangle(0, 0, w + 50, h + 50)

        # Mask colour
        dc.SetPen(wx.Pen((255, 0, 0)))

        # DEBUG: Test rectangle to indicate virtual size area of DC (shows extent of mask at present however)
        ## dc.DrawRectangle(bmp_offset_x,bitmap.GetHeight() + bmp_offset_y, mask_width_off, -mask_height_off)

        # Draw the bitmap
        dc.DrawBitmap(bitmap, bmp_offset_x, bmp_offset_y, True)

        # Then draw the mask
        # Draw x-dimension lines, top bits first
        for xx in range(1, x + 1):
            # Find screen position for this tile
            pos = self.tile_to_screen((xx, 1, 1), (x, y, z), (mask_offset_x, mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)

            if xx == x:
                # Draw vertical line all the way from the bottom of the tile to the top
                dc.DrawLine(pos[0],         pos[1] - p4,           pos[0],          pos[1] - (p * z))
            else:
                # Draw vertical line only in the top quarter for tiles not at the edge
                dc.DrawLine(pos[0],         pos[1] - (p * z) + p4, pos[0],          pos[1] - (p * z))

            # Draw this tile's horizontal line section
            dc.DrawLine(    pos[0],         pos[1] - (p * z),      pos[0] + p2,     pos[1] - (p * z))
            # Draw this tile's diagonal line section (bottom-right for x, bottom-left for y
            pos = self.tile_to_screen((xx, y, 1), (x, y, z), (mask_offset_x, mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            dc.DrawLine(    pos[0] + p - 1, pos[1] - p4,           pos[0] + p2 - 1, pos[1])

        for yy in range(1, y + 1):
            pos = self.tile_to_screen((1, yy, 1), (x, y, z), (mask_offset_x, mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)

            if yy == y:
                # -1's in the x values correct for line-drawing oddness here (line needs to be drawn at position 64, not 65 (1+psize)
                dc.DrawLine(pos[0] + p - 1, pos[1] - p4,           pos[0] + p  - 1, pos[1] - (p * z))
            else:
                dc.DrawLine(pos[0] + p - 1, pos[1] - (p * z) + p4, pos[0] + p  - 1, pos[1] - (p * z))

            dc.DrawLine(    pos[0] + p - 1, pos[1] - (p * z),      pos[0] + p2 - 1, pos[1] - (p * z))
            # Then the bottom ones
            pos = self.tile_to_screen((x, yy, 1), (x, y, z), (mask_offset_x, mask_offset_y), p, bitmap.GetHeight() + bmp_offset_y)
            dc.DrawLine(    pos[0],         pos[1] - p4,           pos[0] + p2,     pos[1])

        logging.debug("Done")

    # Take tile coords and convert into screen coords
    # This function is replicated in tc, and references to it should be made there!
    def tile_to_screen(self, pos, dims, off, p, screen_height=None):
        """Take tile coords and convert to screen coords
        by default converts into bottom-left screen coords,
        but with height attribute supplied converts to top-left
        returns the bottom-left position of the tile on the screen"""
        logging.info("Converting tile coords to screen coords")

        offx, offy = off

        if offx < 0:
            offx = 0

        xpos,  ypos,  zpos  = pos
        xdims, ydims, zdims = dims
        xx = ((ypos  - xpos) + (xdims -    1)) * (p / 2) + offx
        yy = ((xdims - xpos) + (ydims - ypos)) * (p / 4) + ((zpos - 1) * p) + offy

        if screen_height is not None:
            yy = screen_height - yy

        return (xx, yy)
