#
# TileCutter, version 0.5 (rewrite)
#

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
import wx.lib.masked as masked
import wx.lib.scrolledpanel as scrolled
import wx.lib.hyperlink as hl

import ImageDraw, ImageWin
import sys, os

import tc, tcproject

# Init variables
debug = 1

VERSION_NUMBER = "0.5a"
##TRANSPARENT = (231,255,255)
TRANSPARENT = (0,0,0)
DEFAULT_PAKSIZE = "64"
# SB_WIDTH may be different on other platforms...
SCROLLBAR_WIDTH = 16

# Lists of values for choicelists, also provides acceptable values for the project class
##choicelist_anim = ["0",]

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


# Frame, consists of two ProjectImages, for front and back image
# Frames are children of seasons, which are children of directions
# The project object is the parent of the directions, as well as of
# the information describing the project (contained in further forks)
# This comprises the informational model describing a project, which
# is used to intialise the UI, there should be a controller layer
# between the model and the UI with functions to allow setting and
# retrieving of the different parts



class ImageWindow(wx.ScrolledWindow):
    """Window onto which bitmaps may be drawn, background colour is TRANSPARENT"""
    bmp = []
    def __init__(self, parent, id = -1, size = wx.DefaultSize, extended=0):
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



class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self,parent,id,title, windowsize=(800,600)):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), windowsize,
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        # Init stuff
        self.imres = tc.ImRes()

        # self.panel contains all other elements within this frame and must be their parent
        self.panel = wx.Panel(self, -1, (-1,-1), (500,500))

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        # Two vertical divisions
        self.s_panel_top = wx.BoxSizer(wx.HORIZONTAL)
        # Within the top panel, two horizontal divisions, one for the controls, one for the image window
        self.s_panel_controls = wx.BoxSizer(wx.VERTICAL)
        self.s_panel_imagewindow_container = wx.BoxSizer(wx.VERTICAL)
        self.s_panel_imagewindow = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_imagewindow_path = wx.FlexGridSizer(0,5,0,0)
        # Within the bottom panel
        self.s_panel_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_bottom_left = wx.FlexGridSizer(0,3,0,0)    # Contains paths for output .dat and .png
        self.s_panel_bottom_right = wx.BoxSizer(wx.HORIZONTAL)    # Contains cut/export buttons


        # Make the Image Window (DC)
        self.display = ImageWindow(self.panel)
        self.s_panel_imagewindow.Add(self.display, 1, wx.EXPAND, 4)


        # LEFT SIDE CONTROLS
        # Left side controls are contained within static boxes
        # Frame controls
