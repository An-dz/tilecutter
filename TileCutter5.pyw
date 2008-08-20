# coding: UTF-8
#
# TileCutter, version 0.5 (rewrite)
#

# Todo:

# BUG - Set active image to new image, then edit textbox to make path invalid, then edit it back to the original -> highlighting fails
# BUG - Season select does not set to summer when enable winter is unchecked


# Move debug into own module, to allow it to be easily accessed by other modules        - DONE
#   (like imres is at the moment)

# Find some way to eliminate flickering on translation update/initial load              
# Text entry boxes visible position at end, or cursor, rather than beginning            
# Padding/general layout optimisation                                                   
# -> Layout optimisation for mac                                                        
# Cutting mask display based on dimensions                                              - DONE
# Make .dat and input images relative to save location path                             
# Speed optimisations - switching views seems really sluggish!                          
# Optimise code for generating lists in comboboxes (translation slowing this?)          

# Finish output file boxes, switching them to use the new set of functions              - DONE
# Do the project save/load/new etc. and management functionality (using pickle & hash)  
#   Multi-project system for later versions                                             - POSTPONE 0.7

# Program settings, load from a config file (using configparser)                        
# Dialog to set program options                                                         
# Implement use of special menu IDs to make menus work properly on, e.g., mac osx       
# Produce frames picker control                                                         - POSTPONE 0.6
# Offset/Mask control - internal functions, click modifies model & triggers redrawing   - DONE
# Dims control - click modifies model & triggers redrawing                              - DONE
# Direction/Season/Dims - trigger redrawing                                             - DONE

# Translation system - On the fly translation system now possible                       - DONE
# Menu translations                                                                     - DONE
# Translation system needs work to function correctly with unicode strings              - DONE (files MUST be UTF-8)
# Find some way of translating the entries in combo boxes!                              - DONE

# Current view context built into activeproject, details of the currently selected view - DONE
# Implement current view context to all view controls                                   - DONE
# Source image control (needs current view context)                                     - MOSTLY DONE
# -> File must exist                                                                    - DONE
# -> Implement modal dialog for browse                                                  - DONE
# -> Allow text entry, highlight in red if file does not exist??                        - DONE (Needs icons for tick/cross)
# -> Implement modal confirmation dialog for "open same file for all" button            
# "Warning, this will set all views in the project to use the current image, proceed?"  
# -> Function to reload the current view's image                                        - DONE

# Move UI classes into a module to enhance loading speed        - MOSTLY DONE (JUST IMAGEWINDOW TO MOVE)

# Needs much better error handling, add try/except clauses in critical places
# Could also encase entire script in an exception catcher, which can display exception 
#   and then gracefully shutdown wx, to prevent the flashing box/pythonwin crashing problem

# Add the TileCutter icon                                                               - Icon made, works well in windows
# Use img2py to compile icon image into the application                                 - DONE
# Can use the same technique for all the other images, e.g. bitmap buttons etc.         - DONE
# Need higher detail icons for the mac version                                          - DONE (Test icon display in OSX)

# About dialog                                                                          - DONE
# Make py2exe, look into producing smaller packages     - Also py2app                   
#   Import only bits of wx needed, to reduce py2exe package?                            
# Look into producing more mac-native package                                           
# Mac drag + drop support                                                               
# Linux just the script                                                                 
# Test with Linux, Mac OSX, Windows (xp), try and have the same code across all platforms!
# Produce help documentation                                                            
# -> Quick start guide (interface should be fairly self-explanatory though)             


# Aims v.0.5
# Rewrite core cutting engine and output engine
# Produce minimal testing UI
#   - Set X/Y/Z dims, X/Y offsets, facing/season
#   - Determine output .png, .dat etc.
# Debugging system with nice output
# Translation function implemented
# Project save/load functions

# Aims v.0.6
# Extend UI, include dat editor

# Aims v.0.7
# Multi-project support

import wx
##import wx.lib.masked as masked
##import wx.lib.scrolledpanel as scrolled
##import wx.lib.hyperlink as hl

import sys, os, ConfigParser, StringIO, re, codecs, pickle
import tcui
import tc, tcproject, imres
import translator

# Custom platform codecs
import u_newlines, w_newlines

from debug import DebugFrame as debug

# Init variables
debug_on = True

