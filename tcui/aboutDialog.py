# coding: UTF-8
#
# TileCutter, User Interface Module - aboutDialog
#
import wx, imres

class aboutDialog(wx.Dialog):
    """Dialog which displays information about the program"""
    def __init__(self, parent, app, version_number):
        """Intialise the dialog"""
        self.app = app
        self.version_number = version_number
        size = (300,300)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "", (-1,-1), size)

        # Overall panel sizer
        self.s_panel = wx.BoxSizer(wx.VERTICAL)
        self.icon = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["tc_icon2_128_plain"].getBitmap())
        f = self.GetFont()
        self.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.title_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.subtitle_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.SetFont(f)
        self.version_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)
        self.copyright_text = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER)

        # Add close button at the bottom
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.ALIGN_RIGHT)
        self.buttons.Add(self.close_button, 0 ,wx.ALIGN_RIGHT, 0)

        self.s_panel.Add(self.icon,1,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM, 10)
        self.s_panel.Add(self.title_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 2)
        self.s_panel.Add(self.subtitle_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 4)
        self.s_panel.Add(self.version_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 4)
        self.s_panel.Add(self.copyright_text,0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 10)
        # These bits are non-mac only
        self.s_panel.Add(wx.StaticLine(self, wx.ID_ANY, (-1,-1), (-1,1)),0,wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.s_panel.Add(self.buttons,0,wx.ALIGN_RIGHT|wx.ALL, 3)

        # Bind events
        self.close_button.Bind(wx.EVT_BUTTON, self.OnClose, self.close_button)

        # Layout sizers
        self.SetSizer(self.s_panel)
        self.SetAutoLayout(1)
##        self.Layout()

        self.translate()

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.SetLabel(self.gt("About TileCutter"))
        self.close_button.SetLabel(self.gt("Close"))
        self.title_text.SetLabel(self.gt("TileCutter"))
        self.subtitle_text.SetLabel(self.gt("Simutrans Building Editor"))
        self.version_text.SetLabel(self.gt("Version %s") % self.version_number)
        self.copyright_text.SetLabel("Copyright © 2008 Timothy Baldock. All rights reserved.")

        self.Layout()
        self.Refresh()
    def gt(self,text):
        return self.app.tctranslator.gt(text)

    def update(self):
        """Set the values of the controls in this group to the values in the model"""

    def OnClose(self,e):
        """On click of the close button"""
        self.EndModal(wx.ID_OK)
