# coding: UTF-8
#
# TileCutter User Interface Module - translationDialog
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class translationDialog(wx.Dialog):
    """Dialog for choosing which translation to use"""
    def __init__(self, parent, app):
        """Initialise the dialog and populate lists"""
        debug(u"tcui.TranslationDialog: __init__")
        self.app = app
        size = (300,200)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.top_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.language_picker = wx.ComboBox(self, wx.ID_ANY, gt.active.longname(), (-1, -1), (-1, -1), gt.language_longnames_list, wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)

        # Within the static box
        self.dialog_box = wx.StaticBox(self, wx.ID_ANY, gt("Language Details:"))
        self.s_dialog_box = wx.StaticBoxSizer(self.dialog_box, wx.HORIZONTAL)
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
        self.close_button = wx.Button(self, wx.ID_OK, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        # Then add bitmap and texts to the static box sizer
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

        self.translate()    # Load the initial translation
##        self.update()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug(u"tcui.TranslationDialog: translate")
        self.SetLabel(gt("Language"))
        self.top_label.SetLabel(gt("Select from the options below:"))
        self.close_button.SetLabel(gt("Close"))
        # These values taken from the active translation
        self.label_name.SetLabel(gt("Language:"))
        self.label_name_value.SetLabel(gt.active.longname())
        self.label_createdby.SetLabel(gt("Created by:"))
        self.label_createdby_value.SetLabel(gt.active.created_by())
        self.label_createdon.SetLabel(gt("Created on:"))
        self.label_createdon_value.SetLabel(gt.active.created_date())
        self.Layout()
        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        debug(u"tcui.TranslationDialog: update")

    def OnClose(self, e):
        """On click of the close button"""
        debug(u"tcui.TranslationDialog: OnClose")
        self.EndModal(wx.ID_OK)
    def OnSelection(self, e):
        """When user changes the language selection"""
        # Set active translation to the one specified
        debug(u"tcui.TranslationDialog: OnSelection - User selected language: %s" % gt.longnameToName(self.language_picker.GetValue()))
        gt.setActiveTranslation(gt.longnameToName(self.language_picker.GetValue()))
        # Call own translate function
        self.translate()
        self.app.frame.translate()
