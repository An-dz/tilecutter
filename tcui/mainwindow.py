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
        debug(u"tcui.MainWindow: __init__")
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, (-1,-1), (-1,-1),
                                        style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.app = app

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

        # Create the status bar
        self.statusbar = wx.StatusBar(self, wx.ID_ANY)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetStatusText(u"", 0)

        # self.panel contains all other elements within this frame and must be their parent
        self.panel = wx.Panel(self, wx.ID_ANY)

        # Overall panel sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_panel = wx.BoxSizer(wx.HORIZONTAL)

        # Within the top panel, two horizontal divisions, one for the controls, one for the image window
        # Left side - Main controls
        self.s_panel_left = wx.BoxSizer(wx.VERTICAL)
        # Right side - Image window and controls
        self.s_panel_right = wx.BoxSizer(wx.VERTICAL)

        # LEFT SIDE CONTROLS
        # Season controls
        self.control_seasons = tcui.seasonControl(self.panel, app)
        self.s_panel_left.Add(self.control_seasons, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel_left.Add((0,2))
        self.s_panel_left.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.s_panel_left.Add((0,2))

        # Image controls
        self.control_images = tcui.imageControl(self.panel, app)
        self.s_panel_left.Add(self.control_images, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel_left.Add((0,2))
        self.s_panel_left.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.s_panel_left.Add((0,2))

        # Facing controls
        self.control_facing = tcui.facingControl(self.panel, app)
        self.s_panel_left.Add(self.control_facing, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel_left.Add((0,2))
        self.s_panel_left.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.s_panel_left.Add((0,2))

        # Dimension controls
        self.control_dims = tcui.dimsControl(self.panel, app)
        self.s_panel_left.Add(self.control_dims, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel_left.Add((0,2))
        self.s_panel_left.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.s_panel_left.Add((0,2))

        # Offset/mask controls
        self.control_offset = tcui.offsetControl(self.panel, app)
        self.s_panel_left.Add(self.control_offset, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel_left.Add((0,2))
        self.s_panel_left.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL), 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.s_panel_left.Add((0,2))

        # Create Image display window and image path entry control, which adds itself to the sizer
        self.display = tcui.imageWindow(self, app, config.transparent)
        self.s_panel_right.Add(self.display, 1, wx.EXPAND)

        # Save, Dat, Image and Pak output paths
        self.control_paths = tcui.MultiFileControl(self.panel, app)

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
        self.s_panel_rb_inner.Add(self.control_paths, 0, wx.EXPAND|wx.ALL, 4)

        # Add that vertical sizer to a horizontal one, with a vertical line on the left
        self.s_panel_rb.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_VERTICAL), 0, wx.EXPAND, 2)
        self.s_panel_rb.Add(self.s_panel_rb_inner, 1, wx.LEFT, 0)
        # Add that horizontal sizer to the right-side of the application
        self.s_panel_right.Add(self.s_panel_rb, 0, wx.EXPAND)

        # SIZERS
        # Add the remaining sizers to each other
        # Line under menu bar
#        self.sizer.Add(wx.StaticLine(self.panel, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)
        # Left and right panels added
        self.s_panel.Add(self.s_panel_left, 0, wx.EXPAND|wx.RIGHT, 1)
        self.s_panel.Add(self.s_panel_right, 1, wx.EXPAND, 0)
        self.sizer.Add(self.s_panel, 1, wx.EXPAND, 0)
        # Layout sizers
        self.panel.SetSizer(self.sizer)

        self.panel.SetSize((0,0))

        self.translate()

    def get_active_image_path(self, val=None):
        """Return activeproject's active image path"""
        debug(u"tcui.MainWindow: get_active_image_path")
        return self.app.activeproject.active_image_path(val)
    def get_active_savefile_path(self, val=None):
        """Return activeproject's save path"""
        debug(u"tcui.MainWindow: get_active_savefile_path")
        return self.app.activeproject.save_location(val)
    def get_active_datfile_path(self, val=None):
        """Return activeproject's datfile path"""
        debug(u"tcui.MainWindow: get_active_datfile_path")
        return self.app.activeproject.datfile_location(val)
    def get_active_pngfile_path(self, val=None):
        """Return activeproject's pngfile path"""
        debug(u"tcui.MainWindow: get_active_pngfile_path")
        return self.app.activeproject.pngfile_location(val)
    def get_active_pakfile_path(self, val=None):
        """Return activeproject's pakfile path"""
        debug(u"tcui.MainWindow: get_active_pakfile_path")
        return self.app.activeproject.pakfile_location(val)

    def translate(self):
        """Master translate function for the mainwindow object"""
        debug(u"tcui.MainWindow: translate")
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
        self.control_paths.translate()
        # And the menus
        self.menubar.translate()
        # Finally translate the application name in title bar
        self.set_title()

        # Find size of panel and size of window
        # Difference between the two is the difference between client and surrounding area
        prev_panel_size = self.panel.GetSizeTuple()
        prev_window_size = self.GetSizeTuple()

        if prev_panel_size == (0,0):
            # Must be first time this has been run, panel hasn't been laid out yet
            self.panel.Fit()
            self.SetClientSize(self.panel.GetSize())
            prev_panel_size = self.panel.GetSizeTuple()
            prev_window_size = self.GetSizeTuple()

        debug(u"tcui.MainWindow: translate - previous panel size: %s, previous window size: %s" % (prev_panel_size, prev_window_size))

        # Find minimum size of panel
        self.panel.Fit()
        debug(u"tcui.MainWindow: translate - minimum panel size is: %s" % (str(self.panel.GetBestSizeTuple())))

        # If horizontal or vertical size is smaller than it was before set the size to that value
        new_panel_size = (max(prev_panel_size[0], self.panel.GetBestSizeTuple()[0]), max(prev_panel_size[1], self.panel.GetBestSizeTuple()[1]))
        # New window size will be the new panel size plus the difference between the previous window size and panel size
        new_window_size = (prev_window_size[0] - prev_panel_size[0] + new_panel_size[0], 
                           prev_window_size[1] - prev_panel_size[1] + new_panel_size[1])
        debug(u"tcui.MainWindow: translate - new panel size is: %s, new window size is: %s" % (new_panel_size, new_window_size))

        # Set minimum panel size to the minimum allowable height and 1.4* ratio width of that height (or the minimum width if this is larger)
        self.panel.SetMinSize(wx.Size(max(self.panel.GetBestSizeTuple()[1] * 1.4, self.panel.GetBestSizeTuple()[0]), self.panel.GetBestSizeTuple()[1]))
        # Set minimum window size to minimum panel size plus the difference in the previous sizes
        self.SetMinSize(wx.Size(prev_window_size[0] - prev_panel_size[0] + max(self.panel.GetBestSizeTuple()[1] * 1.4, self.panel.GetBestSizeTuple()[0]), 
                                prev_window_size[1] - prev_panel_size[1] + self.panel.GetBestSizeTuple()[1]))

        # Finally set size to the calculated new size, which is the larger of the new minimum or pre-existing
        self.panel.SetSize(new_panel_size)
        self.panel.Layout()
        self.SetClientSize(new_panel_size)
        self.Thaw()

    def set_title(self):
        # Set title text of window
        debug(u"tcui.MainWindow: set_title")
        self.SetTitle(self.app.get_title_text() % _gt("TileCutter"))

    def set_status_text(self, message, field=0):
        """Set the status bar text field specified to the message specified"""
        debug(u"tcui.MainWindow: set_status_text - setting field: %s to string: %s" % (field, message))
        self.statusbar.SetStatusText(message, field)

    def update(self):
        """Update frame and all its children to reflect values in the active project"""
        debug(u"tcui.MainWindow: update")
        self.Freeze()
        self.export_dat_toggle.SetValue(config.write_dat)
        self.control_seasons.update()
        self.control_images.update()
        self.control_facing.update()
        self.control_dims.update()
        self.control_offset.update()
        self.control_paths.update()
        self.display.update()
        self.Thaw()

    def OnToggleDatExport(self, e):
        """Toggle whether .dat file info should be exported, or just the cut image"""
        debug(u"tcui.MainWindow: OnToggleDatExport")
        if config.write_dat != self.export_dat_toggle.GetValue():
            config.write_dat = self.export_dat_toggle.GetValue()
            debug(u"tcui.MainWindow: OnToggleDatExport - Set config.write_dat to %s" % config.write_dat)
