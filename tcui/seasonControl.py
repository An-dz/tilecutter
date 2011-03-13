# coding: UTF-8
#
# TileCutter User Interface Module - seasonControl
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()

import logger
debug = logger.Log()

class seasonControl(object):
    """Box containing season alteration controls"""
    def __init__(self, parent, app, parent_sizer):
        self.app = app
        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0,2,1,0)
        self.s_seasons_flex.AddGrowableCol(1)
        # Header text
        self.label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        # Add items
        self.seasons_select_summer_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageSummer"].getBitmap())
        self.seasons_select_summer = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.seasons_select_summer.SetValue(True)
        self.seasons_select_winter_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageWinter"].getBitmap())
        self.seasons_select_winter = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.seasons_enable_winter = wx.CheckBox(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        # Add to sizers
        self.s_seasons_flex.Add(self.seasons_select_summer_im, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT|wx.BOTTOM, 2)
        self.s_seasons_flex.Add(self.seasons_select_summer, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.BOTTOM, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter_im, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT|wx.BOTTOM, 2)
        self.s_seasons_flex.Add(self.seasons_select_winter, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.BOTTOM, 2)
#        self.s_seasons_flex.Add(wx.Size(1,1))
#        self.s_seasons_flex.Add(self.seasons_enable_winter, 0, wx.ALIGN_LEFT|wx.RIGHT, 2)
        # Add to default sizer with header and line
        self.sizer.Add(self.label, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(self.s_seasons_flex, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL|wx.BOTTOM, 2)
        self.sizer.Add(self.seasons_enable_winter, 0, wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(wx.StaticLine(parent, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 2)
        # Bind functions
        self.seasons_enable_winter.Bind(wx.EVT_CHECKBOX, self.OnToggle, self.seasons_enable_winter)
        self.seasons_select_summer.Bind(wx.EVT_RADIOBUTTON, self.OnSummer, self.seasons_select_summer)
        self.seasons_select_winter.Bind(wx.EVT_RADIOBUTTON, self.OnWinter, self.seasons_select_winter)

        # Add element to its parent sizer
        parent_sizer.Add(self.sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.label.SetLabel(gt("Season:"))
        self.seasons_select_summer.SetLabel(gt("Summer"))
        self.seasons_select_summer.SetToolTipString(gt("tt_seasons_select_summer"))
        self.seasons_select_winter.SetLabel(gt("Winter"))
        self.seasons_select_winter.SetToolTipString(gt("tt_seasons_select_winter"))
        self.seasons_enable_winter.SetLabel(gt("Enable Winter"))
        self.seasons_enable_winter.SetToolTipString(gt("tt_seasons_enable_winter"))

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        if self.app.activeproject.winter() == 0:  # Turn winter image off
            self.seasons_enable_winter.SetValue(False)
            # If currently have winter image selected, switch to summer image
            if self.seasons_select_winter.GetValue() == True:
                # Update model
                self.app.activeproject.active_image(season = 0)
                self.seasons_select_summer.SetValue(True)
                # As active season changed, need to redraw display
                self.app.frame.display.update()
            # Then disable the control
            self.seasons_select_winter.Disable()
        else:
            self.seasons_enable_winter.SetValue(True)
            # User must select the winter image if they wish to view it, so just enable the control
            self.seasons_select_winter.Enable()

    def OnToggle(self,e):
        """Toggling winter image on and off"""
        self.app.activeproject.winter(self.seasons_enable_winter.GetValue())
        self.update()
    def OnSummer(self,e):
        """Change to Summer image"""
        # Set active image to Summer
        self.app.activeproject.active_image(season = 0)
        # Redraw active image
        self.app.frame.display.update()
    def OnWinter(self,e):
        """Change to Winter image"""
        # Set active image to Winter
        self.app.activeproject.active_image(season = 1)
        # Redraw active image
        self.app.frame.display.update()
