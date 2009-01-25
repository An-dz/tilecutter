# coding: UTF-8
#
# TileCutter, version 0.5
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.
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




# Todo:

# BUG - If abs path to save doesn't have slash at the end, browse dialog uses end path
#       segment as filename
# BUG - Set active image to new image, then edit textbox to make path invalid, then edit it back to the original -> highlighting fails
# BUG - Season select does not set to summer when enable winter is unchecked            - FIXED
# BUG - Translation for static boxes in UI components

# Move debug into own module, to allow it to be easily accessed by other modules        - DONE
# Fix debug so that it logs to a file instead                                           - DONE
# Remove debug frame                                                                    - DONE

# Find some way to eliminate flickering on translation update/initial load              - DONE
# Text entry boxes visible position at end, or cursor, rather than beginning            - 0.7
#   - needs full revamp of text entry box class to deal with special stuff really       - 0.7
# Padding/general layout optimisation                                                   
# -> Layout optimisation for mac                                                        
# Cutting mask display based on dimensions                                              - DONE
# Make .dat and input images relative to save location path                             
# Speed optimisations - switching views seems really sluggish!                          
# Optimise code for generating lists in comboboxes (translation slowing this?)          

# Finish output file boxes, switching them to use the new set of functions              - DONE
# Do the project save/load/new etc. and management functionality (using pickle & hash)  
#   Multi-project system for later versions                                             - POSTPONE 0.7

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
# Source image control (needs current view context)                                     - MOSTLY DONE
# -> File must exist                                                                    - DONE
# -> Implement modal dialog for browse                                                  - DONE
# -> Allow text entry, highlight in red if file does not exist??                        - DONE (Needs icons for tick/cross)
# -> Implement modal confirmation dialog for "open same file for all" button            
# "Warning, this will set all views in the project to use the current image, proceed?"  
# -> Function to reload the current view's image                                        - DONE

# UI
# Move UI classes into a module to enhance loading speed                                - DONE
# Add display/direct edit boxes to the offset control                                   - 0.7

# Needs much better error handling, add try/except clauses in critical places
# Could also encase entire script in an exception catcher, which can display exception 
#   and then gracefully shutdown wx, to prevent the flashing box/pythonwin crashing problem

# Add the TileCutter icon                                                               - DONE Icon made, works well in windows
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

# Cutting engine                                                                        
# Dynamic mask generation + caching                                                     - DONE
# New cutting engine able to cope with all settings except frames                       - DONE
#   -> Test this cutting engine in all circumstances                                    
# Ability to add a copyright text notice to bottom of outputted image
# Full .dat editing capability
# "Pretty" output mode


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

import wx

import sys, os, StringIO, pickle
import tcui, tc, tcproject, imres

# Utility functions
import translator
gt = translator.Translator()
# _gt() used where class needs to be fed untranslated string, but we still want TCTranslator
# script to pick it up for the translation file
_gt = gt.loop
import logger
debug = logger.Log()
import config
config = config.Config()
config.save()

# Need some kind of auto-generation function for the translator, to produce a range of numbers (0-64, then in 16 increments to 240)
##choicelist_paksize = [gt("16"),gt("32"),gt("48"),gt("64"),gt("80"),gt("96"),gt("112"),gt("128"),gt("144"),gt("160"),gt("176"),gt("192"),gt("208"),gt("224"),gt("240")]

