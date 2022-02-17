# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import cv2
import wx
import wx.media
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled
from pubsub import pub


class PanelOne(wx.Panel):
    def __init__(self, parent, screenSize, menu_bar, *args, **kwargs):
        super(PanelOne, self).__init__(parent=parent)
        self.width, self.height = screenSize
        self.menu_bar = menu_bar
        self.size = wx.Size(self.width*(0.8), self.height*(0.6)) # For video_panel
        
        self.cwd = os.getcwd()
        self.video_path = "None.mp4" # Non-existent initial files
        self.init_flag = 0
        self.frame_count = 0
        
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
        self.client_size = self.video_panel.GetClientSize()
        #print(self.client_size)
        
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
        
        # # Create slider
        # self.slider = wx.Slider(self, id=-1, value=0, minValue=0, maxValue=10)
        # self.slider.SetMinSize((100, -1))
        # self.slider.Disable()
        
        video_vbox.Add(video_hbox, 1, wx.EXPAND)
        # video_vbox.Add(self.slider, 1, wx.EXPAND)
        video_vbox.AddSpacer(1)
        video_vbox.Add(video_button_hbox, 1, wx.EXPAND)
        
        main_hbox.Add(video_vbox, 0, wx.EXPAND)
        main_hbox.AddSpacer(1)
        main_hbox.Add(button_box_sizer, 1, wx.EXPAND)
        
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
        
        # self.slider.Bind(wx.EVT_SLIDER, self.OnSeek)
        # self.slider.Enable()
        
        self.cv2wx_interface()
                
    def cv2wx_interface(self):
        # ---------- opencv to wxpython interface ---------- #
        # opencv information
        self.capture = cv2.VideoCapture(self.video_path)
        ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        #print(height, width)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        #print(self.fps)
        self.total_frame = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        #print(self.total_frame)
        
        if not ret:
            print("Video file error !!!")
            sys.exit(999)
            
        # resize the frame
        frame = self.rescaleFrame(frame)
        # draw on frame
        self.cv_draw(frame)
        
        # create a wx bitmap
        self.bmp = wx.Bitmap.FromBuffer(self.size[0], self.size[1], frame)
        self.bitmap = wx.StaticBitmap(self.video_panel, bitmap=self.bmp)
        
        # avoid flicker
        self.video_panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.video_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
        # set a timer to handle this event
        self.timer = wx.Timer(self)
        #self.timer.Start(1000./self.fps)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.nextFrame)
        
        # bind to mouse clicked event
        #print(self.video_panel.GetChildren())
        self.video_panel.GetChildren()[0].Bind(wx.EVT_LEFT_DOWN, lambda event: self.OnMouseClicked(frame, event))
        
    # ---------- Event處理 Start ---------- #
    def OnLoadFile(self, event=None):
        wildcard = "Video (*.mp4; *.mov)|*.mp4; *.mov"
        cwd = r""+self.cwd+"/videos/"
        #print(cwd)
        dialog = wx.FileDialog(None, "Select Video", cwd, "", wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            #print(dialog.GetPath())
            self.video_path = dialog.GetPath()    
            
            # First trigger event !
            if not self.init_flag:
                # delete image
                self.img.Destroy()
                del self.img

                self.init_flag = 1
             
            self.video_panel_refresh()
        
        dialog.Destroy()
        
    def OnPlay(self, event=None):
        self.timer.Start(1000./self.fps)
        
        self.btn_play.Disable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()

    def OnPause(self, event=None):
        self.timer.Stop()
        
        self.btn_play.Enable()
        self.btn_pause.Disable()
        self.btn_stop.Enable()

    def OnStop(self, event=None):
        self.frame_count = 0 # reset the frame count
        
        # reload video
        self.video_panel_refresh()
        
        self.btn_play.Enable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()
        
    def OnSeek(self, event=None):
        pass
        
    def OnPaint(self, event=None):
        dc = wx.BufferedPaintDC(self.video_panel)
        dc.DrawBitmap(self.bmp, 0, 0)
        
    def OnEraseBackground(self, event=None):
        pass
        
    def OnMouseClicked(self, frame, event=None):
        print(event.Position)
        
    # ---------- Event處理 End ---------- # 
    
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
        
    # ---------- opencv to wxpython interface ---------- #
    def nextFrame(self, event=None):
        ret, frame = self.capture.read()
        self.frame_count += 1
        #print(self.frame_count)
        
        if (self.frame_count == self.total_frame):
            self.OnStop()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # resize the frame
            frame = self.rescaleFrame(frame)
            # draw on frame
            self.cv_draw(frame)
            
            self.bmp.CopyFromBuffer(frame)
            
            self.video_panel.Refresh()
            
    def rescaleFrame(self, frame):
        """ Rescale Images, Videos and Live Video """
        height, width = frame.shape[:2]
        dimensions = (self.size[0], self.size[1])
        
        if (height == self.size[1]) and (width == self.size[0]):
            return frame
        elif (height > self.size[1]) or (width > self.size[0]):
            method = cv2.INTER_AREA   
        else:
            method = cv2.INTER_CUBIC
            
        return cv2.resize(frame, dimensions, interpolation=method)
        
    # ---------- refresh panel ---------- #
    def video_panel_refresh(self):
        self.video_panel.Destroy()
        self.video_panel = wx.Panel(self, wx.ID_ANY, size=self.size, style=wx.BORDER_THEME)
        self.create_video_panel()
        
    def cv_draw(self, frame): # already BGR -> RGB
        cv2.line(frame, (0, 0), (self.size[0], self.size[1]), (255, 0, 0), 2)