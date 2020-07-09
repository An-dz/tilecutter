# TileCutter, User Interface Module
#            About dialog

import logging
import wx, imres
import translator
gt = translator.Translator()


class DialogAbout(wx.Dialog):
    """Dialog which displays information about the program"""
    def __init__(self, parent, app, version_number):
        """Intialise the dialog"""
        logging.info("Creating about dialog")

        self.app = app
        self.version_number = version_number
        self.size = (400, 1)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1, -1), self.size)

        # All items in panel sit inside individual horizontal sizers, which are contained
        # within a vertical one
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Big TileCutter icon
        self.icon = wx.StaticBitmap(self, wx.ID_ANY, imres.tc_icon2_128_plain.GetBitmap())

        # Store default font to reset to later
        f = self.GetFont()

        # Bigger font for title
        self.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.title_text     = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)

        # Medium font for subtitle
        self.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subtitle_text  = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)

        # Original font for version/copyright
        self.SetFont(f)
        self.version_text   = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)
        self.copyright_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)

        # Add all items to horizontal sizers, to get horizontal centering and expansion
        self.sizer.Add((0, 15))
        self.sizer.Add(self.icon,           0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 15))
        self.sizer.Add(self.title_text,     0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,  2))
        self.sizer.Add(self.subtitle_text,  0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,  4))
        self.sizer.Add(self.version_text,   0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 10))
        self.sizer.Add(self.copyright_text, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 15))

        # Bind events
        self.title_text.Bind(wx.EVT_KEY_DOWN, self.OnClose, self.title_text)
        self.title_text.SetFocus()

        # Layout sizers
        self.SetSizer(self.sizer)
        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("Translate UI")

        self.SetLabel(gt("About TileCutter"))
        self.title_text.SetLabel(gt("TileCutter"))
        self.subtitle_text.SetLabel(gt("Simutrans Building Editor"))
        self.version_text.SetLabel(gt("Version %s") % self.version_number)
        self.copyright_text.SetLabel("\nCopyright © 2018-2020 André Zanghelini. All rights reserved.\nCopyright © 2008-2015 Timothy Baldock. All rights reserved.\n\nThis program uses the wxPython library\nCopyright © 1992-2020 Julian Smart, Robert Roebling, Vadim Zeitlin\nand other members of the wxPython team.\n\nTileCutter is written in Python.")

        self.title_text.Wrap(    self.size[0] - 20)
        self.subtitle_text.Wrap( self.size[0] - 20)
        self.version_text.Wrap(  self.size[0] - 20)
        self.copyright_text.Wrap(self.size[0] - 20)

        self.Fit()
        self.SetSize(wx.Size(400, self.GetBestSize().Get()[1]))
        self.CentreOnParent(wx.BOTH)

    def OnClose(self, e):
        """On click of the close button"""
        logging.info("Closing dialog")
        self.EndModal(wx.ID_OK)