class MainWindow(wx.Frame):
    """Main frame window inside which all else is put"""
    def __init__(self, parent, app, id, title, windowsize, windowposition, windowminsize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, windowposition, windowsize,
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        # Init stuff
        self.SetMinSize(windowminsize)

        # Set the program's icon
        self.icons = wx.IconBundle()
        self.icons.AddIcon(imres.catalog["tc_icon2_16_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_32_plain"].getIcon())
        self.icons.AddIcon(imres.catalog["tc_icon2_48_plain"].getIcon())
        self.SetIcons(self.icons)

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
        self.s_panel_bottom_right = wx.BoxSizer(wx.VERTICAL)            # Contains cut/export buttons

        # LEFT SIDE CONTROLS
        # Season controls
        self.control_seasons    = tcui.seasonControl(self.panel, app, self.s_panel_controls)
        # Image controls
        self.control_images     = tcui.imageControl(self.panel, app, self.s_panel_controls)
        # Facing controls
        self.control_facing     = tcui.facingControl(self.panel, app, self.s_panel_controls)
        # Dimension controls
        self.control_dims       = tcui.dimsControl(self.panel, app, self.s_panel_controls)
        # Offset/mask controls
        self.control_offset     = tcui.offsetControl(self.panel, app, self.s_panel_controls)

        # Create Image display window and image path entry control, which adds itself to the sizer
        self.display = tcui.imageWindow(self.panel, app, self.s_panel_imagewindow_container, config.transparent)

        # Save, Dat, Image and Pak output paths
        self.s_panel_flex = wx.FlexGridSizer(0,4,3,0)
        self.control_savepath = tcui.FileControl(self.panel, app, self.s_panel_flex, app.activeproject.savefile,
                                                 _gt("Project Save Location"), _gt("tt_save_file_location"),
                                                 _gt("Choose a location to save project..."), "TCP files (*.tcp)|*.tcp",
                                                 _gt("Browse..."), _gt("tt_browse_save_file"), None)
        self.control_datpath = tcui.FileControl(self.panel, app, self.s_panel_flex, app.activeproject.datfile,
                                                _gt(".dat Output Location"), _gt("tt_dat_file_location"),
                                                _gt("Choose a location to save .dat file..."), "DAT files (*.dat)|*.dat",
                                                _gt("Browse..."), _gt("tt_browse_dat_file"), app.activeproject.savefile)
        self.control_pngpath = tcui.FileControl(self.panel, app, self.s_panel_flex, app.activeproject.pngfile,
                                                _gt(".png Output Location"), _gt("tt_png_file_location"),
                                                _gt("Choose a location to save .png file..."), "PNG files (*.png)|*.png",
                                                _gt("Browse..."), _gt("tt_browse_png_file"), app.activeproject.savefile)
        self.control_pakpath = tcui.FileControl(self.panel, app, self.s_panel_flex, app.activeproject.pakfile,
                                                _gt(".pak Output Location"), _gt("tt_pak_file_location"),
                                                _gt("Choose a location to export .pak file..."), "PAK files (*.pak)|*.pak",
                                                _gt("Browse..."), _gt("tt_browse_pak_file"), app.activeproject.savefile)

        # Set controls that savepath also alters (ones which are relative to it)
        self.control_savepath.SetDependants([self.control_datpath, self.control_pngpath, self.control_pakpath])

        self.s_panel_flex.AddGrowableCol(1)

        self.s_panel_bottom.Add(self.s_panel_flex, 1, wx.EXPAND|wx.ALL, 4)

        self.s_panel_bottom.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_VERTICAL), 0, wx.EXPAND|wx.LEFT, 2)

        self.cut_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cut_button_sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.export_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # CUT/EXPORT BUTTONS
        # Cut button
        self.cut_button = wx.Button(self.panel, wx.ID_ANY)
        self.cut_button.Bind(wx.EVT_BUTTON, self.menubar.OnCutProject, self.cut_button)
        self.cut_button_sizer2.Add(self.cut_button, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        # Export .dat checkbox
        self.export_dat_toggle = wx.CheckBox(self.panel, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.export_dat_toggle.SetValue(1)
        self.export_dat_toggle.Bind(wx.EVT_CHECKBOX, self.OnToggleDatExport, self.export_dat_toggle)
        self.cut_button_sizer2.Add(self.export_dat_toggle, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, 6)

        self.cut_button_sizer.Add(self.cut_button_sizer2, 0, wx.ALIGN_CENTER_VERTICAL)

        # Export button
        self.export_button = wx.Button(self.panel, wx.ID_ANY)
        self.export_button.Bind(wx.EVT_BUTTON, self.menubar.OnExportProject, self.export_button)
        self.export_button_sizer.Add(self.export_button, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        self.s_panel_bottom_right.Add(self.cut_button_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 4)
        self.s_panel_bottom_right.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 4)
        self.s_panel_bottom_right.Add(self.export_button_sizer, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 4)

        # Add these buttons to the bottom-right panel container
        self.s_panel_bottom.Add(self.s_panel_bottom_right, 0, wx.EXPAND|wx.ALIGN_CENTER|wx.LEFT, 2)

        # SIZERS
        # Add the remaining sizers to each other
        # Top panel, left side controls and right side image window added
        self.s_panel_top.Add(self.s_panel_controls,0,wx.EXPAND|wx.RIGHT, 1)
        self.s_panel_top.Add(self.s_panel_imagewindow_container,1,wx.EXPAND, 0)
        # Line under menu bar
        self.s_panel.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)
        # Add bottom and top parts to overall panel
        self.s_panel.Add(self.s_panel_top,1,wx.EXPAND|wx.BOTTOM, 4)
        self.s_panel.Add(self.s_panel_bottom,0,wx.EXPAND|wx.BOTTOM, 2)

        # Layout sizers
        self.panel.SetSizer(self.s_panel)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()

        self.translate()

    def translate(self):
        """Master translate function for the mainwindow object"""
        self.Freeze()
        self.cut_button.SetLabel(gt("Cut image"))
        self.export_button.SetLabel(gt("Compile pak"))
        self.export_dat_toggle.SetLabel(gt("Write out .dat file"))
        # And translate the window's title string
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
        # Finally re-do the window's layout
        self.panel.Layout()
        self.Thaw()

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        self.Freeze()
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

class TCApp(wx.App):
    """The main application, pre-window launch stuff should go here"""
    def __init__(self):
        self.start_directory = os.getcwd()
        wx.App.__init__(self)

    def OnInit(self):
        """Called after app has been initialised"""
        # Override wx's mechanism for writing stderr/out
        sys.stderr = debug
        sys.stdout = debug
        # Create a default active project
        self.projects = {}
        self.projects["default"] = tcproject.Project()
        self.activeproject = self.projects["default"]
        # Serialise active project, this string is then checked to see if it needs to be saved
        self.activepickle = self.PickleProject(self.activeproject)

        # Active project needs a file save location, by default this is set to a default in the new project
        self.active_save_location = self.activeproject.files.save_location
        self.active_save_name = ""

        # Create and show main frame
        self.frame = MainWindow(None, self, wx.ID_ANY, "TileCutter", config.window_size, config.window_position, config.window_minsize)
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit)
        return True

    def ExportProject(self, project, export=False):
        """Trigger exporting of specified project"""
        # First trigger project to generate cut images
        project.cutImages(tc.export_cutter)
        # Then feed project into outputting routine
        # Will need a way to report back progress to a progress bar/indicator
        tc.export_writer(project)



    def CheckIfChanged(self, project):
        """Returns true if project is unchanged since last save"""
        debug("CheckIfChanged")
        if self.PickleProject(project) == self.activepickle:
            debug("Check Project for changes - Project Unchanged")
            return False
        else:
            debug("Check Project for changes - Project Changed")
            return True
    def CheckIfEverSaved(self, project):
        """Returns true if project has ever been saved (i.e. has a save location)"""
        debug("CheckIfEverSaved")
        if project.saved():
            debug("Project has an existing save location")
            return True
        else:
            debug("Project does not have an existing save location")
            return False
    def PromptToSave(self, project):
        """Prompts user to save file, return wx.ID_YES, wx.ID_NO or wx.ID_CANCEL"""
        debug("PromptToSave")
        dlg = wx.MessageDialog(self.frame, gt("Save changes before proceeding?"),
                               gt("Current project has changed"),
                               style=wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            debug("PromptToSave - Dialog destroyed with result YES")
        if result == wx.ID_NO:
            debug("PromptToSave - Dialog destroyed with result NO")
        if result == wx.ID_CANCEL:
            debug("PromptToSave - Dialog destroyed with result CANCEL")
        return result
    def SaveAsDialog(self, project):
        """Prompts user to select a location to save project to, returns True if location picked,
        False if cancelled. Sets project's save location to result file"""
        debug("SaveAsDialog - Grabbing save path from dialog")
        filesAllowed = "TileCutter Project files (*.tcp)|*.tcp"
        dialogFlags = wx.FD_SAVE|wx.OVERWRITE_PROMPT
        path = os.path.split(project.savefile())[0]
        filename = os.path.split(project.savefile())[1]
        dlg = wx.FileDialog(self.frame, gt("Choose a location to save to..."),
                            path, filename, filesAllowed, dialogFlags)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            project.savefile(os.path.join(dlg.GetDirectory(), dlg.GetFilename()))
            debug("New savefile for project is: %s" % project.savefile())
            dlg.Destroy()
            return True
        else:
            # Else cancel was pressed, do nothing
            debug("User cancelled SaveAs Dialog")
            dlg.Destroy()
            return False
    def LoadDialog(self):
        """Prompts user to select a location to load a project file from, returns filename or wx.ID_CANCEL"""
        debug("LoadDialog - Opening Load Dialog to allow location picking")
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
            debug("User picked location:" % load_location)
            return load_location
        else:
            # Else cancel was pressed, do nothing
            dlg.Destroy()
            debug("User cancelled location picking")
            return False

    def SaveToFile(self, project):
        """Save project to its save location, returns True if success, False if failed"""
        debug("SaveToFile - Save project out to disk")
        # Finally update the frame to display changes
        self.frame.update()
    def LoadFromFile(self, location):
        """Load a project based on a file location"""
        debug("LoadFromFile - Load project from file: %s" % location)
        # Needs exception handling for unpickle failure
        self.activeproject = self.UnPickleProject(load_location)
        self.activepickle = self.PickleProject(self.activeproject)
        self.frame.update()
        debug("Load Project succeeded")
        return True
    def NewProject(self):
        """Create a new project"""
        debug("NewProject - Create new project")
        self.activeproject = tcproject.Project()
        self.activepickle = self.PickleProject(self.activeproject)
        # Reset project save location/name
        self.active_save_location = app.activeproject.files.save_location
        self.active_save_name = ""
        # Finally update the frame to display changes
        self.frame.update()
        debug("NewProject - Complete!")

    def OnNewProject(self):
        """Init process of starting a new project"""
        debug("OnNewProject")
        project = self.activeproject
        if self.CheckIfChanged(project):
            ret = self.PromptToSave(project)
            if ret == wx.ID_YES:
                if not self.CheckIfEverSaved(project):
                    if not self.SaveAsDialog(project):
                        return False
                self.SaveToFile(project)
            elif ret == wx.ID_CANCEL:
                return False
        self.NewProject()
        
    def OnLoadProject(self):
        """Init process of loading a project from file"""
        debug("OnLoadProject")
        project = self.activeproject
        if self.CheckIfChanged(project):                    # If project has changed
            ret = self.PromptToSave(project)                # Prompt to save project
            if ret == wx.ID_YES:                            # If answer is yes
                if not self.CheckIfEverSaved(project):      #  Check if file has a save location
                    if not self.SaveAsDialog(project):      #  If it doesn't, prompt user for one
                        return False                        #  If user cancels, quit out
                self.SaveToFile(project)                    #  Otherwise save the project
            elif ret == wx.ID_CANCEL:                       # If answer is no
                return False                                # Quit out
            # else ret is wx.ID_NO, so we don't want to save but can continue
        ret = self.LoadDialog()                             # Prompt for file to load
        if ret != wx.ID_CANCEL:                             # If file specified
            return self.LoadFromFile()                      # Load the project
        else:                                               # Otherwise
            return False                                    # Quit out

    def OnSaveProject(self, project):
        """Init process of saving a project to file"""
        debug("OnSaveProject")
        if self.CheckIfChanged(project):
            if self.CheckIfEverSaved(project):
                return self.SaveToFile(project)
            else:
                if self.SaveAsDialog(project):
                    return self.SaveToFile(project)
                return False
        # Project already saved
        return True
    def OnSaveAsProject(self, project):
        """Init process of saving a project to a new location"""
        debug("OnSaveAsProject")
        if self.SaveAsDialog(project):
            return self.SaveToFile(project)
        return False



##            file = os.path.join(app.active_save_location, app.active_save_name)
##            debug("Save path:%s" % file)
##            output = open(file, "wb")
##            app.activepickle = pickle_string
##            output.write(pickle_string)
##            output.close()
##            debug("Save project success")
##            return True


    def PickleProject(self, project, picklemode = 0):
        """Pickle a project, returns a pickled string"""
        # Remove all image information, as this can't be pickled (and doesn't need to be anyway)
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
        file.close()
        return project

    def Exit(self):
        """Quit the application indirectly"""
        debug("app.Exit -> app.OnQuit()")
        self.OnQuit(None)

    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        debug("Application quitting...")
        self.frame.Destroy()


if __name__ == '__main__':
    # Redirect stdout/err to internal logging mechanism
    sys.stderr = debug
    sys.stdout = debug
    start_directory = os.getcwd()
    # Create the application
    debug("--------------------------------------------------------------------------")
    debug("Init - Creating app")
    app = TCApp()

    display = app.frame.display
    # Init all main frame controls
    app.frame.update()
    # Show the main window frame
    app.frame.Show(1)

    # Launch into application's main loop
    app.MainLoop()
    app.Destroy()



# BackImage[direction][ydim][xdim][zdim][frame][season]=path.ypos.xpos



