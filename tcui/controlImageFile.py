# TileCutter User Interface Module
#       Image File Controls

import logging
import wx
import tcui, translator
gt = translator.Translator()


class ControlImageFile(wx.Panel):
    """Box containig the Image location controls"""
    def __init__(self, parent, app):
        """parent, ref to app"""
        logging.info("Creating image location controls")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.ftbox = tcui.FilePicker(parent)
        self.app = app
        self.parent = parent

        self.sizer = wx.FlexGridSizer(0, 7, 3, 0)

        # Create UI elements
        self.path_label      = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.path_box        = wx.TextCtrl(  self, wx.ID_ANY, value="", style=wx.TE_RICH | wx.BORDER_SUNKEN)
        self.path_filebrowse = wx.Button(    self, wx.ID_ANY, label="")
        self.path_reloadfile = wx.Button(    self, wx.ID_ANY)

        # Add to sizer (which must be a wx.FlexGridSizer)
        self.sizer.Add(self.path_label,      0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.path_box,        0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.TE_READONLY)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.path_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.path_reloadfile, 0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.AddGrowableCol(2)

        # Bind events
        self.path_box.Bind(       wx.EVT_TEXT,   self.OnTextChange,  self.path_box)
        self.path_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowse,      self.path_filebrowse)
        self.path_reloadfile.Bind(wx.EVT_BUTTON, self.OnReloadImage, self.path_reloadfile)

        # Set panel's sizer
        self.SetSizer(self.sizer)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("Translate UI")

        self.path_label.SetLabel(gt("Source image location:"))
        self.path_box.SetToolTip(gt("tt_image_file_location"))
        self.path_filebrowse.SetLabel(gt("Browse..."))
        self.path_filebrowse.SetToolTip(gt("tt_browse_input_file"))
        self.path_reloadfile.SetLabel(gt("Reload Image"))
        self.path_reloadfile.SetToolTip(gt("tt_reload_input_file"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        logging.info("Update controls")
        # Setting these values should also cause text highlighting to occur
        self.path_box.ChangeValue(self.app.activeproject.active_image_path())

    def OnTextChange(self, e):
        """Triggered when the text in the path box is changed"""
        logging.info("Path was changed")

        if self.app.activeproject.active_image_path() != self.path_box.GetValue():
            self.app.activeproject.active_image_path(self.path_box.GetValue())
            logging.debug("Text changed in Active Image entry box, new text: %s" % str(self.path_box.GetValue()))
            # Refresh image in parent window
            self.parent.refresh_if_valid()

    def OnBrowse(self, e):
        """Triggered when the browse button is clicked"""
        logging.info("Browsing for new path")
        value = self.ftbox.file_picker_dialog(
            self.app.activeproject.active_image_path(),
            self.app.activeproject.save_location(),
            gt("Choose an image file to open..."),
            "PNG files (*.png)|*.png",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        )
        logging.debug("Path selected by user is: %s" % value)
        self.path_box.SetValue(value)

    def OnReloadImage(self, e):
        """When reload image button clicked"""
        logging.info("Reload image")
        self.app.activeproject.reload_active_image()
