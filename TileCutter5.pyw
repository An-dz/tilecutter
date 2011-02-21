#!/usr/bin/python
# coding: UTF-8
#
# TileCutter, version 0.5
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. The name of the author may not be used to endorse or promote products derived from this software without specific prior written permission from the author.
#
# 4. Products derived from this software may not be called "TileCutter" nor may "TileCutter" appear in their names without specific prior written permission from the author.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 


# UI Change suggestions:
# Move same image for all button to the menu bar under tools                                        - Moved to tools
# Make icon for reload image much bigger or replace with text button                                - Replaced with text
# Make icons in main menu much bigger (double size)
# Replace direction facing control with "compass", or depiction of a tile with directions marked    - Added tile graphic with directions
# Make buttons on the mask offset control 2x bigger with better graphics                            - Bigger, need new graphics
# Move the "fine" selection below the mask offset control                                           - Done
# Move the paths at the bottom into either a dialog box or into a "pop-up" panel at the bottom of
#   the image window, which can then be accessed via a button
# Add a status bar, displaying status information about the program
# Add a progress indicator for export
# Move the Cut image and Compile .pak buttons onto a single bottom bar after relocating file paths  - Done
# Have the right/left toolbar run all the way down to the bottom of the screen                      - Done

# Release 0.5.5 (beta)
# ADD: Proper selection of path to makeobj via GUI
# ADD: Command line scriptability: 
#      Specify path to multiple .tcp files for automatic processing
#      Override output location of .dat/.png
#      Specify .pak output if required
#      Usage: "TileCutter5 -h" will give command line usage info
# ADD: Ability to select .dat file output via UI checkbox
# FIX: Selecting a file at the root of a drive on Windows leads to wrong path display
# ADD: Basic documentation now available on website (via Online Help link in menu)

# Release 0.5.4
# FIX: Better controls layout
# FIX: Bug with mask production on wxGTK
# FIX: Better handling of save locations, caching of last save location
# FIX: Dialog boxes positioned centered on application, not centered on window
# ADD: Application window fits to size of contents on start
# ADD: Updated translations

# Release 0.5.3
# FIX: Export error with Python character mapping
# FIX: Translation of strings in image path entry box
# FIX: Layout of About window incorrect
# FIX: Default language setting not being saved

# ADD: Filepath of saved file displayed in the title bar, indicates saved/unsaved status
# ADD: Exception handling for case of no WX being installed
# ADD: Better integration with SimuTranslator

# DEL: Removed flags for country code - not a good way to indicate language



# Todo:

# BUG - If abs path to save doesn't have slash at the end, browse dialog uses end path
#       segment as filename
# BUG - Season select does not set to summer when enable winter is unchecked            - FIXED
# BUG - Translation for static boxes in UI components                                   - DONE
# BUG - Active image isn't set to the correct one after project load                    - FIXED
# BUG - Translation file with windows newlines on unix doesn't work			
# BUG - Selecting a file at the root of a drive on Windows leads to wrong path display  - FIXED 0.5.5
# BUG - Source image locations do not update to reflect changes to the project save path
# BUG - Unicode filenames causing logging to break, due to str() rather than unicode()
#       and also due to incorrect codec used in logging module                          - FIXED 0.5.2

# Move debug into own module, to allow it to be easily accessed by other modules        - DONE
# Fix debug so that it logs to a file instead                                           - DONE
# Remove debug frame                                                                    - DONE

# Find some way to eliminate flickering on translation update/initial load              - DONE
# Text entry boxes visible position at end, or cursor, rather than beginning            - 0.7
#   - needs full revamp of text entry box class to deal with special stuff really       - 0.7
# Padding/general layout optimisation                                                   
# -> Layout optimisation for mac                                                        
# Cutting mask display based on dimensions                                              - DONE
# Make .dat and input images relative to save location path                             - DONE
# Speed optimisations - switching views seems really sluggish!                          
# Optimise code for generating lists in comboboxes (translation slowing this?)          

# Finish output file boxes, switching them to use the new set of functions              - DONE
# Do the project save/load/new etc. and management functionality (using pickle & hash)  - DONE
#   Multi-project system for later versions                                             - POSTPONE 0.7
#   Multi-project version implemented as object, contains projects in a dict
#   referenced by keyword lookup, this has lookup methods for the active project
#   so that all of that stuff can be taken out of the main program entirely
#   This stuff will likely go into tcproject


