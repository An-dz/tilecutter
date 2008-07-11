#
# TileCutter, version 0.5 (rewrite)
#

# Todo:
# Finish output file boxes, switching them to use the new set of functions
# Do the project save/load/new etc. and management functionality (using pickle)
# Program settings, load from a config file (using configparser), later implement dialog to set these
# Implement use of special menu IDs to make menus work properly on, e.g., mac osx
# Produce frames picker control
# Offset/Mask control - internal functions, click modifies model & triggers redrawing
# Dims control - click modifies model & triggers redrawing
# Direction/Season/Dims - trigger redrawing

# Translation system (look into changing translations on-the-fly, but not that important)
# Probably best to just destroy the app window and recreate it with the correct translation, keeping the program running
# Menu translations

# Current view context built into activeproject, details of the currently selected view (persistent across saves)
# Implement current view context to all view controls, need to update based on this setting in activeproject
# Source image control (needs current view context)
# -> File must exist
# -> Implement modal dialog for browse
# -> Allow text entry, highlight in red if file does not exist??
# -> Implement modal confirmation dialog for "open same file for all" button
# "Warning, this will set all views and frames in the project to use the current image, proceed?"
# -> Function to reload the current view's image (flush the cache and redraw, essentially)

# Move most of the UI classes, app etc. into a module, to enhance loading speed
# Replace all ID's of -1 with wx.ID_ANY

# Add the TileCutter icon
# About dialog
# Make py2exe, look into producing smaller packages
# Look into producing more mac-native package
# Same for linux, platform native packages
# Test with Linux, Mac OSX, Windows (xp), try and have the same code across all platforms!
# Produce help documentation
# -> Quick start guide (interface should be fairly self-explanatory though)



# Aims v.0.5

# Rewrite core cutting engine and output engine
# Produce minimal testing UI
#   - Set X/Y/Z dims, X/Y offsets, facing/season
#   - Determine output .png, .dat etc.
# Debugging system with nice output

# Aims v.0.6

# Extend UI, include dat editor
# Translation function implemented
# Start to build project management/switching and save/load functions

# Hack to make PIL work with py2exe
import Image
import PngImagePlugin
import JpegImagePlugin
import GifImagePlugin
import BmpImagePlugin
Image._initialized=2

import wx
##import wx.lib.masked as masked
##import wx.lib.scrolledpanel as scrolled
##import wx.lib.hyperlink as hl

import sys, os

import tc, tcproject

# Init variables
debug_on = 1

VERSION_NUMBER = "0.5a"
##TRANSPARENT = (231,255,255)
TRANSPARENT = (0,0,0)
DEFAULT_PAKSIZE = "64"
### SB_WIDTH may be different on other platforms...
##SCROLLBAR_WIDTH = 16

# Lists of values for choicelists, also provides acceptable values for the project class
# Also set in tcproject module
choicelist_anim = ["0",]
choicelist_paksize_int = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240]
choicelist_paksize = ["16","32","48","64","80","96","112","128","144","160","176","192","208","224","240"]
choicelist_views_int = [1,2,4]
choicelist_views = ["1","2","4"]
choicelist_dims_int = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
choicelist_dims = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
choicelist_dims_z_int = [1,2,3,4]
choicelist_dims_z = ["1","2","3","4"]

# Temporary translation function
def gt(text):
    return text

class ImageWindow(wx.ScrolledWindow):
    """Window onto which bitmaps may be drawn, background colour is TRANSPARENT"""
    bmp = []
    def __init__(self, parent, id = wx.ID_ANY, size = wx.DefaultSize, extended=0):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.bmp = wx.EmptyBitmap(1,1)
        self.lines = []
        self.x = self.y = 0
        self.drawing = False

        self.SetVirtualSize((1, 1))
        self.SetScrollRate(20,20)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        if extended == 1:
            #self.Bind(wx.EVT_LEFT_DOWN, self.Draww)
            self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
##            self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
##            self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            self.Bind(wx.EVT_MOTION, self.OnMotion)

        #Need to make intelligent buffer bitmap sizing work!
        
        self.buffer = wx.EmptyBitmap(4000,2500)
        dc = wx.BufferedDC(None, self.buffer)
        dc.SetBackground(wx.Brush(TRANSPARENT))
        dc.Clear()
        self.DrawBitmap(dc)
        self.lastisopos = (-1,-1)
        self.isopos = (-1,-1)

    def OnPaint(self, e):
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)
    def DrawBitmap(self, dc):
        bitmap = self.bmp
        #self.buffer.SetWidth(bitmap.GetWidth())
        #self.buffer.SetHeight(bitmap.GetHeight())
        self.SetVirtualSize((bitmap.GetWidth(), bitmap.GetHeight()))
        if dc == 1:
            cdc = wx.ClientDC(self)
            self.PrepareDC(cdc)            
            dc = wx.BufferedDC(cdc, self.buffer)
        dc.SetBackground(wx.Brush(TRANSPARENT))
        dc.Clear()
        dc.DrawBitmap(bitmap, 0, 0, True)   # Invokes OnDraw method

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


