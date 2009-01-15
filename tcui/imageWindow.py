# coding: UTF-8
#
# TileCutter, User Interface Module - imageWindow
#
import os, wx, imres, tcui, tc

# Utility functions
import translator
gt = translator.Translator()

from debug import DebugFrame as debug

class imageWindow(wx.ScrolledWindow, tcui.fileTextBox):
    """Window onto which bitmaps may be drawn, background colour is set by bgcolor
    Also contains the image path entry box and associated controls"""
    bmp = []
    def __init__(self, parent, app, parent_sizer, bgcolor, id=wx.ID_ANY, size=wx.DefaultSize, extended=0):
        self.bgcolor = bgcolor
        self.app = app
        self.parent = parent
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        # Make controls for the image path entry box
        self.s_panel_imagewindow_path = wx.FlexGridSizer(0,6,0,0)
            # Make controls
        self.impath_entry_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.impath_entry_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)
        self.impath_entry_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
##        self.impath_entry_icon = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["FileReload"].getBitmap())
        self.impath_entry_icon = wx.StaticBitmap(parent, wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
        self.impath_entry_filebrowse = wx.Button(parent, wx.ID_ANY, "")
        self.impath_entry_reloadfile = wx.BitmapButton(parent, wx.ID_ANY, size=(25,-1), bitmap=imres.catalog["FileReload"].getBitmap())
        self.impath_entry_sameforall = wx.BitmapButton(parent, wx.ID_ANY, size=(25,-1), bitmap=imres.catalog["FileSameForAll"].getBitmap())
            # Add them to sizer...
        self.s_panel_imagewindow_path.Add(self.impath_entry_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_imagewindow_path.Add(self.impath_entry_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 2)
        self.s_panel_imagewindow_path.Add(self.impath_entry_icon, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 4)
        self.s_panel_imagewindow_path.Add(self.impath_entry_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 4)
        self.s_panel_imagewindow_path.Add(self.impath_entry_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_imagewindow_path.Add(self.impath_entry_sameforall, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_imagewindow_path.AddGrowableCol(1)
            # Bind them to events
        self.impath_entry_box.Bind(wx.EVT_TEXT, self.OnTextChange, self.impath_entry_box)
        self.impath_entry_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseSource, self.impath_entry_filebrowse)
        self.impath_entry_reloadfile.Bind(wx.EVT_BUTTON, self.OnReloadImage, self.impath_entry_reloadfile)
        self.impath_entry_sameforall.Bind(wx.EVT_BUTTON, self.OnLoadImageForAll, self.impath_entry_sameforall)
            # Add element to its parent sizer
        parent_sizer.Add(self.s_panel_imagewindow_path, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)

        self.s_panel_imagewindow = wx.BoxSizer(wx.HORIZONTAL)           # Right side (bottom part for the image window
        self.s_panel_imagewindow.Add(self, 1, wx.EXPAND, 4)

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
        self.impath_entry_label.SetLabel(gt("Source image location:"))
        self.impath_entry_box.SetToolTipString(gt("ttinputpath"))
        self.impath_entry_filebrowse.SetLabel(gt("Browse..."))
        self.impath_entry_filebrowse.SetToolTipString(gt("ttbrowseinputfile"))
        self.impath_entry_reloadfile.SetToolTipString(gt("ttreloadinputfile"))
        self.impath_entry_sameforall.SetToolTipString(gt("ttsamefileforall"))

    # Update refreshes both textbox (if it's changed) and the device context
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Setting these values should also cause text highlighting to occur
        if self.impath_entry_box.GetValue() != self.app.activeproject.activeImage().path() and self.impath_entry_box.GetValue() != self.app.activeproject.activeImage().lastpath():
            self.impath_entry_box.SetValue(self.app.activeproject.activeImage().path())
        # And then redraw the active image in the window, with mask etc.
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
        dc.SetBrush(wx.Brush((0,128,0)))
        # Clear ready for drawing
        dc.Clear()

        # Test rectangle to indicate virtual size area of DC (shows extent of mask at present however)
        dc.DrawRectangle(bmp_offset_x,bitmap.GetHeight() + bmp_offset_y, mask_width_off, -mask_height_off)

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

    # Image path entry events and methods
    def OnTextChange(self,e):
        """When text changes in the entry box"""
        # If text has actually changed (i.e. it's different to that set in the image's info)
        if self.impath_entry_box.GetValue() != self.app.activeproject.activeImage().path() and self.impath_entry_box.GetValue() != self.app.activeproject.activeImage().lastpath():
            debug("Text changed in image path box, new text: " + self.impath_entry_box.GetValue())
            # Check whether the entered path exists or not, if it does update the value in the activeproject (which will cause
            # that new image to be loaded & displayed) if not don't set this value
            if os.path.isfile(self.impath_entry_box.GetValue()) and os.path.splitext(self.impath_entry_box.GetValue())[1] in self.app.VALID_IMAGE_EXTENSIONS:
                # Is a valid file, display green tick icon
                debug("...new text is a valid file")
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
                # Update the active image with the new path
                self.app.activeproject.activeImage().path(self.impath_entry_box.GetValue())
                # Then redraw the image
                self.update()
            else:
                # Not a valid file, display red cross icon
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK))
                debug("...but new text not a valid file!")
                # Highlight text function only needed if it isn't a valid file, obviously
                self.highlightText(self.impath_entry_box, self.impath_entry_box.GetValue())
            # Update the last path
            self.app.activeproject.activeImage().lastpath(self.impath_entry_box.GetValue())
    def OnBrowseSource(self,e):
        """When browse source button clicked"""
        value = self.filePickerDialog(self.app.activeproject.activeImage().path(), "", gt("Choose a source image for this view:"),
                                      "PNG files (*.png)|*.png", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        self.impath_entry_box.SetValue(value)
    def OnReloadImage(self,e):
        """When reload image button clicked"""
        self.app.activeproject.activeImage().reloadImage()
        self.update()
    def OnLoadImageForAll(self,e):
        """When "load same image for all" button is clicked"""
