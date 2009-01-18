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

class FileControl(object):
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

        self.app = app
        self.parent = parent

        # Create UI elements
        self.path_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.path_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.path_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.path_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
        # Add to parent sizer (which must be a wx.FlexGridSizer)
        parent_sizer.Add(self.path_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        parent_sizer.Add(self.path_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        parent_sizer.Add(self.path_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        parent_sizer.AddGrowableCol(1)
        # Bind events
        self.path_box.Bind(wx.EVT_TEXT, self.OnTextChange, self.path_box)
        self.path_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowse, self.path_filebrowse)


    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.path_label.SetLabel(gt(self.label))
        self.path_box.SetToolTipString(gt(self.tooltip))
        self.path_filebrowse.SetLabel(gt(self.browse_string))
        self.path_filebrowse.SetToolTipString(gt(self.browse_tooltip))


    def OnTextChange(self, e):
        """Triggered when the text in the path box is changed"""
    def OnBrowse(self, e):
        """Triggered when the browse button is clicked"""


