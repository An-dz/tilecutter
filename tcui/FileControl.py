# coding: UTF-8
#
# TileCutter, User Interface Module - FileControl
#

# FileControl is a combination of controls and methods:
# Static Text (description)
# TextCtrl (display/editing file path
# StaticBitmap (display file validity status, X no exists, tick does exist)
# Browse Button (open dialog to pick file)

# Path may be absolute, or relative to a specified path - relative paths stay relative
# and the browse property browses from the combination of the relative path and its parent

# Has usual translate/update methods.

import wx

import tcui

import translator
gt = translator.Translator()
import logger
debug = logger.Log()

class FileControl(tcui.fileTextBox):
    def __init__(self, parent, app, parent_sizer, linked,
                 label, tooltip,
                 filepicker_title, filepicker_allowed,
                 browse_string, browse_tooltip, relative=None):
        """parent, ref to app, ref to parent sizer, description, variable to link to
        title for file picker, allowed types for file picker, variable this is relative to (if any)"""
        self.filepicker_title = filepicker_title
        self.filepicker_allowed = filepicker_allowed
        self.relative = relative
        self.label = label
        self.tooltip = tooltip
        self.linked = linked
        self.browse_string = browse_string
        self.browse_tooltip = browse_tooltip

        self.dependants = None
        self.app = app
        self.parent = parent

        # Create UI elements
        self.path_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.path_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.path_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.path_icon = wx.StaticBitmap(parent, wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
        self.path_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
        # Add to parent sizer (which must be a wx.FlexGridSizer)
        parent_sizer.Add(self.path_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        parent_sizer.Add(self.path_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 5)
        parent_sizer.Add(self.path_icon, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        parent_sizer.Add(self.path_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5)
        # Bind events
        self.path_box.Bind(wx.EVT_TEXT, self.OnTextChange, self.path_box)
        self.path_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowse, self.path_filebrowse)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.path_label.SetLabel(gt(self.label))
        self.path_box.SetToolTipString(gt(self.tooltip))
        self.path_filebrowse.SetLabel(gt(self.browse_string))
        self.path_filebrowse.SetToolTipString(gt(self.browse_tooltip))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Setting these values should also cause text highlighting to occur
        self.path_box.ChangeValue(self.linked())
        debug("update file control")
        self.highlight()

    def SetDependants(self, list):
        """When highlight method is called for this control, also call it for the controls in this list
        Should be used when the dependant controls rely on this one for their relative path info"""
        self.dependants = list

    def highlight(self):
        """Highlight entry box text"""
        debug("highlighting %s entry box" % self.label)
        if self.relative != None:
            debug("highlight with relative, %s | %s" % (self.linked(), self.relative()))
            self.highlightText(self.path_box, self.linked(), self.relative())
        else:
            debug("highlight without relative, %s" % self.linked())
            self.highlightText(self.path_box, self.linked())
        if self.dependants:
            debug("highlighting dependants: %s" % (str(self.dependants)))
            for i in self.dependants:
                i.highlight()


    def OnTextChange(self, e):
        """Triggered when the text in the path box is changed"""
        if self.linked() != self.path_box.GetValue():
            self.linked(self.path_box.GetValue())
            debug("Text changed in %s entry box, new text: %s" % (self.label, str(self.path_box.GetValue())))
            self.highlight()

    def OnBrowse(self, e):
        """Triggered when the browse button is clicked"""
        if self.relative:
            rel = self.relative()
        else:
            rel = ""
        value = self.filePickerDialog(self.linked(), rel, self.filepicker_title,
                                      self.filepicker_allowed, wx.FD_SAVE|wx.OVERWRITE_PROMPT)
        self.path_box.SetValue(value)


