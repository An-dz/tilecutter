# TileCutter User Interface Module
#      Season Images Control

import logging
import wx, imres
import translator
gt = translator.Translator()

class controlSeason(wx.Panel):
    """Box containing season image controls"""
    season_names = ["summer", "snow", "autumn", "winter", "spring"]
    season_title = ["Summer", "Snow", "Autumn", "Winter", "Spring"]

    def __init__(self, parent, app):
        logging.info("tcui.controlSeason: __init__")

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.app = app

        # Setup sizers
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.s_seasons_flex = wx.FlexGridSizer(0, 5, 0, 0)
        self.s_seasons_flex.AddGrowableCol(4)
        # Header text
        self.label = wx.StaticText(self, wx.ID_ANY, "", (-1, -1), (-1, -1), wx.ALIGN_LEFT)

        # Add items
        self.seasons_images = [0, 1, 2, 3, 4]
        self.seasons_select = [0, 1, 2, 3, 4]
        self.seasons_enable = [0, 1, 2, 3, 4]

        for season in range(5):
            self.seasons_images[season] = wx.StaticBitmap(self, wx.ID_ANY, imres.catalog["ImageSeasons" + self.season_title[season]].GetBitmap())
            self.seasons_select[season] =  wx.RadioButton(self, wx.ID_ANY, "", (-1, -1), (-1, -1))
            self.seasons_enable[season] =     wx.CheckBox(self, wx.ID_ANY, "", (-1, -1), (-1, -1))

            # Add to sizers
            self.s_seasons_flex.Add(self.seasons_images[season], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            self.s_seasons_flex.Add((5, 0))
            self.s_seasons_flex.Add(self.seasons_enable[season], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)
            self.s_seasons_flex.Add((5, 0))
            self.s_seasons_flex.Add(self.seasons_select[season], 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

            # Bind functions
            self.seasons_enable[season].Bind(wx.EVT_CHECKBOX,    self.OnToggle(season), self.seasons_enable[season])
            self.seasons_select[season].Bind(wx.EVT_RADIOBUTTON, self.OnSelect(season), self.seasons_select[season])

        self.seasons_select[0].SetValue(True)
        self.seasons_enable[0].SetValue(True)
        self.seasons_enable[0].Disable()

        # Add to default sizer with header and line
        self.sizer.Add((0, 2))
        self.sizer.Add(self.label,          0, wx.LEFT, 2)
        self.sizer.Add((0, 4))
        self.sizer.Add(self.s_seasons_flex, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.sizer.Add((0, 2))

        # Set panel's sizer
        self.SetSizer(self.sizer)

    def translate(self):
        """Update the text of all controls to reflect a new translation"""
        logging.info("tcui.controlSeason: translate")

        self.label.SetLabel(gt("Season:"))

        for season in range(5):
            self.seasons_select[season].SetLabel(gt(self.season_title[season]))
            self.seasons_select[season].SetToolTip(gt("tt_seasons_select_" + self.season_names[season]))
            self.seasons_enable[season].SetToolTip(gt("tt_seasons_enable_" + self.season_names[season]))

        self.Fit()

    def update(self):
        """Set the values of the controls in this group to the values in the project"""
        logging.info("tcui.controlSeason: update")

        # check enabled state for each station skipping summer that is always enabled
        for i in range(1, 5):
            enabled = True if (self.app.activeproject.seasons(season=self.season_names[i]) == 1) else False
            self.seasons_enable[i].SetValue(enabled)
            self.seasons_select[i].Enable(enabled)

            # if season was disabled but is the currently selected image, switch to summer image
            if not enabled and self.seasons_select[i].GetValue() == True:
                self.seasons_select[0].SetValue(True)
                self.app.activeproject.active_image(season=0)
                # As active season changed, need to redraw display
                self.app.frame.display.update()

    def OnToggle(self, arg):
        def OnChoice(e):
            """Toggling season image on and off"""
            logging.info("tcui.controlSeason: OnToggle %i" % arg)
            self.app.activeproject.seasons(self.seasons_enable[arg].GetValue(), season=self.season_names[arg])
            self.update()
        return OnChoice

    def OnSelect(self, arg):
        def OnChoice(e):
            """Change to a selected season image"""
            logging.info("tcui.controlSeason: OnSelect %i" % arg)
            # Set active image to Winter
            self.app.activeproject.active_image(season=arg)
            # Redraw active image
            self.app.frame.display.update()
        return OnChoice
