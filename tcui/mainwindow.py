# coding: UTF-8
#
# User Interface Module - Main Window
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

import sys, os, StringIO, pickle

import logger
debug = logger.Log()

try:
    import wx
    debug(u"WX version is: %s" % wx.version())
except ImportError:
    debug(u"WXPython not installed, please install module and try again!")
    raise

import translator
gt = translator.Translator()
# _gt() used where class needs to be fed untranslated string, but we still want TCTranslator
# script to pick it up for the translation file
_gt = gt.loop


import tcui, tc, imres

import config
config = config.Config()
config.save()

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
        return self.app.activeproject.save_location(val)
    def get_active_datfile_path(self, val=None):
        """Return activeproject's datfile path"""
        return self.app.activeproject.datfile_location(val)
    def get_active_pngfile_path(self, val=None):
        """Return activeproject's pngfile path"""
        return self.app.activeproject.pngfile_location(val)
    def get_active_pakfile_path(self, val=None):
        """Return activeproject's pakfile path"""
        return self.app.activeproject.pakfile_location(val)

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
        """Toggle whether .dat file info should be exported, or just the cut image"""
        if config.write_dat != self.export_dat_toggle.GetValue():
            config.write_dat = self.export_dat_toggle.GetValue()
            debug(u"mainwindow: OnToggleDatExport: Set config.write_dat to %s" % config.write_dat)
