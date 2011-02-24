# coding: UTF-8
#
# TileCutter User Interface Module - facingControl
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.

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
        self.s_facing_flex = wx.FlexGridSizer(0,3,0,0)
        self.s_facing_flex.AddGrowableCol(0)
        self.s_facing_flex.AddGrowableCol(2)

        # Header text
        self.label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        # Components which make up the tile graphic
        self.facing_tile_left = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["tilegraphic_left"].getBitmap())
        self.facing_tile_right = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["tilegraphic_right"].getBitmap())
        self.facing_tile_middle = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["tilegraphic_middle"].getBitmap())
        self.facing_tile_bottom = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["tilegraphic_bottom"].getBitmap())
        self.facing_tile_top = wx.StaticBitmap(parent, wx.ID_ANY, imres.catalog["tilegraphic_top"].getBitmap())

        # Add items
        self.s_facing_select_south = wx.BoxSizer(wx.HORIZONTAL)
        self.facing_select_south_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        self.facing_select_south = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1), wx.RB_GROUP)
        self.s_facing_select_south.Add(self.facing_select_south_label, 0)
        self.s_facing_select_south.Add(self.facing_select_south, 0)

        self.s_facing_select_east = wx.BoxSizer(wx.HORIZONTAL)
        self.facing_select_east_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_select_east = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.s_facing_select_east.Add(self.facing_select_east, 0)
        self.s_facing_select_east.Add(self.facing_select_east_label, 0)

        self.s_facing_select_north = wx.BoxSizer(wx.HORIZONTAL)
        self.facing_select_north_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)
        self.facing_select_north = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.s_facing_select_north.Add(self.facing_select_north, 0)
        self.s_facing_select_north.Add(self.facing_select_north_label, 0)

        self.s_facing_select_west = wx.BoxSizer(wx.HORIZONTAL)
        self.facing_select_west_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_RIGHT)
        self.facing_select_west = wx.RadioButton(parent, wx.ID_ANY, "", (-1,-1), (-1,-1))
        self.s_facing_select_west.Add(self.facing_select_west_label, 0)
        self.s_facing_select_west.Add(self.facing_select_west, 0)

        self.facing_enable_label = wx.StaticText(parent, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_CENTER_HORIZONTAL)
        self.facing_enable_select = wx.ComboBox(parent, wx.ID_ANY, "", (-1, -1), (70, -1), "", wx.CB_READONLY)

        # Add to sizers
        self.s_facing_flex.Add(self.s_facing_select_west, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        self.s_facing_flex.Add(self.facing_tile_top, 0, wx.ALIGN_BOTTOM)
        self.s_facing_flex.Add(self.s_facing_select_north, 0, wx.ALIGN_LEFT|wx.ALIGN_BOTTOM)
        self.s_facing_flex.Add(self.facing_tile_left, 0, wx.ALIGN_RIGHT)
        self.s_facing_flex.Add(self.facing_tile_middle, 0, wx.ALIGN_CENTER)
        self.s_facing_flex.Add(self.facing_tile_right, 0, wx.ALIGN_LEFT)
        self.s_facing_flex.Add(self.s_facing_select_south, 0, wx.ALIGN_RIGHT|wx.ALIGN_TOP)
        self.s_facing_flex.Add(self.facing_tile_bottom, 0, wx.ALIGN_TOP)
        self.s_facing_flex.Add(self.s_facing_select_east, 0, wx.ALIGN_LEFT|wx.ALIGN_TOP)

        # Add to default sizer with header and line
        # Adding to vertical sizer, so expand to use all horizontal space
        self.sizer.Add(self.label, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 2)
        self.sizer.Add(self.s_facing_flex, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 2)
        self.sizer.Add(self.facing_enable_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add(self.facing_enable_select, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add(wx.StaticLine(parent, wx.ID_ANY, (-1,-1),(-1,-1), wx.LI_HORIZONTAL), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 2)
        # Bind events
        self.facing_enable_select.Bind(wx.EVT_COMBOBOX, self.OnToggle, self.facing_enable_select)
        self.facing_select_south.Bind(wx.EVT_RADIOBUTTON, self.OnSouth, self.facing_select_south)
        self.facing_select_south_label.Bind(wx.EVT_LEFT_DOWN, self.OnSouth, self.facing_select_south_label)
        self.facing_select_east.Bind(wx.EVT_RADIOBUTTON, self.OnEast, self.facing_select_east)
        self.facing_select_east_label.Bind(wx.EVT_LEFT_DOWN, self.OnEast, self.facing_select_east_label)
        self.facing_select_north.Bind(wx.EVT_RADIOBUTTON, self.OnNorth, self.facing_select_north)
        self.facing_select_north_label.Bind(wx.EVT_LEFT_DOWN, self.OnNorth, self.facing_select_north_label)
        self.facing_select_west.Bind(wx.EVT_RADIOBUTTON, self.OnWest, self.facing_select_west)
        self.facing_select_west_label.Bind(wx.EVT_LEFT_DOWN, self.OnWest, self.facing_select_west_label)

        # Add element to its parent sizer
        # Adding elements to vertical sizer, so Expand to take up all horizontal space
        parent_sizer.Add(self.sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 3)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        self.label.SetLabel(gt("Direction Facing:"))
        self.facing_select_south_label.SetLabel(gt("South"))
        self.facing_select_south.SetToolTipString(gt("tt_facing_select_south"))
        self.facing_select_east_label.SetLabel(gt("East"))
        self.facing_select_east.SetToolTipString(gt("tt_facing_select_east"))
        self.facing_select_north_label.SetLabel(gt("North"))
        self.facing_select_north.SetToolTipString(gt("tt_facing_select_north"))
        self.facing_select_west_label.SetLabel(gt("West"))
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
            debug(u"self.app.activeproject.views = 1")
            self.facing_enable_select.SetValue(self.choicelist_views[0])
            # Update controls
            self.facing_select_south.Enable()
            self.facing_select_south_label.Enable()
            self.facing_select_east.Disable()
            self.facing_select_east_label.Disable()
            self.facing_select_north.Disable()
            self.facing_select_north_label.Disable()
            self.facing_select_west.Disable()
            self.facing_select_west_label.Disable()
            if self.facing_select_east.GetValue() == True or self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_south.SetValue(1)
                # Modify active image to only available option
                self.app.activeproject.activeImage(direction = 0)
                # Redraw active image
                self.app.frame.display.update()
        elif self.app.activeproject.views() == 2:
            debug(u"self.app.activeproject.views = 2")
            self.facing_enable_select.SetValue(self.choicelist_views[1])
            self.facing_select_south.Enable()
            self.facing_select_south_label.Enable()
            self.facing_select_east.Enable()
            self.facing_select_east_label.Enable()
            self.facing_select_north.Disable()
            self.facing_select_north_label.Disable()
            self.facing_select_west.Disable()
            self.facing_select_west_label.Disable()
            if self.facing_select_north.GetValue() == True or self.facing_select_west.GetValue() == True:
                self.facing_select_east.SetValue(1)
                # Modify active image to available option
                self.app.activeproject.activeImage(direction = 1)
                # Redraw active image
                self.app.frame.display.update()
        else:
            debug(u"self.app.activeproject.views = 4")
            self.facing_enable_select.SetValue(self.choicelist_views[2])
            self.facing_select_south.Enable()
            self.facing_select_south_label.Enable()
            self.facing_select_east.Enable()
            self.facing_select_east_label.Enable()
            self.facing_select_north.Enable()
            self.facing_select_north_label.Enable()
            self.facing_select_west.Enable()
            self.facing_select_west_label.Enable()
        # Update the combobox
        self.facing_enable_select.SetStringSelection(self.choicelist_views[config.choicelist_views.index(self.app.activeproject.views())])

    def OnToggle(self, e):
        """Changing the value in the selection box"""
        debug(u"facing_control: OnToggle - Updating model")
        self.app.activeproject.views(config.choicelist_views[self.choicelist_views.index(self.facing_enable_select.GetValue())])
        debug(u"facing_control: OnToggle - Updating self")
        self.update()

    def OnSouth(self, e):
        """Toggle South direction"""
        # If called from the label, ensure radio button is selected
        self.facing_select_south.SetValue(True)
        # Set active image to South
        self.app.activeproject.activeImage(direction = 0)
        # Redraw active image
        self.app.frame.display.update()
    def OnEast(self, e):
        """Toggle East direction"""
        # If called from the label, ensure radio button is selected
        self.facing_select_east.SetValue(True)
        # Set active image to East
        self.app.activeproject.activeImage(direction = 1)
        # Redraw active image
        self.app.frame.display.update()
    def OnNorth(self, e):
        """Toggle North direction"""
        # If called from the label, ensure radio button is selected
        self.facing_select_north.SetValue(True)
        # Set active image to North
        self.app.activeproject.activeImage(direction = 2)
        # Redraw active image
        self.app.frame.display.update()
    def OnWest(self, e):
        """Toggle West direction"""
        # If called from the label, ensure radio button is selected
        self.facing_select_west.SetValue(True)
        # Set active image to West
        self.app.activeproject.activeImage(direction = 3)
        # Redraw active image
        self.app.frame.display.update()