VERSION_NUMBER = "0.5a"
TRANSPARENT = (0,0,0)
##TRANSPARENT = (231,255,255)
DEFAULT_PAKSIZE = "64"
PROJECT_FILE_EXTENSION = ".tcp"
### SB_WIDTH may be different on other platforms...
##SCROLLBAR_WIDTH = 16
VALID_IMAGE_EXTENSIONS = tcproject.VALID_IMAGE_EXTENSIONS
MAIN_WINDOW_SIZE=(800,500)
MAIN_WINDOW_MINSIZE=(800,500)
MAIN_WINDOW_POSITION=(100,50)

# Static variables
South   = 0
East    = 1
North   = 2
West    = 3
Back    = 0
Front   = 1
Summer  = 0
Winter  = 1

# Lists of values for choicelists, also provides acceptable values for the project class
# Also set in tcproject module
choicelist_anim = ["0",]
choicelist_paksize_int = [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240]
choicelist_views_int = [1,2,4]
choicelist_dims_int = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
choicelist_dims_z_int = [1,2,3,4]
# Need some kind of auto-generation function for the translator, to produce a range of numbers (0-64, then in 16 increments to 240)
##choicelist_paksize = [gt("16"),gt("32"),gt("48"),gt("64"),gt("80"),gt("96"),gt("112"),gt("128"),gt("144"),gt("160"),gt("176"),gt("192"),gt("208"),gt("224"),gt("240")]
##choicelist_views = ["1","2","4"]
##choicelist_dims = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
##choicelist_dims_z = ["1","2","3","4"]

# Translation function, simply calls tctranslator object's gt method
def gt(text):
    """Get text, return translation of string"""
    return app.tctranslator.gt(text)

