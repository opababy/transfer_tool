# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import wx
import wx.media
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled
from pubsub import pub


class PanelOne(wx.Panel):
    def __init__(self, parent, screenSize, menu_bar, *args, **kwargs):
        super(PanelOne, self).__init__(parent=parent)
        self.width, self.high = screenSize
        self.menu_bar = menu_bar
        self.size = wx.Size(self.width*(0.8), self.high*(0.6))
        
        self.cwd = os.getcwd()
        self.video_path = "None.mp4" # Non-existent initial files
        self.init_flag = 0
        
        self.config = args[0]
        
        # set font
        font = self.GetFont()
        font.SetPointSize(14)
        font.SetWeight(wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)
        
        # set background color
        #colors = ["white", "red", "blue", "gray", "yellow", "green"]
        #self.SetBackgroundColour(colors[0])
        
        self.create_init_panel()
        
    def create_init_panel(self):
        """
        Create the main panel
        """
        main_hbox = wx.BoxSizer(wx.HORIZONTAL)
        # ---------- Button Panel Start ---------- #
        # scrolled panel stuff
        self.scrolled_panel = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL, name="scrolled_panel")
        self.scrolled_panel.SetAutoLayout(1)
        self.scrolled_panel.SetupScrolling()        
        
        # put the scrolled panel
        button_box = wx.StaticBox(self, wx.ID_ANY, u"Button")
        button_box_sizer = wx.StaticBoxSizer(button_box, wx.VERTICAL)
        button_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # put the button
        item_vbox = wx.BoxSizer(wx.VERTICAL)

        # define the buttons
        self.btn_load = wx.Button(self.scrolled_panel, label="Load video", size=(-1, 30))
        self.btn_load.Bind(wx.EVT_BUTTON, self.OnLoadFile)
        self.btn_load.Enable()
        
        # put to boxes
        item_vbox.Add(self.btn_load, 0, wx.ALL, 10)
        button_vbox.Add(item_vbox, 0, wx.ALL, 10)
        
        self.scrolled_panel.SetSizer(button_vbox)
        
        button_box_sizer.Add(self.scrolled_panel, 1, wx.EXPAND)
        # ---------- Video Panel Start ---------- #
        # create video panel part
        video_vbox = wx.BoxSizer(wx.VERTICAL)
        video_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.video_panel = wx.Panel(self, wx.ID_ANY, size=self.size, style=wx.BORDER_THEME)
        
        # put an initial image
        self.img = wx.Image("icon/init.png", wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(self.size[0], self.size[1])
        self.img = wx.StaticBitmap(self.video_panel, -1, wx.BitmapFromImage(self.img))
        
        video_hbox.Add(self.video_panel, 0, wx.ALL, 10)
        
        # create buttons
        video_button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_play = wx.Button(self, label="Play", size=(-1, 30))
        self.btn_play.Disable()
        
        self.btn_pause = wx.Button(self, label="Pause", size=(-1, 30))
        self.btn_pause.Disable()

        self.btn_stop = wx.Button(self, label="Stop", size=(-1, 30))
        self.btn_stop.Disable()
        
        video_button_hbox.Add(self.btn_play, 0, wx.ALL, 10)
        video_button_hbox.Add(self.btn_pause, 0, wx.ALL, 10)
        video_button_hbox.Add(self.btn_stop, 0, wx.ALL, 10)
        
        # Create slider
        self.slider = wx.Slider(self, id=-1, value=0, minValue=0, maxValue=10)
        self.slider.SetMinSize((100, -1))
        self.slider.Disable()
        
        video_vbox.Add(video_hbox, 1, wx.EXPAND)
        video_vbox.Add(self.slider, 1, wx.EXPAND)
        video_vbox.AddSpacer(1)
        video_vbox.Add(video_button_hbox, 1, wx.EXPAND)
        
        main_hbox.Add(video_vbox, 0, wx.EXPAND)
        main_hbox.AddSpacer(1)
        main_hbox.Add(button_box_sizer, 1, wx.EXPAND)
        
        # ---------- Load Media Start ---------- #
        # wx.CallAfter(self.DoLoadFile, self.video_path)
        
        # ---------- Load Media End ---------- #
        
        self.SetSizer(main_hbox)
        #self.Layout()
        
    def create_video_panel(self): # after trigger "Load video" btn
        # bind events
        self.btn_play.Bind(wx.EVT_BUTTON, self.OnPlay)
        self.btn_play.Enable()
        
        self.btn_pause.Bind(wx.EVT_BUTTON, self.OnPause)
        self.btn_pause.Enable()
        
        self.btn_stop.Bind(wx.EVT_BUTTON, self.OnStop)
        self.btn_stop.Enable()
        
        self.slider.Bind(wx.EVT_SLIDER, self.OnSeek)
        self.slider.Enable()
        
        # create MediaCtrl
        self.mc = wx.media.MediaCtrl()
        # try: 'szBackend=wx.media.MEDIABACKEND_WMP10' if cannot run on windows!
        self.mcCreate = self.mc.Create(self.video_panel, style=wx.BORDER_SIMPLE, szBackend=wx.media.MEDIABACKEND_WMP10)
        
        self.video_panel.Bind(wx.EVT_SIZE, self.ReSize)
        self.video_panel.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        
        # set timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100) # (Re)starts the timer. (milliseconds)
        
        self.Bind(wx.EVT_CLOSE, self.OnQuit)
        
    # ---------- Event處理 Start ---------- #
    def OnLoadFile(self, event=None):
        wildcard = "Video (*.mp4; *.mov)|*.mp4; *.mov"
        cwd = r""+self.cwd+"/videos/"
        #print(cwd)
        dialog = wx.FileDialog(None, "Select Video", cwd, "", wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            # First trigger event !
            if not self.init_flag:
                self.create_video_panel()
            
                # delete image
                self.img.Destroy()
                del self.img
                
                self.init_flag = 1
                
            #print(dialog.GetPath())
            self.video_path = dialog.GetPath()
            self.DoLoadFile(self.video_path)
                
        dialog.Destroy()
        
    def DoLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % str(path),
                          "ERROR",
                          wx.ICON_ERROR|wx.OK)
            self.btn_play.Disable()
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.btn_play.Enable()    
    
    def OnMediaLoaded(self, event=None):
        self.btn_play.Enable()
        
    def OnPlay(self, event=None):
        if not self.mc.Play():
            wx.MessageBox("Unable to Play media: Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR|wx.OK)
        else:
            self.mc.SetInitialSize()
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            
            self.btn_play.Disable()
            self.btn_pause.Enable()
            self.btn_stop.Enable()

    def OnPause(self, event=None):
        self.mc.Pause()
        
        self.btn_play.Enable()
        self.btn_pause.Disable()
        self.btn_stop.Enable()

    def OnStop(self, event=None):
        self.mc.Stop()
        
        self.btn_play.Enable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()

    def ReSize(self, event=None):
        """
        https://stackoverflow.com/questions/7120634/how-to-resize-videos-in-wx-media-mediactrl/15456853
        """
        self.mc.Pause()     
        self.video_panel.Layout()
        self.mc.SetSize(self.size)
        self.mc.Play()
        
    def OnSeek(self, event=None):
        offset = self.slider.GetValue()
        self.mc.Seek(offset) # Obtains the current position in time within the media in milliseconds.
        
    def OnTimer(self, event=None):
        try:
            offset = self.mc.Tell()
            #print(offset)
            self.slider.SetValue(offset)
            
            if offset == 0:
                self.init()
            
        except Exception as e:
            print(e)
        
    def OnQuit(self, event=None):
        """
        https://stackoverflow.com/questions/62103498/learning-python-runtimeerror-wrapped-c-c-object-of-type-staticbitmap-has-bee
        """
        self.timer.Stop()
        self.Unbind(wx.EVT_TIMER)
        self.Destroy()
    # ---------- Event處理 End ---------- # 
    
    def init(self):
        self.btn_play.Enable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()
        
    def press_state(self):
        # disable others & enable logs
        self.btn_play.Disable()
        self.btn_pause.Disable()
        self.btn_stop.Disable()
        self.menu_bar.EnableTop(pos=0, enable=False)
        
        # scrolled_panel back to (0, 0)
        self.scrolled_panel.Scroll(0, 0)   
        
        # disable other tabs
        self.GetParent().EnableTab(0, False)
        