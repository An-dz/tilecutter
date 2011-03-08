# coding: UTF-8
#
# TileCutter User Interface Module - menuObject
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

# This module creates the program's menus

import wx, imres, tcui
import os

# Utility functions
import translator
gt = translator.Translator()
import config
config = config.Config()

import logger
debug = logger.Log()

class menuObject:
    """Class containing the main program menu"""
    def __init__(self, parent, app):
        """Create the menu"""
        self.app = app
        self.parent = parent
        self.menu = wx.MenuBar()
        # File menu
        self.fileMenu = wx.Menu()
        self.menu_file_new = self.AddMenuItem(self.fileMenu, self.OnNewProject)
        self.menu_file_open = self.AddMenuItem(self.fileMenu, self.OnOpenProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_save = self.AddMenuItem(self.fileMenu, self.OnSaveProject)
        self.menu_file_saveas = self.AddMenuItem(self.fileMenu, self.OnSaveProjectAs)
        self.fileMenu.AppendSeparator()
        self.menu_file_cut = self.AddMenuItem(self.fileMenu, self.OnCutProject)
        self.menu_file_export = self.AddMenuItem(self.fileMenu, self.OnExportProject)
        self.fileMenu.AppendSeparator()
        self.menu_file_exit = self.AddMenuItem(self.fileMenu, self.OnExit, id=wx.ID_EXIT)
        # Tools menu
        self.toolsMenu = wx.Menu()
        self.menu_tools_dat = self.AddMenuItem(self.toolsMenu, self.OnDatEdit)
        self.menu_tools_smoke = self.AddMenuItem(self.toolsMenu, self.OnSmokeEdit)
        self.menu_tools_smoke.Enable(False)
        self.toolsMenu.AppendSeparator()
        self.menu_tools_sameforall = self.AddMenuItem(self.toolsMenu, self.OnSameForAll)
        self.toolsMenu.AppendSeparator()
        self.menu_tools_language = self.AddMenuItem(self.toolsMenu, self.OnSelectLanguage)
        self.menu_tools_prefs = self.AddMenuItem(self.toolsMenu, self.OnPreferences, id=wx.ID_PREFERENCES)
        # Help menu
        self.helpMenu = wx.Menu()
        self.menu_help_help = self.AddMenuItem(self.helpMenu, self.OnHelp, id=wx.ID_HELP)
        # Need to fix this so that separator doesn't appear on the mac
        self.helpMenu.AppendSeparator()
        self.menu_help_about = self.AddMenuItem(self.helpMenu, self.OnAbout, id=wx.ID_ABOUT)

        self.menu.Append(self.fileMenu, "")
        self.menu.Append(self.toolsMenu, "")
        self.menu.Append(self.helpMenu, "")

        self.translate()    # Load the initial translation
##        self.update()       # Init this control with the default values from the active project

    def translate(self):
        """Update the text of all menu items to reflect a new translation"""
        # File menu
        self.menu.SetMenuLabel(0,gt("&File"))
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
        self.menu.SetMenuLabel(1,gt("&Tools"))
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
        self.menu.SetMenuLabel(2,gt("&Help"))
        self.menu_help_help.SetItemLabel(gt("TileCutter Online Help") + self.gsc("", ""))
        self.menu_help_help.SetHelp(gt("tt_menu_help_help"))
        self.menu_help_about.SetItemLabel(gt("&About TileCutter") + self.gsc("", ""))
        self.menu_help_about.SetHelp(gt("tt_menu_help_about"))
    def gsc(self, text, default=None):
        """Return the keyboard shortcut associated with a menu item"""
        # Filler function for now
        if default != None:
            return "\t" + default


    def AddMenuItem(self, menu, itemHandler, enabled=1, id=None):
        itemText = "--!--"  # Item text must be set to something, or wx thinks this is a stock menu item
        if id == None:
            menuId = wx.NewId()
            menuItem = wx.MenuItem(menu, menuId, itemText)
            menu.AppendItem(menuItem)
        else:
            menuId = id
            menuItem = wx.MenuItem(menu, menuId)         # Stock menu item based on a specified id
            menu.AppendItem(menuItem)
        # Bind event to parent frame
        self.parent.Bind(wx.EVT_MENU, itemHandler, id=menuId)
        if enabled == 0:
            menu.Enable(menuId, 0)
        return menuItem

    # Menu event functions
    def OnNewProject(self, e):
        debug(u"menu_object: OnNewProject - Menu-File-> New Project")
        # Call app's NewProject method
        self.app.OnNewProject()
    def OnOpenProject(self, e):
        debug(u"menu_object: OnOpenProject - Menu-File-> Open Project")
        # Call app's OpenProject method
        self.app.OnLoadProject()
    def OnSaveProject(self, e):
        debug(u"menu_object: OnSaveProject - Menu-File-> Save Project")
        # Call app's SaveProject method
        self.app.OnSaveProject(self.app.activeproject)
    def OnSaveProjectAs(self, e):
        debug(u"menu_object: OnSaveProjectAs - Menu-File-> Save Project As...")
        # Call app's SaveProject method with saveas set to True
        self.app.OnSaveAsProject(self.app.activeproject)
    def OnCutProject(self, e):
        debug(u"menu_object: OnCutProject - Menu-File-> Cut Project")
        self.app.export_project(self.app.activeproject, pak_output=False)
    def OnExportProject(self, e):
        debug(u"menu_object: OnExportProject - Menu-File-> Export Project")
        self.app.export_project(self.app.activeproject, pak_output=True)
    def OnExit(self, e):
        debug(u"menu_object: OnExit - Menu-File-> Exit Program")
        # Call app's Exit method
        self.app.Exit()

    def OnDatEdit(self, e):
        debug(u"menu_object: OnDatEdit - Menu-Tools-> Open .dat edit dialog")
        dlg = tcui.DatFileEditDialog(self.parent, self.app)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
    def OnSmokeEdit(self, e):
        debug(u"menu_object: OnSmokeEdit - Menu-Tools-> Open smoke edit dialog")
        return 1

    def OnSameForAll(self, e):
        """When "load same image for all" button is clicked"""
        debug(u"menu_object: OnSameForAll - Load active image for all images")
        dlg = wx.MessageDialog(self.parent, gt("This action will set all images in the project to be the same as this one. Do you wish to proceed?"),
                               gt("Load same image for all"),
                               style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            debug(u"menu_object: OnSameForAll - LoadImageForAll - Result YES")
            self.app.activeproject.set_all_images(self.app.activeproject.active_image_path())
        else:
            debug(u"menu_object: OnSameForAll - LoadImageForAll - Result NO")

    def OnSelectLanguage(self, e):
        debug(u"menu_object: OnSelectLanguage - Menu-Tools-> Open select language dialog")
        dlg = tcui.translationDialog(self.parent, self.app)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
    def OnPreferences(self, e):
        debug(u"menu_object: OnPreferences - Menu-Tools-> Open preferences dialog")
        dlg = tcui.preferencesDialog(self.parent, self.app)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()

    def OnHelp(self, e):
        debug(u"menu_object: OnHelp - Menu-Help-> Open online help")
        wx.LaunchDefaultBrowser("http://entropy.me.uk/tilecutter/docs")
    def OnAbout(self, e):
        debug(u"menu_object: OnAbout - Menu-Help-> Open about dialog")
        dlg = tcui.aboutDialog(self.parent, self.app, config.version)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