class ImageWindow(wx.ScrolledWindow, tcui.fileTextBox):
    """Window onto which bitmaps may be drawn, background colour is TRANSPARENT colour
    Also contains the image path entry box and associated controls"""
    bmp = []
    def __init__(self, parent, parent_sizer, id = wx.ID_ANY, size = wx.DefaultSize, extended=0):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.parent = parent
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
        if self.impath_entry_box.GetValue() != app.activeproject.activeImage().path() and self.impath_entry_box.GetValue() != app.activeproject.activeImage().lastpath():
            self.impath_entry_box.SetValue(app.activeproject.activeImage().path())
        # And then redraw the active image in the window, with mask etc.
        bitmap = app.activeproject.activeImage().bitmap()

        # Setup image properties for mask generation
        x = app.activeproject.x()
        y = app.activeproject.y()
        z = app.activeproject.z()
        p = app.activeproject.paksize()
        p2 = p/2
        p4 = p/4
        mask_offset_x, mask_offset_y = app.activeproject.offset()
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
        dc.SetBackground(wx.Brush(TRANSPARENT))
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
        if self.impath_entry_box.GetValue() != app.activeproject.activeImage().path() and self.impath_entry_box.GetValue() != app.activeproject.activeImage().lastpath():
            debug("Text changed in image path box, new text: " + self.impath_entry_box.GetValue())
            # Check whether the entered path exists or not, if it does update the value in the activeproject (which will cause
            # that new image to be loaded & displayed) if not don't set this value
            if os.path.isfile(self.impath_entry_box.GetValue()) and os.path.splitext(self.impath_entry_box.GetValue())[1] in VALID_IMAGE_EXTENSIONS:
                # Is a valid file, display green tick icon
                debug("...new text is a valid file")
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
                # Update the active image with the new path
                app.activeproject.activeImage().path(self.impath_entry_box.GetValue())
                # Then redraw the image
                self.update()
            else:
                # Not a valid file, display red cross icon
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK))
                debug("...but new text not a valid file!")
                # Highlight text function only needed if it isn't a valid file, obviously
                self.highlightText(self.impath_entry_box, self.impath_entry_box.GetValue())
            # Update the last path
            app.activeproject.activeImage().lastpath(self.impath_entry_box.GetValue())
    def OnBrowseSource(self,e):
        """When browse source button clicked"""
        value = self.filePickerDialog(app.activeproject.activeImage().path(), "", gt("Choose a source image for this view:"),
                                      "PNG files (*.png)|*.png", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        self.impath_entry_box.SetValue(value)
    def OnReloadImage(self,e):
        """When reload image button clicked"""
        app.activeproject.activeImage().reloadImage()
        self.update()
    def OnLoadImageForAll(self,e):
        """When "load same image for all" button is clicked"""


class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self, parent, id, title, windowsize, windowposition, windowminsize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, windowposition, windowsize,
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        # Init stuff
        self.SetMinSize(windowminsize)

        # Set the program's icon
        self.icons = wx.IconBundle()
        self.icons.AddIcon(imres.catalog["tc_icon2_16_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_32_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_48_plain"].getIcon())
        self.SetIcons(self.icons)
        app.debug.SetIcons(self.icons)

        # Create the menus
        self.menubar = tcui.menuObject(self, app)
        self.SetMenuBar(self.menubar.menu)

        # self.panel contains all other elements within this frame and must be their parent
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        # Two vertical divisions
        self.s_panel_top = wx.BoxSizer(wx.HORIZONTAL)
        # Within the top panel, two horizontal divisions, one for the controls, one for the image window
        self.s_panel_controls = wx.BoxSizer(wx.VERTICAL)                # Left side

        self.s_panel_imagewindow_container = wx.BoxSizer(wx.VERTICAL)   # Right side

        self.s_panel_bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_bottom_right = wx.BoxSizer(wx.HORIZONTAL)          # Contains cut/export buttons

        # LEFT SIDE CONTROLS
        # Left side controls are contained within static boxes
        # Frame controls-------------------------------------------------------------------

        # Season controls------------------------------------------------------------------
        self.control_seasons    = tcui.seasonControl(self.panel, app, self.s_panel_controls)
        # Image controls-------------------------------------------------------------------
        self.control_images     = tcui.imageControl(self.panel, app, self.s_panel_controls)
        # Facing controls------------------------------------------------------------------
        self.control_facing     = tcui.facingControl(self.panel, app, self.s_panel_controls)
        # Dimension controls---------------------------------------------------------------
        self.control_dims       = tcui.dimsControl(self.panel, app, self.s_panel_controls)
        # Offset/mask controls-------------------------------------------------------------
        self.control_offset     = tcui.offsetControl(self.panel, app, self.s_panel_controls)

        # Create Image display window and image path entry control, which adds itself to the sizer
        self.display = ImageWindow(self.panel, self.s_panel_imagewindow_container)

        # IMAGE/DAT OUTPUT PATHS
        # Create the I/O path inputs, which are added to the bottom-left panel container
        self.control_iopaths = tcui.twoFileControl(self.panel, app, self.s_panel_bottom)

        # CUT/EXPORT BUTTONS
        # Cut button
        self.cut_button = wx.Button(self.panel, wx.ID_ANY)
        self.cut_button.Bind(wx.EVT_BUTTON, self.menubar.OnCutProject, self.cut_button)
        self.s_panel_bottom_right.Add(self.cut_button, 1, wx.EXPAND, 4)
        # Export button
        self.export_button = wx.Button(self.panel, wx.ID_ANY)
        self.export_button.Bind(wx.EVT_BUTTON, self.menubar.OnExportProject, self.export_button)
        self.s_panel_bottom_right.Add(self.export_button, 1, wx.EXPAND, 4)
        # Add these buttons to the bottom-right panel container
        self.s_panel_bottom.Add(self.s_panel_bottom_right,0,wx.EXPAND, 0)

        # SIZERS
        # Add the remaining sizers to each other
        # Top panel, left side controls and right side image window added
        self.s_panel_top.Add(self.s_panel_controls,0,wx.EXPAND|wx.RIGHT, 1)
        self.s_panel_top.Add(self.s_panel_imagewindow_container,1,wx.EXPAND, 0)
        # Add bottom and top parts to overall panel 
        self.s_panel.Add(self.s_panel_top,1,wx.EXPAND, 0)
        self.s_panel.Add(self.s_panel_bottom,0,wx.EXPAND|wx.RIGHT, 0)

        # Layout sizers
        self.panel.SetSizer(self.s_panel)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()

        self.translate()

    def translate(self):
        """Master translate function for the mainwindow object"""
        self.cut_button.SetLabel(gt("Cut"))
        self.export_button.SetLabel(gt("Export"))
        # And translate the window's title string
        # Then call translate methods of all child controls
        self.control_seasons.translate()
        self.control_images.translate()
        self.control_facing.translate()
        self.control_dims.translate()
        self.control_offset.translate()
        self.control_iopaths.translate()
        # And the menus
        self.menubar.translate()
        # Finally re-do the window's layout
        self.panel.Layout()
##        self.update()

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        self.control_seasons.update()
        self.control_images.update()
        self.control_facing.update()
        self.control_dims.update()
        self.control_offset.update()
        self.control_iopaths.update()
        self.display.update()

class MyApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    VERSION_NUMBER = VERSION_NUMBER
    # Static variables
    South   = 0
    East    = 1
    North   = 2
    West    = 3
    Back    = 0
    Front   = 1
    Summer  = 0
    Winter  = 1
    choicelist_anim = choicelist_anim
    choicelist_paksize_int = choicelist_paksize_int
    choicelist_views_int = choicelist_views_int
    choicelist_dims_int = choicelist_dims_int
    choicelist_dims_z_int = choicelist_dims_z_int
    def OnInit(self):
        """Things to do immediately after the wx.App has been created"""
        # Load Program Options

        # Create and show debug window if debugging turned on
        
        # Could improve debug window by only initialising the frame etc. if debugging is turned on,
        # if it isn't then nothing gets created and calls to debug() simply log in the background
        # Debug frame also needs a save/export control to save messages (and some way to redirect
        # error output to the same frame)
        
        self.debug = debug(None, wx.ID_ANY, "Debugging", debug_on)
        if debug_on:
            self.debug.Show(1)
        return True

    def CheckProjectChanged(self):
        """Check if the active project has been changed since it was saved last,
           returns True if it's changed"""
        if self.PickleProject(app.activeproject) == app.activepickle:
            debug("Check Project for changes - Project Unchanged")
            return False
        else:
            debug("Check Project for changes - Project Changed")
            return True

    def SaveProject(self, project, file):
        """Save a project to the file location specified"""
        debug("Saving project to: %s" % file)

        pickle_string = self.PickleProject(project, 0)

        output = open(file, "wb")
        app.activepickle = pickle_string
        output.write(pickle_string)
        output.close()
        debug("Save project success")

    def NewProject(self):
        """Replace a project with a new one"""
        # Call init on the project, this will reset it to its defaults
        app.activeproject = tcproject.Project()
        app.activepickle = self.PickleProject(app.activeproject)
        debug("Active project reset to defaults (New project)")

    def LoadProject(self, file):
        """Load project from file, replacing the current activeproject"""
        app.activeproject = self.UnPickleProject(file)
        app.activepickle = self.PickleProject(app.activeproject)
        debug("Loaded project from: %s" % file)
        debug(app.activeproject.paksize())

    def PickleProject(self, project, picklemode = 0):
        """Pickle a project, returns a pickled string"""
        project.delImages()
        outstring = StringIO.StringIO()
        pickle.dump(project, outstring, picklemode)
        pickle_string = outstring.getvalue()
        outstring.close()
        debug("PickleProject, object type: %s pickle type: %s" % (str(project), picklemode))
        return pickle_string

    def UnPickleProject(self, filename):
        """Unpickle a project from file, returning a tcproject object"""
        file = open(filename, "rb")
        project = pickle.load(file)
        return project

    def ReloadWindow(self):
        """Reload the main window, e.g. to effect a translation change, does not affect debugging window"""

    def MainWindow(self):
        """Create main window after intialising project and debugging etc."""

        # Create a default active project
        self.projects = {}
        self.projects["default"] = tcproject.Project()
        self.activeproject = self.projects["default"]
        # Active hash is regenerated each time the project is saved, if the activeproject's current hash
        # differs from the saved one, then we know the project has been changed since last change and so
        # needs to be saved on new project/quit/load etc.
        self.activepickle = app.PickleProject(app.activeproject)

        # Single project implementation
        # Only one project in the dict at a time, prompt on new project to save etc.
        # New project -> If default changed, prompt to save, then create a new tcproject object and init frame
        # Load project -> prompt save, prompt to load, load in project and init frame
        # Need to write save/load routine, using pickle for data persistence
        # Higher level function to set activeproject, so can abstract for multi-project implementation

        # Create and show main frame
        self.frame = MainWindow(None, wx.ID_ANY, "TileCutter", MAIN_WINDOW_SIZE, MAIN_WINDOW_POSITION, MAIN_WINDOW_MINSIZE)
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)


    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        self.debug.Destroy()
        self.frame.Destroy()

# Run the program
if __name__ == '__main__':
    start_directory = os.getcwd()
    # Create the application
    app = MyApp()
    # Create the translation manager
    app.tctranslator = translator.Translator()
##    sys.stderr = open("error.txt","w")

    # Create the main application window
    app.MainWindow()
    display = app.frame.display
    # Init all main frame controls
    app.frame.update()
    # Show the main window frame
    app.frame.Show(1)

    # Launch into application's main loop
    app.MainLoop()
    app.Destroy()






