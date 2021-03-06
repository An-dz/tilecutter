# TileCutter User Interface Module
#           Main Menu Bar

import logging
import wx
import tcui, translator, config
gt = translator.Translator()
config = config.Config()


class MenuObject(object):
    """Class containing the main program menu"""
    def __init__(self, parent, app):
        """Create the menu"""
        logging.info("Creating menu")

        self.app = app
        self.parent = parent
        self.menu = wx.MenuBar()

        # File menu
        self.fileMenu = wx.Menu()
        self.menu_file_new    = self.add_menu_item(self.fileMenu, self.OnNewProject)
        self.menu_file_open   = self.add_menu_item(self.fileMenu, self.OnOpenProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_save   = self.add_menu_item(self.fileMenu, self.OnSaveProject)
        self.menu_file_saveas = self.add_menu_item(self.fileMenu, self.OnSaveProjectAs)
        self.fileMenu.AppendSeparator()
        self.menu_file_cut    = self.add_menu_item(self.fileMenu, self.OnCutProject)
        self.menu_file_export = self.add_menu_item(self.fileMenu, self.OnExportProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_exit   = self.add_menu_item(self.fileMenu, self.OnExit, item_id=wx.ID_EXIT)

        # Tools menu
        self.toolsMenu = wx.Menu()
        self.menu_tools_dat        = self.add_menu_item(self.toolsMenu, self.OnDatEdit)
        self.menu_tools_smoke      = self.add_menu_item(self.toolsMenu, self.OnSmokeEdit, False)
        self.toolsMenu.AppendSeparator()
        self.menu_tools_sameforall = self.add_menu_item(self.toolsMenu, self.OnSameForAll)
        self.toolsMenu.AppendSeparator()
        self.menu_tools_language   = self.add_menu_item(self.toolsMenu, self.OnSelectLanguage)
        self.menu_tools_prefs      = self.add_menu_item(self.toolsMenu, self.OnPreferences, item_id=wx.ID_PREFERENCES)

        # Help menu
        self.helpMenu = wx.Menu()
        self.menu_help_help  = self.add_menu_item(self.helpMenu, self.OnHelp, item_id=wx.ID_HELP)
        # Need to fix this so that separator doesn't appear on mac
        self.helpMenu.AppendSeparator()
        self.menu_help_about = self.add_menu_item(self.helpMenu, self.OnAbout, item_id=wx.ID_ABOUT)

        self.menu.Append(self.fileMenu, "tc.file")
        self.menu.Append(self.toolsMenu, "tc.tools")
        self.menu.Append(self.helpMenu, "tc.help")

        # Load the initial translation
        self.translate()

    def translate(self):
        """Update the text of all menu items to reflect a new translation"""
        logging.info("Translating Menu")

        # File menu
        self.menu.SetMenuLabel(0, gt("&File"))
        self.menu_file_new.SetItemLabel(gt("&New Project") + self.gsc("menu_file_new", "Ctrl-N"))
        self.menu_file_new.SetHelp(gt("tt_menu_file_new"))
        self.menu_file_open.SetItemLabel(gt("&Open Project") + self.gsc("menu_file_open", "Ctrl-O"))
        self.menu_file_open.SetHelp(gt("tt_menu_file_open"))
        self.menu_file_save.SetItemLabel(gt("&Save Project") + self.gsc("menu_file_save", "Ctrl-S"))
        self.menu_file_save.SetHelp(gt("tt_menu_file_save"))
        self.menu_file_saveas.SetItemLabel(gt("Save Project &As") + self.gsc("menu_file_saveas", "Ctrl-A"))
        self.menu_file_saveas.SetHelp(gt("tt_menu_file_saveas"))
        self.menu_file_cut.SetItemLabel(gt("&Cut Image") + self.gsc("menu_file_cut", "Ctrl-K"))
        self.menu_file_cut.SetHelp(gt("tt_menu_file_cut"))
        self.menu_file_export.SetItemLabel(gt("&Export .pak") + self.gsc("menu_file_export", "Ctrl-E"))
        self.menu_file_export.SetHelp(gt("tt_menu_file_export"))
        self.menu_file_exit.SetItemLabel(gt("E&xit") + self.gsc("menu_file_exit", "Alt-Q"))
        self.menu_file_exit.SetHelp(gt("tt_menu_file_exit"))

        # Tools menu
        self.menu.SetMenuLabel(1, gt("&Tools"))
        self.menu_tools_dat.SetItemLabel(gt(".&dat file options") + self.gsc("menu_tools_dat", "Ctrl-D"))
        self.menu_tools_dat.SetHelp(gt("tt_menu_tools_dat"))
        self.menu_tools_smoke.SetItemLabel(gt("&Smoke options") + self.gsc("menu_tools_smoke", "Ctrl-M"))
        self.menu_tools_smoke.SetHelp(gt("tt_menu_tools_smoke"))

        self.menu_tools_sameforall.SetItemLabel(gt("Same File For All &Images") + self.gsc("menu_tools_sameforall", ""))
        self.menu_tools_sameforall.SetHelp(gt("tt_same_file_for_all"))

        self.menu_tools_language.SetItemLabel(gt("&Language") + self.gsc("menu_tools_language", "Ctrl-L"))
        self.menu_tools_language.SetHelp(gt("tt_menu_languages"))
        self.menu_tools_prefs.SetItemLabel(gt("&Preferences...") + self.gsc("menu_tools_prefs", "Ctrl-P"))
        self.menu_tools_prefs.SetHelp(gt("tt_menu_tools_prefs"))

        # Help menu
        self.menu.SetMenuLabel(2, gt("&Help"))
        self.menu_help_help.SetItemLabel(gt("TileCutter Online Help") + self.gsc("", ""))
        self.menu_help_help.SetHelp(gt("tt_menu_help_help"))
        self.menu_help_about.SetItemLabel(gt("&About TileCutter") + self.gsc("", ""))
        self.menu_help_about.SetHelp(gt("tt_menu_help_about"))

    @staticmethod
    def gsc(text, default=None):
        """Return the keyboard shortcut associated with a menu item"""
        logging.info("Keyboard shortcuts")
        # Filler function for now
        if default is not None:
            return "\t" + default

    def add_menu_item(self, menu, item_handler, enabled=True, item_id=None):
        """Appends a menu item into a menu button"""
        logging.info("Adding item")
        # Item text must be set to something, or wx thinks this is a stock menu item
        item_text = "--!--"

        if item_id is None:
            menu_item = wx.MenuItem(menu, wx.ID_ANY, item_text)
            menu_id = menu_item.GetId()
        else:
            menu_id = item_id
            # Stock menu item based on a specified id
            menu_item = wx.MenuItem(menu, menu_id)

        menu.Append(menu_item)
        # Bind event to parent frame
        self.parent.Bind(wx.EVT_MENU, item_handler, id=menu_id)
        menu.Enable(menu_id, enabled)
        return menu_item

    #############################
    # File menu event functions #
    #############################
    def OnNewProject(self, e):
        """Call creation of new project"""
        logging.info("Menu-File-> New Project")
        # Call app's NewProject method
        self.app.OnNewProject()

    def OnOpenProject(self, e):
        """Call project open dialog"""
        logging.info("Menu-File-> Open Project")
        # Call app's OpenProject method
        self.app.OnLoadProject()

    def OnSaveProject(self, e):
        """Call project saving"""
        logging.info("Menu-File-> Save Project")
        # Call app's SaveProject method
        self.app.OnSaveProject(self.app.activeproject)

    def OnSaveProjectAs(self, e):
        """Call project saving dialog"""
        logging.info("Menu-File-> Save Project As...")
        # Call app's SaveProject method with saveas set to True
        self.app.OnSaveAsProject(self.app.activeproject)

    def OnCutProject(self, e):
        """Call image cutting"""
        logging.info("Menu-File-> Cut Project")
        self.app.export_project(self.app.activeproject, pak_output=False)

    def OnExportProject(self, e):
        """Call .pak export"""
        logging.info("Menu-File-> Export Project")
        self.app.export_project(self.app.activeproject, pak_output=True)

    def OnExit(self, e):
        """Call program exit"""
        logging.info("Menu-File-> Exit Program")
        # Call app's Exit method
        self.app.Exit()

    ##############################
    # Tools menu event functions #
    ##############################
    def OnDatEdit(self, e):
        """Open .dat editor dialog"""
        logging.info("Menu-Tools-> Open .dat edit dialog")
        dlg = tcui.DialogDatFileEdit(self.parent, self.app)
        # Needed so that on mac this window comes back into foreground after switching to/from application
        self.app.SetTopWindow(dlg)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def OnSmokeEdit(self, e):
        """"""
        logging.info("Menu-Tools-> Open smoke edit dialog")
        return 1

    def OnSameForAll(self, e):
        """When 'load same image for all' button is clicked"""
        logging.info("Load active image for all images")

        dlg = wx.MessageDialog(self.parent,
                               gt("This action will set all images in the project to be the same as this one. Do you wish to proceed?"),
                               gt("Load same image for all"),
                               style=wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            logging.debug("LoadImageForAll - Result YES")
            self.app.activeproject.set_all_images(self.app.activeproject.active_image_path())
        else:
            logging.debug("LoadImageForAll - Result NO")

    def OnSelectLanguage(self, e):
        """Open language selection dialog"""
        logging.info("Menu-Tools-> Open select language dialog")
        dlg = tcui.DialogLanguage(self.parent, self.app)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def OnPreferences(self, e):
        """Open the preferences dialog"""
        logging.info("Menu-Tools-> Open preferences dialog")
        dlg = tcui.DialogPreferences(self.parent, self.app)
        # Needed so that on mac this window comes back into foreground after switching to/from application
        self.app.SetTopWindow(dlg)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    #############################
    # Help menu event functions #
    #############################
    @staticmethod
    def OnHelp(e):
        """Open online help page"""
        logging.info("Menu-Help-> Open online help")
        wx.LaunchDefaultBrowser("https://github.com/An-dz/tilecutter")

    def OnAbout(self, e):
        """Open About dialog"""
        logging.info("Menu-Help-> Open about dialog")
        dlg = tcui.DialogAbout(self.parent, self.app, config.version)
        # Needed so that on mac this window comes back into foreground after switching to/from application
        self.app.SetTopWindow(dlg)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
