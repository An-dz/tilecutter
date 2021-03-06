# TileCutter User Interface Module
#    Image Layer Controls Panel

import logging
import wx, imres
import translator
gt = translator.Translator()


class ControlImage(wx.Panel):
    """Box containing Front/Back image and Transparency controls"""
    def __init__(self, parent, app):
        logging.info("Creating image controls")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.app = app

        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_images_flex = wx.FlexGridSizer(0, 3, 0, 0)
        self.s_images_flex.AddGrowableCol(2)
        # Header text
        self.label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)

        # Add items
        self.images_select_back_im      = wx.StaticBitmap(self, wx.ID_ANY, imres.ImageBack.GetBitmap())
        self.images_select_back         =  wx.RadioButton(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.RB_GROUP)
        self.images_select_back.SetValue(True)
        self.images_select_front_im     = wx.StaticBitmap(self, wx.ID_ANY, imres.ImageFront.GetBitmap())
        self.images_select_front        =  wx.RadioButton(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.images_enable_front        =     wx.CheckBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.images_enable_transparency =     wx.CheckBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1))

        # Add to sizers
        self.s_images_flex.Add(self.images_select_back_im,  0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.s_images_flex.Add((4, 0))
        self.s_images_flex.Add(self.images_select_back,     0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.s_images_flex.Add((0, 2))
        self.s_images_flex.Add((0, 2))
        self.s_images_flex.Add((0, 2))
        self.s_images_flex.Add(self.images_select_front_im, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.s_images_flex.Add((4, 0))
        self.s_images_flex.Add(self.images_select_front,    0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        # Add to default sizer with header and line
        self.sizer.Add((0, 2))
        self.sizer.Add(self.label,                      0, wx.LEFT, 2)
        self.sizer.Add((0, 4))
        self.sizer.Add(self.images_enable_transparency, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 2))
        self.sizer.Add(self.s_images_flex,              0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 6))
        self.sizer.Add(self.images_enable_front,        0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 2))
        # Bind events
        self.images_enable_transparency.Bind( wx.EVT_CHECKBOX,    self.OnTransparency, self.images_enable_transparency)
        self.images_enable_front.Bind(        wx.EVT_CHECKBOX,    self.OnFrontBack,    self.images_enable_front)
        self.images_select_back.Bind(         wx.EVT_RADIOBUTTON, self.OnBackImage,    self.images_select_back)
        self.images_select_front.Bind(        wx.EVT_RADIOBUTTON, self.OnFrontImage,   self.images_select_front)

        # Set panel's sizer
        self.SetSizer(self.sizer)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("Translate UI")

        self.label.SetLabel(gt("Image:"))
        self.images_select_back.SetLabel(gt("BackImage"))
        self.images_select_back.SetToolTip(gt("tt_images_select_back"))
        self.images_select_front.SetLabel(gt("FrontImage"))
        self.images_select_front.SetToolTip(gt("tt_images_select_front"))
        self.images_enable_front.SetLabel(gt("Enable FrontImage"))
        self.images_enable_front.SetToolTip(gt("tt_images_enable_front"))
        self.images_enable_transparency.SetLabel(gt("Transparency"))
        self.images_enable_transparency.SetToolTip(gt("tt_images_enable_transparency"))

        self.Fit()

    def update(self):
        """Set the values of the controls in this group to the values in the project"""
        logging.info("Update controls")

        self.images_enable_transparency.SetValue(self.app.activeproject.transparency())

        # Turn frontimage off
        if self.app.activeproject.frontimage() == 0:
            self.images_enable_front.SetValue(0)

            # If currently have frontimage selected, switch to backimage
            if self.images_select_front.GetValue() is True:
                # Update model
                self.app.activeproject.active_image(layer=0)
                self.images_select_back.SetValue(1)
                # As active layer changed, need to redraw display
                self.app.frame.display.update()

            # Then disable the control
            self.images_select_front.Disable()
        else:
            self.images_enable_front.SetValue(1)
            # User must select the frontimage if they wish to view it, so just enable the control
            self.images_select_front.Enable()

    def OnTransparency(self, e):
        """Toggling transparency on and off"""
        logging.info("Transparency changed")
        self.app.activeproject.transparency(self.images_enable_transparency.GetValue())
        self.update()

    def OnFrontBack(self, e):
        """Toggling frontimage on and off"""
        logging.info("FrontImage/BackImage changed")
        self.app.activeproject.frontimage(self.images_enable_front.GetValue())
        self.update()

    def OnBackImage(self, e):
        """Called when user wishes to display back image"""
        logging.info("Display BackImage")
        # Set active image to Back
        self.app.activeproject.active_image(layer=0)
        # Redraw active image
        self.app.frame.display.update()

    def OnFrontImage(self, e):
        """Called when user wishes to display front image"""
        logging.info("Display FrontImage")
        # Set active image to Front
        self.app.activeproject.active_image(layer=1)
        # Redraw active image
        self.app.frame.display.update()
