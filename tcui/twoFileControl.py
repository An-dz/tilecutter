# coding: UTF-8
#
# TileCutter, User Interface Module - twoFileControl
#
import wx, imres, tcui

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class twoFileControl(tcui.fileTextBox):
    """Controls at the bottom of the window, file output locations"""
    def __init__(self, parent, app, parent_sizer):
        """Produce controls, two file path entries"""
        self.app = app
        self.parent = parent
##        fileTextBoxControls.__init__()
            # Bottom panel sizers
        self.s_panel_bottom_left = wx.FlexGridSizer(0,3,0,0)    # Contains paths for output .dat and .png
            # Dat/pak output path entry
        self.dat_outpath_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dat_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.dat_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.dat_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
            # Add them to sizer...
        self.s_panel_bottom_left.Add(self.dat_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.dat_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.dat_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangeDat, self.dat_outpath_box)
        self.dat_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowseDat, self.dat_outpath_filebrowse)

            # Image output path entry
        self.im_outpath_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.im_outpath_box = wx.TextCtrl(parent, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.im_outpath_box.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.im_outpath_filebrowse = wx.Button(parent, wx.ID_ANY, label="")
            # Add to sizer...
        self.s_panel_bottom_left.Add(self.im_outpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_box, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.TE_READONLY, 2)
        self.s_panel_bottom_left.Add(self.im_outpath_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 1)
        self.s_panel_bottom_left.AddGrowableCol(1)
            # Bind them to events
        self.im_outpath_box.Bind(wx.EVT_TEXT, self.OnTextChangePng, self.im_outpath_box)
        self.im_outpath_filebrowse.Bind(wx.EVT_BUTTON, self.OnBrowsePng, self.im_outpath_filebrowse)
        parent_sizer.Add(self.s_panel_bottom_left, 1, wx.EXPAND, 0)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.dat_outpath_label.SetLabel(gt("Output Dat or Pak File Location:"))
        self.dat_outpath_box.SetToolTipString(gt("tt_output_dat_file_location"))
        self.dat_outpath_filebrowse.SetLabel(gt("Browse..."))
        self.dat_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_dat_file_location"))

        self.im_outpath_label.SetLabel(gt("Path from .dat to .png:"))
        self.im_outpath_box.SetToolTipString(gt("tt_output_image_location"))
        self.im_outpath_filebrowse.SetLabel(gt("Browse..."))
        self.im_outpath_filebrowse.SetToolTipString(gt("tt_browse_output_image_location"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Setting these values should also cause text highlighting to occur
        self.dat_outpath_box.SetValue(self.app.activeproject.datfile())
        self.im_outpath_box.SetValue(self.app.activeproject.pngfile())
        self.highlightText(self.dat_outpath_box, self.app.activeproject.datfile())
        self.highlightText(self.im_outpath_box, self.app.activeproject.pngfile(), self.app.activeproject.datfile())

    def OnTextChangeDat(self,e):
        """When the text in the .dat/.pak output file entry box changes"""
        if self.app.activeproject.datfile() != self.dat_outpath_box.GetValue():
            self.app.activeproject.datfile(self.dat_outpath_box.GetValue())
##            debug("Text changed in DAT entry box, new text: " + str(self.app.activeproject.datfile()))
            self.highlightText(self.dat_outpath_box, self.app.activeproject.datfile())
            self.highlightText(self.im_outpath_box, self.app.activeproject.pngfile(), self.app.activeproject.datfile())
    def OnTextChangePng(self,e):
        """When the text in the .png output file entry box changes"""
        if self.app.activeproject.pngfile() != self.im_outpath_box.GetValue():
            self.app.activeproject.pngfile(self.im_outpath_box.GetValue())
##            debug("Text changed in PNG entry box, new text: " + str(self.app.activeproject.pngfile()))
            self.highlightText(self.dat_outpath_box, self.app.activeproject.datfile())
            self.highlightText(self.im_outpath_box, self.app.activeproject.pngfile(), self.app.activeproject.datfile())

    def OnBrowseDat(self,e):
        """Opens a file save as dialog for the dat/pak output file"""
        value = self.filePickerDialog(self.app.activeproject.datfile(), "", gt("Choose a location to output .dat/.pak to"),
                                      "DAT/PAK files (*.dat)|*.dat|(*.pak)|*.pak", wx.FD_SAVE|wx.OVERWRITE_PROMPT)
        self.dat_outpath_box.SetValue(value)

    def OnBrowsePng(self,e):
        """Opens a file save as dialog for the png output file"""
        value = self.filePickerDialog(self.app.activeproject.pngfile(), self.app.activeproject.datfile(), gt("Choose a file to save to..."),
                                      "PNG files (*.png)|*.png", wx.FD_SAVE|wx.OVERWRITE_PROMPT)
        self.im_outpath_box.SetValue(value)