# Program settings, load from a config file (using json)                                - DONE
# Dialog to set program options                                                         - 0.7
# Move all static variables and program option variables into config class              - DONE
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
# Source image control (needs current view context)                                     - DONE
# -> File must exist                                                                    - DONE
# -> Implement modal dialog for browse                                                  - DONE
# -> Allow text entry, highlight in red if file does not exist??                        - DONE
# -> Implement modal confirmation dialog for "open same file for all" button            - DONE
# -> Function to reload the current view's image                                        - DONE
# Add tick/cross functionality to input boxes                                           
# Extend tick/cross functionality to provide more info                                  - POSTPONE 0.6

# UI
# Move UI classes into a module to enhance loading speed                                - DONE
# Add display/direct edit boxes to the offset control                                   - 0.7

# Needs much better error handling, add try/except clauses in critical places

# Add the TileCutter icon                                                               - DONE Icon made, works well in windows
# Use img2py to compile icon image into the application                                 - DONE
# Can use the same technique for all the other images, e.g. bitmap buttons etc.         - DONE
# Need higher detail icons for the mac version                                          - DONE (Test icon display in OSX)

# About dialog                                                                          - DONE

# Distribution
# Make py2exe, look into producing smaller packages                                     - DONE
# -> Produce msi installer for windows                                                  - 0.6
# Make py2app distribution template                                                     - 0.6
# -> Make .dmg distribution of the py2app application (automated if possible)           - 0.6
# Import only bits of wx needed, to reduce py2exe package?                              
# Look into producing more mac-native package                                           - 0.6
# Mac drag + drop support                                                               - 0.6
# Test with Linux, Mac OSX, Windows (xp), try and have the same code across all platforms!
# Produce help documentation                                                            
# -> Quick start guide (interface should be fairly self-explanatory though)             

# Cutting engine                                                                        
# Dynamic mask generation + caching                                                     - DONE
# New cutting engine able to cope with all settings except frames                       - DONE
#   -> Test this cutting engine in all circumstances                                    
#   -> Add unit tests for cutting engine
# Ability to add a copyright text notice to bottom of outputted image                   - 0.6
# Full .dat editing capability                                                          - 0.6
# "Pretty" output mode                                                                  - 0.6


# Aims v.0.5
# Rewrite core cutting engine and output engine
# Produce minimal testing UI
#   - Set X/Y/Z dims, X/Y offsets, facing/season
#   - Determine output .png, .dat etc.
# Debugging system with nice output
# Translation function implemented
# Project save/load functions
#   - Implement using pickle

# Aims v.0.6
# Extend UI, include dat editor
# Project save/load functions
#   - Change to use more robust system (maybe XML?)

# Aims v.0.7
# Multi-project support

import logger
debug = logger.Log()

debug("\n--------------------------------------------------------------------------")

try:
    import wx
except ImportError:
    debug("WXPython not installed, please install module and try again!")
    raise

debug("WX version is: %s" % wx.version())

import sys, os, StringIO, pickle
import tcui, tc, tcproject, imres

# Utility functions
import translator
gt = translator.Translator()
# _gt() used where class needs to be fed untranslated string, but we still want TCTranslator
# script to pick it up for the translation file
_gt = gt.loop

import config
config = config.Config()
config.save()

debug(unicode(config))

# Need some kind of auto-generation function for the translator, to produce a range of numbers (0-64, then in 16 increments to 240)
##choicelist_paksize = [gt("16"),gt("32"),gt("48"),gt("64"),gt("80"),gt("96"),gt("112"),gt("128"),gt("144"),gt("160"),gt("176"),gt("192"),gt("208"),gt("224"),gt("240")]

