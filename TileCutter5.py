# coding: UTF-8
#
# TileCutter, version 0.5 (rewrite)
#

# Todo:

# BUG - Set active image to new image, then edit textbox to make path invalid, then edit it back to the original -> highlighting fails

# Find some way to eliminate flickering on translation update/initial load
# Text entry boxes visible position at end, or cursor, rather than beginning
# Padding/general layout optimisation
# -> Layout optimisation for mac
# Cutting mask display based on dimensions
# Make .dat and input images relative to save location path
# Speed optimisations - switching views seems really sluggish!
# Optimise code for generating lists in comboboxes (translation seems to be slowing this)

# Finish output file boxes, switching them to use the new set of functions              - DONE
# Do the project save/load/new etc. and management functionality (using pickle & hash)
# Program settings, load from a config file (using configparser)
# Dialog to set program options
# Implement use of special menu IDs to make menus work properly on, e.g., mac osx
# Produce frames picker control
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

# Move the UI classes, app etc. into a module, to enhance loading speed

# Needs much better error handling, add try/except clauses in critical places
# Could also encase entire script in an exception catcher, which can display exception 
#   and then gracefully shutdown wx, to prevent the flashing box/pythonwin crashing problem

# Add the TileCutter icon                                                               - Icon made, works well in windows
# Use img2py to compile icon image into the application                                 - DONE
# Can use the same technique for all the other images, e.g. bitmap buttons etc.         - DONE
# Need higher detail icons for the mac version                                          - DONE (Test icon display in OSX)

# About dialog                                                                          - DONE
# Make py2exe, look into producing smaller packages     - Also py2app
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

import sys, os, ConfigParser, StringIO, re, codecs

import tc, tcproject, imres, translator
# Custom platform codecs
import u_newlines, w_newlines

# Init variables
debug_on = True

VERSION_NUMBER = "0.5a"
##TRANSPARENT = (231,255,255)
TRANSPARENT = (0,0,0)
DEFAULT_PAKSIZE = "64"
PROJECT_FILE_EXTENSION = ".tcp"
### SB_WIDTH may be different on other platforms...
##SCROLLBAR_WIDTH = 16
VALID_IMAGE_EXTENSIONS = tcproject.VALID_IMAGE_EXTENSIONS

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
##choicelist_paksize = ["16","32","48","64","80","96","112","128","144","160","176","192","208","224","240"]
##choicelist_paksize = [gt("16"),gt("32"),gt("48"),gt("64"),gt("80"),gt("96"),gt("112"),gt("128"),gt("144"),gt("160"),gt("176"),gt("192"),gt("208"),gt("224"),gt("240")]
##choicelist_views = ["1","2","4"]
##choicelist_dims = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16"]
##choicelist_dims_z = ["1","2","3","4"]

# Translation function, simply calls tctranslator object's gt method
def gt(text):
    """Get text, return translation of string"""
    return tctranslator.gt(text)

def gsc(text, default=None):
    """Return the keyboard shortcut associated with a menu item"""
    # Filler function for now
    if default != None:
        return "\t" + default

def translateIntArray(intlist):
    """Takes an array of int values and translates them"""
    stringlist = []
    for i in intlist:
        stringlist.append(gt(str(i)))
    return stringlist

class fileTextBoxControls:
    """Methods for text boxes displaying URLs"""
    #                   Path 1 joined onto the end of path 2, to allow for relative paths, also used to calculate relative output
    def filePickerDialog(self, path1, path2=None, dialogText="", dialogFilesAllowed="", dialogFlags=None):
        """File picker dialog with additional methods"""
        if path2 == None:
            path2 = ""
        # If path exists, and is a file, or the path up to the last bit exists and is a directory
        if os.path.isfile(os.path.join(os.path.split(path2)[0],path1)) or os.path.isfile(os.path.join(path2,path1)) or os.path.isdir(os.path.join(path2,os.path.split(path1)[0])) or os.path.isdir(os.path.join(os.path.split(path2)[0],os.path.split(path1)[0])):
            a = os.path.join(os.path.split(path2)[0],os.path.split(path1)[0])
            b = os.path.split(path1)[1]
        # If path exists, and is a directory
        elif os.path.isdir(os.path.join(os.path.split(path2)[0],path1)) or os.path.isdir(os.path.join(path2,path1)):
            a = os.path.join(os.path.split(path2)[0],path1)
            b = ""
        # If path does not exist
        else:
            # Assume that the last component of the png path is the filename, and find the largest component of the dat
            # path which exists
            a = self.existingPath(path2)
            b = os.path.split(path1)[1]
        # Show the dialog
        pickerDialog = wx.FileDialog(self.parent, dialogText,
                                     a, b, dialogFilesAllowed, dialogFlags)
        if pickerDialog.ShowModal() == wx.ID_OK:
            # This needs to calculate a relative path between the location of the output png and the location of the output dat
            value = os.path.join(pickerDialog.GetDirectory(), pickerDialog.GetFilename())
            relative = self.comparePaths(value, path2)
            pickerDialog.Destroy()
            return relative
        else:
            # Else cancel was pressed, do nothing
            return path1

    # Needs to be recoded to use generator/list comprehension stuff
    # Also needs to add caching of directory existance check and more intelligent updating based on the editing position of the
    # text entry, maybe even make this a persistent object modified along with the text entry

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

    def highlightText(self, box, p1, p2=None):
        """Update the highlighting in a text entry box"""
        # Path value, optionally relative to a second path
        a = self.splitPath(p1, p2)
        # Set entire length of the box to default colour
        box.SetStyle(0,len(p1), wx.TextAttr(None, "white"))
        # Then recolour both boxes to reflect path existence
        for k in range(len(a)):
            if a[k][3]:         # If this path section exists, colour it white
                box.SetStyle(a[k][1],a[k][1] + a[k][2], wx.TextAttr(None, "white"))
            else:               # If path section doesn't exist, colour it yellow
                box.SetStyle(a[k][1],a[k][1] + a[k][2], wx.TextAttr(None, "#FFFF00"))

    # All of this file manipulation stuff could potentially be built into an extended text control

    # Path manipulation functions
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
            a.insert(0,    [n[1],  len(p1)-len(n[1]),   len(n[1]),  os.path.exists(self.joinPaths(p2, p1))])#, existsAsType(p)])
            p1 = n[0]
        return a

    def joinPaths(self, p1, p2):
        """Join p2 to p1, accounting for end cases (is directory, is file etc.)"""
        if p1 != None:
            # Workdir is a working directory optionally used to check for existence of relative paths
            # Need to check the end component
            if os.path.isfile(p1):
                # If it's a file that exists, split the directory off
                p1 = os.path.split(p1)[0]
            else:
                # Otherwise hard to tell, best to just split it (assuming here that there's a filename at the end)
                p1 = os.path.split(p1)[0]
        else:
            p1 = ""
        return os.path.join(p1, p2)

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

    def comparePaths(self, p1, p2):
        """Compare two absolute paths, returning either a relative path from p1 to p2, or p1 if no relative path exists"""
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