class seasonControl(wx.StaticBox):
    """Box containing season alteration controls"""
    def __init__(self,parent,parent_sizer,imres):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Season"))
        self.imres = imres
            # Setup sizers
        self.s_seasons = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_seasons_flex.AddGrowableCol(1)
            # Add items
        self.seasons_select_summer_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.summer)
        self.seasons_select_summer = wx.RadioButton(parent, wx.ID_ANY, gt("Summer"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.seasons_select_summer.SetToolTipString(gt("tt_seasons_select_summer"))
        self.seasons_select_winter_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.winter)
        self.seasons_select_winter = wx.RadioButton(parent, wx.ID_ANY, gt("Winter"), (-1,-1), (-1,-1))
        self.seasons_select_winter.SetToolTipString(gt("tt_seasons_select_winter"))
        self.seasons_enable_winter = wx.CheckBox(parent, wx.ID_ANY, gt("Enable Winter"), (-1,-1), (-1,-1))
        self.seasons_enable_winter.SetToolTipString(gt("tt_seasons_enable_winter"))
            # Add to sizers
        self.s_seasons_flex.Add(self.seasons_select_summer_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_seasons_flex.Add(self.seasons_select_summer, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons_flex.Add(wx.Size(1,1))
        self.s_seasons_flex.Add(self.seasons_enable_winter, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons.Add(self.s_seasons_flex, 0, wx.RIGHT, 0)
            # Bind functions
        self.seasons_enable_winter.Bind(wx.EVT_CHECKBOX, self.OnToggle, self.seasons_enable_winter)
        self.seasons_select_summer.Bind(wx.EVT_RADIOBUTTON, self.OnSummer, self.seasons_select_summer)
        self.seasons_select_winter.Bind(wx.EVT_RADIOBUTTON, self.OnWinter, self.seasons_select_winter)

            # Add element to its parent sizer
        parent_sizer.Add(self.s_seasons, 0, wx.EXPAND, 0)

        self.update()    # Init this control with the default values from the active project

    def OnToggle(self,e):
        """Toggling between summer and winter imagesf"""
        activeproject.winter(self.seasons_enable_winter.GetValue())
        self.update()
    def OnSummer(self,e):
        """Toggle Summer image"""
        # Set active image to Summer
        # Redraw active image
    def OnWinter(self,e):
        """Toggle Winter image"""
        # Set active image to Winter
        # Redraw active image
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if activeproject.winter() == 0:  # Turn winter image off
            self.seasons_enable_winter.SetValue(0)
            # If currently have winter image selected, switch to summer image
            self.seasons_select_summer.SetValue(1)
##            self.images_select_front.SetValue(0)
            # Then disable the control
            self.seasons_select_winter.Disable()
        else:
            self.seasons_enable_winter.SetValue(1)
            # User must select the winter image if they wish to view it, so just enable the control
            self.seasons_select_winter.Enable()

class imageControl(wx.StaticBox):
    """Box containing Front/Back image controls"""
    def __init__(self,parent,parent_sizer,imres):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Image"))
        self.imres = imres
            # Setup sizers
        self.s_images = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_images_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_images_flex.AddGrowableCol(1)
            # Add items
        self.images_select_back_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.back)
        self.images_select_back = wx.RadioButton(parent, wx.ID_ANY, gt("BackImage"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.images_select_back.SetToolTipString(gt("tt_images_select_back"))
        self.images_select_front_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.front)
        self.images_select_front = wx.RadioButton(parent, wx.ID_ANY, gt("FrontImage"), (-1,-1), (-1,-1))
        self.images_select_front.SetToolTipString(gt("tt_images_select_front"))
        self.images_enable_front = wx.CheckBox(parent, wx.ID_ANY, gt("Enable FrontImage"), (-1,-1), (-1,-1))
        self.images_enable_front.SetToolTipString(gt("tt_images_enable_front"))
            # Add to sizers
        self.s_images_flex.Add(self.images_select_back_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_images_flex.Add(self.images_select_back, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images_flex.Add(self.images_select_front_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_images_flex.Add(self.images_select_front, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images_flex.Add(wx.Size(1,1))
        self.s_images_flex.Add(self.images_enable_front, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images.Add(self.s_images_flex, 1, wx.RIGHT, 0)
            # Bind events
        self.images_enable_front.Bind(wx.EVT_CHECKBOX, self.OnToggle, self.images_enable_front)
        self.images_select_back.Bind(wx.EVT_RADIOBUTTON, self.OnBackImage, self.images_select_back)
        self.images_select_front.Bind(wx.EVT_RADIOBUTTON, self.OnFrontImage, self.images_select_front)
            # Add element to its parent sizer
        parent_sizer.Add(self.s_images, 0, wx.EXPAND, 0)
        self.update()    # Init this control with the default values from the active project

    def OnToggle(self,e):
        """Toggling frontimage on and off"""
        activeproject.frontimage(self.images_enable_front.GetValue())
        self.update()
    def OnBackImage(self,e):
        """Toggle BackImage on"""
        # Set active image to Back
        # Redraw active image
    def OnFrontImage(self,e):
        """Toggle FrontImage on"""
        # Set active image to Front
        # Redraw active image
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if activeproject.frontimage() == 0:  # Turn frontimage off
            self.images_enable_front.SetValue(0)
            # If currently have frontimage selected, switch to backimage
            self.images_select_back.SetValue(1)
##            self.images_select_front.SetValue(0)
            # Then disable the control
            self.images_select_front.Disable()
        else:
            self.images_enable_front.SetValue(1)
            # User must select the frontimage if they wish to view it, so just enable the control
            self.images_select_front.Enable()

class facingControl(wx.StaticBox):
    """Box containing direction facing controls"""
    def __init__(self,parent,parent_sizer,imres):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Direction Facing"))
        self.imres = imres
            # Setup sizers
        self.s_facing = wx.StaticBoxSizer(self, wx.HORIZONTAL)
        self.s_facing_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_facing_flex.AddGrowableCol(1)
        self.s_facing_right = wx.BoxSizer(wx.VERTICAL)
        self.s_facing_1 = wx.BoxSizer(wx.HORIZONTAL)
            # Add items
        self.facing_select_south_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.south)
        self.facing_select_south = wx.RadioButton(parent, wx.ID_ANY, gt("South"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.facing_select_south.SetToolTipString(gt("tt_facing_select_south"))
        self.facing_select_east_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.east)
        self.facing_select_east = wx.RadioButton(parent, wx.ID_ANY, gt("East"), (-1,-1), (-1,-1))
        self.facing_select_east.SetToolTipString(gt("tt_facing_select_east"))
        self.facing_select_north_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.north)
        self.facing_select_north = wx.RadioButton(parent, wx.ID_ANY, gt("North"), (-1,-1), (-1,-1))
        self.facing_select_north.SetToolTipString(gt("tt_facing_select_north"))
        self.facing_select_west_im = wx.StaticBitmap(parent, wx.ID_ANY, self.imres.west)
        self.facing_select_west = wx.RadioButton(parent, wx.ID_ANY, gt("West"), (-1,-1), (-1,-1))
        self.facing_select_west.SetToolTipString(gt("tt_facing_select_west"))
        self.facing_enable_label = wx.StaticText(parent, wx.ID_ANY, gt("Number\nof views:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_enable_select = wx.ComboBox(parent, wx.ID_ANY, "1", (-1, -1), (54, -1), ["1","2","4"], wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        self.facing_enable_select.SetToolTipString(gt("tt_facing_enable_select"))
            # Add to sizers
        self.s_facing_flex.Add(self.facing_select_south_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_south, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_east_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_east, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_north_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_north, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_west_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_west, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)

        self.s_facing_right.Add(self.facing_enable_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 0)
        self.s_facing_right.Add(self.facing_enable_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 0)
        self.s_facing_1.Add(self.s_facing_flex, 0, wx.RIGHT, 0)
        self.s_facing_1.Add(self.s_facing_right, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.s_facing.Add(self.s_facing_1, 1, wx.RIGHT, 0)
            # Bind events
        self.facing_enable_select.Bind(wx.EVT_COMBOBOX, self.OnToggle, self.facing_enable_select)
        self.facing_select_south.Bind(wx.EVT_RADIOBUTTON, self.OnSouth, self.facing_select_south)
        self.facing_select_east.Bind(wx.EVT_RADIOBUTTON, self.OnEast, self.facing_select_east)
        self.facing_select_north.Bind(wx.EVT_RADIOBUTTON, self.OnNorth, self.facing_select_north)
        self.facing_select_west.Bind(wx.EVT_RADIOBUTTON, self.OnWest, self.facing_select_west)

            # Add element to its parent sizer
        parent_sizer.Add(self.s_facing, 0, wx.EXPAND, 0)
        self.update()    # Init this control with the default values from the active project

    def OnToggle(self,e):
        """Changing the value in the selection box"""
        activeproject.views(self.facing_enable_select.GetValue())
        self.update()
    def OnSouth(self,e):
        """Toggle South direction"""
        # Set active image to South
        # Redraw active image
    def OnEast(self,e):
        """Toggle East direction"""
        # Set active image to East
        # Redraw active image
    def OnNorth(self,e):
        """Toggle North direction"""
        # Set active image to North
        # Redraw active image
    def OnWest(self,e):
        """Toggle West direction"""
        # Set active image to West
        # Redraw active image
    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if activeproject.views() == 1:
            self.facing_enable_select.SetValue(choicelist_views[0])
            self.facing_select_south.Enable()
            self.facing_select_east.Disable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_east.GetValue() == True or self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_south.SetValue(1)
        elif activeproject.views() == 2:
            self.facing_enable_select.SetValue(choicelist_views[1])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_east.SetValue(1)
        else:
            self.facing_enable_select.SetValue(choicelist_views[2])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Enable()
            self.facing_select_west.Enable()

class dimsControl(wx.StaticBox):
    """Box containing dimensions controls"""
    def __init__(self,parent,parent_sizer,imres):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Dimensions"))
        self.imres = imres
            # Setup sizers
        self.s_dims = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_dims_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_dims_flex.AddGrowableCol(1)
            # Add items
        self.dims_p_label = wx.StaticText(parent, wx.ID_ANY, gt("Paksize"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_p_select = wx.ComboBox(parent, wx.ID_ANY, DEFAULT_PAKSIZE, (-1, -1), (54, -1), choicelist_paksize, wx.CB_READONLY)
        self.dims_p_select.SetToolTipString(gt("tt_dims_paksize_select"))
        self.dims_z_label = wx.StaticText(parent, wx.ID_ANY, gt("Z dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_z_select = wx.ComboBox(parent, wx.ID_ANY, "1", (-1, -1), (54, -1), choicelist_dims_z, wx.CB_READONLY)
        self.dims_z_select.SetToolTipString(gt("tt_dims_z_select"))
        self.dims_x_label = wx.StaticText(parent, wx.ID_ANY, gt("X dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_x_select = wx.ComboBox(parent, wx.ID_ANY, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.dims_x_select.SetToolTipString(gt("tt_dims_x_select"))
        self.dims_y_label = wx.StaticText(parent, wx.ID_ANY, gt("Y dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_y_select = wx.ComboBox(parent, wx.ID_ANY, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.dims_y_select.SetToolTipString(gt("tt_dims_y_select"))
            # Add to sizers
        self.s_dims_flex.Add(self.dims_p_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 3)
        self.s_dims_flex.Add(self.dims_x_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, 3)
        self.s_dims_flex.Add(self.dims_p_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT|wx.BOTTOM, 3)
        self.s_dims_flex.Add(self.dims_x_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.BOTTOM, 3)
        self.s_dims_flex.Add(self.dims_z_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 3)
        self.s_dims_flex.Add(self.dims_y_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, 3)
        self.s_dims_flex.Add(self.dims_z_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 3)
        self.s_dims_flex.Add(self.dims_y_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT, 3)
        self.s_dims.Add(self.s_dims_flex, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
            # Bind functions
            # Add element to its parent sizer
        parent_sizer.Add(self.s_dims, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)

class offsetControl(wx.StaticBox):
    """Box containing offset controls"""
    def __init__(self,parent,parent_sizer,imres):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Offset/Mask"))
        self.imres = imres
            # Setup sizers
        self.s_offset = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0,4,0,0)
            # Add items
        self.offset_button_up = wx.BitmapButton(parent, wx.ID_ANY, self.imres.up2, (-1,-1), (18,18))
        self.offset_button_up.SetToolTipString(gt("tt_offset_button_up"))
        self.offset_button_left = wx.BitmapButton(parent, wx.ID_ANY, self.imres.left2, (-1,-1), (18,18))
        self.offset_button_left.SetToolTipString(gt("tt_offset_button_left"))
        self.offset_button_reset = wx.BitmapButton(parent, wx.ID_ANY, self.imres.center, (-1,-1), (18,18))
        self.offset_button_reset.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_right = wx.BitmapButton(parent, wx.ID_ANY, self.imres.right2, (-1,-1), (18,18))
        self.offset_button_right.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_down = wx.BitmapButton(parent, wx.ID_ANY, self.imres.down2, (-1,-1), (18,18))
        self.offset_button_down.SetToolTipString(gt("tt_offset_button_down"))
        self.offset_selector = wx.CheckBox(parent, wx.ID_ANY, gt("Fine"), (-1,-1), (-1,-1))
        self.offset_selector.SetToolTipString(gt("tt_offset_selector"))
            # Add to sizers
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_button_up, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_selector, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
        self.s_offset_flex.Add(self.offset_button_left, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_reset, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_right, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_button_down, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset.Add(self.s_offset_flex, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
            # Bind functions
            # Add element to its parent sizer
        parent_sizer.Add(self.s_offset, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)
    

class imagePathControl:
    """Image path entry control, with browse, reload image and "load same image for all" buttons"""
    def __init__(self,parent,parent_sizer,imres,label):
        """Produce all of the controls, which are placed within a sizer"""
        self.imres = imres
            # Sizer for these controls
        self.s_panel_imagewindow_path = wx.FlexGridSizer(0,5,0,0)
            # Next the lower DC controls
        self.impath_entry_label = wx.StaticText(parent, wx.ID_ANY, label, (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.impath_entry_box = wx.TextCtrl(parent, wx.ID_ANY, value="")#, style=wx.TE_READONLY)
        self.impath_entry_box.SetToolTipString(gt("ttinputpath"))
        self.impath_entry_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.impath_entry_filebrowse = wx.Button(parent, wx.ID_ANY, label=gt("Browse..."))
        self.impath_entry_filebrowse.SetToolTipString(gt("ttbrowseinputfile"))
        self.impath_entry_reloadfile = wx.BitmapButton(parent, wx.ID_ANY, size=(25,-1), bitmap=self.imres.reload)
        self.impath_entry_reloadfile.SetToolTipString(gt("ttreloadinputfile"))
        self.impath_entry_sameforall = wx.BitmapButton(parent, wx.ID_ANY, size=(25,-1), bitmap=self.imres.sameforall)
        self.impath_entry_sameforall.SetToolTipString(gt("ttsamefileforall"))
            # Add them to sizer...
        self.s_panel_imagewindow_path.Add(self.impath_entry_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_imagewindow_path.Add(self.impath_entry_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_imagewindow_path.Add(self.impath_entry_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_imagewindow_path.Add(self.impath_entry_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_imagewindow_path.Add(self.impath_entry_sameforall, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_imagewindow_path.AddGrowableCol(1)
            # Bind them to events
##        self.impath_entry_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseSource, self.impath_entry_filebrowse)
##        self.impath_entry_reloadfile.Bind(wx.EVT_BUTTON, self.OnReloadImage, self.impath_entry_reloadfile)
##        self.impath_entry_sameforall.Bind(wx.EVT_BUTTON, self.OnLoadImageForAll, self.impath_entry_sameforall)
            # Add element to its parent sizer
        parent_sizer.Add(self.s_panel_imagewindow_path, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)

class fileControls:
    """Controls at the bottom of the window, file output locations"""
    def __init__(self,parent,parent_sizer,imres):
        """Produce controls, two file path entries"""
        self.parent = parent
        self.imres = imres
            # Bottom panel sizers
        self.s_panel_bottom_left = wx.FlexGridSizer(0,3,0,0)    # Contains paths for output .dat and .png
            # Dat/pak output path entry
        self.dat_outpath_label = wx.StaticText(parent, wx.ID_ANY, gt("Output Dat or Pak File Location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dat_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.dat_outpath_box.SetToolTipString(gt("tt_output_dat_file_location"))
        self.dat_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.dat_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label=gt("Browse..."))
        self.dat_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_dat_file_location"))
            # Add them to sizer...
        self.s_panel_bottom_left.Add(self.dat_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.dat_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangeDat, self.dat_outpath_box)
        self.dat_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseDat, self.dat_outpath_filebrowse)

            # Image output path entry
        self.im_outpath_label = wx.StaticText(parent, wx.ID_ANY, gt("Path from .dat to .png:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.im_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="images\\", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.im_outpath_box.SetToolTipString(gt("tt_output_image_location"))
        self.im_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.im_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label=gt("Browse..."))
        self.im_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_image_location"))
            # Add to sizer...
        self.s_panel_bottom_left.Add(self.im_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.im_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangePng, self.im_outpath_box)
        self.im_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowsePng, self.im_outpath_filebrowse)
        parent_sizer.Add(self.s_panel_bottom_left, 1, wx.EXPAND, 0)

        self.update()    # Init this control with the default values from the active project

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Setting these values should also cause text highlighting to occur
        self.dat_outpath_box.SetValue(activeproject.datfile())
        self.im_outpath_box.SetValue(activeproject.pngfile())
        self.highlightText()

    def OnTextChangeDat(self,e):
        """When the text in the .dat/.pak output file entry box changes"""
        if activeproject.datfile() != self.dat_outpath_box.GetValue():
            activeproject.datfile(self.dat_outpath_box.GetValue())
            debug.out("Text changed in DAT entry box, new text: " + str(activeproject.datfile()))
            self.highlightText()
    def OnTextChangePng(self,e):
        """When the text in the .png output file entry box changes"""
        if activeproject.pngfile() != self.im_outpath_box.GetValue():
            activeproject.pngfile(self.im_outpath_box.GetValue())
            debug.out("Text changed in DAT entry box, new text: " + str(activeproject.datfile()))
            self.highlightText()

    def highlightText(self):
        """Update the highlighting in both DAT and PNG text entry boxes"""
        # Datfile
        a = pathObject(activeproject.datfile())
        # Pngfile, relative to the datfile so has second parameter
        b = pathObject(activeproject.pngfile(), activeproject.datfile())
        # Set entire length of both boxes to default colours
        self.dat_outpath_box.SetStyle(0,len(activeproject.datfile()), wx.TextAttr(None, "white"))
        self.im_outpath_box.SetStyle(0,len(activeproject.pngfile()), wx.TextAttr(None, "white"))
        # Then recolour both boxes to reflect path existence
        for k in range(len(a)):
            if a[k].exists:         # If this path section exists, colour it yellow
                self.dat_outpath_box.SetStyle(a[k].offset,a[k].offset + a[k].length, wx.TextAttr(None, "white"))
            else:                   # Otherwise colour it the normal way
                self.dat_outpath_box.SetStyle(a[k].offset,a[k].offset + a[k].length, wx.TextAttr(None, "#FFFF00"))
        for k in range(len(b)):
            if b[k].exists:
                self.im_outpath_box.SetStyle(b[k].offset,b[k].offset + b[k].length, wx.TextAttr(None, "white"))
            else:
                self.im_outpath_box.SetStyle(b[k].offset,b[k].offset + b[k].length, wx.TextAttr(None, "#FFFF00"))

        debug.out("DAT new array: " + str(a) + " PNG new array: " + str(b))

    def OnBrowseDat(self,e):
        """Opens a file save as dialog for the dat/pak output file"""
        # If path exists, and is a file, or the path up to the last bit exists and is a directory
        if os.path.isfile(activeproject.datfile()) or os.path.isdir(os.path.split(activeproject.datfile())[0]):
            a = os.path.split(activeproject.datfile())[0]
            b = os.path.split(activeproject.datfile())[1]
        # If path exists, and is a directory
        elif os.path.isdir(activeproject.datfile()):
            a = activeproject.datfile()
            b = ""
        # If path does not exist
        else:
            # Assume that the last component of the path is the filename, and find the largest component of the path
            # which exists
            c = pathObject(activeproject.datfile())
            a = c.exists
            b = os.path.split(activeproject.datfile())[1]
            
        # name, default path, default name
        datoutdialog = wx.FileDialog(self.parent, gt("Choose a location to output .dat/.pak to"),
                                     a, b, "DAT/PAK files (*.dat)|*.dat|(*.pak)|*.pak", wx.SAVE|wx.OVERWRITE_PROMPT)
        if datoutdialog.ShowModal() == wx.ID_OK:
            # OK was pressed, update text box with new file location, which will cause it to update itself
            #
            # This location will always be absolute as returned by the dialog, which is what we want
            #
            self.dat_outpath_box.SetValue(os.path.join(datoutdialog.GetDirectory(), datoutdialog.GetFilename()))
            datoutdialog.Destroy()
        else:
            # Else cancel was pressed, do nothing
            return 0


    def OnBrowsePng(self,e):
        """Opens a file save as dialog for the png output file"""
        # If path exists, and is a file, or the path up to the last bit exists and is a directory
        if os.path.isfile(os.path.join(os.path.split(activeproject.datfile())[0],activeproject.pngfile())) or os.path.isfile(os.path.join(activeproject.datfile(),activeproject.pngfile())) or os.path.isdir(os.path.join(activeproject.datfile(),os.path.split(activeproject.pngfile())[0])) or os.path.isdir(os.path.join(os.path.split(activeproject.datfile())[0],os.path.split(activeproject.pngfile())[0])):
            a = os.path.join(os.path.split(activeproject.datfile())[0],os.path.split(activeproject.pngfile())[0])
            b = os.path.split(activeproject.pngfile())[1]
        # If path exists, and is a directory
        elif os.path.isdir(os.path.join(os.path.split(activeproject.datfile())[0],activeproject.pngfile())) or  os.path.isdir(os.path.join(activeproject.datfile(),activeproject.pngfile())):
            a = os.path.join(os.path.split(activeproject.datfile())[0],activeproject.pngfile())
            b = ""
        # If path does not exist
        else:
            # Assume that the last component of the png path is the filename, and find the largest component of the dat
            # path which exists
            c = pathObject(activeproject.datfile())
            a = c.exists
            b = os.path.split(activeproject.pngfile())[1]

        pngoutdialog = wx.FileDialog(self.parent, gt("Choose a file to save to..."),
                                     a, b, "PNG files (*.png)|*.png", wx.SAVE|wx.OVERWRITE_PROMPT)
        if pngoutdialog.ShowModal() == wx.ID_OK:
            # OK was pressed, update text box with new file location, which will cause it to update itself
            #
            # This needs to calculate a relative path between the location of the output png and the location of the output dat
            # to display in the box and for use in the outputting!!
            #
            
            self.im_outpath_box.SetValue(os.path.join(pngoutdialog.GetDirectory(), pngoutdialog.GetFilename()))
            pngoutdialog.Destroy()
        else:
            # Else cancel was pressed, do nothing
            return 0

    # All of this file manipulation stuff could potentially be built into an extended text control

    # Path manipulation functions
    # splitPath     breaks a string up into path components
    # joinPaths     joins two paths together, taking end components (filenames etc.) into account
    # existingPath  returns the largest section of a path which exists on the filesystem
    # comparePaths  produces a relative path from two absolute ones
    def splitPath(p1, p2=None):
        """Split a path into an array, index[0] being the first path section, index[len-1] being the last
        Optionally takes a second path which is joined with the first for existence checks, to allow for
        checking existence of relative paths"""
        if os.path.split(p)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p)[0])[1] != "":
                p = os.path.split(p)[0]
        a = []
        while os.path.split(p)[1] != "":
            n = os.path.split(p)
            # Add at front, text,   offset,             length,     exists or not,      File or Directory?
            a.insert(0,    [n[1],  len(p)-len(n[1]),   len(n[1]),  os.path.exists(p)])#, existsAsType(p)])
            p = n[0]
        print a
        return a

    def joinPaths(p1,p2):
        """Join p2 to p1, accounting for end cases (is directory, is file etc.)"""

    def existingPath(p):
        """Take a path and return the largest section of this path that exists
        on the filesystem"""
        if os.path.split(p)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p)[0])[1] != "":
                p = os.path.split(p)[0]
        while not os.path.exists(p):
            p = os.path.split(p)[0]
        return p

    def comparePaths(p1,p2):
        """Compare two absolute paths, returning either a relative path from p1 to p2, or p1 if no relative path exists"""
        # First check that both paths are on the same drive, if drives exist
        if os.path.splitdrive(p1)[0] != os.path.splitdrive(p2)[0]:
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


# Needs to be recoded to use generator/list comprehension stuff
# Also needs to add caching of directory existance check and more intelligent updating based on the editing position of the
# text entry, maybe even make this a persistent object modified along with the text entry

class pathObject:
    """Contains a path as an array of parts with some methods for analysing them"""
    def __init__(self, pathstring, workdir=None):
        """Take a raw pathstring, normalise it and split it up into an array of parts"""
        path = pathstring
        norm_path = os.path.abspath(pathstring)
        if workdir != None:
            # Workdir is a working directory optionally used to check for existence of relative paths
            # Need to check the end component
            if os.path.isdir(workdir):
                # If it's a directory which exists, do nothing
                self.workdir = workdir
            elif os.path.isfile(workdir):
                # If it's a file that exists, split the directory off
                self.workdir = os.path.split(workdir)[0]
            else:
                # Otherwise hard to tell, best to just split it (assuming here that there's a filename at the end)
                self.workdir = os.path.split(workdir)[0]
        else:
            self.workdir = ""
        p = path
        self.path_array = []
        self.raw_path = path
        self.exists = ""
        # Iterate through the user supplied path, splitting it into sections to store in the array
        if os.path.split(p)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p)[0])[1] != "":
                p = os.path.split(p)[0]
        while os.path.split(p)[1] != "":
            n = os.path.split(p)
            self.path_array.append(path2(n[1],os.path.exists(os.path.join(self.workdir,p)),len(p) - len(n[1])))
            if os.path.exists(p) and self.exists == "":
                self.exists = p     # Longest bit of the path which exists
            p = os.path.split(p)[0]
    def compare(self,path2):
        """Compare own path with a second path, should return a relative path from second path to own path"""
        # First create a path object from the second path
        p2 = pathObject(path2)
        # Then check through to find the key value where the two differ
        a = 0
        f = 0
        while f == 0:
            if a != len(self) and a != len(p2):            
                if self[a] == p2[a]:
                    a += 1
##                else:
                    # If not the same, set calculation values for the path
    def __getitem__(self, key):
        return self.path_array[key]
    def __len__(self):
        return len(self.path_array)
    def __str__(self):
        a = ""
        for k in range(len(self.path_array)):
            a = a + "<[" + str(k) + "]\"" + self.path_array[k].text + "\"," + str(self.path_array[k].offset) + "-" + str(self.path_array[k].offset+self.path_array[k].length) + "," + str(self.path_array[k].exists) + ">, "
        return a

class path2:
    def __init__(self,text,exists,offset):
        self.text = text            # Textual content of this section of the path
        self.length = len(text)     # Length of this section of the path
        self.offset = offset        # Offset from start of string
        self.exists = exists        # Does this path section exist in the filesystem
    def __len__(self):
        return self.length
    def __str__(self):
        return self.text
    def exists(self):
        return self.exists

# Three paths - Current Working Directory (typically where the script is run from)
#             - .dat file directory, which is either given as an absolute path or is taken to be relative to CWD
#             - .png file directory, which is either given as an absolute path (and must be turned into a relative path
#               to the .dat file) or as a relative path to the .dat file (which needs to be turned into an absolute path
#               for actual file output)
#
# So need:      Abspath, CWD        (to turn relative .dat path into absolute one)
#               Abspath, .dat       (output location of the file)   From: either absolute path or one relative to CWD
#               Relpath, .dat->.png (to write into the .dat file)   From: either relative path to .dat, or absolute one
#               Abspath, .png       (output location of the file)   From: either relative path to .dat, or absolute one

# .png display as relative path

class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self,parent,id,title, windowsize=(800,600)):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), windowsize,
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        # Init stuff
        self.imres = tc.ImRes()

        # self.panel contains all other elements within this frame and must be their parent
        self.panel = wx.Panel(self, wx.ID_ANY, (-1,-1), (-1,-1))

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        # Two vertical divisions
        self.s_panel_top = wx.BoxSizer(wx.HORIZONTAL)
        # Within the top panel, two horizontal divisions, one for the controls, one for the image window
        self.s_panel_controls = wx.BoxSizer(wx.VERTICAL)                # Left side
        self.s_panel_imagewindow_container = wx.BoxSizer(wx.VERTICAL)   # Right side
        self.s_panel_imagewindow = wx.BoxSizer(wx.HORIZONTAL)           # Right side (bottom part for the image window
                                                                        # Right side top part created in class imagePathControl
        self.s_panel_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_bottom_right = wx.BoxSizer(wx.HORIZONTAL)          # Contains cut/export buttons

        # Make the Image Window (DC)
        self.display = ImageWindow(self.panel)
        self.s_panel_imagewindow.Add(self.display, 1, wx.EXPAND, 4)

        # LEFT SIDE CONTROLS
        # Left side controls are contained within static boxes
        # Frame controls-------------------------------------------------------------------

        # Season controls------------------------------------------------------------------
        self.control_seasons = seasonControl(self.panel, self.s_panel_controls, self.imres)
        # Image controls-------------------------------------------------------------------
        self.control_images = imageControl(self.panel, self.s_panel_controls, self.imres)
        # Facing controls------------------------------------------------------------------
        self.control_facing = facingControl(self.panel, self.s_panel_controls, self.imres)
        # Dimension controls---------------------------------------------------------------
        self.control_dims = dimsControl(self.panel, self.s_panel_controls, self.imres)
        # Offset/mask controls-------------------------------------------------------------
        self.control_offset = offsetControl(self.panel, self.s_panel_controls, self.imres)

        # Create the image path input, which adds itself to the image window container
        self.control_impath = imagePathControl(self.panel, self.s_panel_imagewindow_container,
                                               self.imres, gt("Source image location:"))
        # Add the image display window
        self.s_panel_imagewindow_container.Add(self.s_panel_imagewindow,1,wx.EXPAND, 0)

        # IMAGE/DAT OUTPUT PATHS
        # Create the I/O path inputs, which are added to the bottom-left panel container
        self.control_iopaths = fileControls(self.panel, self.s_panel_bottom, self.imres)

        # CUT/EXPORT BUTTONS
        # Cut button
        self.cut_button = wx.Button(self.panel, wx.ID_ANY, label=gt("Cut"))
        self.cut_button.Bind(wx.EVT_BUTTON, self.OnCutProject, self.cut_button)
        self.s_panel_bottom_right.Add(self.cut_button, 1, wx.EXPAND, 4)

        self.export_button = wx.Button(self.panel, wx.ID_ANY, label=gt("Export"))
        self.export_button.Bind(wx.EVT_BUTTON, self.OnExportProject, self.export_button)
        self.s_panel_bottom_right.Add(self.export_button, 1, wx.EXPAND, 4)
        # Add these buttons to the bottom-right panel container
        self.s_panel_bottom.Add(self.s_panel_bottom_right,0,wx.EXPAND, 0)

        # SIZERS
        # Add the remaining sizers to each other
        # Top panel, left side controls and right side image window added
        self.s_panel_top.Add(self.s_panel_controls,0,wx.EXPAND, 0)
        self.s_panel_top.Add(self.s_panel_imagewindow_container,1,wx.EXPAND, 0)
        # Add bottom and top parts to overall panel 
        self.s_panel.Add(self.s_panel_top,1,wx.EXPAND, 0)
        self.s_panel.Add(self.s_panel_bottom,0,wx.EXPAND|wx.RIGHT, 0)

        # Layout sizers
        self.panel.SetSizer(self.s_panel)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()

        # Create the menus
        self.menu = wx.MenuBar()
        self.AddMenus(self.menu)
        self.SetMenuBar(self.menu)

        # misc testing stuff
        im = Image.open("dino.png")
        outimage = wx.EmptyImage(im.size[0], im.size[1])
        outimage.SetData(im.convert("RGB").tostring())
        outimage = outimage.ConvertToBitmap()
        self.display.bmp = outimage
        self.display.DrawBitmap(1)

    # Menu functions
    def OnNewProject(self,e):
        self.debug.out("Menu-File-> New Project")
        return 1
    def OnOpenProject(self,e):
        self.debug.out("Menu-File-> Open Project")
        return 1
    def OnCloseProject(self,e):
        self.debug.out("Menu-File-> Close Project")
        return 1
    def OnSaveProject(self,e):
        self.debug.out("Menu-File-> Save Project")
        return 1
    def OnSaveProjectAs(self,e):
        self.debug.out("Menu-File-> Save Project As...")
        return 1
    def OnCutProject(self,e):
        self.debug.out("Menu-File-> Cut Project")
        return 1
    def OnExportProject(self,e):
        self.debug.out("Menu-File-> Export Project")
        return 1
    def OnExit(self,e):
        self.debug.out("Menu-File-> Exit Program")
        return 1

    def OnDatEdit(self,e):
        self.debug.out("Menu-Tools-> Open .dat edit dialog")
        return 1
    def OnSmokeEdit(self,e):
        self.debug.out("Menu-Tools-> Open smoke edit dialog")
        return 1
    def OnPreferences(self,e):
        self.debug.out("Menu-Tools-> Open preferences dialog")
        return 1

    def OnHelp(self,e):
        self.debug.out("Menu-Help-> Open help")
        return 1
    def OnAbout(self,e):
        self.debug.out("Menu-Help-> Open about dialog")
        blah.meh()
        return 1

    def AddMenus(self, menu):
        """Create menus during initialisation"""
        # File menu
        fileMenu = wx.Menu()
        self.AddMenuItem(fileMenu, '&New Project\tCtrl-N', 'New Project', self.OnNewProject)
        self.AddMenuItem(fileMenu, '&Open Project\tCtrl-O', 'Open Project', self.OnOpenProject)
        # Close project not needed? Would just do the same thing as new project anyway...
##        self.AddMenuItem(fileMenu, '&Close Project', 'Close Project', self.OnCloseProject)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, '&Save Project\tCtrl-S', 'Save Project', self.OnSaveProject)
        self.AddMenuItem(fileMenu, 'Save Project &As\tCtrl-A', 'Save Project As',self.OnSaveProjectAs)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, '&Cut Image\tCtrl-C', 'Export .png and .dat source files', self.OnCutProject)
##        self.AddMenuItem(fileMenu, 'Export Dat &file only', 'Export dat file', self.OnSaveProject)
        self.AddMenuItem(fileMenu, '&Export .pak\tCtrl-E', 'Export project as .pak file', self.OnExportProject)
        fileMenu.AppendSeparator()
        self.AddMenuItem(fileMenu, 'E&xit\tAlt-Q', 'Exit', self.OnExit)
        menu.Append(fileMenu, 'File')
        # Tools menu
        toolsMenu = wx.Menu()
        self.AddMenuItem(toolsMenu, '.&dat file options\tCtrl-D', 'Edit .dat file options', self.OnDatEdit, 0)
        self.AddMenuItem(toolsMenu, '&Smoke options\tCtrl-M', 'Add or edit a smoke object associated with this project', self.OnSmokeEdit, 0)
        toolsMenu.AppendSeparator()
        self.AddMenuItem(toolsMenu, '&Preferences\tCtrl-P', 'Change program preferences', self.OnPreferences)
        menu.Append(toolsMenu, 'Tools')
        # Help menu
        helpMenu = wx.Menu()
        self.AddMenuItem(helpMenu, 'Help Topics\tCtrl-H', '', self.OnHelp, 0)
        helpMenu.AppendSeparator()
        self.AddMenuItem(helpMenu, '&About TileCutter', 'Information about this program', self.OnAbout)
        menu.Append(helpMenu, 'Help')
        
    def AddMenuItem(self, menu, itemText, itemDescription, itemHandler, enabled=1):
        menuId = wx.NewId()
        menu.Append(menuId, itemText, itemDescription)
        self.Bind(wx.EVT_MENU, itemHandler, id=menuId)
        if enabled == 0:
            menu.Enable(menuId, 0)
        return menuId

class DebugFrame(wx.Frame):
    """Debugging output display, debug.out() (or just debug()) to output debugging text"""
    def __init__(self,parent,id,title):
        # Init text and counter
        self.text = ""
        self.count = 0
        # Frame init
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (0,0), (300,200),style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textbox = wx.TextCtrl(self.panel, wx.ID_ANY, self.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)
        self.sizer.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        #Layout sizers
        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()
    def out(self,line):
        self.count += 1
        t = "[" + str(self.count) + "] " + line + "\n"
        self.text = self.text + t
        self.textbox.SetValue(self.text)
        self.textbox.ShowPosition(len(self.text))
    def __call__(self,line):
        self.out(line)

class MyApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def OnInit(self):
        # Initialise the debugging frame and show if debug set
        # Load Program Options

        # Create and show debug window if debugging turned on
        self.debug = DebugFrame(None, wx.ID_ANY, "Debugging")
        if debug_on == 1:
            self.debug.Show(1)

        return True

    def ReloadWindow(self):
        """Reload the main window, e.g. to effect a translation change, does not affect debugging window"""

    def MainWindow(self):
        """Create main window after intialising project and debugging etc."""
        # Create and show main frame
        self.frame = MainWindow(None, wx.ID_ANY, "TileCutter v.%s"%VERSION_NUMBER, (800,600))
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.frame.debug = self.debug

        # Bind the debugging output for the active project functions to the same debug output
        activeproject.debug = self.debug
        # Produce aliases to activeproject at different levels
        self.activeproject = activeproject
        self.frame.activeproject = activeproject

        # Show the main window frame
        self.frame.Show(1)
    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        self.debug.Destroy()
        self.frame.Destroy()

# Run the program
if __name__ == '__main__':
##    makeobj = Makeobj()
    start_directory = os.getcwd()
    # Create the application
    app = MyApp()
    # Make debug global in all modules
    debug = tcproject.debug = tc.debug = app.debug
##    sys.stderr = open("error.txt","w")
    # Create a default active project
    activeproject = tcproject.Project()
    # Create the main application window
    app.MainWindow()
##    app.LoadProgramOps()
##    app.NewProject()
    app.MainLoop()
    app.Destroy()
