# coding: UTF-8
#
# TileCutter, User Interface Module - aboutDialog
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

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
        self.app = app
        self.version_number = version_number
        self.size = (400,1)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), self.size)

        # All items in panel sit inside individual horizontal sizers, which are contained
        # within a vertical one
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)

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

        # Add close button at the bottom
        self.close_button = wx.Button(self, wx.ID_OK, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)

        # Add all items to horizontal sizers, to get horizontal centering and expansion
        self.hbox1.Add(self.icon,           0, wx.TOP|wx.BOTTOM, 15)
        self.hbox2.Add(self.title_text,     0, wx.BOTTOM, 2)
        self.hbox3.Add(self.subtitle_text,  0, wx.BOTTOM, 4)
        self.hbox4.Add(self.version_text,   0, wx.BOTTOM, 10)
        self.hbox5.Add(self.copyright_text, 0, wx.BOTTOM|wx.RIGHT|wx.LEFT, 10)
        self.hbox6.Add(self.close_button,   1, wx.ALIGN_RIGHT, 0)

        # Add horizontal sizers to the vertical one (along with a static line)
        self.vbox.Add(self.hbox1, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.hbox2, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.hbox3, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.hbox4, 0, wx.ALIGN_CENTER)
        self.vbox.Add(self.hbox5, 1, wx.BOTTOM, 10)
        self.vbox.Add(wx.StaticLine(self, wx.ID_ANY, (-1,-1), (-1,1)), 0, wx.EXPAND|wx.ALL, 3)
        self.vbox.Add(self.hbox6, 0, wx.ALIGN_RIGHT|wx.ALL, 3)

        # Bind events
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        # Layout sizers
        self.SetSizer(self.vbox)

        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(gt("About TileCutter"))
        self.close_button.SetLabel(gt("Close"))
        self.title_text.SetLabel(gt("TileCutter"))
        self.subtitle_text.SetLabel(gt("Simutrans Building Editor"))
        self.version_text.SetLabel(gt("Version %s") % self.version_number)
        self.copyright_text.SetLabel(u"\nCopyright \u00A9 2008-2009 Timothy Baldock. All rights reserved.\n\nThis program makes use of the wxWidgets library, which is Copyright \u00A9 1992-2006 Julian Smart, Robert Roebling, Vadim Zeitlin and other members of the wxWidgets team\n\nTileCutter is written in Python")
        self.title_text.Wrap(self.size[0])
        self.subtitle_text.Wrap(self.size[0])
        self.version_text.Wrap(self.size[0])
        self.copyright_text.Wrap(self.size[0])

        self.Layout()
        self.Fit()
        self.Refresh()
        self.CentreOnParent(wx.BOTH)

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnClose(self,e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)
