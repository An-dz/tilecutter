# coding: UTF-8
#
# TileCutter User Interface Module - preferencesDialog
#

# Copyright © 2010-2012 Timothy Baldock. All Rights Reserved.

import wx, imres

import tcui

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

        self.ftbox = tcui.fileTextBox(parent)

        # Overall panel sizer
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Path to makeobj
        self.makeobj_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.makeobj_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.makeobj_box = wx.TextCtrl(self, wx.ID_ANY, value="")
        self.makeobj_filebrowse = wx.Button(self, wx.ID_ANY, label="")

        # Logfile location
        self.logfile_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.logfile_box = wx.TextCtrl(self, wx.ID_ANY, value=config.logfile)
        self.logfile_checkbox = wx.CheckBox(self, wx.ID_ANY, "", (-1,-1), (-1,-1))

        # Default paksize
        self.paksize_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.paksize_select = wx.ComboBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1), "", wx.CB_READONLY)

        # Logging level
        self.loglevel_label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.loglevel_select = wx.ComboBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1), "", wx.CB_READONLY)

        # Add close button at the bottom
        self.close_button = wx.Button(self, wx.ID_OK, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        # And finally add that, the language picker and the other static text to the panel sizer
        self.v_sizer.Add((0,10))
        self.v_sizer.Add(self.makeobj_label, 0, wx.EXPAND)
        self.v_sizer.Add((0,3))
        self.makeobj_sizer.Add(self.makeobj_box, 1)
        self.makeobj_sizer.Add((5,0))
        self.makeobj_sizer.Add(self.makeobj_filebrowse, 0)
        self.v_sizer.Add(self.makeobj_sizer, 0, wx.EXPAND)

        self.v_sizer.Add((0,15))
        self.v_sizer.Add(self.logfile_label, 0, wx.EXPAND)
        self.v_sizer.Add((0,3))
        self.v_sizer.Add(self.logfile_box, 0, wx.EXPAND)
        self.v_sizer.Add((0,3))
        self.v_sizer.Add(self.logfile_checkbox, 0, wx.EXPAND)

        self.v_sizer.Add((0,15))
        self.v_sizer.Add(self.paksize_label, 0, wx.EXPAND)
        self.v_sizer.Add((0,3))
        self.v_sizer.Add(self.paksize_select, 0, wx.EXPAND)

        self.v_sizer.Add((0,15))
        self.v_sizer.Add(self.loglevel_label, 0, wx.EXPAND)
        self.v_sizer.Add((0,3))
        self.v_sizer.Add(self.loglevel_select, 0, wx.EXPAND)

        self.v_sizer.Add((0,15))
        self.v_sizer.Add(self.buttons, 0, wx.ALIGN_RIGHT)
        self.v_sizer.Add((0,10))

        self.sizer.Add((20,0))
        self.sizer.Add(self.v_sizer, 1, wx.EXPAND)
        self.sizer.Add((20,0))

        # Bind events
        self.makeobj_box.Bind(wx.EVT_TEXT, self.OnMakeobjTextChange, self.makeobj_box)
        self.makeobj_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseMakeobj, self.makeobj_filebrowse)
        self.logfile_box.Bind(wx.EVT_TEXT, self.OnLogfileTextChange, self.logfile_box)
        self.logfile_checkbox.Bind(wx.EVT_CHECKBOX, self.OnLogfileDefaultToggle, self.logfile_checkbox)
        self.paksize_select.Bind(wx.EVT_COMBOBOX, self.OnPaksizeSelect, self.paksize_select)
        self.loglevel_select.Bind(wx.EVT_COMBOBOX, self.OnLoglevelSelect, self.loglevel_select)
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
        self.makeobj_filebrowse.SetLabel(gt("Browse..."))
        self.makeobj_filebrowse.SetToolTipString(gt("tt_browse_makeobj_location"))
        self.logfile_label.SetLabel(gt("Location of TileCutter log file:"))
        self.logfile_box.SetToolTipString(gt("tt_config_logfile"))
        self.logfile_checkbox.SetLabel(gt("Use system default location"))
        self.logfile_checkbox.SetToolTipString(gt("tt_config_logfile_default"))

        # Translate the choicelist values for paksize
        self.paksize_label.SetLabel(gt("Default paksize for new projects:"))
        self.choicelist_paksize = gt.translateIntArray(config.choicelist_paksize)
        self.paksize_select.Clear()
        for i in self.choicelist_paksize:
            self.paksize_select.Append(i)

        # Translate the choicelist values for logging level
        self.loglevel_label.SetLabel(gt("Logging verbosity level:"))
        self.choicelist_loglevel = [gt("0 - logging disabled"), gt("1 - normal logging"), gt("2 - verbose logging"),]
        self.loglevel_select.Clear()
        for i in self.choicelist_loglevel:
            self.loglevel_select.Append(i)

        self.close_button.SetLabel(gt("OK"))

        self.update()

        self.Fit()

        # Set width of panel to be calculated size or 1.4* height
        self.SetSize(wx.Size(max(self.GetBestSizeTuple()[1] * 1.4, self.GetBestSizeTuple()[0]), self.GetBestSizeTuple()[1]))

        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        debug(u"tcui.PreferencesDialog: update")
        self.makeobj_box.SetValue(config.path_to_makeobj)

        if config.logfile_platform_default:
            self.logfile_box.SetValue(debug.platform_default_log_location()[0])
            self.logfile_box.Disable()
            self.logfile_checkbox.SetValue(1)
        else:
            self.logfile_box.SetValue(config.logfile)
            self.logfile_box.Enable()
            self.logfile_checkbox.SetValue(0)

        self.paksize_select.SetStringSelection(self.choicelist_paksize[config.choicelist_paksize.index(config.default_paksize)])

        self.loglevel_select.SetStringSelection(self.choicelist_loglevel[config.debug_level])


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

    def OnBrowseMakeobj(self, e):
        """Triggered when the browse button is clicked for the makeobj path"""
        debug(u"tcui.ImageFileControl: OnBrowseMakeobj")
        value = self.ftbox.filePickerDialog(config.path_to_makeobj, 
                                            None, 
                                            gt("Select a makeobj binary to use"),
                                            "", 
                                            wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        debug(u"tcui.ImageFileControl: OnBrowseMakeobj - Path selected by user is: %s" % value)
        config.path_to_makeobj = value
        self.makeobj_box.SetValue(value)

    def OnLogfileTextChange(self, e):
        """Triggered when user changes log file location"""
        debug(u"tcui.PreferencesDialog: OnLogfileTextChange")
        if config.logfile != self.logfile_box.GetValue():
            config.logfile = self.logfile_box.GetValue()
            debug(u"tcui.PreferencesDialog: OnLogfileTextChange - Text changed in logfile path entry box, new text: %s" % unicode(config.logfile))

    def OnLogfileDefaultToggle(self, e):
        """Triggered when user selects the system default location for the log file"""
        debug(u"tcui.PreferencesDialog: OnLogfileDefaultToggle - set to %s" % self.logfile_checkbox.GetValue())
        if self.logfile_checkbox.GetValue():
            config.logfile_platform_default = True
        else:
            config.logfile_platform_default = False
        self.update()

    def OnPaksizeSelect(self, e):
        """"""
        config.default_paksize = config.choicelist_paksize[self.choicelist_paksize.index(self.paksize_select.GetValue())]
        debug(u"tcui.PreferencesDialog: OnPaksizeSelect - set to: %s" % config.default_paksize)

    def OnLoglevelSelect(self, e):
        """"""
        config.debug_level = self.choicelist_loglevel.index(self.loglevel_select.GetValue())
        debug(u"tcui.PreferencesDialog: OnLoglevelSelect - set to: %s" % config.debug_level)