##        self.s_frames_box = wx.StaticBox(self.panel, -1, gt("Frame X of Y"))
##        self.s_frames = wx.StaticBoxSizer(self.s_frames_box, wx.VERTICAL)
##        self.s_frames_flex= wx.FlexGridSizer(0,2,0,0)
##        self.s_frames_flex.AddGrowableCol(1)
        # Season controls---------------------------------------------------------------------------------------
            # Create the box and sizers
        self.s_seasons_box = wx.StaticBox(self.panel, -1, gt("Season"))
        self.s_seasons = wx.StaticBoxSizer(self.s_seasons_box, wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_seasons_flex.AddGrowableCol(1)
            # Add items
        self.seasons_select_summer_im = wx.StaticBitmap(self.panel, -1, self.imres.summer)
        self.seasons_select_summer = wx.RadioButton(self.panel, -1, gt("Summer"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.seasons_select_summer.SetToolTipString(gt("tt_seasons_select_summer"))
        self.seasons_select_winter_im = wx.StaticBitmap(self.panel, -1, self.imres.winter)
        self.seasons_select_winter = wx.RadioButton(self.panel, -1, gt("Winter"), (-1,-1), (-1,-1))
        self.seasons_select_winter.SetToolTipString(gt("tt_seasons_select_winter"))
        self.seasons_enable_winter = wx.CheckBox(self.panel, -1, gt("Enable Winter"), (-1,-1), (-1,-1))
        self.seasons_enable_winter.SetToolTipString(gt("tt_seasons_enable_winter"))
            # Add to sizers
        self.s_seasons_flex.Add(self.seasons_select_summer_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_seasons_flex.Add(self.seasons_select_summer, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons_flex.Add(wx.Size(1,1))
        self.s_seasons_flex.Add(self.seasons_enable_winter, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_seasons.Add(self.s_seasons_flex, 1, wx.RIGHT, 0)
        self.s_panel_controls.Add(self.s_seasons, 0, wx.EXPAND, 0)
            # Bind functions
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleWinter, self.seasons_enable_winter)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeSeason, self.seasons_select_summer)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeSeason, self.seasons_select_winter)
        # Image controls---------------------------------------------------------------------------------------
            # Create the box and sizers
        self.s_images_box = wx.StaticBox(self.panel, -1, gt("Image"))
        self.s_images = wx.StaticBoxSizer(self.s_images_box, wx.VERTICAL)
        self.s_images_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_images_flex.AddGrowableCol(1)
            # Add items
        self.images_select_back_im = wx.StaticBitmap(self.panel, -1, self.imres.back)
        self.images_select_back = wx.RadioButton(self.panel, -1, gt("BackImage"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.images_select_back.SetToolTipString(gt("tt_images_select_back"))
        self.images_select_front_im = wx.StaticBitmap(self.panel, -1, self.imres.front)
        self.images_select_front = wx.RadioButton(self.panel, -1, gt("FrontImage"), (-1,-1), (-1,-1))
        self.images_select_front.SetToolTipString(gt("tt_images_select_front"))
        self.images_enable_front = wx.CheckBox(self.panel, -1, gt("Enable FrontImage"), (-1,-1), (-1,-1))
        self.images_enable_front.SetToolTipString(gt("tt_images_enable_front"))
            # Add to sizers
        self.s_images_flex.Add(self.images_select_back_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_images_flex.Add(self.images_select_back, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images_flex.Add(self.images_select_front_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_images_flex.Add(self.images_select_front, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images_flex.Add(wx.Size(1,1))
        self.s_images_flex.Add(self.images_enable_front, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        self.s_images.Add(self.s_images_flex, 1, wx.RIGHT, 0)
        self.s_panel_controls.Add(self.s_images, 0, wx.EXPAND, 0)
            # Bind functions
        # Facing controls---------------------------------------------------------------------------------------
            # Create the box and sizers
        self.s_facing_box = wx.StaticBox(self.panel, -1, gt("Direction Facing"))
        self.s_facing = wx.StaticBoxSizer(self.s_facing_box, wx.HORIZONTAL)
        self.s_facing_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_facing_flex.AddGrowableCol(1)
        self.s_facing_right = wx.BoxSizer(wx.VERTICAL)
        self.s_facing_1 = wx.BoxSizer(wx.HORIZONTAL)
            # Add items
        self.facing_select_south_im = wx.StaticBitmap(self.panel, -1, self.imres.south)
        self.facing_select_south = wx.RadioButton(self.panel, -1, gt("South"), (-1,-1), (-1,-1), wx.RB_GROUP)
        self.facing_select_south.SetToolTipString(gt("tt_facing_select_south"))
        self.facing_select_east_im = wx.StaticBitmap(self.panel, -1, self.imres.east)
        self.facing_select_east = wx.RadioButton(self.panel, -1, gt("East"), (-1,-1), (-1,-1))
        self.facing_select_east.SetToolTipString(gt("tt_facing_select_east"))
        self.facing_select_north_im = wx.StaticBitmap(self.panel, -1, self.imres.north)
        self.facing_select_north = wx.RadioButton(self.panel, -1, gt("North"), (-1,-1), (-1,-1))
        self.facing_select_north.SetToolTipString(gt("tt_facing_select_north"))
        self.facing_select_west_im = wx.StaticBitmap(self.panel, -1, self.imres.west)
        self.facing_select_west = wx.RadioButton(self.panel, -1, gt("West"), (-1,-1), (-1,-1))
        self.facing_select_west.SetToolTipString(gt("tt_facing_select_west"))
        self.facing_enable_label = wx.StaticText(self.panel, -1, gt("Number\nof views:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_enable_select = wx.ComboBox(self.panel, -1, "1", (-1, -1), (54, -1), ["1","2","4"], wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
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
        self.s_panel_controls.Add(self.s_facing, 0, wx.EXPAND, 0)
            # Bind functions
        # Dimension controls---------------------------------------------------------------------------------------
            # Create the box and sizers
        self.s_dims_box = wx.StaticBox(self.panel, -1, gt("Dimensions"))
        self.s_dims = wx.StaticBoxSizer(self.s_dims_box, wx.VERTICAL)
        self.s_dims_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_dims_flex.AddGrowableCol(1)
            # Add items
        self.dims_p_label = wx.StaticText(self.panel, -1, gt("Paksize"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_p_select = wx.ComboBox(self.panel, -1, DEFAULT_PAKSIZE, (-1, -1), (54, -1), choicelist_paksize, wx.CB_READONLY)
        self.dims_p_select.SetToolTipString(gt("tt_dims_paksize_select"))
        self.dims_z_label = wx.StaticText(self.panel, -1, gt("Z dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_z_select = wx.ComboBox(self.panel, -1, "1", (-1, -1), (54, -1), choicelist_dims_z, wx.CB_READONLY)
        self.dims_z_select.SetToolTipString(gt("tt_dims_z_select"))
        self.dims_x_label = wx.StaticText(self.panel, -1, gt("X dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_x_select = wx.ComboBox(self.panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
        self.dims_x_select.SetToolTipString(gt("tt_dims_x_select"))
        self.dims_y_label = wx.StaticText(self.panel, -1, gt("Y dimension"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_y_select = wx.ComboBox(self.panel, -1, "1", (-1, -1), (54, -1), choicelist_dims, wx.CB_READONLY)
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
        self.s_panel_controls.Add(self.s_dims, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)
            # Bind functions
        # Offset/mask controls-------------------------------------------------------------------------------------
            # Create the box and sizers
        self.s_offset_box = wx.StaticBox(self.panel, -1, gt("Offset/Mask"))
        self.s_offset = wx.StaticBoxSizer(self.s_offset_box, wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0,4,0,0)
            # Add items
        self.offset_button_up = wx.BitmapButton(self.panel, -1, self.imres.up2, (-1,-1), (18,18))
        self.offset_button_up.SetToolTipString(gt("tt_offset_button_up"))
        self.offset_button_left = wx.BitmapButton(self.panel, -1, self.imres.left2, (-1,-1), (18,18))
        self.offset_button_left.SetToolTipString(gt("tt_offset_button_left"))
        self.offset_button_reset = wx.BitmapButton(self.panel, -1, self.imres.center, (-1,-1), (18,18))
        self.offset_button_reset.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_right = wx.BitmapButton(self.panel, -1, self.imres.right2, (-1,-1), (18,18))
        self.offset_button_right.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_down = wx.BitmapButton(self.panel, -1, self.imres.down2, (-1,-1), (18,18))
        self.offset_button_down.SetToolTipString(gt("tt_offset_button_down"))
        self.offset_selector = wx.CheckBox(self.panel, -1, gt("Fine"), (-1,-1), (-1,-1))
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
        self.s_panel_controls.Add(self.s_offset, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)
            # Bind functions

##        # May not be necessary anymore
##        self.hack2 = wx.RadioButton(self.panel, -1, "", (-1,-1), (-1,-1), wx.RB_GROUP|wx.ALIGN_RIGHT)
##        self.hack2.Show(False)

        # IMAGE PATH INPUT
        # Next the lower DC controls
        self.impath_entry_label = wx.StaticText(self.panel, -1, gt("Source image location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.impath_entry_box = wx.TextCtrl(self.panel, -1, value="", style=wx.TE_READONLY)
        self.impath_entry_box.SetToolTipString(gt("ttinputpath"))
        self.impath_entry_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.impath_entry_filebrowse = wx.Button(self.panel, -1, label=gt("Browse..."))
        self.impath_entry_filebrowse.SetToolTipString(gt("ttbrowseinputfile"))
        self.impath_entry_reloadfile = wx.BitmapButton(self.panel, -1, size=(25,-1), bitmap=self.imres.reload)
        self.impath_entry_reloadfile.SetToolTipString(gt("ttreloadinputfile"))
        self.impath_entry_sameforall = wx.BitmapButton(self.panel, -1, size=(25,-1), bitmap=self.imres.sameforall)
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


        # IMAGE/DAT OUTPUT PATHS
        # Image output path entry
        self.im_outpath_label = wx.StaticText(self.panel, -1, gt("Output PNG Image Location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.im_outpath_box = wx.TextCtrl(self.panel, -1, value="", style=wx.TE_READONLY)
        self.im_outpath_box.SetToolTipString(gt("tt_output_image_location"))
        self.im_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.im_outpath_filebrowse = wx.Button(self.panel, -1, label=gt("Browse..."))
        self.im_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_image_location"))
        # Add them to sizer...
        self.s_panel_bottom_left.Add(self.im_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
        # Bind them to events
##        self.im_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseSource, self.impath_entry_filebrowse)
        # Image output path entry
        self.dat_outpath_label = wx.StaticText(self.panel, -1, gt("Output Dat/Pak File Location:"), (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dat_outpath_box = wx.TextCtrl(self.panel, -1, value="", style=wx.TE_READONLY)
        self.dat_outpath_box.SetToolTipString(gt("tt_output_dat_file_location"))
        self.dat_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.dat_outpath_filebrowse = wx.Button(self.panel, -1, label=gt("Browse..."))
        self.dat_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_dat_file_location"))
        # Add them to sizer...
        self.s_panel_bottom_left.Add(self.dat_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
        # Bind them to events
##        self.impath_entry_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseSource, self.impath_entry_filebrowse)

        # CUT/EXPORT BUTTONS
        # Cut button
        self.cut_button = wx.Button(self.panel, -1, label=gt("Cut"))
        self.cut_button.Bind(wx.EVT_BUTTON, self.OnCutProject, self.cut_button)
        self.s_panel_bottom_right.Add(self.cut_button, 1, wx.EXPAND, 4)

        self.export_button = wx.Button(self.panel, -1, label=gt("Export"))
        self.export_button.Bind(wx.EVT_BUTTON, self.OnExportProject, self.export_button)
        self.s_panel_bottom_right.Add(self.export_button, 1, wx.EXPAND, 4)


        # SIZERS
        # Add the sizers to each other
        # Image window, path at the top and device context display at the bottom
        self.s_panel_imagewindow_container.Add(self.s_panel_imagewindow_path,0,wx.EXPAND, 0)
        self.s_panel_imagewindow_container.Add(self.s_panel_imagewindow,1,wx.EXPAND, 0)
        # Top panel, left side controls and right side image window added
        self.s_panel_top.Add(self.s_panel_controls,0,wx.EXPAND, 0)
        self.s_panel_top.Add(self.s_panel_imagewindow_container,1,wx.EXPAND, 0)
        # Bottom panel, left side path controls and right side cut/export controls added
        self.s_panel_bottom.Add(self.s_panel_bottom_left,1,wx.EXPAND, 0)
        self.s_panel_bottom.Add(self.s_panel_bottom_right,0,wx.EXPAND, 0)
        # Top and bottom panels added to main sizer
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

        im = Image.open("dino.png")
        outimage = wx.EmptyImage(im.size[0], im.size[1])
        outimage.SetData(im.convert("RGB").tostring())
        outimage = outimage.ConvertToBitmap()
        self.display.bmp = outimage
        self.display.DrawBitmap(1)

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
        return 1

    def AddMenus(self, menu):
        """Create menus during initialisation"""
        # File menu
        fileMenu = wx.Menu()
        self.AddMenuItem(fileMenu, '&New Project\tCtrl-N', 'New Project', self.OnNewProject)
        self.AddMenuItem(fileMenu, '&Open Project\tCtrl-O', 'Open Project', self.OnOpenProject)
        self.AddMenuItem(fileMenu, '&Close Project', 'Close Project', self.OnCloseProject)
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
    """Debugging output frame, just a text box with some additional functions really"""
    text = "Debug Console"
    joiner = ""
    count = 0
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (0,0), (300,200),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        self.panel = wx.Panel(self, -1, (-1,-1), (500,500))

        self.debug_boxsizer = wx.BoxSizer(wx.VERTICAL)

        self.textbox = wx.TextCtrl(self.panel, -1, self.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)

        self.debug_boxsizer.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)

        #Layout sizers
        self.panel.SetSizer(self.debug_boxsizer)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()
    def out(self,line):
        self.count += 1
        t = "\n[" + str(self.count) + "] " + line
        self.text = self.text + t
        self.textbox.SetValue(self.text)
        self.textbox.ShowPosition(len(self.text))

class MyApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def OnInit(self):
        # Initialise the debugging frame and show if debug set
        # Load Program Options

        # Create and show debug window if debugging turned on
        self.debug = DebugFrame(None, -1, "Debugging")
        if debug == 1:
            self.debug.Show(1)

        # Create and show main frame
        self.frame = MainWindow(None, -1, "TileCutter v.%s"%VERSION_NUMBER, (800,600))
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.frame.debug = self.debug

        # Init the active project
        self.activeproject = tcproject.Project()
        self.frame.activeproject = self.activeproject

        # Show the main window frame
        self.frame.Show(1)
        return True
    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        self.debug.Destroy()
        self.frame.Destroy()

# Run the program
if __name__ == '__main__':
##    makeobj = Makeobj()
    app = MyApp()
##    app.LoadProgramOps()
##    app.NewProject()
    app.MainLoop()
    app.Destroy()
