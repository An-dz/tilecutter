# coding: UTF-8
#
# TileCutter, User Interface Module - aboutDialog
#

# Copyright © 2008-2012 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class aboutDialog(wx.Dialog):
    """Dialog which displays information about the program"""
    def __init__(self, parent, app, version_number):
        """Intialise the dialog"""
        debug(u"tcui.AboutDialog: __init__")
        self.app = app
        self.version_number = version_number
        self.size = (400,1)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), self.size)

        # All items in panel sit inside individual horizontal sizers, which are contained
        # within a vertical one
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Big TileCutter icon
        self.icon = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["tc_icon2_128_plain"].getBitmap())
        # Store default font to reset to later
        f = self.GetFont()
        # Bigger font for title
        self.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.title_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)
        # Medium font for subtitle
        self.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subtitle_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)
        # Original font for version/copyright
        self.SetFont(f)
        self.version_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)
        self.copyright_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)

        # Add all items to horizontal sizers, to get horizontal centering and expansion
        self.sizer.Add((0,15))
        self.sizer.Add(self.icon,           0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,15))
        self.sizer.Add(self.title_text,     0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,2))
        self.sizer.Add(self.subtitle_text,  0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,4))
        self.sizer.Add(self.version_text,   0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,10))
        self.sizer.Add(self.copyright_text, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0,15))

        # Bind events
        self.title_text.Bind(wx.EVT_KEY_DOWN, self.OnClose, self.title_text)

        self.title_text.SetFocus()

        # Layout sizers
        self.SetSizer(self.sizer)

        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug(u"tcui.AboutDialog: translate")
        self.SetLabel(gt("About TileCutter"))
        self.title_text.SetLabel(gt("TileCutter"))
        self.subtitle_text.SetLabel(gt("Simutrans Building Editor"))
        self.version_text.SetLabel(gt("Version %s") % self.version_number)
        self.copyright_text.SetLabel(u"\nCopyright \u00A9 2008-2012 Timothy Baldock. All rights reserved.\n\nThis program makes use of the wxWidgets library, which is Copyright \u00A9 1992-2006 Julian Smart, Robert Roebling, Vadim Zeitlin and other members of the wxWidgets team.\n\nTileCutter is written in Python.")
        self.title_text.Wrap(self.size[0]-20)
        self.subtitle_text.Wrap(self.size[0]-20)
        self.version_text.Wrap(self.size[0]-20)
        self.copyright_text.Wrap(self.size[0]-20)

        self.Fit()
        self.SetSize(wx.Size(400, self.GetBestSizeTuple()[1]))
        self.CentreOnParent(wx.BOTH)

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        debug(u"tcui.AboutDialog: update")

    def OnClose(self,e):
        """On click of the close button"""
        debug(u"tcui.AboutDialog: OnClose")
        self.EndModal(wx.ID_OK)
