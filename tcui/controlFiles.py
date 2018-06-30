# coding: UTF-8
#
# TileCutter User Interface Module
#       Project Files Panel

import wx

# imports from tilecutter
import tcui
import translator
gt = translator.Translator()
import logger
debug = logger.Log()

class controlFiles(wx.Panel):
    """Box containing the project files locations"""
    def __init__(self, parent, app):
        """parent, ref to app"""
        debug("tcui.controlFiles: __init__")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.ftbox = tcui.filePicker(parent)
        self.app = app
        self.parent = parent

        self.sizer = wx.FlexGridSizer(0, 5, 3, 0)

        # Save, dat, png, pak

        # Create UI elements for save location
        self.save_path_label      = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.save_path_box        = wx.TextCtrl(self,   wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.save_path_filebrowse = wx.Button(self,     wx.ID_ANY, label="")

        # Create UI elements for dat location
        self.dat_path_label       = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.dat_path_box         = wx.TextCtrl(  self, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.dat_path_filebrowse  = wx.Button(    self, wx.ID_ANY, label="")

        # Create UI elements for png location
        self.png_path_label       = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.png_path_box         = wx.TextCtrl(  self, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.png_path_filebrowse  = wx.Button(    self, wx.ID_ANY, label="")

        # Create UI elements for pak location
        self.pak_path_label       = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.pak_path_box         = wx.TextCtrl(  self, wx.ID_ANY, value="", style=wx.TE_RICH|wx.BORDER_SUNKEN)#|wx.TE_MULTILINE)#, style=wx.TE_READONLY)
        self.pak_path_filebrowse  = wx.Button(    self, wx.ID_ANY, label="")

        # Add to sizer
        self.sizer.Add(self.save_path_label,      0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.save_path_box,        0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TE_READONLY)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.save_path_filebrowse, 0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(self.dat_path_label,       0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.dat_path_box,         0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TE_READONLY)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.dat_path_filebrowse,  0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(self.png_path_label,       0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.png_path_box,         0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TE_READONLY)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.png_path_filebrowse,  0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.Add(self.pak_path_label,       0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.pak_path_box,         0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.TE_READONLY)
        self.sizer.Add((5, 0))
        self.sizer.Add(self.pak_path_filebrowse,  0, wx.ALIGN_CENTER_VERTICAL)

        self.sizer.AddGrowableCol(2)

        # Bind events
        self.save_path_box.Bind(       wx.EVT_TEXT,   self.OnSaveTextChange, self.save_path_box)
        self.save_path_filebrowse.Bind(wx.EVT_BUTTON, self.OnSaveBrowse,     self.save_path_filebrowse)
        self.dat_path_box.Bind(        wx.EVT_TEXT,   self.OnDatTextChange,  self.dat_path_box)
        self.dat_path_filebrowse.Bind( wx.EVT_BUTTON, self.OnDatBrowse,      self.dat_path_filebrowse)
        self.png_path_box.Bind(        wx.EVT_TEXT,   self.OnPngTextChange,  self.png_path_box)
        self.png_path_filebrowse.Bind( wx.EVT_BUTTON, self.OnPngBrowse,      self.png_path_filebrowse)
        self.pak_path_box.Bind(        wx.EVT_TEXT,   self.OnPakTextChange,  self.pak_path_box)
        self.pak_path_filebrowse.Bind( wx.EVT_BUTTON, self.OnPakBrowse,      self.pak_path_filebrowse)

        # Set panel's sizer
        self.SetSizer(self.sizer)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug("tcui.controlFiles: translate")

        self.save_path_label.SetLabel(gt("Project Save Location"))
        self.save_path_box.SetToolTip(gt("tt_save_file_location"))
        self.save_path_filebrowse.SetLabel(gt("Browse..."))
        self.save_path_filebrowse.SetToolTip(gt("tt_browse_save_file"))

        self.dat_path_label.SetLabel(gt(".dat Output Location"))
        self.dat_path_box.SetToolTip(gt("tt_dat_file_location"))
        self.dat_path_filebrowse.SetLabel(gt("Browse..."))
        self.dat_path_filebrowse.SetToolTip(gt("tt_browse_dat_file"))

        self.png_path_label.SetLabel(gt(".png Output Location"))
        self.png_path_box.SetToolTip(gt("tt_png_file_location"))
        self.png_path_filebrowse.SetLabel(gt("Browse..."))
        self.png_path_filebrowse.SetToolTip(gt("tt_browse_png_file"))

        self.pak_path_label.SetLabel(gt(".pak Output Location"))
        self.pak_path_box.SetToolTip(gt("tt_pak_file_location"))
        self.pak_path_filebrowse.SetLabel(gt("Browse..."))
        self.pak_path_filebrowse.SetToolTip(gt("tt_browse_pak_file"))

        self.Fit()

    def update(self):
        """Set the values of the controls in this group to the values in the project"""
        # Setting these values should also cause text highlighting to occur
        debug("tcui.controlFiles: update")
        self.save_path_box.ChangeValue(self.app.activeproject.save_location())
        self.dat_path_box.ChangeValue( self.app.activeproject.datfile_location())
        self.png_path_box.ChangeValue( self.app.activeproject.pngfile_location())
        self.pak_path_box.ChangeValue( self.app.activeproject.pakfile_location())
        ## self.highlight()

    ## def SetDependants(self, list):
    ##     """When highlight method is called for this control, also call it for the controls in this list
    ##     Should be used when the dependant controls rely on this one for their relative path info"""
    ##     self.dependants = list

    ## def highlight(self):
    ##     """Highlight entry box text"""
    ##     debug(u"file_control: highlight - highlighting %s entry box" % self.label)
    ##     if self.relative != None:
    ##         debug(u"file_control: highlight - highlight with relative, %s | %s" % (self.linked(), self.relative()))
    ##         self.ftbox.highlightText(self.path_box, self.linked(), self.relative())
    ##     else:
    ##         debug(u"file_control: highlight - highlight without relative, %s" % self.linked())
    ##         self.ftbox.highlightText(self.path_box, self.linked())
    ##     if self.dependants:
    ##         debug(u"file_control: highlight - highlighting dependants: %s" % (unicode(self.dependants)))
    ##         for i in self.dependants:
    ##             i.highlight()

    def OnSaveTextChange(self, e):
        """Triggered when the text in the save path box is changed"""
        debug("tcui.controlFiles: OnSaveTextChange")
        if self.app.activeproject.save_location() != self.save_path_box.GetValue():
            self.app.activeproject.save_location(self.save_path_box.GetValue())
            debug("tcui.controlFiles: OnSaveTextChange - Text changed in save path entry box, new text: %s" % str(self.save_path_box.GetValue()))
            ## self.highlight()

    def OnDatTextChange(self, e):
        """Triggered when the text in the dat path box is changed"""
        debug("tcui.controlFiles: OnDatTextChange")
        if self.app.activeproject.datfile_location() != self.dat_path_box.GetValue():
            self.app.activeproject.datfile_location(self.dat_path_box.GetValue())
            debug("tcui.controlFiles: OnDatTextChange - Text changed in dat path entry box, new text: %s" % str(self.dat_path_box.GetValue()))
            ## self.highlight()

    def OnPngTextChange(self, e):
        """Triggered when the text in the png path box is changed"""
        debug("tcui.controlFiles: OnPngTextChange")
        if self.app.activeproject.pngfile_location() != self.png_path_box.GetValue():
            self.app.activeproject.pngfile_location(self.png_path_box.GetValue())
            debug("tcui.controlFiles: OnPngTextChange - Text changed in png path entry box, new text: %s" % str(self.png_path_box.GetValue()))
            ## self.highlight()

    def OnPakTextChange(self, e):
        """Triggered when the text in the pak path box is changed"""
        debug("tcui.controlFiles: OnPakTextChange")
        if self.app.activeproject.pakfile_location() != self.pak_path_box.GetValue():
            self.app.activeproject.pakfile_location(self.pak_path_box.GetValue())
            debug("tcui.controlFiles: OnePakTextChange - Text changed in pak path entry box, new text: %s" % str(self.pak_path_box.GetValue()))
            ## self.highlight()

    def OnSaveBrowse(self, e):
        """Triggered when the save browse button is clicked"""
        debug("tcui.controlFiles: OnSaveBrowse")
        value = self.ftbox.filePickerDialog(self.app.activeproject.save_location(), 
                                            "", 
                                            gt("Choose a location to save project..."),
                                            "TCP files (*.tcp)|*.tcp", 
                                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        debug("tcui.controlFiles: OnSaveBrowse - Path selected by user is: %s" % value)
        self.save_path_box.SetValue(value)

    def OnDatBrowse(self, e):
        """Triggered when the dat browse button is clicked"""
        debug("tcui.controlFiles: OnDatBrowse")
        value = self.ftbox.filePickerDialog(self.app.activeproject.datfile_location(), 
                                            self.app.activeproject.save_location(), 
                                            gt("Choose a location to save .dat file..."),
                                            "DAT files (*.dat)|*.dat", 
                                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        debug("tcui.controlFiles: OnDatBrowse - Path selected by user is: %s" % value)
        self.dat_path_box.SetValue(value)

    def OnPngBrowse(self, e):
        """Triggered when the png browse button is clicked"""
        debug("tcui.controlFiles: OnPngBrowse")
        value = self.ftbox.filePickerDialog(self.app.activeproject.pngfile_location(), 
                                            self.app.activeproject.save_location(), 
                                            gt("Choose a location to save .png file..."),
                                            "PNG files (*.png)|*.png", 
                                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        debug("tcui.controlFiles: OnPngBrowse - Path selected by user is: %s" % value)
        self.png_path_box.SetValue(value)

    def OnPakBrowse(self, e):
        """Triggered when the pak browse button is clicked"""
        debug("tcui.controlFiles: OnPakBrowse")
        value = self.ftbox.filePickerDialog(self.app.activeproject.pakfile_location(), 
                                            self.app.activeproject.save_location(), 
                                            gt("Choose a location to export .pak file..."),
                                            "PAK files (*.pak)|*.pak", 
                                            wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        debug("tcui.controlFiles: OnPakBrowse - Path selected by user is: %s" % value)
        self.pak_path_box.SetValue(value)
