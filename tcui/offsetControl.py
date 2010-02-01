# coding: UTF-8
#
# TileCutter User Interface Module - offsetControl
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class offsetControl(wx.StaticBox):
    """Box containing offset controls"""
    def __init__(self, parent, app, parent_sizer):
        self.app = app
        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0,4,2,2)
        # Header text
        self.label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        # Add items
        self.offset_button_up = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveUpDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_left = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveLeftDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_reset = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveCenter"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_right = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveRightDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_down = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveDownDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_up_left = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveUpAndLeftDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_up_right = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveUpAndRightDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_down_left = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveDownAndLeftDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_button_down_right = wx.BitmapButton(parent, wx.ID_ANY, imres.catalog["MoveDownAndRightDouble"].getBitmap(), (-1,-1), (-1,-1))
        self.offset_selector = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        # Add to sizers
        self.s_offset_flex.Add(self.offset_button_up_left, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_up, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_up_right, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(wx.Size(1,1))
        self.s_offset_flex.Add(self.offset_button_left, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_reset, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_right, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_selector, 0, wx.ALIGN_LEFT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.s_offset_flex.Add(self.offset_button_down_left, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_down, 0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_down_right, 0, wx.LEFT, 0)
        # Add to default sizer with header and line
        self.sizer.Add(self.label, 0, wx.LEFT|wx.BOTTOM|wx.TOP, 2)
        self.sizer.Add(self.s_offset_flex, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(wx.StaticLine(parent, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 2)
        # Add element to its parent sizer
        parent_sizer.Add(self.sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND|wx.LEFT|wx.RIGHT, 3)
        # Bind functions
        self.offset_button_up.Bind(wx.EVT_BUTTON, self.OnUp, self.offset_button_up)
        self.offset_button_left.Bind(wx.EVT_BUTTON, self.OnLeft, self.offset_button_left)
        self.offset_button_reset.Bind(wx.EVT_BUTTON, self.OnCenter, self.offset_button_reset)
        self.offset_button_right.Bind(wx.EVT_BUTTON, self.OnRight, self.offset_button_right)
        self.offset_button_down.Bind(wx.EVT_BUTTON, self.OnDown, self.offset_button_down)
        self.offset_button_up_left.Bind(wx.EVT_BUTTON, self.OnUpLeft, self.offset_button_up_left)
        self.offset_button_up_right.Bind(wx.EVT_BUTTON, self.OnUpRight, self.offset_button_up_right)
        self.offset_button_down_left.Bind(wx.EVT_BUTTON, self.OnDownLeft, self.offset_button_down_left)
        self.offset_button_down_right.Bind(wx.EVT_BUTTON, self.OnDownRight, self.offset_button_down_right)
        self.offset_selector.Bind(wx.EVT_CHECKBOX, self.OnFine, self.offset_selector)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.label.SetLabel(gt("Mask Offset:"))
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
            self.offset_button_up_left.SetBitmapLabel(imres.catalog["MoveUpAndLeft"].getBitmap())
            self.offset_button_up_right.SetBitmapLabel(imres.catalog["MoveUpAndRight"].getBitmap())
            self.offset_button_down_left.SetBitmapLabel(imres.catalog["MoveDownAndLeft"].getBitmap())
            self.offset_button_down_right.SetBitmapLabel(imres.catalog["MoveDownAndRight"].getBitmap())
        else:
            self.offset_button_up.SetBitmapLabel(imres.catalog["MoveUpDouble"].getBitmap())
            self.offset_button_left.SetBitmapLabel(imres.catalog["MoveLeftDouble"].getBitmap())
            self.offset_button_right.SetBitmapLabel(imres.catalog["MoveRightDouble"].getBitmap())
            self.offset_button_down.SetBitmapLabel(imres.catalog["MoveDownDouble"].getBitmap())
            self.offset_button_up_left.SetBitmapLabel(imres.catalog["MoveUpAndLeftDouble"].getBitmap())
            self.offset_button_up_right.SetBitmapLabel(imres.catalog["MoveUpAndRightDouble"].getBitmap())
            self.offset_button_down_left.SetBitmapLabel(imres.catalog["MoveDownAndLeftDouble"].getBitmap())
            self.offset_button_down_right.SetBitmapLabel(imres.catalog["MoveDownAndRightDouble"].getBitmap())

    def OnUpLeft(self,e):
        """Move mask up and left"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=-2,y=1)
        else:
            r = self.app.activeproject.offset(x=-self.app.activeproject.paksize()/2,
                                              y=self.app.activeproject.paksize()/4)
        if r == 1:
            self.app.frame.display.update()
    def OnUpRight(self,e):
        """Move mask up and right"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=2,y=1)
        else:
            r = self.app.activeproject.offset(x=self.app.activeproject.paksize()/2,
                                              y=self.app.activeproject.paksize()/4)
        if r == 1:
            self.app.frame.display.update()
    def OnDownLeft(self,e):
        """Move mask down and left"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=-2,y=-1)
        else:
            r = self.app.activeproject.offset(x=-self.app.activeproject.paksize()/2,
                                              y=-self.app.activeproject.paksize()/4)
        if r == 1:
            self.app.frame.display.update()
    def OnDownRight(self,e):
        """Move mask down and right"""
        if self.offset_selector.GetValue():
            r = self.app.activeproject.offset(x=2,y=-1)
        else:
            r = self.app.activeproject.offset(x=self.app.activeproject.paksize()/2,
                                              y=-self.app.activeproject.paksize()/4)
        if r == 1:
            self.app.frame.display.update()
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
