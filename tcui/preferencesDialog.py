# coding: UTF-8
#
# TileCutter User Interface Module - preferencesDialog
#

# Copyright © 2010 Timothy Baldock. All Rights Reserved.

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
        self.app = app
        size = (300,200)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.makeobj_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.makeobj_box = wx.TextCtrl(self, wx.ID_ANY, value=config.path_to_makeobj)

        # Add close button at the bottom
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        # And finally add that, the language picker and the other static text to the panel sizer
        self.s_panel.Add(self.makeobj_label, 0, wx.EXPAND|wx.ALL, 3)
        self.s_panel.Add(self.makeobj_box, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        self.s_panel.Add(self.buttons, 0, wx.ALIGN_RIGHT|wx.ALL, 3)

        # Bind events
        self.makeobj_box.Bind(wx.EVT_TEXT, self.OnMakeobjTextChange, self.makeobj_box)
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        self.SetEscapeId(self.close_button.GetId())

        # Layout sizers
        self.SetSizer(self.s_panel)

        self.translate()    # Load the initial translation
##        self.update()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(gt("Preferences"))
        self.makeobj_label.SetLabel(gt("Path to makeobj binary:"))
        self.makeobj_box.SetToolTipString(gt("Relative paths are interpreted relative to TileCutter's start location"))
        self.close_button.SetLabel(gt("Close"))

        self.Layout()
        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnClose(self, e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)
    def OnMakeobjTextChange(self, e):
        """When user changes the makeobj path text"""
        if config.path_to_makeobj != self.makeobj_box.GetValue():
            config.path_to_makeobj = self.makeobj_box.GetValue()
            debug("Preferences: Text changed in makeobj path entry box, new text: %s" % unicode(self.makeobj_box.GetValue()))

