# coding: UTF-8
#
# TileCutter, User Interface Module - offsetControl
#
import wx, imres

# Utility functions
from translator import gt as gt
from debug import DebugFrame as debug

class offsetControl(wx.StaticBox):
    """Box containing offset controls"""
    def __init__(self, parent, app, parent_sizer):
        self.app = app
        wx.StaticBox.__init__(self, parent, wx.ID_ANY, gt("Offset/Mask"))
            # Setup sizers
        self.s_offset = wx.StaticBoxSizer(self, wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0,4,0,0)
            # Add items
        self.offset_button_up = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveUpDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_left = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveLeftDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_reset = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveCenter"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_right = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveRightDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_button_down = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveDownDouble"].getBitmap(), (-1,-1), (18,18))
        self.offset_selector = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
            # Add to sizers
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_button_up, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_selector, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
        self.s_offset_flex.Add(self.offset_button_left, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_reset, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_right, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_button_down, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset.Add(self.s_offset_flex, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
            # Add element to its parent sizer
        parent_sizer.Add(self.s_offset, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
            # Bind functions
        self.offset_button_up.Bind(wx.EVT_BUTTON, self.OnUp, self.offset_button_up)
        self.offset_button_left.Bind(wx.EVT_BUTTON, self.OnLeft, self.offset_button_left)
        self.offset_button_reset.Bind(wx.EVT_BUTTON, self.OnCenter, self.offset_button_reset)
        self.offset_button_right.Bind(wx.EVT_BUTTON, self.OnRight, self.offset_button_right)
        self.offset_button_down.Bind(wx.EVT_BUTTON, self.OnDown, self.offset_button_down)
        self.offset_selector.Bind(wx.EVT_CHECKBOX, self.OnFine, self.offset_selector)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.offset_button_up.SetToolTipString(gt("tt_offset_button_up"))
        self.offset_button_left.SetToolTipString(gt("tt_offset_button_left"))
        self.offset_button_reset.SetToolTipString(gt("offset_button_reset"))
        self.offset_button_right.SetToolTipString(gt("tt_offset_button_right"))
        self.offset_button_down.SetToolTipString(gt("tt_offset_button_down"))
        self.offset_selector.SetLabel(gt("Fine"))
        self.offset_selector.SetToolTipString(gt("tt_offset_selector"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Offset control doesn't have any controls which are determined by the model, "fine" checkbox always off by default

    def OnFine(self,e):
        """On toggle of the "fine" checkbox, change images on the buttons"""
        if self.offset_selector.GetValue():
            self.offset_button_up.SetBitmapLabel(imres.catalog["MoveUp"].getBitmap())
            self.offset_button_left.SetBitmapLabel(imres.catalog["MoveLeft"].getBitmap())
            self.offset_button_right.SetBitmapLabel(imres.catalog["MoveRight"].getBitmap())
            self.offset_button_down.SetBitmapLabel(imres.catalog["MoveDown"].getBitmap())
        else:
            self.offset_button_up.SetBitmapLabel(imres.catalog["MoveUpDouble"].getBitmap())
            self.offset_button_left.SetBitmapLabel(imres.catalog["MoveLeftDouble"].getBitmap())
            self.offset_button_right.SetBitmapLabel(imres.catalog["MoveRightDouble"].getBitmap())
            self.offset_button_down.SetBitmapLabel(imres.catalog["MoveDownDouble"].getBitmap())

    def OnUp(self,e):
        """Move mask up"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(y=1)
        else:
            r = self.app.activeproject.offset(y=self.app.activeproject.paksize())
        if r == 1:
            self.app.frame.display.update()
    def OnLeft(self,e):
        """Move mask left"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=-1)
        else:
            r = self.app.activeproject.offset(x=-self.app.activeproject.paksize())
        if r == 1:
            self.app.frame.display.update()
    def OnCenter(self,e):
        """Reset mask position"""
        r = self.app.activeproject.offset(x=0, y=0)
        if r == 1:
            self.app.frame.display.update()
    def OnRight(self,e):
        """Move mask right"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=1)
        else:
            r = self.app.activeproject.offset(x=self.app.activeproject.paksize())
        if r == 1:
            self.app.frame.display.update()
    def OnDown(self,e):
        """Move mask down"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(y=-1)
        else:
            r = self.app.activeproject.offset(y=-self.app.activeproject.paksize())
        if r == 1:
            self.app.frame.display.update()
