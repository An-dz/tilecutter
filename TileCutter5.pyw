# coding: UTF-8
#
# TileCutter, version 0.5
#

# Todo:

# BUG - Set active image to new image, then edit textbox to make path invalid, then edit it back to the original -> highlighting fails
# BUG - Season select does not set to summer when enable winter is unchecked            - FIXED
# BUG - Translation for static boxes in UI components

# Move debug into own module, to allow it to be easily accessed by other modules        - DONE
# Fix debug so that it logs to a file instead                                           - DONE
# Remove debug frame                                                                    - DONE

# Find some way to eliminate flickering on translation update/initial load              - DONE
# Text entry boxes visible position at end, or cursor, rather than beginning            
#   - needs full revamp of text entry box class to deal with special stuff really       
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
# Dialog to set program options                                                         
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
# Add display/direct edit boxes to the offset control                                   

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
        self.s_panel_bottom_right_buttons = wx.BoxSizer(wx.HORIZONTAL)  # "export dat" checkbox

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

        # IMAGE/DAT OUTPUT PATHS
        # Create the I/O path inputs, which are added to the bottom-left panel container
        self.control_iopaths = tcui.twoFileControl(self.panel, app, self.s_panel_bottom)

        # CUT/EXPORT BUTTONS
        # Cut button
        self.cut_button = wx.Button(self.panel, wx.ID_ANY)
        self.cut_button.Bind(wx.EVT_BUTTON, self.menubar.OnCutProject, self.cut_button)
        self.s_panel_bottom_right_buttons.Add(self.cut_button, 1, wx.EXPAND, 4)
        # Export button
        self.export_button = wx.Button(self.panel, wx.ID_ANY)
        self.export_button.Bind(wx.EVT_BUTTON, self.menubar.OnExportProject, self.export_button)
        self.s_panel_bottom_right_buttons.Add(self.export_button, 1, wx.EXPAND, 4)
        # Export .dat checkbox
        self.export_dat_toggle = wx.CheckBox(self.panel, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.export_dat_toggle.SetValue(1)
        self.export_dat_toggle.Bind(wx.EVT_CHECKBOX, self.OnToggleDatExport, self.export_dat_toggle)
        # Add buttons and checkbox to sizer
        self.s_panel_bottom_right.Add(self.s_panel_bottom_right_buttons, 1, wx.EXPAND, 4)
        self.s_panel_bottom_right.Add(self.export_dat_toggle, 1, wx.ALIGN_CENTER, 4)

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
        self.Freeze()
        self.cut_button.SetLabel(gt("Cut"))
        self.export_button.SetLabel(gt("Export"))
        self.export_dat_toggle.SetLabel(gt("Export .dat file"))
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
        self.Thaw()

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        self.Freeze()
        self.control_seasons.update()
        self.control_images.update()
        self.control_facing.update()
        self.control_dims.update()
        self.control_offset.update()
        self.control_iopaths.update()
        self.display.update()
        self.Thaw()

    def OnToggleDatExport(self):
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

    def CheckProjectChanged(self, project):
        """Return True if project changed since last save"""
        if self.PickleProject(project) == self.activepickle:
            debug("Check Project for changes - Project Unchanged")
            return False
        else:
            debug("Check Project for changes - Project Changed")
            return True

    def SaveProject(self, project, saveas=False):
        """Save a project to the file location specified
        return True if save successful or not needed, false otherwise"""
        # If not saving-as (which will always happen) and there is no difference in the string, don't continue
        if self.CheckProjectChanged(project) or saveas:
            pickle_string = self.PickleProject(project, 0)
            if saveas or app.active_save_name == "":
                debug("Grabbing save path from dialog")
                filesAllowed = "TileCutter Project files (*.tcp)|*.tcp"
                dialogFlags = wx.FD_SAVE|wx.OVERWRITE_PROMPT
                path = app.active_save_location
                filename = app.active_save_name
                dlg = wx.FileDialog(self.frame, gt("Choose a location to save to..."),
                                    path, filename, filesAllowed, dialogFlags)
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    # This needs to calculate a relative path between the location of the output png and the location of the output dat
                    app.active_save_location = dlg.GetDirectory()
                    app.active_save_name = dlg.GetFilename()
                    value = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
                    debug(value)
##                    relative = self.comparePaths(value, path2)
##                    pickerDialog.Destroy()
##                    return relative
                    dlg.Destroy()
                else:
                    # Else cancel was pressed, do nothing
                    dlg.Destroy()
                    return False
            else:
                # Else save it in the same place
                debug("Using existing save path")
            file = os.path.join(app.active_save_location, app.active_save_name)
            debug("Save path:%s" % file)
            output = open(file, "wb")
            app.activepickle = pickle_string
            output.write(pickle_string)
            output.close()
            debug("Save project success")
            return True
        else:
            debug("No changes in file, doing nothing")
            return True

    def NewProject(self):
        """Replace a project with a new one"""
        continue_new_project = True
        if self.CheckProjectChanged(app.activeproject):
            # If so, pop up a confirmation dialog offering the chance to save the file
            dlg = wx.MessageDialog(self.frame, gt("Save changes before proceeding?"),
                                   gt("Current project has changed"),
                                   style=wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                # Save current working, display save-as if not previously saved
                dlg.Destroy()
                # Invoke the standard project saving system (check if this works, abandon new file if it does)
                if not self.SaveProject(app.activeproject):
                    continue_new_project = False
            elif result == wx.ID_NO:
                # Do not save file, continue
                dlg.Destroy()
                continue_new_project = True
            elif result == wx.ID_CANCEL:
                # Cancel, do nothing
                dlg.Destroy()
                continue_new_project = False

        if continue_new_project:
            # If we should continue (e.g. user hasn't cancelled on confirmation or save dialog)

            # Call init on the project, this will reset it to its defaults
            self.activeproject = tcproject.Project()
            self.activepickle = self.PickleProject(self.activeproject)
            debug("Active project reset to defaults (New project)")
            # Reset project save location/name
            self.active_save_location = app.activeproject.files.save_location
            self.active_save_name = ""

            self.frame.update()

    def OpenProject(self):
        """Load project from file, replacing the current activeproject"""
        continue_open_project = True
        if self.CheckProjectChanged(app.activeproject):
            # If so, pop up a confirmation dialog offering the chance to save the file
            dlg = wx.MessageDialog(self.frame, gt("Save changes before proceeding?"),
                                   gt("Current project has changed"),
                                   style=wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                # Save current working, display save-as if not previously saved
                dlg.Destroy()
                # Invoke the standard project saving system (check if this works, abandon new file if it does)
                if not self.SaveProject(app.activeproject):
                    continue_open_project = False
            elif result == wx.ID_NO:
                # Do not save file, continue
                dlg.Destroy()
                continue_open_project = True
            elif result == wx.ID_CANCEL:
                # Cancel, do nothing
                dlg.Destroy()
                continue_open_project = False

        if continue_open_project:
            # File open dialog
            filesAllowed = "TileCutter Project files (*.tcp)|*.tcp"
            dialogFlags = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
            path = app.active_save_location
            dlg = wx.FileDialog(self.frame, gt("Choose a project file to open..."),
                                path, "", filesAllowed, dialogFlags)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                # This needs to calculate a relative path between the location of the output png and the location of the output dat
                app.active_save_location = dlg.GetDirectory()
                app.active_save_name = dlg.GetFilename()
                debug("app.active_save_location: %s" % app.active_save_location)
                debug("app.active_save_name: %s" % app.active_save_name)
                file = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
                self.activeproject = self.UnPickleProject(file)
                self.activepickle = self.PickleProject(self.activeproject)
                dlg.Destroy()
                self.frame.update()
                debug("Loaded project from: %s" % file)
    ##                    relative = self.comparePaths(value, path2)
    ##                    pickerDialog.Destroy()
    ##                    return relative
            else:
                # Else cancel was pressed, do nothing
                dlg.Destroy()
                debug("Cancel Open Project")
                return False

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
        return project

    def Exit(self):
        """Quit the application indirectly"""
        self.OnQuit(None)

    def OnQuit(self, e):
        """Close the debugging window and quit the application on a quit event in the main window
        closing the debugging window doesn't do anything"""
        self.frame.Destroy()


if __name__ == '__main__':
    # Redirect stdout/err to internal logging mechanism
    sys.stderr = debug
    sys.stdout = debug
    start_directory = os.getcwd()
    # Create the application
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



