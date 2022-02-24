# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import argparse
import configparser
import wx
import wx.lib.agw.aui as aui
from pubsub import pub

from panel_one import PanelOne


class TaskConfig():
    """
    Read config settings
    """
    def __init__(self):
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.criteria = configparser.RawConfigParser()
        self.criteria.optionxform = str 
        self.config_file = "config/settings.ini"
        
        # read the file
        self.read_config_file()

    def read_config_file(self):
        # print("Read config file {}".format(self.config_file))
        if not os.path.exists(self.config_file):
            print("Config file ({}) does not exist.".format(self.config_file))
            sys.exit(999)
        else:
            self.config.read(self.config_file, encoding="utf-8")
            
    def get_config_item(self, category, item):
        return self.config.get(category, item).strip()
        
    def get_criteria_item(self, category, item):
        return self.criteria.get(category, item).strip()
        
        
class TaskFrame(wx.Frame):
    """ 
    The main frame of the application
    """
    def __init__(self, title, icon):
        # ensure the parent's __init__ is called
        super(TaskFrame, self).__init__(None, title=title, style=wx.DEFAULT_FRAME_STYLE)
        
        # get screen size
        self.screenSize = wx.DisplaySize()
        #self.width, self.high = self.screenSize
        #print(self.width, self.high)
        
        # set icon
        self.SetIcon(wx.Icon(icon))
        # ----------
        # get current work path
        self.cwd = os.getcwd()

        # read config files
        self.config = TaskConfig()

        # set font size for all control, 9 is default
        font = self.GetFont()
        font.SetPointSize(15)
        #self.SetFont(font)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        
        # create menu bar
        self.create_menu()
        
        # create status bar
        self.create_statusBar()
        self.statusBar.SetStatusText("Program Idle...")
        
        # create panel
        self.panel = wx.Panel(self)
        # self.notebook = wx.Notebook(self.panel) # "wx.Notebook" cannot disable tabs... Use "wx.lib.agw.aui.AuiNotebook" instead
        self.notebook = aui.AuiNotebook(self.panel, agwStyle=aui.AUI_NB_DEFAULT_STYLE^aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)    
        self.notebook.SetFont(font)
   
        self.notebook.pageChanged_count = 0 # !!! when page changed, we need a count to initial the pages....   
        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.PageChanged)
        
        self.page1 = PanelOne(self.notebook, self.screenSize, self.menu_bar, self.config)
        self.notebook.AddPage(self.page1, "Calibration")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, border=5, proportion=1, flag=wx.ALL|wx.EXPAND)
        self.panel.SetSizer(sizer)
   
        # remove black rectangular issue !!!
        self.Layout()

    def delNotebookPage(self, pageTitle):
        for index in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPageText(index)
            if page == pageTitle:
                self.notebook.DeletePage(index)
                self.notebook.SendSizeEvent()
                break
        
    # ---------- 菜單相關 Start ---------- #
    def create_menu(self):
        """
        Create the menu
        """
        self.menu_bar = wx.MenuBar()
        
        menu_file = wx.Menu()
        
        m_reload = menu_file.Append(-1, "Reload Initial Setting Files\tCtrl-R", "Reload Initial Setting Files")
        self.Bind(wx.EVT_MENU, self.on_reload, m_reload)
        menu_file.AppendSeparator() # adds a separator to the end of the menu
        
        m_exit = menu_file.Append(-1, "Exit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        
        self.menu_bar.Append(menu_file, "&File")
        
        self.SetMenuBar(self.menu_bar)
        
    def on_reload(self, event):
        # reload config files
        self.config = TaskConfig()
        
        self.notebook.Unbind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED) # because the page has not been created yet
        
        # destory pages
        self.delNotebookPage("Calibration")

        # create new pages        
        self.page1 = PanelOne(self.notebook, self.screenSize, self.menu_bar, self.config)
        self.notebook.AddPage(self.page1, "Calibration")
        
        self.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.PageChanged)

        self.Layout()
    
    def on_exit(self, event):
        self.Destroy()
    # ---------- 菜單相關 End ---------- #
    
    # ---------- 狀態欄 Start ---------- #
    def create_statusBar(self):
        """
        Create the status bar
        """
        self.statusBar = self.CreateStatusBar()
        
    def updateStatusBar(self, msg):
        self.statusBar.SetStatusText(msg)
    # ---------- 狀態欄 End ---------- #
    
    # ---------- Tab相關 Start ---------- #
    def PageChanged(self, event=None):
        if self.notebook.pageChanged_count > 0:
            #print(self.notebook.GetChildren())
            children = self.notebook.GetChildren()
            for child in children:
                if isinstance(child, wx.Panel):
                    child.init_state()
                    
        #print(self.notebook.pageChanged_count)
        self.notebook.pageChanged_count+=1
    # ---------- Tab相關 End ---------- #
    
def create_output_folders(paths):
    for path in paths:
        os.makedirs(path, exist_ok=True)
        
        
def main():    
    # # create output folder
    # create_output_folders(["output"])
    
    # init settings
    tool_title = "Coordinate Transfer Tool"
    tool_version = "v1.1.0"
    tool_icon = "icon/logo.png"
    
    # create application
    app = wx.App()
    app.frame = TaskFrame(title="%s_%s"%(tool_title, tool_version), icon=tool_icon)
    app.frame.Show()
    app.frame.Maximize(True)
    app.MainLoop()
    
    
if __name__ == "__main__":
    main()
    