class ImageWindow(wx.ScrolledWindow, fileTextBoxControls):
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
        debug("blah")
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
        if self.impath_entry_box.GetValue() != activeproject.activeImage().path() and self.impath_entry_box.GetValue() != activeproject.activeImage().lastpath():
            self.impath_entry_box.SetValue(activeproject.activeImage().path())
        # And then redraw the active image in the window, with mask etc.
        bitmap = activeproject.activeImage().bitmap()

        # Setup image properties for mask generation
        x = activeproject.x()
        y = activeproject.y()
        z = activeproject.z()
        p = activeproject.paksize()
        p2 = p/2
        p4 = p/4
        mask_offset_x, mask_offset_y = activeproject.offset()
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

##            dc.SetPen(wx.Pen((0,255,0)))
##            dc.DrawPoint(pos[0]+p2,pos[1])
##            dc.DrawPoint(pos[0],pos[1]-p4)
##            dc.SetPen(wx.Pen((255,0,0)))

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
        if self.impath_entry_box.GetValue() != activeproject.activeImage().path() and self.impath_entry_box.GetValue() != activeproject.activeImage().lastpath():
            debug("Text changed in image path box, new text: " + self.impath_entry_box.GetValue())
            # Check whether the entered path exists or not, if it does update the value in the activeproject (which will cause
            # that new image to be loaded & displayed) if not don't set this value
            if os.path.isfile(self.impath_entry_box.GetValue()) and os.path.splitext(self.impath_entry_box.GetValue())[1] in VALID_IMAGE_EXTENSIONS:
                # Is a valid file, display green tick icon
                debug("...new text is a valid file")
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
                # Update the active image with the new path
                activeproject.activeImage().path(self.impath_entry_box.GetValue())
                # Then redraw the image
                self.update()
            else:
                # Not a valid file, display red cross icon
                self.impath_entry_icon.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK))
                debug("...but new text not a valid file!")
                # Highlight text function only needed if it isn't a valid file, obviously
                self.highlightText(self.impath_entry_box, self.impath_entry_box.GetValue())
            # Update the last path
            activeproject.activeImage().lastpath(self.impath_entry_box.GetValue())
    def OnBrowseSource(self,e):
        """When browse source button clicked"""
        value = self.filePickerDialog(activeproject.activeImage().path(), "", gt("Choose a source image for this view:"),
                                      "PNG files (*.png)|*.png", wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        self.impath_entry_box.SetValue(value)
    def OnReloadImage(self,e):
        """When reload image button clicked"""
        activeproject.activeImage().reloadImage()
        self.update()
    def OnLoadImageForAll(self,e):
        """When "load same image for all" button is clicked"""

    # Old extended display methods
##    def OnLeftDown(self, e):
##        """Called when the left mouse button is pressed"""
##        self.pos = self.CalcUnscrolledPosition(e.GetPosition())
##        app.debug_frame.WriteLine("DC: MouseLeftClick: %s"%str(self.pos))
##        # If the mouse is within the region of the cutting mask
##        # then check to see if it's
##        #if self.realpos 
##
##    def OnMotion(self, e):
##        """Called when the mouse moves over the DC"""
##        self.pos = self.CalcUnscrolledPosition(e.GetPosition())
##        #app.debug_frame.WriteLine("DC: MouseMoveTo: %s"%str(self.pos))
##        # Check if the mouse is within the base of the cutting mask
##        offset_x = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_x
##        offset_y = self.active.frame[self.active.activeimage[0]].direction[self.active.activeimage[1]].image[self.active.activeimage[2]].offset_y
##        self.lastisopos = self.isopos
##        self.isopos = self.ScreenToIso(self.pos, (offset_x,offset_y))
##        if self.isopos != self.lastisopos:
##            app.debug_frame.WriteLine("DC: MouseMoveTo: %s, ISO: %s"%(str(self.pos),str(self.isopos)))
##            if self.isopos == (-1,-1):
##                self.active.temp.draw_iso = 0
##                self.active.temp.iso_pos = self.isopos
##                self.GetGrandParent().GetParent().DrawImage()       # Needs alteration
##            else:
##                self.active.temp.draw_iso = 1
##                self.active.temp.iso_pos = self.isopos
##                self.GetGrandParent().GetParent().DrawImage()       # Needs alteration
##
##    def ScreenToIso(self, wxy=(0,0), offset=(0,0)):
##        """Convert screen coordinates to Iso world coordinates
##        returns tuple of iso coords"""
##        offx, offy = offset
##        if offx < 0:
##            offx = 0
##        if offy < 0:
##            offy = 0
##
##        p = self.active.info.paksize
##
##        # If east/west reverse dims
##        if self.active.activeimage[1] in [0,2]:
##            xdims = self.active.info.xdims
##            ydims = self.active.info.ydims
##        else:
##            ydims = self.active.info.xdims
##            xdims = self.active.info.ydims
##
##        TileRatio = 2
##        wx, wy = wxy
##
##        widthx = xdims * (p/2)
##
##        dx = wx - widthx - offx
##        dy = wy - ((self.active.info.zdims-1) * p) - offy - p/2
##
##        x = int((dy - dx / TileRatio) * (TileRatio / 2) / (p/2))
##        y = int((dy + dx / TileRatio) * (TileRatio / 2) / (p/2))
##        if x < 0 or y < 0:
##            return (-1,-1)
##        if x == 0 and y == 0:
##            return (x,y)
##        if x >= (xdims) or y >= (ydims):
##            return (-1,-1)
##        
##        return (x,y)




class seasonControl(wx.StaticBox):
    """Box containing season alteration controls"""
    def __init__(self,parent,parent_sizer):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Season"))
            # Setup sizers
        self.s_seasons = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_seasons_flex.AddGrowableCol(1)
            # Add items
        self.seasons_select_summer_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageSummer"].getBitmap())
        self.seasons_select_summer = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.seasons_select_winter_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageWinter"].getBitmap())
        self.seasons_select_winter = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.seasons_enable_winter = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
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

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.seasons_select_summer.SetLabel(gt("Summer"))
        self.seasons_select_summer.SetToolTipString(gt("tt_seasons_select_summer"))
        self.seasons_select_winter.SetLabel(gt("Winter"))
        self.seasons_select_winter.SetToolTipString(gt("tt_seasons_select_winter"))
        self.seasons_enable_winter.SetLabel(gt("Enable Winter"))
        self.seasons_enable_winter.SetToolTipString(gt("tt_seasons_enable_winter"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if activeproject.winter() == 0:  # Turn winter image off
            self.seasons_enable_winter.SetValue(0)
            # If currently have winter image selected, switch to summer image
            if self.seasons_select_summer.GetValue() == True:
                # Update model
                activeproject.activeImage(season=Summer)
                self.seasons_select_summer.SetValue(1)
                # As active season changed, need to redraw display
                display.update()
            # Then disable the control
            self.seasons_select_winter.Disable()
        else:
            self.seasons_enable_winter.SetValue(1)
            # User must select the winter image if they wish to view it, so just enable the control
            self.seasons_select_winter.Enable()

    def OnToggle(self,e):
        """Toggling between summer and winter imagesf"""
        activeproject.winter(self.seasons_enable_winter.GetValue())
        self.update()
    def OnSummer(self,e):
        """Toggle Summer image"""
        # Set active image to Summer
        activeproject.activeImage(season=Summer)
        # Redraw active image
        display.update()
    def OnWinter(self,e):
        """Toggle Winter image"""
        # Set active image to Winter
        activeproject.activeImage(season=Winter)
        # Redraw active image
        display.update()

class imageControl(wx.StaticBox):
    """Box containing Front/Back image controls"""
    def __init__(self,parent,parent_sizer):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Image"))
            # Setup sizers
        self.s_images = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_images_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_images_flex.AddGrowableCol(1)
            # Add items
        self.images_select_back_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageBack"].getBitmap())
        self.images_select_back = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.images_select_front_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageFront"].getBitmap())
        self.images_select_front = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.images_enable_front = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
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

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.images_select_back.SetLabel(gt("BackImage"))
        self.images_select_back.SetToolTipString(gt("tt_images_select_back"))
        self.images_select_front.SetLabel(gt("FrontImage"))
        self.images_select_front.SetToolTipString(gt("tt_images_select_front"))
        self.images_enable_front.SetLabel(gt("Enable FrontImage"))
        self.images_enable_front.SetToolTipString(gt("tt_images_enable_front"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if activeproject.frontimage() == 0:  # Turn frontimage off
            self.images_enable_front.SetValue(0)
            # If currently have frontimage selected, switch to backimage
            if self.images_select_front.GetValue() == True:
                # Update model
                activeproject.activeImage(layer=Back)
                self.images_select_back.SetValue(1)
                # As active layer changed, need to redraw display
                display.update()
            # Then disable the control
            self.images_select_front.Disable()
        else:
            self.images_enable_front.SetValue(1)
            # User must select the frontimage if they wish to view it, so just enable the control
            self.images_select_front.Enable()

    def OnToggle(self,e):
        """Toggling frontimage on and off"""
        activeproject.frontimage(self.images_enable_front.GetValue())
        self.update()
    def OnBackImage(self,e):
        """Toggle BackImage on"""
        # Set active image to Back
        activeproject.activeImage(layer=Back)
        # Redraw active image
        display.update()
    def OnFrontImage(self,e):
        """Toggle FrontImage on"""
        # Set active image to Front
        activeproject.activeImage(layer=Front)
        # Redraw active image
        display.update()

class facingControl(wx.StaticBox):
    """Box containing direction facing controls"""
    def __init__(self,parent,parent_sizer):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Direction Facing"))
            # Setup sizers
        self.s_facing = wx.StaticBoxSizer(self, wx.HORIZONTAL)
        self.s_facing_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_facing_flex.AddGrowableCol(1)
        self.s_facing_right = wx.BoxSizer(wx.VERTICAL)
        self.s_facing_1 = wx.BoxSizer(wx.HORIZONTAL)
            # Add items
        self.facing_select_south_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageSouth"].getBitmap())
        self.facing_select_south = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.facing_select_east_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageEast"].getBitmap())
        self.facing_select_east = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_select_north_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageNorth"].getBitmap())
        self.facing_select_north = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_select_west_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageWest"].getBitmap())
        self.facing_select_west = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_enable_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_enable_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
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

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.facing_select_south.SetLabel(gt("South"))
        self.facing_select_south.SetToolTipString(gt("tt_facing_select_south"))
        self.facing_select_east.SetLabel(gt("East"))
        self.facing_select_east.SetToolTipString(gt("tt_facing_select_east"))
        self.facing_select_north.SetLabel(gt("North"))
        self.facing_select_north.SetToolTipString(gt("tt_facing_select_north"))
        self.facing_select_west.SetLabel(gt("West"))
        self.facing_select_west.SetToolTipString(gt("tt_facing_select_west"))
        self.facing_enable_label.SetLabel(gt("Number\nof views:"))
        self.facing_enable_select.SetToolTipString(gt("tt_facing_enable_select"))
        # Translate the choicelist values for paksize
        self.choicelist_views = translateIntArray(choicelist_views_int)
        self.facing_enable_select.Clear()
        for i in self.choicelist_views:
            self.facing_enable_select.Append(i)
        # And set value to value in the project
        self.facing_enable_select.SetStringSelection(self.choicelist_views[choicelist_views_int.index(activeproject.views())])

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Set value of the toggle control (to set number of directions)
        if activeproject.views() == 1:
            self.facing_enable_select.SetValue(self.choicelist_views[0])
            # Update controls
            self.facing_select_south.Enable()
            self.facing_select_east.Disable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_east.GetValue() == True or self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_south.SetValue(1)
                # Modify active image to only available option
                activeproject.activeImage(direction=South)
                # Redraw active image
                display.update()
        elif activeproject.views() == 2:
            self.facing_enable_select.SetValue(self.choicelist_views[1])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_east.SetValue(1)
                # Modify active image to available option
                activeproject.activeImage(direction=East)
                # Redraw active image
                display.update()
        else:
            self.facing_enable_select.SetValue(self.choicelist_views[2])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Enable()
            self.facing_select_west.Enable()
        # Update the combobox
        self.facing_enable_select.SetStringSelection(self.choicelist_views[choicelist_views_int.index(activeproject.views())])

    def OnToggle(self,e):
        """Changing the value in the selection box"""
        activeproject.views(choicelist_views_int[self.choicelist_views.index(self.facing_enable_select.GetValue())])
        self.update()
    def OnSouth(self,e):
        """Toggle South direction"""
        # Set active image to South
        activeproject.activeImage(direction=South)
        # Redraw active image
        display.update()
    def OnEast(self,e):
        """Toggle East direction"""
        # Set active image to East
        activeproject.activeImage(direction=East)
        # Redraw active image
        display.update()
    def OnNorth(self,e):
        """Toggle North direction"""
        # Set active image to North
        activeproject.activeImage(direction=North)
        # Redraw active image
        display.update()
    def OnWest(self,e):
        """Toggle West direction"""
        # Set active image to West
        activeproject.activeImage(direction=West)
        # Redraw active image
        display.update()

class dimsControl(wx.StaticBox):
    """Box containing dimensions controls"""
    def __init__(self,parent,parent_sizer):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Dimensions"))
            # Setup sizers
        self.s_dims = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_dims_flex = wx.FlexGridSizer(0,2,0,0)
        self.s_dims_flex.AddGrowableCol(1)
            # Add items
        self.dims_p_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_p_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY)
        self.dims_z_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_z_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY)
        self.dims_x_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_x_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY)
        self.dims_y_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dims_y_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY)
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
            # Add element to its parent sizer
        parent_sizer.Add(self.s_dims, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)
            # Bind functions
        self.dims_p_select.Bind(wx.EVT_COMBOBOX, self.OnPaksizeSelect, self.dims_p_select)
        self.dims_z_select.Bind(wx.EVT_COMBOBOX, self.OnZdimsSelect, self.dims_z_select)
        self.dims_x_select.Bind(wx.EVT_COMBOBOX, self.OnXdimsSelect, self.dims_x_select)
        self.dims_y_select.Bind(wx.EVT_COMBOBOX, self.OnYdimsSelect, self.dims_y_select)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.dims_p_label.SetLabel(gt("Paksize"))
        self.dims_p_select.SetToolTipString(gt("tt_dims_paksize_select"))
        self.dims_z_label.SetLabel(gt("Z dimension"))
        self.dims_z_select.SetToolTipString(gt("tt_dims_z_select"))
        self.dims_x_label.SetLabel(gt("X dimension"))
        self.dims_x_select.SetToolTipString(gt("tt_dims_x_select"))
        self.dims_y_label.SetLabel(gt("Y dimension"))
        self.dims_y_select.SetToolTipString(gt("tt_dims_y_select"))
        # To allow for translation of values in combobox controls, master list is int list, translated list is generated
        #   on the fly from the master list, these lists then index each other to determine the values to set
        # Translate the choicelist values for paksize
        self.choicelist_packsize = translateIntArray(choicelist_paksize_int)
        self.dims_p_select.Clear()
        for i in self.choicelist_packsize:
            self.dims_p_select.Append(i)
        # And set value to value in the project
        self.dims_p_select.SetStringSelection(self.choicelist_packsize[choicelist_paksize_int.index(activeproject.paksize())])
        # Translate the choicelist values for z dims
        self.choicelist_dims_z = translateIntArray(choicelist_dims_z_int)
        self.dims_z_select.Clear()
        for i in self.choicelist_dims_z:
            self.dims_z_select.Append(i)
        # And set value to value in the project
        self.dims_z_select.SetStringSelection(self.choicelist_dims_z[choicelist_dims_z_int.index(activeproject.z())])
        # Translate the choicelist values for x and y dims
        self.choicelist_dims = translateIntArray(choicelist_dims_int)
        self.dims_x_select.Clear()
        self.dims_y_select.Clear()
        for i in self.choicelist_dims:
            self.dims_x_select.Append(i)
            self.dims_y_select.Append(i)
        # And set value to value in the project
        self.dims_x_select.SetStringSelection(self.choicelist_dims[choicelist_dims_int.index(activeproject.x())])
        self.dims_y_select.SetStringSelection(self.choicelist_dims[choicelist_dims_int.index(activeproject.y())])

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        self.dims_p_select.SetStringSelection(self.choicelist_packsize[choicelist_paksize_int.index(activeproject.paksize())])
        self.dims_z_select.SetStringSelection(self.choicelist_dims_z[choicelist_dims_z_int.index(activeproject.z())])
        self.dims_x_select.SetStringSelection(self.choicelist_dims[choicelist_dims_int.index(activeproject.x())])
        self.dims_y_select.SetStringSelection(self.choicelist_dims[choicelist_dims_int.index(activeproject.y())])

    def OnPaksizeSelect(self,e):
        """Change value of the paksize"""
        activeproject.paksize(choicelist_paksize_int[self.choicelist_packsize.index(self.dims_p_select.GetValue())])
        display.update()
    def OnZdimsSelect(self,e):
        """Change value of the Z dims"""
        activeproject.z(choicelist_dims_z_int[self.choicelist_dims_z.index(self.dims_z_select.GetValue())])
        display.update()
    def OnXdimsSelect(self,e):
        """Change value of the X dims"""
        activeproject.x(choicelist_dims_int[self.choicelist_dims.index(self.dims_x_select.GetValue())])
        display.update()
    def OnYdimsSelect(self,e):
        """Change value of the Y dims"""
        activeproject.y(choicelist_dims_int[self.choicelist_dims.index(self.dims_y_select.GetValue())])
        display.update()

class offsetControl(wx.StaticBox):
    """Box containing offset controls"""
    def __init__(self,parent,parent_sizer):
        wx.StaticBox.__init__(self,parent,wx.ID_ANY,gt("Offset/Mask"))
            # Setup sizers
        self.s_offset = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0,4,0,0)
            # Add items
        self.offset_button_up = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveUpDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_left = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveLeftDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_reset = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveCenter"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_right = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveRightDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_down = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveDownDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_selector = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
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
            # Add element to its parent sizer
        parent_sizer.Add(self.s_offset, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 0)
            # Bind functions
        self.offset_button_up.Bind(wx.EVT_BUTTON, self.OnUp, self.offset_button_up)
        self.offset_button_left.Bind(wx.EVT_BUTTON, self.OnLeft, self.offset_button_left)
        self.offset_button_reset.Bind(wx.EVT_BUTTON, self.OnCenter, self.offset_button_reset)
        self.offset_button_right.Bind(wx.EVT_BUTTON, self.OnRight, self.offset_button_right)
        self.offset_button_down.Bind(wx.EVT_BUTTON, self.OnDown, self.offset_button_down)
        self.offset_selector.Bind(wx.EVT_CHECKBOX, self.OnFine, self.offset_selector)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.offset_button_up.SetToolTipString(gt("tt_offset_button_up"))
        self.offset_button_left.SetToolTipString(gt("tt_offset_button_left"))
        self.offset_button_reset.SetToolTipString(gt("offset_button_reset"))
        self.offset_button_right.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_down.SetToolTipString(gt("tt_offset_button_down"))
        self.offset_selector.SetLabel(gt("Fine"))
        self.offset_selector.SetToolTipString(gt("tt_offset_selector"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Offset control doesn't have any controls which are determined by the model, "fine" checkbox always off by default

    def OnFine(self,e):
        """On toggle of the "fine" checkbox, change images on the buttons"""
        if self.offset_selector.GetValue():
            self.offset_button_up.SetBitmapLabel(imres.catalog["MoveUp"].getBitmap())
            self.offset_button_left.SetBitmapLabel(imres.catalog["MoveLeft"].getBitmap())
            self.offset_button_right.SetBitmapLabel(imres.catalog["MoveRight"].getBitmap())
            self.offset_button_down.SetBitmapLabel(imres.catalog["MoveDown"].getBitmap())
        else:
            self.offset_button_up.SetBitmapLabel(imres.catalog["MoveUpDouble"].getBitmap())
            self.offset_button_left.SetBitmapLabel(imres.catalog["MoveLeftDouble"].getBitmap())
            self.offset_button_right.SetBitmapLabel(imres.catalog["MoveRightDouble"].getBitmap())
            self.offset_button_down.SetBitmapLabel(imres.catalog["MoveDownDouble"].getBitmap())

    def OnUp(self,e):
        """Move mask up"""
        if self.offset_selector.GetValue():
            r = activeproject.offset(y=1)
        else:
            r = activeproject.offset(y=activeproject.paksize())
        if r == 1:
            display.update()
    def OnLeft(self,e):
        """Move mask left"""
        if self.offset_selector.GetValue():
            r = activeproject.offset(x=-1)
        else:
            r = activeproject.offset(x=-activeproject.paksize())
        if r == 1:
            display.update()
    def OnCenter(self,e):
        """Reset mask position"""
        r = activeproject.offset(x=0, y=0)
        if r == 1:
            display.update()
    def OnRight(self,e):
        """Move mask right"""
        if self.offset_selector.GetValue():
            r = activeproject.offset(x=1)
        else:
            r = activeproject.offset(x=activeproject.paksize())
        if r == 1:
            display.update()
    def OnDown(self,e):
        """Move mask down"""
        if self.offset_selector.GetValue():
            r = activeproject.offset(y=-1)
        else:
            r = activeproject.offset(y=-activeproject.paksize())
        if r == 1:
            display.update()

class fileControls(fileTextBoxControls):
    """Controls at the bottom of the window, file output locations"""
    def __init__(self,parent,parent_sizer):
##        fileTextBoxControls.__init__()
        """Produce controls, two file path entries"""
        self.parent = parent
            # Bottom panel sizers
        self.s_panel_bottom_left = wx.FlexGridSizer(0,3,0,0)    # Contains paths for output .dat and .png
            # Dat/pak output path entry
        self.dat_outpath_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dat_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.dat_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.dat_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
            # Add them to sizer...
        self.s_panel_bottom_left.Add(self.dat_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.dat_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangeDat, self.dat_outpath_box)
        self.dat_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseDat, self.dat_outpath_filebrowse)

            # Image output path entry
        self.im_outpath_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.im_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.im_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.im_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
            # Add to sizer...
        self.s_panel_bottom_left.Add(self.im_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.im_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangePng, self.im_outpath_box)
        self.im_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowsePng, self.im_outpath_filebrowse)
        parent_sizer.Add(self.s_panel_bottom_left, 1, wx.EXPAND, 0)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.dat_outpath_label.SetLabel(gt("Output Dat or Pak File Location:"))
        self.dat_outpath_box.SetToolTipString(gt("tt_output_dat_file_location"))
        self.dat_outpath_filebrowse.SetLabel(gt("Browse..."))
        self.dat_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_dat_file_location"))

        self.im_outpath_label.SetLabel(gt("Path from .dat to .png:"))
        self.im_outpath_box.SetToolTipString(gt("tt_output_image_location"))
        self.im_outpath_filebrowse.SetLabel(gt("Browse..."))
        self.im_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_image_location"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Setting these values should also cause text highlighting to occur
        self.dat_outpath_box.SetValue(activeproject.datfile())
        self.im_outpath_box.SetValue(activeproject.pngfile())
        self.highlightText(self.dat_outpath_box, activeproject.datfile())
        self.highlightText(self.im_outpath_box, activeproject.pngfile(), activeproject.datfile())

    def OnTextChangeDat(self,e):
        """When the text in the .dat/.pak output file entry box changes"""
        if activeproject.datfile() != self.dat_outpath_box.GetValue():
            activeproject.datfile(self.dat_outpath_box.GetValue())
            debug("Text changed in DAT entry box, new text: " + str(activeproject.datfile()))
            self.highlightText(self.dat_outpath_box, activeproject.datfile())
            self.highlightText(self.im_outpath_box, activeproject.pngfile(), activeproject.datfile())
    def OnTextChangePng(self,e):
        """When the text in the .png output file entry box changes"""
        if activeproject.pngfile() != self.im_outpath_box.GetValue():
            activeproject.pngfile(self.im_outpath_box.GetValue())
            debug("Text changed in PNG entry box, new text: " + str(activeproject.pngfile()))
            self.highlightText(self.dat_outpath_box, activeproject.datfile())
            self.highlightText(self.im_outpath_box, activeproject.pngfile(), activeproject.datfile())

    def OnBrowseDat(self,e):
        """Opens a file save as dialog for the dat/pak output file"""
        value = self.filePickerDialog(activeproject.datfile(), "", gt("Choose a location to output .dat/.pak to"),
                                      "DAT/PAK files (*.dat)|*.dat|(*.pak)|*.pak", wx.FD_SAVE|wx.OVERWRITE_PROMPT)
        self.dat_outpath_box.SetValue(value)

    def OnBrowsePng(self,e):
        """Opens a file save as dialog for the png output file"""
        value = self.filePickerDialog(activeproject.pngfile(), activeproject.datfile(), gt("Choose a file to save to..."),
                                      "PNG files (*.png)|*.png", wx.FD_SAVE|wx.OVERWRITE_PROMPT)
        self.im_outpath_box.SetValue(value)


