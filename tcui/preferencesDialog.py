# coding: UTF-8
#
# TileCutter User Interface Module - preferencesDialog
#

# Copyright © 2010-2011 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

import config
config = config.Config()

class preferencesDialog(wx.Dialog):
    """Dialog for setting program preferences"""
    def __init__(self, parent, app):
        """Initialise the dialog and populate lists"""
        debug(u"tcui.PreferencesDialog: __init__")
        self.app = app
#        size = (300,200)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), (-1,-1))

        # Overall panel sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Path to makeobj
        self.makeobj_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.makeobj_box = wx.TextCtrl(self, wx.ID_ANY, value=config.path_to_makeobj)

        # Logfile location
        self.logfile_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.logfile_box = wx.TextCtrl(self, wx.ID_ANY, value=config.logfile)

        # Default paksize
        self.paksize_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.paksize_select = wx.ComboBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1), "", wx.CB_READONLY)

        # Default paksize
        self.loglevel_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.loglevel_select = wx.ComboBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1), "", wx.CB_READONLY)

        # Add close button at the bottom
        self.close_button = wx.Button(self, wx.ID_OK, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        # And finally add that, the language picker and the other static text to the panel sizer
        self.sizer.Add((0,3))
        self.sizer.Add(self.makeobj_label, 0, wx.EXPAND)
        self.sizer.Add((0,3))
        self.sizer.Add(self.makeobj_box, 0, wx.EXPAND)

        self.sizer.Add((0,3))
        self.sizer.Add(self.logfile_label, 0, wx.EXPAND)
        self.sizer.Add((0,3))
        self.sizer.Add(self.logfile_box, 0, wx.EXPAND)

        self.sizer.Add((0,3))
        self.sizer.Add(self.paksize_label, 0, wx.EXPAND)
        self.sizer.Add((0,3))
        self.sizer.Add(self.paksize_select, 0, wx.EXPAND)

        self.sizer.Add((0,3))
        self.sizer.Add(self.loglevel_label, 0, wx.EXPAND)
        self.sizer.Add((0,3))
        self.sizer.Add(self.loglevel_select, 0, wx.EXPAND)

        self.sizer.Add((0,3))
        self.sizer.Add(self.buttons, 0, wx.ALIGN_RIGHT)
        self.sizer.Add((0,3))

        # Bind events
        self.makeobj_box.Bind(wx.EVT_TEXT, self.OnMakeobjTextChange, self.makeobj_box)
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        # Layout sizers
        self.SetSizer(self.sizer)

        self.translate()    # Load the initial translation
##        self.update()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug(u"tcui.PreferencesDialog: translate")
        self.SetLabel(gt("Preferences"))
        self.makeobj_label.SetLabel(gt("Path to makeobj binary:"))
        self.makeobj_box.SetToolTipString(gt("Relative paths are interpreted relative to TileCutter's start location"))
        self.logfile_label.SetLabel(gt("Location of TileCutter log file:"))
        self.logfile_box.SetToolTipString(gt("tt_config_logfile"))

        # Translate the choicelist values for paksize
        self.paksize_label.SetLabel(gt("Default paksize for new projects:"))
        self.choicelist_paksize = gt.translateIntArray(config.choicelist_paksize)
        self.paksize_select.Clear()
        for i in self.choicelist_paksize:
            self.paksize_select.Append(i)
        # And set value to value in the project
        self.paksize_select.SetStringSelection(self.choicelist_paksize[config.choicelist_paksize.index(config.default_paksize)])

        # Translate the choicelist values for logging level
        self.loglevel_label.SetLabel(gt("Logging verbosity level:"))
        self.loglevel_select
        self.loglevel_options = gt.translateIntArray(config.loglevel_options)
        self.loglevel_select.Clear()
        for i in self.loglevel_options:
            self.loglevel_select.Append(i)
        # And set value to value in the project
        self.loglevel_select.SetStringSelection(self.loglevel_options[config.loglevel_options.index(config.debug_level)])

        self.close_button.SetLabel(gt("OK"))

        self.Fit()

        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        debug(u"tcui.PreferencesDialog: update")

    def OnClose(self, e):
        """On click of the close button"""
        debug(u"tcui.PreferencesDialog: OnClose")
        self.EndModal(wx.ID_OK)

    def OnMakeobjTextChange(self, e):
        """When user changes the makeobj path text"""
        debug(u"tcui.PreferencesDialog: OnMakeobjTextChange")
        if config.path_to_makeobj != self.makeobj_box.GetValue():
            config.path_to_makeobj = self.makeobj_box.GetValue()
            debug(u"tcui.PreferencesDialog: OnMakeobjTextChange - Preferences: Text changed in makeobj path entry box, new text: %s" % unicode(self.makeobj_box.GetValue()))

