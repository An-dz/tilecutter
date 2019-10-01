# TileCutter User Interface Module
#      Image Offset Controls

import logging
import wx, imres
import translator
gt = translator.Translator()

class controlOffset(wx.Panel):
    """Box containing image offset controls"""
    def __init__(self, parent, app):
        logging.info("tcui.controlOffset: __init__")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.app = app

        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_offset_flex = wx.FlexGridSizer(0, 3, 2, 2)
        # Header text
        self.label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)

        # Add items
        self.offset_button_up         = wx.BitmapButton(self, wx.ID_ANY, imres.MoveUpDouble.GetBitmap(),           (-1, -1), (-1, -1))
        self.offset_button_left       = wx.BitmapButton(self, wx.ID_ANY, imres.MoveLeftDouble.GetBitmap(),         (-1, -1), (-1, -1))
        self.offset_button_reset      = wx.BitmapButton(self, wx.ID_ANY, imres.MoveCenter.GetBitmap(),             (-1, -1), (-1, -1))
        self.offset_button_right      = wx.BitmapButton(self, wx.ID_ANY, imres.MoveRightDouble.GetBitmap(),        (-1, -1), (-1, -1))
        self.offset_button_down       = wx.BitmapButton(self, wx.ID_ANY, imres.MoveDownDouble.GetBitmap(),         (-1, -1), (-1, -1))
        self.offset_button_up_left    = wx.BitmapButton(self, wx.ID_ANY, imres.MoveUpAndLeftDouble.GetBitmap(),    (-1, -1), (-1, -1))
        self.offset_button_up_right   = wx.BitmapButton(self, wx.ID_ANY, imres.MoveUpAndRightDouble.GetBitmap(),   (-1, -1), (-1, -1))
        self.offset_button_down_left  = wx.BitmapButton(self, wx.ID_ANY, imres.MoveDownAndLeftDouble.GetBitmap(),  (-1, -1), (-1, -1))
        self.offset_button_down_right = wx.BitmapButton(self, wx.ID_ANY, imres.MoveDownAndRightDouble.GetBitmap(), (-1, -1), (-1, -1))
        self.offset_selector = wx.CheckBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1))

        # Add to sizers
        self.s_offset_flex.Add(self.offset_button_up_left,    0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_up,         0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_up_right,   0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_left,       0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_reset,      0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_right,      0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_down_left,  0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_down,       0, wx.LEFT, 0)
        self.s_offset_flex.Add(self.offset_button_down_right, 0, wx.LEFT, 0)

        # Add to default sizer with header and line
        self.sizer.Add((0, 2))
        self.sizer.Add(self.label,           0, wx.LEFT, 2)
        self.sizer.Add((0, 4))
        self.sizer.Add(self.s_offset_flex,   1, wx.ALIGN_CENTER_HORIZONTAL)

        # Add fine button to vertical sizer
        self.sizer.Add((0, 7))
        self.sizer.Add(self.offset_selector, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 4))

        # Set panel's sizer
        self.SetSizer(self.sizer)

        # Bind functions
        self.offset_button_up.Bind(         wx.EVT_BUTTON,   self.OnUp,        self.offset_button_up)
        self.offset_button_left.Bind(       wx.EVT_BUTTON,   self.OnLeft,      self.offset_button_left)
        self.offset_button_reset.Bind(      wx.EVT_BUTTON,   self.OnCenter,    self.offset_button_reset)
        self.offset_button_right.Bind(      wx.EVT_BUTTON,   self.OnRight,     self.offset_button_right)
        self.offset_button_down.Bind(       wx.EVT_BUTTON,   self.OnDown,      self.offset_button_down)
        self.offset_button_up_left.Bind(    wx.EVT_BUTTON,   self.OnUpLeft,    self.offset_button_up_left)
        self.offset_button_up_right.Bind(   wx.EVT_BUTTON,   self.OnUpRight,   self.offset_button_up_right)
        self.offset_button_down_left.Bind(  wx.EVT_BUTTON,   self.OnDownLeft,  self.offset_button_down_left)
        self.offset_button_down_right.Bind( wx.EVT_BUTTON,   self.OnDownRight, self.offset_button_down_right)
        self.offset_selector.Bind(          wx.EVT_CHECKBOX, self.OnFine,      self.offset_selector)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("tcui.controlOffset: translate")

        self.label.SetLabel(gt("Mask Offset:"))
        self.offset_button_up.SetToolTip(gt("tt_offset_button_up"))
        self.offset_button_left.SetToolTip(gt("tt_offset_button_left"))
        self.offset_button_reset.SetToolTip(gt("offset_button_reset"))
        self.offset_button_right.SetToolTip(gt("tt_offset_button_right"))
        self.offset_button_down.SetToolTip(gt("tt_offset_button_down"))
        self.offset_selector.SetLabel(gt("Fine"))
        self.offset_selector.SetToolTip(gt("tt_offset_selector"))

        self.Fit()

    def update(self):
        """Set the values of the controls in this group to the values in the project"""
        logging.info("tcui.controlOffset: update")
        # Offset control doesn't have any controls which are determined by the project, "fine" checkbox always off by default

    def OnFine(self, e):
        """On toggle of the "fine" checkbox, change images on the buttons"""
        logging.info("tcui.controlOffset: OnFine")

        if self.offset_selector.GetValue():
            self.offset_button_up.SetBitmapLabel(imres.MoveUp.GetBitmap())
            self.offset_button_left.SetBitmapLabel(imres.MoveLeft.GetBitmap())
            self.offset_button_right.SetBitmapLabel(imres.MoveRight.GetBitmap())
            self.offset_button_down.SetBitmapLabel(imres.MoveDown.GetBitmap())
            self.offset_button_up_left.SetBitmapLabel(imres.MoveUpAndLeft.GetBitmap())
            self.offset_button_up_right.SetBitmapLabel(imres.MoveUpAndRight.GetBitmap())
            self.offset_button_down_left.SetBitmapLabel(imres.MoveDownAndLeft.GetBitmap())
            self.offset_button_down_right.SetBitmapLabel(imres.MoveDownAndRight.GetBitmap())
        else:
            self.offset_button_up.SetBitmapLabel(imres.MoveUpDouble.GetBitmap())
            self.offset_button_left.SetBitmapLabel(imres.MoveLeftDouble.GetBitmap())
            self.offset_button_right.SetBitmapLabel(imres.MoveRightDouble.GetBitmap())
            self.offset_button_down.SetBitmapLabel(imres.MoveDownDouble.GetBitmap())
            self.offset_button_up_left.SetBitmapLabel(imres.MoveUpAndLeftDouble.GetBitmap())
            self.offset_button_up_right.SetBitmapLabel(imres.MoveUpAndRightDouble.GetBitmap())
            self.offset_button_down_left.SetBitmapLabel(imres.MoveDownAndLeftDouble.GetBitmap())
            self.offset_button_down_right.SetBitmapLabel(imres.MoveDownAndRightDouble.GetBitmap())

    def OnUpLeft(self, e):
        """Move mask up and left"""
        logging.debug("tcui.controlOffset: OnUpLeft")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_offset([max(0, self.app.activeproject.active_x_offset() - 2), 
                                                  self.app.activeproject.active_y_offset() + 1])
        else:
            self.app.activeproject.active_offset([max(0, self.app.activeproject.active_x_offset() - self.app.activeproject.paksize() / 2), 
                                                  self.app.activeproject.active_y_offset() + self.app.activeproject.paksize() / 4])

    def OnUpRight(self, e):
        """Move mask up and right"""
        logging.debug("tcui.controlOffset: OnUpRight")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_offset([self.app.activeproject.active_x_offset() + 2, 
                                                  self.app.activeproject.active_y_offset() + 1])
        else:
            self.app.activeproject.active_offset([self.app.activeproject.active_x_offset() + self.app.activeproject.paksize() / 2, 
                                                  self.app.activeproject.active_y_offset() + self.app.activeproject.paksize() / 4])

    def OnDownLeft(self, e):
        """Move mask down and left"""
        logging.debug("tcui.controlOffset: OnDownLeft")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_offset([max(0, self.app.activeproject.active_x_offset() - 2), 
                                                  max(0, self.app.activeproject.active_y_offset() - 1)])
        else:
            self.app.activeproject.active_offset([max(0, self.app.activeproject.active_x_offset() - self.app.activeproject.paksize() / 2), 
                                                  max(0, self.app.activeproject.active_y_offset() - self.app.activeproject.paksize() / 4)])

    def OnDownRight(self, e):
        """Move mask down and right"""
        logging.debug("tcui.controlOffset: OnDownRight")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_offset([self.app.activeproject.active_x_offset() + 2, 
                                                  max(0, self.app.activeproject.active_y_offset() - 1)])
        else:
            self.app.activeproject.active_offset([self.app.activeproject.active_x_offset() + self.app.activeproject.paksize() / 2, 
                                                  max(0, self.app.activeproject.active_y_offset() - self.app.activeproject.paksize() / 4)])

    def OnUp(self, e):
        """Move mask up"""
        logging.debug("tcui.controlOffset: OnUp")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_y_offset(self.app.activeproject.active_y_offset() + 1)
        else:
            self.app.activeproject.active_y_offset(self.app.activeproject.active_y_offset() + self.app.activeproject.paksize())

    def OnLeft(self, e):
        """Move mask left"""
        logging.debug("tcui.controlOffset: OnLeft")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_x_offset(max(0, self.app.activeproject.active_x_offset() - 1))
        else:
            self.app.activeproject.active_x_offset(max(0, self.app.activeproject.active_x_offset() - self.app.activeproject.paksize()))

    def OnCenter(self, e):
        """Reset mask position"""
        logging.debug("tcui.controlOffset: OnCenter")
        self.app.activeproject.active_offset([0, 0])

    def OnRight(self, e):
        """Move mask right"""
        logging.debug("tcui.controlOffset: OnRight")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_x_offset(self.app.activeproject.active_x_offset() + 1)
        else:
            self.app.activeproject.active_x_offset(self.app.activeproject.active_x_offset() + self.app.activeproject.paksize())

    def OnDown(self, e):
        """Move mask down"""
        logging.debug("tcui.controlOffset: OnDown")
        if self.offset_selector.GetValue():
            self.app.activeproject.active_y_offset(max(0, self.app.activeproject.active_y_offset() - 1))
        else:
            self.app.activeproject.active_y_offset(max(0, self.app.activeproject.active_y_offset() - self.app.activeproject.paksize()))
