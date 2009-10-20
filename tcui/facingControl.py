# coding: UTF-8
#
# TileCutter User Interface Module - facingControl
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.

import wx, imres

# Utility functions
import translator
gt = translator.Translator()
import config
config = config.Config()

import logger
debug = logger.Log()

class facingControl(object):
    """Box containing direction facing controls"""
    def __init__(self, parent, app, parent_sizer):
        self.app = app
        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_facing = wx.BoxSizer(wx.HORIZONTAL)
        self.s_facing_flex = wx.FlexGridSizer(0,2,1,0)
        self.s_facing_flex.AddGrowableCol(1)
        self.s_facing_right = wx.BoxSizer(wx.VERTICAL)
        self.s_facing_1 = wx.BoxSizer(wx.HORIZONTAL)
        # Header text
        self.label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        # Add items
        self.facing_select_south_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageSouth"].getBitmap())
        self.facing_select_south = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.facing_select_east_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageEast"].getBitmap())
        self.facing_select_east = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_select_north_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageNorth"].getBitmap())
        self.facing_select_north = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_select_west_im = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["ImageWest"].getBitmap())
        self.facing_select_west = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.facing_enable_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_enable_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (54, -1), "", wx.CB_READONLY|wx.ALIGN_CENTER_VERTICAL)
        # Add to sizers
        self.s_facing_flex.Add(self.facing_select_south_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_south, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_east_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_east, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_north_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_north, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)
        self.s_facing_flex.Add(self.facing_select_west_im, 0, wx.ALIGN_LEFT|wx.RIGHT|wx.LEFT, 2)
        self.s_facing_flex.Add(self.facing_select_west, 0, wx.ALIGN_LEFT|wx.RIGHT, 0)

        self.s_facing_right.Add(self.facing_enable_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 0)
        self.s_facing_right.Add(self.facing_enable_select, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.RIGHT, 0)
        self.s_facing_1.Add(self.s_facing_flex, 0, wx.RIGHT, 0)
        self.s_facing_1.Add(self.s_facing_right, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.s_facing.Add(self.s_facing_1, 1, wx.RIGHT|wx.TOP|wx.BOTTOM, 2)
        # Add to default sizer with header and line
        self.sizer.Add(self.label, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(self.s_facing, 1, wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(wx.StaticLine(parent, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 2)
        # Bind events
        self.facing_enable_select.Bind(wx.EVT_COMBOBOX, self.OnToggle, self.facing_enable_select)
        self.facing_select_south.Bind(wx.EVT_RADIOBUTTON, self.OnSouth, self.facing_select_south)
        self.facing_select_east.Bind(wx.EVT_RADIOBUTTON, self.OnEast, self.facing_select_east)
        self.facing_select_north.Bind(wx.EVT_RADIOBUTTON, self.OnNorth, self.facing_select_north)
        self.facing_select_west.Bind(wx.EVT_RADIOBUTTON, self.OnWest, self.facing_select_west)

        # Add element to its parent sizer
        parent_sizer.Add(self.sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.label.SetLabel(gt("Direction Facing:"))
        self.facing_select_south.SetLabel(gt("South"))
        self.facing_select_south.SetToolTipString(gt("tt_facing_select_south"))
        self.facing_select_east.SetLabel(gt("East"))
        self.facing_select_east.SetToolTipString(gt("tt_facing_select_east"))
        self.facing_select_north.SetLabel(gt("North"))
        self.facing_select_north.SetToolTipString(gt("tt_facing_select_north"))
        self.facing_select_west.SetLabel(gt("West"))
        self.facing_select_west.SetToolTipString(gt("tt_facing_select_west"))
        self.facing_enable_label.SetLabel(gt("Number\nof views:"))
        self.facing_enable_select.SetToolTipString(gt("tt_facing_enable_select"))
        # Translate the choicelist values for paksize
        self.choicelist_views = gt.translateIntArray(config.choicelist_views)
        self.facing_enable_select.Clear()
        for i in self.choicelist_views:
            self.facing_enable_select.Append(i)
        # And set value to value in the project
        self.facing_enable_select.SetStringSelection(self.choicelist_views[config.choicelist_views.index(self.app.activeproject.views())])

    def update(self):
        """Set the values of the controls in this group to the values in the model"""
        # Set value of the toggle control (to set number of directions)
        if self.app.activeproject.views() == 1:
            self.facing_enable_select.SetValue(self.choicelist_views[0])
            # Update controls
            self.facing_select_south.Enable()
            self.facing_select_east.Disable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_east.GetValue() == True or self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_south.SetValue(1)
                # Modify active image to only available option
                self.app.activeproject.activeImage(direction = 0)
                # Redraw active image
                self.app.frame.display.update()
        elif self.app.activeproject.views() == 2:
            self.facing_enable_select.SetValue(self.choicelist_views[1])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Disable()
            self.facing_select_west.Disable()
            if self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_east.SetValue(1)
                # Modify active image to available option
                self.app.activeproject.activeImage(direction = 1)
                # Redraw active image
                self.app.frame.display.update()
        else:
            self.facing_enable_select.SetValue(self.choicelist_views[2])
            self.facing_select_south.Enable()
            self.facing_select_east.Enable()
            self.facing_select_north.Enable()
            self.facing_select_west.Enable()
        # Update the combobox
        self.facing_enable_select.SetStringSelection(self.choicelist_views[config.choicelist_views.index(self.app.activeproject.views())])

    def OnToggle(self,e):
        """Changing the value in the selection box"""
        self.app.activeproject.views(config.choicelist_views[self.choicelist_views.index(self.facing_enable_select.GetValue())])
        self.update()
    def OnSouth(self,e):
        """Toggle South direction"""
        # Set active image to South
        self.app.activeproject.activeImage(direction = 0)
        # Redraw active image
        self.app.frame.display.update()
    def OnEast(self,e):
        """Toggle East direction"""
        # Set active image to East
        self.app.activeproject.activeImage(direction = 1)
        # Redraw active image
        self.app.frame.display.update()
    def OnNorth(self,e):
        """Toggle North direction"""
        # Set active image to North
        self.app.activeproject.activeImage(direction = 2)
        # Redraw active image
        self.app.frame.display.update()
    def OnWest(self,e):
        """Toggle West direction"""
        # Set active image to West
        self.app.activeproject.activeImage(direction = 3)
        # Redraw active image
        self.app.frame.display.update()
