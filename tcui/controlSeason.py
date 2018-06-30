# coding: UTF-8
#
# TileCutter User Interface Module
#      Season Images Control

import wx, imres

# imports from tilecutter
import translator
gt = translator.Translator()
import logger
debug = logger.Log()

class controlSeason(wx.Panel):
    """Box containing season image controls"""
    def __init__(self, parent, app):
        debug("tcui.controlSeason: __init__")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.app = app

        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0, 3, 0, 0)
        self.s_seasons_flex.AddGrowableCol(2)
        # Header text
        self.label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)

        # Add items
        self.seasons_select_summer_im = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["ImageSummer"].getBitmap())
        self.seasons_select_summer    =  wx.RadioButton(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.RB_GROUP)
        self.seasons_select_summer.SetValue(True)
        self.seasons_select_winter_im = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["ImageWinter"].getBitmap())
        self.seasons_select_winter    =  wx.RadioButton(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
        self.seasons_enable_winter    =     wx.CheckBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1))

        # Add to sizers
        self.s_seasons_flex.Add(self.seasons_select_summer_im, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.s_seasons_flex.Add((4, 0))
        self.s_seasons_flex.Add(self.seasons_select_summer,    0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.s_seasons_flex.Add((0, 2))
        self.s_seasons_flex.Add((0, 2))
        self.s_seasons_flex.Add((0, 2))
        self.s_seasons_flex.Add(self.seasons_select_winter_im, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
        self.s_seasons_flex.Add((4, 0))
        self.s_seasons_flex.Add(self.seasons_select_winter,    0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        # Add to default sizer with header and line
        self.sizer.Add((0, 2))
        self.sizer.Add(self.label,                 0, wx.LEFT, 2)
        self.sizer.Add((0, 4))
        self.sizer.Add(self.s_seasons_flex,        0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 6))
        self.sizer.Add(self.seasons_enable_winter, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 2))

        # Bind functions
        self.seasons_enable_winter.Bind(wx.EVT_CHECKBOX,    self.OnToggle, self.seasons_enable_winter)
        self.seasons_select_summer.Bind(wx.EVT_RADIOBUTTON, self.OnSummer, self.seasons_select_summer)
        self.seasons_select_winter.Bind(wx.EVT_RADIOBUTTON, self.OnWinter, self.seasons_select_winter)

        # Set panel's sizer
        self.SetSizer(self.sizer)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        debug("tcui.controlSeason: translate")

        self.label.SetLabel(gt("Season:"))
        self.seasons_select_summer.SetLabel(gt("Summer"))
        self.seasons_select_summer.SetToolTip(gt("tt_seasons_select_summer"))
        self.seasons_select_winter.SetLabel(gt("Winter"))
        self.seasons_select_winter.SetToolTip(gt("tt_seasons_select_winter"))
        self.seasons_enable_winter.SetLabel(gt("Enable Winter"))
        self.seasons_enable_winter.SetToolTip(gt("tt_seasons_enable_winter"))

        self.Fit()

    def update(self):
        """Set the values of the controls in this group to the values in the project"""
        debug("tcui.controlSeason: update")

        # Turn winter image off
        if self.app.activeproject.winter() == 0:
            self.seasons_enable_winter.SetValue(False)

            # If currently have winter image selected, switch to summer image
            if self.seasons_select_winter.GetValue() == True:
                # Update model
                self.app.activeproject.active_image(season=0)
                self.seasons_select_summer.SetValue(True)
                # As active season changed, need to redraw display
                self.app.frame.display.update()

            # Then disable the control
            self.seasons_select_winter.Disable()
        else:
            self.seasons_enable_winter.SetValue(True)
            # User must select the winter image if they wish to view it, so just enable the control
            self.seasons_select_winter.Enable()

    def OnToggle(self, e):
        """Toggling winter image on and off"""
        debug("tcui.controlSeason: OnToggle")
        self.app.activeproject.winter(self.seasons_enable_winter.GetValue())
        self.update()

    def OnSummer(self, e):
        """Change to Summer image"""
        debug("tcui.controlSeason: OnSummer")
        # Set active image to Summer
        self.app.activeproject.active_image(season=0)
        # Redraw active image
        self.app.frame.display.update()

    def OnWinter(self, e):
        """Change to Winter image"""
        debug("tcui.controlSeason: OnWinter")
        # Set active image to Winter
        self.app.activeproject.active_image(season=1)
        # Redraw active image
        self.app.frame.display.update()
