# coding: UTF-8
#
# TileCutter, User Interface Module - DatFileEditDialog
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class DatFileEditDialog(wx.Dialog):
    """Dialog for editing dat file parameters"""
    def __init__(self, parent, app):
        """Intialise the dialog"""
        self.app = app
        size = (500,400)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)

        self.description = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)

        self.text_input = wx.TextCtrl(self, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.text_input.Bind(wx.EVT_TEXT, self.OnTextChange, self.text_input)

        # Add close button at the bottom
        self.buttons = self.CreateButtonSizer(wx.OK)

        self.s_panel.Add(self.description,0,wx.ALIGN_LEFT|wx.ALL, 3)
        self.s_panel.Add(self.text_input,1,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        # These bits are non-mac only
        self.s_panel.Add(self.buttons,0,wx.ALIGN_RIGHT|wx.ALL, 3)

        # Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
##        self.Layout()

        self.translate()

        self.text_input.ChangeValue(self.app.activeproject.temp_dat_properties())

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(gt("Datfile Properties"))
        self.description.SetLabel(gt("Here you can enter the datfile properties necessary to produce a building using makeobj"))

        self.Layout()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnTextChange(self, e):
        """Triggered when the text in the path box is changed"""
        if self.app.activeproject.temp_dat_properties() != self.text_input.GetValue():
            self.app.activeproject.temp_dat_properties(self.text_input.GetValue())
            debug("Text changed in dat file properties entry box, new text: %s" % (unicode(self.text_input.GetValue())))


    def OnClose(self,e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)
