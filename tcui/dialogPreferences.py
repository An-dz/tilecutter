# TileCutter User Interface Module
#        Preferences Dialog

import logging
import wx
import config, tcui, translator
config = config.Config()
gt = translator.Translator()


class DialogPreferences(wx.Dialog):
    """Dialog for setting program preferences"""
    def __init__(self, parent, app):
        """Initialise the dialog and populate lists"""
        logging.info("Create preferences dialog")

        self.app = app
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.ftbox = tcui.FilePicker(parent)

        # Overall panel sizer
        self.sizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)

        # Path to makeobj
        self.makeobj_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.makeobj_label = wx.StaticText( self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.makeobj_box   = wx.TextCtrl(   self, wx.ID_ANY, value="")
        self.makeobj_filebrowse = wx.Button(self, wx.ID_ANY, label="")
        self.makeobj_sizer.Add(self.makeobj_box, 1)
        self.makeobj_sizer.Add((5, 0))
        self.makeobj_sizer.Add(self.makeobj_filebrowse, 0)

        # Logfile location
        self.logfile_label    = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.logfile_box      = wx.TextCtrl(  self, wx.ID_ANY, value=config.logfile)
        self.logfile_checkbox = wx.CheckBox(  self, wx.ID_ANY, "", (-1, -1), (-1, -1))

        # Default paksize
        self.paksize_label    = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.paksize_select   = wx.ComboBox(  self, wx.ID_ANY, "", (-1, -1), (-1, -1), style=wx.CB_READONLY)

        # Logging level
        self.loglevel_label   = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.loglevel_select  = wx.ComboBox(  self, wx.ID_ANY, "", (-1, -1), (-1, -1), style=wx.CB_READONLY)

        # Add close button at the bottom
        self.close_button     = wx.Button(    self, wx.ID_OK,  "", (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        self.buttons.Add(self.close_button, 0, 0, 0)

        # And finally add that, the language picker and the other static text to the panel sizer
        self.v_sizer.Add((0, 10))
        self.v_sizer.Add(self.makeobj_label,    0, wx.EXPAND)
        self.v_sizer.Add((0,  3))
        self.v_sizer.Add(self.makeobj_sizer,    0, wx.EXPAND)

        self.v_sizer.Add((0, 15))
        self.v_sizer.Add(self.logfile_label,    0, wx.EXPAND)
        self.v_sizer.Add((0,  3))
        self.v_sizer.Add(self.logfile_box,      0, wx.EXPAND)
        self.v_sizer.Add((0,  3))
        self.v_sizer.Add(self.logfile_checkbox, 0, wx.EXPAND)

        self.v_sizer.Add((0, 15))
        self.v_sizer.Add(self.paksize_label,    0, wx.EXPAND)
        self.v_sizer.Add((0,  3))
        self.v_sizer.Add(self.paksize_select,   0, wx.EXPAND)

        self.v_sizer.Add((0, 15))
        self.v_sizer.Add(self.loglevel_label,   0, wx.EXPAND)
        self.v_sizer.Add((0,  3))
        self.v_sizer.Add(self.loglevel_select,  0, wx.EXPAND)

        self.v_sizer.Add((0, 15))
        self.v_sizer.Add(self.buttons,          0, wx.ALIGN_RIGHT)
        self.v_sizer.Add((0, 10))

        self.sizer.Add(  (20, 0))
        self.sizer.Add(self.v_sizer,            1, wx.EXPAND)
        self.sizer.Add(  (20, 0))

        # Bind events
        self.makeobj_box.Bind(       wx.EVT_TEXT,     self.OnMakeobjTextChange,    self.makeobj_box)
        self.makeobj_filebrowse.Bind(wx.EVT_BUTTON,   self.OnBrowseMakeobj,        self.makeobj_filebrowse)
        self.logfile_box.Bind(       wx.EVT_TEXT,     self.OnLogfileTextChange,    self.logfile_box)
        self.logfile_checkbox.Bind(  wx.EVT_CHECKBOX, self.OnLogfileDefaultToggle, self.logfile_checkbox)
        self.paksize_select.Bind(    wx.EVT_COMBOBOX, self.OnPaksizeSelect,        self.paksize_select)
        self.loglevel_select.Bind(   wx.EVT_COMBOBOX, self.OnLoglevelSelect,       self.loglevel_select)
        self.close_button.Bind(      wx.EVT_BUTTON,   self.OnClose,                self.close_button)

        # Layout sizers
        self.SetSizer(self.sizer)

        # Load the initial translation
        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("Translate UI")

        self.SetLabel(gt("Preferences"))
        self.makeobj_label.SetLabel(gt("Path to makeobj binary:"))
        self.makeobj_box.SetToolTip(gt("Relative paths are interpreted relative to TileCutter's start location"))
        self.makeobj_filebrowse.SetLabel(gt("Browse..."))
        self.makeobj_filebrowse.SetToolTip(gt("tt_browse_makeobj_location"))
        self.logfile_label.SetLabel(gt("Location of TileCutter log file:"))
        self.logfile_box.SetToolTip(gt("tt_config_logfile"))
        self.logfile_checkbox.SetLabel(gt("Use system default location"))
        self.logfile_checkbox.SetToolTip(gt("tt_config_logfile_default"))

        # Translate the choicelist values for paksize
        self.paksize_label.SetLabel(gt("Default paksize for new projects:"))
        self.choicelist_paksize = gt.translate_int_array(config.choicelist_paksize)
        self.paksize_select.Clear()
        self.paksize_select.Append(self.choicelist_paksize)

        # Translate the choicelist values for logging level
        self.loglevel_label.SetLabel(gt("Logging verbosity level:"))
        self.choicelist_loglevel = [
            gt("0 - logging disabled"),
            gt("1 - normal logging"),
            gt("2 - verbose logging"),
        ]
        self.loglevel_select.Clear()
        self.loglevel_select.Append(self.choicelist_loglevel)

        self.close_button.SetLabel(gt("OK"))

        self.update()

        self.SetClientSize(self.sizer.GetSize())

        # Set width of panel to be calculated size or 1.4* height
        self.SetSize(wx.Size(max(self.GetBestSize().Get()[1] * 1.4, self.GetBestSize().Get()[0]), self.GetBestSize().Get()[1]))

        self.CentreOnParent()
        self.Refresh()

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        logging.info("Update controls")
        self.makeobj_box.SetValue(config.path_to_makeobj)

        if config.logfile_platform_default:
            self.logfile_box.SetValue(config.logs_path)
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
        logging.info("Closing window")
        self.EndModal(wx.ID_OK)

    def OnMakeobjTextChange(self, e):
        """When user changes the makeobj path text"""
        logging.info("Change makeobj location")
        if config.path_to_makeobj != self.makeobj_box.GetValue():
            config.path_to_makeobj = self.makeobj_box.GetValue()
            logging.debug("Preferences: Text changed in makeobj path entry box, new text: %s" % str(self.makeobj_box.GetValue()))

    def OnBrowseMakeobj(self, e):
        """Triggered when the browse button is clicked for the makeobj path"""
        logging.info("Browse for makeobj")
        value = self.ftbox.file_picker_dialog(
            config.path_to_makeobj,
            None,
            gt("Select a makeobj binary to use"),
            "",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        logging.debug("Path selected by user is: %s" % value)
        config.path_to_makeobj = value
        self.makeobj_box.SetValue(value)

    def OnLogfileTextChange(self, e):
        """Triggered when user changes log file location"""
        logging.info("Changed log file location")
        if config.logfile != self.logfile_box.GetValue():
            config.logfile = self.logfile_box.GetValue()
            logging.debug("Text changed in logfile path entry box, new text: %s" % str(config.logfile))

    def OnLogfileDefaultToggle(self, e):
        """Triggered when user selects the system default location for the log file"""
        logging.info("Set to %s" % self.logfile_checkbox.GetValue())

        if self.logfile_checkbox.GetValue():
            config.logfile_platform_default = True
        else:
            config.logfile_platform_default = False

        self.update()

    def OnPaksizeSelect(self, e):
        """Triggered when user selects a default pakset size"""
        config.default_paksize = config.choicelist_paksize[self.choicelist_paksize.index(self.paksize_select.GetValue())]
        logging.debug("Set to: %s" % config.default_paksize)

    def OnLoglevelSelect(self, e):
        """Triggered when user selects a logging level"""
        config.debug_level = self.choicelist_loglevel.index(self.loglevel_select.GetValue())
        logging.debug("Set to: %s" % config.debug_level)