class aboutDialog(wx.Dialog):
    """Dialog which displays information about the program"""
    def __init__(self, parent):
        """Intialise the dialog"""
##        "TileCutter v.%s"%VERSION_NUMBER
        size = (300,300)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.icon = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["tc_icon2_128_plain"].getBitmap())
        f = self.GetFont()
        self.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.title_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subtitle_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.SetFont(f)
        self.version_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.copyright_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)

        # Add close button at the bottom
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        self.s_panel.Add(self.icon,1,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM, 10)
        self.s_panel.Add(self.title_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 2)
        self.s_panel.Add(self.subtitle_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 4)
        self.s_panel.Add(self.version_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 4)
        self.s_panel.Add(self.copyright_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 10)
        # These bits are non-mac only
        self.s_panel.Add(wx.StaticLine(self, wx.ID_ANY, (-1,-1), (-1,1)),0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.s_panel.Add(self.buttons,0,wx.ALIGN_RIGHT|wx.ALL, 3)

        # Bind events
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        # Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()

        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(gt("About TileCutter"))
        self.close_button.SetLabel(gt("Close"))
        self.title_text.SetLabel(gt("TileCutter"))
        self.subtitle_text.SetLabel(gt("Simutrans Building Editor"))
        self.version_text.SetLabel(gt("Version %s") % VERSION_NUMBER)
        self.copyright_text.SetLabel("Copyright © 2008 Timothy Baldock. All rights reserved.")

        self.Layout()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnClose(self,e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)

class translationDialog(wx.Dialog):
    """Dialog for choosing which translation to use"""
    def __init__(self,parent):
        """Initialise the dialog and populate lists"""
        size = (300,200)
        wx.Dialog.__init__(self,parent,wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.top_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.language_picker = wx.ComboBox(self, wx.ID_ANY, tctranslator.active.longname(), (-1, -1), (-1, -1), tctranslator.language_longnames_list, wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)

        # Within the static box
        self.dialog_box = wx.StaticBox(self, wx.ID_ANY, gt("Language Details:"))
        self.s_dialog_box = wx.StaticBoxSizer(self.dialog_box, wx.HORIZONTAL)
        # Bitmap flag display on the left
        self.country_icon = wx.StaticBitmap(self, wx.ID_ANY, tctranslator.active.icon())
        # Three static texts on the right containing information within a vertical sizer
        self.s_dialog_box_right = wx.FlexGridSizer(0,2,0,0)
        self.s_dialog_box_right.AddGrowableCol(1)
        self.label_name = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.label_createdby = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.label_createdon = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.label_name_value = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.label_createdby_value = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.label_createdon_value = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        # Add these to their sizer
        self.s_dialog_box_right.Add(self.label_name,0,wx.EXPAND, 0)
        self.s_dialog_box_right.Add(self.label_name_value,0,wx.EXPAND|wx.LEFT, 3)
        self.s_dialog_box_right.Add(self.label_createdby,0,wx.EXPAND, 0)
        self.s_dialog_box_right.Add(self.label_createdby_value,0,wx.EXPAND|wx.LEFT, 3)
        self.s_dialog_box_right.Add(self.label_createdon,0,wx.EXPAND, 0)
        self.s_dialog_box_right.Add(self.label_createdon_value,0,wx.EXPAND|wx.LEFT, 3)
        
        # Add close button at the bottom
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        # Then add bitmap and texts to the static box sizer
        self.s_dialog_box.Add(self.country_icon,0,wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        self.s_dialog_box.Add(self.s_dialog_box_right,1,wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 10)

        # And finally add that, the language picker and the other static text to the panel sizer
        self.s_panel.Add(self.top_label,0,wx.EXPAND|wx.ALL, 3)
        self.s_panel.Add(self.language_picker,0,wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel.Add(self.s_dialog_box,1,wx.EXPAND|wx.ALL, 3)
        self.s_panel.Add(self.buttons,0,wx.ALIGN_RIGHT|wx.ALL, 3)

        # Bind events
        self.language_picker.Bind(wx.EVT_COMBOBOX, self.OnSelection, self.language_picker)
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        # Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
        self.Layout()

        self.translate()    # Load the initial translation
##        self.update()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(gt("Language"))
        self.top_label.SetLabel(gt("Select from the options below:"))
        self.close_button.SetLabel(gt("Close"))
        # These values taken from the active translation
        self.label_name.SetLabel(gt("Language:"))
        self.label_name_value.SetLabel(tctranslator.active.longname())
        self.label_createdby.SetLabel(gt("Created by:"))
        self.label_createdby_value.SetLabel(tctranslator.active.created_by())
        self.label_createdon.SetLabel(gt("Created on:"))
        self.label_createdon_value.SetLabel(tctranslator.active.created_date())
        # And finally change the image
        self.country_icon.SetBitmap(tctranslator.active.icon())
        self.Layout()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnClose(self,e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)
    def OnSelection(self,e):
        """When user changes the language selection"""
        # Set active translation to the one specified
        tctranslator.setActiveTranslation(tctranslator.longnameToName(self.language_picker.GetValue()))
        # Call own translate function
        self.translate()
        app.frame.translate()


class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self,parent,id,title, windowsize=(800,600)):
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (200,100), windowsize,
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
                                        )
        # Init stuff
        self.SetMinSize(windowsize)

        # Set the program's icon
        self.icons = wx.IconBundle()
        self.icons.AddIcon(imres.catalog["tc_icon2_16_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_32_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_48_plain"].getIcon())
        self.SetIcons(self.icons)
        app.debug.SetIcons(self.icons)

        # Create the menus
        self.menubar = menuObject(self)
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
        self.control_seasons = seasonControl(self.panel, self.s_panel_controls)
        # Image controls-------------------------------------------------------------------
        self.control_images = imageControl(self.panel, self.s_panel_controls)
        # Facing controls------------------------------------------------------------------
        self.control_facing = facingControl(self.panel, self.s_panel_controls)
        # Dimension controls---------------------------------------------------------------
        self.control_dims = dimsControl(self.panel, self.s_panel_controls)
        # Offset/mask controls-------------------------------------------------------------
        self.control_offset = offsetControl(self.panel, self.s_panel_controls)

        # Create Image display window and image path entry control, which adds itself to the sizer
        self.display = ImageWindow(self.panel, self.s_panel_imagewindow_container)

        # IMAGE/DAT OUTPUT PATHS
        # Create the I/O path inputs, which are added to the bottom-left panel container
        self.control_iopaths = fileControls(self.panel, self.s_panel_bottom)

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
        self.s_panel_top.Add(self.s_panel_controls,0,wx.EXPAND, 0)
        self.s_panel_top.Add(self.s_panel_imagewindow_container,1,wx.EXPAND, 0)
        # Add bottom and top parts to overall panel 
        self.s_panel.Add(self.s_panel_top,1,wx.EXPAND, 0)
        self.s_panel.Add(self.s_panel_bottom,0,wx.EXPAND|wx.RIGHT, 0)

        # Layout sizers
        self.panel.SetSizer(self.s_panel)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()

        # misc testing stuff
        im = Image.open("dino.png")
        outimage = wx.EmptyImage(im.size[0], im.size[1])
        outimage.SetData(im.convert("RGB").tostring())
        outimage = outimage.ConvertToBitmap()
        self.display.bmp = outimage

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
##        self.Update()

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        self.control_seasons.update()
        self.control_images.update()
        self.control_facing.update()
        self.control_dims.update()
        self.control_offset.update()
        self.control_iopaths.update()
##        self.display.update()

class menuObject:
    """Class containing the main program menu"""
    def __init__(self, parent):
        """Create the menu"""
        self.parent = parent
        self.menu = wx.MenuBar()
        # File menu
        self.fileMenu = wx.Menu()
        self.menu_file_new = self.AddMenuItem(self.fileMenu, self.OnNewProject)
        self.menu_file_open = self.AddMenuItem(self.fileMenu, self.OnOpenProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_save = self.AddMenuItem(self.fileMenu, self.OnSaveProject)
        self.menu_file_saveas = self.AddMenuItem(self.fileMenu, self.OnSaveProjectAs)
        self.fileMenu.AppendSeparator()
        self.menu_file_cut = self.AddMenuItem(self.fileMenu, self.OnCutProject)
        self.menu_file_export = self.AddMenuItem(self.fileMenu, self.OnExportProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_exit = self.AddMenuItem(self.fileMenu, self.OnExit, id=wx.ID_EXIT)
        # Tools menu
        self.toolsMenu = wx.Menu()
        self.menu_tools_dat = self.AddMenuItem(self.toolsMenu, self.OnDatEdit)
        self.menu_tools_smoke = self.AddMenuItem(self.toolsMenu, self.OnSmokeEdit)
        self.toolsMenu.AppendSeparator()
        self.menu_tools_language = self.AddMenuItem(self.toolsMenu, self.OnSelectLanguage)
        self.menu_tools_prefs = self.AddMenuItem(self.toolsMenu, self.OnPreferences, id=wx.ID_PREFERENCES)
        # Help menu
        self.helpMenu = wx.Menu()
        self.menu_help_help = self.AddMenuItem(self.helpMenu, self.OnHelp, id=wx.ID_HELP)
        # Need to fix this so that separator doesn't appear on the mac
        self.helpMenu.AppendSeparator()
        self.menu_help_about = self.AddMenuItem(self.helpMenu, self.OnAbout, id=wx.ID_ABOUT)

        self.menu.Append(self.fileMenu, "")
        self.menu.Append(self.toolsMenu, "")
        self.menu.Append(self.helpMenu, "")

        self.translate()    # Load the initial translation
##        self.update()       # Init this control with the default values from the active project

    def translate(self):
        """Update the text of all menu items to reflect a new translation"""
        # File menu
        self.menu.SetMenuLabel(0,"&File")
        self.menu_file_new.SetItemLabel(gt("&New Project") + gsc("menu_file_new", "Ctrl-N"))
        self.menu_file_new.SetHelp(gt("tt_menu_file_new"))
        self.menu_file_open.SetItemLabel(gt("&Open Project") + gsc("menu_file_open", "Ctrl-O"))
        self.menu_file_open.SetHelp(gt("tt_menu_file_open"))
        self.menu_file_save.SetItemLabel(gt("&Save Project") + gsc("menu_file_save", "Ctrl-S"))
        self.menu_file_save.SetHelp(gt("tt_menu_file_save"))
        self.menu_file_saveas.SetItemLabel(gt("Save Project &As") + gsc("menu_file_saveas", "Ctrl-A"))
        self.menu_file_saveas.SetHelp(gt("tt_menu_file_saveas"))
        self.menu_file_cut.SetItemLabel(gt("&Cut Image") + gsc("menu_file_cut", "Ctrl-K"))
        self.menu_file_cut.SetHelp(gt("tt_menu_file_cut"))
        self.menu_file_export.SetItemLabel(gt("&Export .pak") + gsc("menu_file_export", "Ctrl-E"))
        self.menu_file_export.SetHelp(gt("tt_menu_file_export"))
        self.menu_file_exit.SetItemLabel(gt("E&xit") + gsc("menu_file_exit", "Alt-Q"))
        self.menu_file_exit.SetHelp(gt("tt_menu_file_exit"))
        # Tools menu
        self.menu.SetMenuLabel(1,"&Tools")
        self.menu_tools_dat.SetItemLabel(gt(".&dat file options") + gsc("menu_tools_dat", "Ctrl-D"))
        self.menu_tools_dat.SetHelp(gt("tt_menu_tools_dat"))
        self.menu_tools_smoke.SetItemLabel(gt("&Smoke options") + gsc("menu_tools_smoke", "Ctrl-M"))
        self.menu_tools_smoke.SetHelp(gt("tt_menu_tools_smoke"))
        self.menu_tools_language.SetItemLabel(gt("&Language") + gsc("menu_tools_language", "Ctrl-L"))
        self.menu_tools_language.SetHelp(gt("tt_menu_languages"))
        self.menu_tools_prefs.SetItemLabel(gt("&Preferences...") + gsc("menu_tools_prefs", "Ctrl-P"))
        self.menu_tools_prefs.SetHelp(gt("tt_menu_tools_prefs"))
        # Help menu
        self.menu.SetMenuLabel(2,"&Help")
        self.menu_help_help.SetItemLabel(gt("TileCutter Help") + gsc("", ""))
        self.menu_help_help.SetHelp(gt("tt_menu_help_help"))
        self.menu_help_about.SetItemLabel(gt("&About TileCutter") + gsc("", ""))
        self.menu_help_about.SetHelp(gt("tt_menu_help_about"))


    def AddMenuItem(self, menu, itemHandler, enabled=1, id=None):
        itemText = "--!--"  # Item text must be set to something, or wx thinks this is a stock menu item
        if id == None:
            menuId = wx.NewId()
            menuItem = wx.MenuItem(menu, menuId, itemText)
            menu.AppendItem(menuItem)
        else:
            menuId = id
            menuItem = wx.MenuItem(menu, menuId)         # Stock menu item based on a specified id
            menu.AppendItem(menuItem)
        # Bind event to parent frame
        self.parent.Bind(wx.EVT_MENU, itemHandler, id=menuId)
        if enabled == 0:
            menu.Enable(menuId, 0)
        return menuItem

    # Menu event functions
    def OnNewProject(self,e):
        debug("Menu-File-> New Project")
        return 1
    def OnOpenProject(self,e):
        debug("Menu-File-> Open Project")
        return 1
    def OnCloseProject(self,e):
        debug("Menu-File-> Close Project")
        return 1
    def OnSaveProject(self,e):
        debug("Menu-File-> Save Project")
        return 1
    def OnSaveProjectAs(self,e):
        debug("Menu-File-> Save Project As...")
        return 1
    def OnCutProject(self,e):
        debug("Menu-File-> Cut Project")
        return 1
    def OnExportProject(self,e):
        debug("Menu-File-> Export Project")
        return 1
    def OnExit(self,e):
        debug("Menu-File-> Exit Program")
        return 1

    def OnDatEdit(self,e):
        debug("Menu-Tools-> Open .dat edit dialog")
        return 1
    def OnSmokeEdit(self,e):
        debug("Menu-Tools-> Open smoke edit dialog")
        return 1
    def OnSelectLanguage(self,e):
        debug("Menu-Tools-> Open select language dialog")
        dlg = translationDialog(self.parent)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
    def OnPreferences(self,e):
        debug("Menu-Tools-> Open preferences dialog")
        return 1

    def OnHelp(self,e):
        debug("Menu-Help-> Open help")
        return 1
    def OnAbout(self,e):
        debug("Menu-Help-> Open about dialog")
        dlg = aboutDialog(self.parent)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()


class DebugFrame(wx.Frame):
    """Debugging output display, debug.out() (or just debug()) to output debugging text"""
    def __init__(self,parent,id,title):
        # Init text and counter
        self.text = ""
        self.count = 0
        # Frame init
        wx.Frame.__init__(self,parent,wx.ID_ANY, title, (0,0), (600,300),style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textbox = wx.TextCtrl(self.panel, wx.ID_ANY, self.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)
        self.sizer.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        #Layout sizers
        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()
    def out(self,line):
        if debug_on:
            self.count += 1
            t = "[" + str(self.count) + "] " + line + "\n"
            self.text = self.text + t
            self.textbox.SetValue(self.text)
            self.textbox.ShowPosition(len(self.text))
    def __call__(self,line):
        if debug_on:
            self.out(line)

class MyApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def OnInit(self):
        """Things to do immediately after the wx.App has been created"""
        # Load Program Options

        # Create and show debug window if debugging turned on
        self.debug = DebugFrame(None, wx.ID_ANY, "Debugging")
        if debug_on:
            self.debug.Show(1)

        return True

    def ReloadWindow(self):
        """Reload the main window, e.g. to effect a translation change, does not affect debugging window"""

    def MainWindow(self):
        """Create main window after intialising project and debugging etc."""
        # Create and show main frame
        self.frame = MainWindow(None, wx.ID_ANY, "TileCutter", (800,600))
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)
        self.frame.debug = self.debug

        # Bind the debugging output for the active project functions to the same debug output
        activeproject.debug = self.debug
        # Produce aliases to activeproject at different levels
        self.activeproject = activeproject
        self.frame.activeproject = activeproject

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
    # Make debug global in all modules
    debug = tcproject.debug = tc.debug = translator.debug = app.debug
    # Create the translation manager
    tctranslator = translator.Translator()
##    sys.stderr = open("error.txt","w")
    # Create a default active project
    projects = {}
    p = {"default": tcproject.Project()}
    projects.update(p)
    activeproject = projects["default"]
    activeproject.activeImage()
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






