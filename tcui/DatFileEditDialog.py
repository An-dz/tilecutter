# coding: UTF-8
#
# TileCutter, User Interface Module - DatFileEditDialog
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

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
        debug(u"tcui.DatFileDialog: __init__")
        self.app = app
        # Height will be 0.7*width
        self.min_width = 500
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), (-1,-1))

        # Overall panel sizer
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.description = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)

        self.text_input = wx.TextCtrl(self, wx.ID_ANY, value="", style=wx.BORDER_SUNKEN|wx.TE_MULTILINE)
        self.text_input.Bind(wx.EVT_TEXT, self.OnTextChange, self.text_input)

        # Add close button at the bottom
        self.buttons = self.CreateButtonSizer(wx.OK)

        self.v_sizer.Add((0,5))
        self.v_sizer.Add(self.description, 0, wx.ALIGN_LEFT)
        self.v_sizer.Add((0,5))
        self.v_sizer.Add(self.text_input, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
        self.v_sizer.Add((0,10))
        self.v_sizer.Add(self.buttons, 0, wx.ALIGN_RIGHT)
        self.v_sizer.Add((0,10))

        self.sizer.Add((5,0))
        self.sizer.Add(self.v_sizer, 1, wx.EXPAND)
        self.sizer.Add((5,0))

        # Layout sizers
        self.SetSizer(self.sizer)

        self.translate()

        self.update()


    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug(u"tcui.DatFileDialog: translate")
        self.SetLabel(gt("Datfile Properties"))
        self.description.SetLabel(gt("Here you can enter the datfile properties necessary to produce a building using makeobj"))

        self.Fit()
        
        # Set height of panel to be calculated size or 0.7* width
        self.SetSize(wx.Size(max(self.GetBestSize().Get()[0], self.min_width), max(self.GetBestSize().Get()[0] * 0.7, self.min_width * 0.7, self.GetBestSize().Get()[1])))

        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        debug(u"tcui.DatFileDialog: update")
        self.text_input.ChangeValue(self.app.activeproject.dat_lump())

    def OnTextChange(self, e):
        """Triggered when the text in the path box is changed"""
        debug(u"tcui.DatFileDialog: OnTextChange")
        if self.app.activeproject.dat_lump() != self.text_input.GetValue():
            self.app.activeproject.dat_lump(self.text_input.GetValue())
            debug(u"tcui.DatFileDialog: OnTextChange - Text changed in dat file properties entry box, new text: %s" % (unicode(self.text_input.GetValue())))

    def OnClose(self,e):
        """On click of the close button"""
        debug(u"tcui.DatFileDialog: OnClose")
        self.EndModal(wx.ID_OK)