class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self, parent, app, id, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, (-1,-1), (-1,-1),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.app = app
        # Init stuff

        # Set the program's icon
        self.icons = wx.IconBundle()
        self.icons.AddIcon(imres.catalog["tc_icon2_16_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_32_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_48_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_128_plain"].getIcon())
        self.SetIcons(self.icons)

        # Create the menus
        self.menubar = tcui.menuObject(self, app)
        self.SetMenuBar(self.menubar.menu)

        # self.panel contains all other elements within this frame and must be their parent
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Overall panel sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_panel = wx.BoxSizer(wx.HORIZONTAL)

        # Within the top panel, two horizontal divisions, one for the controls, one for the image window
        self.s_panel_left = wx.BoxSizer(wx.VERTICAL)        # Left side - Main controls
        self.s_panel_right = wx.BoxSizer(wx.VERTICAL)       # Right side - Image window and controls

        # LEFT SIDE CONTROLS
        # Season controls
        self.control_seasons    = tcui.seasonControl(self.panel, app, self.s_panel_left)
        # Image controls
        self.control_images     = tcui.imageControl(self.panel, app, self.s_panel_left)
        # Facing controls
        self.control_facing     = tcui.facingControl(self.panel, app, self.s_panel_left)
        # Dimension controls
        self.control_dims       = tcui.dimsControl(self.panel, app, self.s_panel_left)
        # Offset/mask controls
        self.control_offset     = tcui.offsetControl(self.panel, app, self.s_panel_left)

        # Create Image display window and image path entry control, which adds itself to the sizer
        self.display = tcui.imageWindow(self, self.panel, app, self.s_panel_right, config.transparent)

        # Save, Dat, Image and Pak output paths
        self.s_panel_export_paths = wx.FlexGridSizer(0,3,3,0)
        # Passing through reference to app.activeproject.XXXfile doesn't work here when we make a new
        # project/load a project, since it still points to the old one! needs to access these values
        # some other way...
        self.control_savepath = tcui.FileControl(self.panel, app, self.s_panel_export_paths, self.get_active_savefile_path,
                                                 _gt("Project Save Location"), _gt("tt_save_file_location"),
                                                 _gt("Choose a location to save project..."), "TCP files (*.tcp)|*.tcp",
                                                 _gt("Browse..."), _gt("tt_browse_save_file"), None)
        self.control_datpath = tcui.FileControl(self.panel, app, self.s_panel_export_paths, self.get_active_datfile_path,
                                                _gt(".dat Output Location"), _gt("tt_dat_file_location"),
                                                _gt("Choose a location to save .dat file..."), "DAT files (*.dat)|*.dat",
                                                _gt("Browse..."), _gt("tt_browse_dat_file"), self.get_active_savefile_path)
        self.control_pngpath = tcui.FileControl(self.panel, app, self.s_panel_export_paths, self.get_active_pngfile_path,
                                                _gt(".png Output Location"), _gt("tt_png_file_location"),
                                                _gt("Choose a location to save .png file..."), "PNG files (*.png)|*.png",
                                                _gt("Browse..."), _gt("tt_browse_png_file"), self.get_active_savefile_path)
        self.control_pakpath = tcui.FileControl(self.panel, app, self.s_panel_export_paths, self.get_active_pakfile_path,
                                                _gt(".pak Output Location"), _gt("tt_pak_file_location"),
                                                _gt("Choose a location to export .pak file..."), "PAK files (*.pak)|*.pak",
                                                _gt("Browse..."), _gt("tt_browse_pak_file"), self.get_active_savefile_path)

        # Set controls that savepath also alters (ones which are relative to it)
        self.control_savepath.SetDependants([self.control_datpath, self.control_pngpath, self.control_pakpath])

        self.s_panel_export_paths.AddGrowableCol(1)

        # CUT/EXPORT BUTTONS
        # Export .dat checkbox
        self.export_dat_toggle = wx.CheckBox(self.panel, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.export_dat_toggle.Bind(wx.EVT_CHECKBOX, self.OnToggleDatExport, self.export_dat_toggle)
        # Cut button
        self.cut_button = wx.Button(self.panel, wx.ID_ANY)
        self.cut_button.Bind(wx.EVT_BUTTON, self.menubar.OnCutProject, self.cut_button)
        # Export button
        self.export_button = wx.Button(self.panel, wx.ID_ANY)
        self.export_button.Bind(wx.EVT_BUTTON, self.menubar.OnExportProject, self.export_button)

        # Sizers
        # Bottom section of the right-hand side requires some more sizers
        self.s_panel_rb = wx.BoxSizer(wx.HORIZONTAL)
        self.s_panel_rb_inner = wx.BoxSizer(wx.VERTICAL)
        self.s_panel_export_buttons = wx.BoxSizer(wx.HORIZONTAL)
        # Bar containing cut, export buttons etc.
        self.s_panel_export_buttons.Add(self.export_dat_toggle, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        self.s_panel_export_buttons.Add(self.cut_button, 0, wx.ALL, 4)
        self.s_panel_export_buttons.Add(self.export_button, 0, wx.ALL, 4)

        # Add export buttons, horizontal line and path bars to vertical sizer
        self.s_panel_rb_inner.Add(self.s_panel_export_buttons, 0, wx.ALIGN_RIGHT, 0)
        self.s_panel_rb_inner.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.LEFT, 2)
        self.s_panel_rb_inner.Add(self.s_panel_export_paths, 0, wx.EXPAND|wx.ALL, 4)

        # Add that vertical sizer to a horizontal one, with a vertical line on the left
        self.s_panel_rb.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_VERTICAL), 0, wx.EXPAND, 2)
        self.s_panel_rb.Add(self.s_panel_rb_inner, 1, wx.LEFT, 0)
        # Add that horizontal sizer to the right-side of the application
        self.s_panel_right.Add(self.s_panel_rb, 0, wx.EXPAND)

        # SIZERS
        # Add the remaining sizers to each other
        # Line under menu bar
        self.sizer.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)
        # Left and right panels added
        self.s_panel.Add(self.s_panel_left, 0, wx.EXPAND|wx.RIGHT, 1)
        self.s_panel.Add(self.s_panel_right, 1, wx.EXPAND, 0)
        self.sizer.Add(self.s_panel, 1, wx.EXPAND, 0)
        # Layout sizers
        self.panel.SetSizer(self.sizer)

        self.translate()

    def get_active_image_path(self, val=None):
        """Return activeproject's active image path"""
        return self.app.activeproject.active_image_path(val)
    def get_active_savefile_path(self, val=None):
        """Return activeproject's save path"""
        return self.app.activeproject.savefile(val)
    def get_active_datfile_path(self, val=None):
        """Return activeproject's datfile path"""
        return self.app.activeproject.datfile(val)
    def get_active_pngfile_path(self, val=None):
        """Return activeproject's pngfile path"""
        return self.app.activeproject.pngfile(val)
    def get_active_pakfile_path(self, val=None):
        """Return activeproject's pakfile path"""
        return self.app.activeproject.pakfile(val)

    def translate(self):
        """Master translate function for the mainwindow object"""
        self.Freeze()
        self.cut_button.SetLabel(gt("Cut image"))
        self.export_button.SetLabel(gt("Compile pak"))
        self.export_dat_toggle.SetLabel(gt("Write out .dat file"))
        # And translate the window's title string
        # And translate the display window
        self.display.translate()
        # Then call translate methods of all child controls
        self.control_seasons.translate()
        self.control_images.translate()
        self.control_facing.translate()
        self.control_dims.translate()
        self.control_offset.translate()
        # Path entry controls
        self.control_savepath.translate()
        self.control_datpath.translate()
        self.control_pngpath.translate()
        self.control_pakpath.translate()
        # And the menus
        self.menubar.translate()
        # Finally translate the application name in title bar
        self.set_title()

        # Store previous size of window
        prev_size = self.GetSizeTuple()
        # Finally re-do the window's layout
        self.panel.Layout()
        self.Layout()
        self.panel.Fit()
        self.Fit()

        self.SetMinSize(wx.Size(int(self.GetBestSize().GetHeight() * 1.4),
                                self.GetBestSize().GetHeight()))
        self.SetSize(prev_size)
        self.panel.Layout()
        self.Layout()
        self.Thaw()

    def set_title(self):
        # Set title text of window
        self.SetTitle(self.app.get_title_text() % _gt("TileCutter"))

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        self.Freeze()
        self.export_dat_toggle.SetValue(config.write_dat)
        self.control_seasons.update()
        self.control_images.update()
        self.control_facing.update()
        self.control_dims.update()
        self.control_offset.update()
        self.control_datpath.update()
        self.control_pngpath.update()
        self.control_pakpath.update()
        self.control_savepath.update()
        self.display.update()
        self.Thaw()

    def OnToggleDatExport(self, e):
        """Toggle whether .dat file info should be exported, or just the cut image
        if .dat file exporting is disabled the .dat file will be displayed in a dialog"""
        if config.write_dat != self.export_dat_toggle.GetValue():
            config.write_dat = self.export_dat_toggle.GetValue()
            debug("OnToggleDatExport: Set config.write_dat to %s" % config.write_dat)


class TCApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def __init__(self, gui):
        self.gui = gui
        self.start_directory = os.getcwd()
        wx.App.__init__(self)

    def OnInit(self):
        """Called after app has been initialised"""
        # Wx also overrides stderr/stdout, override this
        if self.gui:
            sys.stderr = debug
            sys.stdout = debug
        else:
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

        debug("App OnInit: Starting...")
        self.start_directory = os.getcwd()

        # Create a default active project
        debug("App OnInit: Create default project")
        self.projects = {}
        self.projects["default"] = tcproject.Project(self)
        self.activeproject = self.projects["default"]
        # Serialise active project, this string is then checked to see if it needs to be saved
        self.activepickle = self.pickle_project(self.activeproject)
        # Active project needs a file save location, by default this is set to a default in the new project
        self.active_save_location = self.activeproject.files.save_location
        self.update_title_text()

        if self.gui:
            debug("App OnInit: Create + Show main frame")
            # Create and show main frame
            self.frame = MainWindow(None, self, wx.ID_ANY, "TileCutter")
            self.SetTopWindow(self.frame)

            debug("App OnInit: Bind Quit Event")
            # Bind quit event
            self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)
            self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)

            debug("App OnInit: Init window sizes")
            # Window inits itself to its minimum size
            # If a larger size is specified in config, set to this instead
            if config.window_size[0] > self.frame.GetBestSize().GetWidth() and config.window_size[1] > self.frame.GetBestSize().GetHeight():
                self.frame.SetSize(config.window_size)
            else:
                # Otherwise just use the minimum size
                self.frame.Fit()
            debug("App OnInit: Init window position")
            # If a window position is saved, place the window there
            if config.window_position != [-1,-1]:
                self.frame.SetPosition(config.window_position)
            else:
                # Otherwise center window on the screen
                self.frame.CentreOnScreen(wx.BOTH)
        else:
            debug("App OnInit: Command line mode, not creating GUI")



        debug("App OnInit: Completed!")
        return True

    # Called by the currently active project
    def project_has_changed(self):
        """Whenever the active project changes, this function is called"""
        # If it has, update the title text
        if self.gui:
            self.update_title_text()
            self.frame.set_title()

    # Functions concerning the title text of the program window
    def get_title_text(self):
        """Get a string to use for the window's title text"""
        return self.title_text
    def update_title_text(self):
        """Updates the title text with the details of the currently active project"""
        debug("update_title_text")
        if self.activeproject.has_save_location():
            # Project has been previously saved
            if self.project_changed(self.activeproject):
                # Project has changed but was previously saved
                # Title string will be *FileName.tcp - TileCutter
                self.title_text = "*%s - %s" % (self.activeproject.savefile(), "%s")
            else:
                # Project hasn't changed and is saved
                # Title string will be FileName.tcp - TileCutter
                self.title_text = "%s - %s" % (self.activeproject.savefile(), "%s")
        else:
            # Project hasn't been saved before
            if self.project_changed(self.activeproject):
                # Unsaved, but changed
                # Title string will be *(New Project) - TileCutter
                self.title_text = "*(%s) - %s" % (_gt("New Project"), "%s")
            else:
                # Unsaved and unchanged
                # Title string will be (New Project) - TileCutter
                self.title_text = "(%s) - %s" % (_gt("New Project"), "%s")
        debug("  Setting title_text to: %s" % self.title_text)

    # Method to invoke cutting engine on a particular project
    def export_project(self, project, pak_output=False, return_dat=None, write_dat=None):
        """Trigger exporting of specified project"""
        if return_dat is None:
            return_dat = not config.write_dat
        if write_dat is None:
            write_dat = config.write_dat
        # First trigger project to generate cut images
        project.cutImages(tc.export_cutter)
        # Then feed project into outputting routine
        # Will need a way to report back progress to a progress bar/indicator
        ret = tc.export_writer(project, pak_output, return_dat, write_dat)
        if self.gui and ret != True:
            # Pop up a modal dialog box to display the .dat file info
            pass

    # Checks on project relative to the active project
    def project_changed(self, project):
        """Returns true if project has changed since last save"""
        debug("project_changed")
        if self.pickle_project(project) == self.activepickle:
            debug("  Check Project for changes - Project Unchanged")
            return False
        else:
            debug("  Check Project for changes - Project Changed")
            return True

    # Dialogs involved in loading/saving
    def dialog_save_changes(self, project):
        """Prompts user to save file, return wx.ID_YES, wx.ID_NO or wx.ID_CANCEL"""
        debug("dialog_save_changes")
        dlg = wx.MessageDialog(self.frame, gt("Save changes before proceeding?"),
                               gt("Current project has changed"),
                               style=wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            debug("  dialog_save_changes - Result YES")
        if result == wx.ID_NO:
            debug("  dialog_save_changes - Result NO")
        if result == wx.ID_CANCEL:
            debug("  dialog_save_changes - Result CANCEL")
        return result
    def dialog_save_location(self, project):
        """Prompts user to select a location to save project to, returns True if location picked,
        False if cancelled. Sets project's save location to result file"""
        debug("dialog_save_location - Grabbing save path from dialog")
        filesAllowed = "TileCutter Project files (*.tcp)|*.tcp"
        dialogFlags = wx.FD_SAVE|wx.OVERWRITE_PROMPT
        path = os.path.split(project.savefile())[0]
        filename = os.path.split(project.savefile())[1]
        dlg = wx.FileDialog(self.frame, gt("Choose a location to save to..."),
                            path, filename, filesAllowed, dialogFlags)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            project.savefile(os.path.join(dlg.GetDirectory(), dlg.GetFilename()))
            config.last_save_path = dlg.GetDirectory()
            debug("  New savefile for project is: %s" % project.savefile())
            dlg.Destroy()
            return True
        else:
            # Else cancel was pressed, do nothing
            debug("  User cancelled save_location Dialog")
            dlg.Destroy()
            return False
    def dialog_load(self):
        """Prompts user to select a location to load a project file from, returns filename or wx.ID_CANCEL"""
        debug("dialog_load - Opening Load Dialog to allow location picking")
        filesAllowed = "TileCutter Project files (*.tcp)|*.tcp"
        dialogFlags = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
        # This probably needs to be more robust
        path = os.path.split(app.activeproject.savefile())[0]
        file = os.path.split(app.activeproject.savefile())[1]
        dlg = wx.FileDialog(self.frame, gt("Choose a project file to open..."),
                            path, file, filesAllowed, dialogFlags)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            load_location = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            dlg.Destroy()
            debug("  User picked location: %s" % load_location)
            return load_location
        else:
            # Else cancel was pressed, do nothing
            dlg.Destroy()
            debug("  User cancelled location picking")
            return False

    # Methods for loading/saving projects
    def pickle_project(self, project, picklemode = 0):
        """Pickle a project, returns a pickled string"""
        # Remove all image information, as this can't be pickled (and doesn't need to be anyway)
        project.delImages()
        project.del_parent()
        outstring = StringIO.StringIO()
        pickle.dump(project, outstring, picklemode)
        project.set_parent(self)
        pickle_string = outstring.getvalue()
        outstring.close()
        debug("pickle_project, object type: %s pickle type: %s" % (unicode(project), picklemode))
        return pickle_string
    def unpickle_project(self, filename):
        """Unpickle a project from file, returning a tcproject object"""
        file = open(filename, "rb")
        project = pickle.load(file)
        project.set_parent(self)
        file.close()
        return project
    def save_project(self, project):
        """Save project to its save location, returns True if success, False if failed"""
        debug("save_project - Save project out to disk")
        # Finally update the frame to display changes
        project.saved(True)
        self.activepickle = self.pickle_project(app.activeproject)
        # Pickling the project/unpickling the project should strip all active image info
        file = app.activeproject.savefile()
        debug("Save path:%s" % file)
        output = open(file, "wb")
        output.write(self.activepickle)
        output.close()
        self.frame.update()
        self.project_has_changed()
        debug("save_project - Save project success")
        return True
    def load_project(self, location):
        """Load a project based on a file location"""
        debug("load_project - Load project from file: %s" % location)
        # Needs exception handling for unpickle failure
        self.activeproject = self.unpickle_project(location)
        # Here we need to set the savefile location of the active project to its current location
        # since this may have changed since it was saved
        # Do this before making the active pickle, so that this change doesn't count as save-worthy
        self.activepickle = self.pickle_project(self.activeproject)
        if self.gui:
            self.frame.update()
            self.project_has_changed()
        debug("  Load Project succeeded")
        return True
    def new_project(self):
        """Create a new project"""
        debug("new_project - Create new project")
        self.activeproject = tcproject.Project(self)
        self.activepickle = self.pickle_project(self.activeproject)
        # Reset project save location/name
        self.active_save_location = app.activeproject.files.save_location
        # Finally update the frame to display changes
        self.frame.update()
        self.project_has_changed()
        debug("  new_project - Complete!")

    def OnNewProject(self):
        """Init process of starting a new project"""
        debug("OnNewProject")
        project = self.activeproject
        if self.project_changed(project):
            ret = self.dialog_save_changes(project)
            if ret == wx.ID_YES:
                if not project.saved():
                    if not self.dialog_save_location(project):
                        return False
                self.save_project(project)
            elif ret == wx.ID_CANCEL:
                return False
        self.new_project()
    def OnLoadProject(self):
        """Init process of loading a project from file"""
        debug("OnLoadProject")
        project = self.activeproject
        if self.project_changed(project):                           # If project has changed
            ret = self.dialog_save_changes(project)                 # Prompt to save project
            if ret == wx.ID_YES:                                    # If answer is yes
                if not project.saved():                             #  Check if file has a save location
                    if not self.dialog_save_location(project):      #  If it doesn't, prompt user for one
                        return False                                #  If user cancels, quit out
                self.save_project(project)                          #  Otherwise save the project
            elif ret == wx.ID_CANCEL:                               # If answer is no
                return False                                        # Quit out
            # else ret is wx.ID_NO, so we don't want to save but can continue
        ret = self.dialog_load()                                    # Prompt for file to load
        if ret != wx.ID_CANCEL:                                     # If file specified
            return self.load_project(ret)                           # Load the project
        else:                                                       # Otherwise
            return False                                            # Quit out
    def OnSaveProject(self, project):
        """Init process of saving a project to file"""
        debug("OnSaveProject")
        if project.saved():
            return self.save_project(project)
        else:
            if self.dialog_save_location(project):
                return self.save_project(project)
            return False
        # Project already saved
        return True
    def OnSaveAsProject(self, project):
        """Init process of saving a project to a new location"""
        debug("OnSaveAsProject")
        if self.dialog_save_location(project):
            return self.save_project(project)
        return False



    def Exit(self):
        """Quit the application indirectly"""
        debug("app.Exit -> app.OnQuit()")
        self.OnQuit(None)

    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        debug("Application quitting...")
        debug("Saving current application window size and position for next time")
        config.window_position = self.frame.GetPositionTuple()
        config.window_size = self.frame.GetSizeTuple()
        debug("Destroying frame...")
        self.frame.Destroy()
        debug("End")


if __name__ == "__main__":

    # Create app, but don't show the frame if command line being used
    # For each file in the input list, load the file (abort if load fails),
    # then do a standard export, plus compilation if needed
    # If any override flags are set, modify the output paths of the project before continuing

    # Any command line arguments turn off the GUI
    if len(sys.argv) == 1:
    	gui = True
    else:
    	gui = False
    start_directory = os.getcwd()
    if gui:
        # Redirect stdout/err to internal logging mechanism
        # Only do this redirection if running in GUI mode
        # Needs tweaks to the debug module for -q option etc., different logging levels?
        sys.stderr = debug
        sys.stdout = debug
        # Create the application with GUI
        debug("Init - Creating app with GUI")
        app = TCApp(gui=True)
        # Init all main frame controls
        app.frame.update()
        # Show the main window frame
        app.frame.Show(1)
        # Launch into application's main loop
        app.MainLoop()
        app.Destroy()
    else:
        # Create the application without GUI
        debug("Init - Creating app without GUI")
        app = TCApp(gui=False)
        # Not making use of app's event handling loop etc., so don't start it
        #app.MainLoop()

        # Do command line stuff here...
        from optparse import OptionParser
        usage = "usage: %prog [options] filename1 [filename2 ... ]"
        parser = OptionParser(usage=usage)

        parser.set_defaults(pak_output=False, dat_output=True)

        parser.add_option("-i", dest="png_directory",
                          help="override .png file output location to DIRECTORY", metavar="DIRECTORY")
        parser.add_option("-I", dest="png_filename",
                          help="override .png file output name to FILENAME", metavar="FILENAME")

        parser.add_option("-n", action="store_false", dest="dat_output",
                          help="disable .dat file output (if -m specified, dat info will be output to tempfile)")
        parser.add_option("-d", dest="dat_directory",
                          help="override .dat file output location to DIRECTORY", metavar="DIRECTORY")
        parser.add_option("-D", dest="dat_filename",
                          help="override .dat file output name to FILENAME", metavar="FILENAME")

        parser.add_option("-m", action="store_true", dest="pak_output",
                          help="enable .pak file output (requires Makeobj)")
#        parser.add_option("-M", dest="makeobj_directory",
#                          help="override object specific makeobj with PATH", metavar="PATH")
        parser.add_option("-p", dest="pak_directory",
                          help="override .pak file output location to DIRECTORY", metavar="DIRECTORY")
        parser.add_option("-P", dest="pak_filename",
                          help="override .pak file output name to FILENAME", metavar="FILENAME")

        parser.add_option("-v", action="store_true", dest="verbose",
                          help="enable verbose output")
        parser.add_option("-q", action="store_false", dest="verbose",
                          help="suppress stdout")

        # options are the defined options, args are the list of files to process
        options, args = parser.parse_args()
        if options.verbose is True:
            print "options: %s" % str(options)
            print "args: %s" % str(args)
        # Another good option would be to support "stub" datfiles
        # produced as part of a pakset, which would have some kind of
        # marker to allow inserting the image array matrix in a particular location

        # Check through all args for directories, and expand these to list
        # all contained .tcp files for processing

        for file in args:
            if options.verbose is not False:
                print "processing file: %s" % file
            # For every filename specified by the user, perform export
            app.load_project(file)
            # Apply any command line overrides specified by user
            # For PNG file
            if options.png_directory is not None:
            	png_dir = options.png_directory
            else:
            	png_dir = os.path.split(app.activeproject.pngfile())[0]
            if options.png_filename is not None:
            	png_file = options.png_filename
            else:
            	png_file = os.path.split(app.activeproject.pngfile())[1]
            app.activeproject.pngfile(os.path.join(png_dir, png_file))
            # For DAT file
            if options.dat_directory is not None:
            	dat_dir = options.dat_directory
            else:
            	dat_dir = os.path.split(app.activeproject.datfile())[0]
            if options.dat_filename is not None:
            	dat_file = options.dat_filename
            else:
            	dat_file = os.path.split(app.activeproject.datfile())[1]
            app.activeproject.datfile(os.path.join(dat_dir, dat_file))
            # For PAK file
            if options.pak_directory is not None:
            	pak_dir = options.pak_directory
            else:
            	pak_dir = os.path.split(app.activeproject.pakfile())[0]
            if options.pak_filename is not None:
            	pak_file = options.pak_filename
            else:
            	pak_file = os.path.split(app.activeproject.pakfile())[1]
            app.activeproject.pakfile(os.path.join(pak_dir, pak_file))

            app.export_project(app.activeproject, pak_output=options.pak_output, return_dat=False, write_dat=options.dat_output)
            if options.verbose is not False:
                print "...Done!"

        # Finally destroy app
        app.Destroy()




# BackImage[direction][ydim][xdim][zdim][frame][season]=path.ypos.xpos



