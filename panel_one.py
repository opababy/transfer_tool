# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import cv2
import wx
import wx.media
import wx.lib.agw.aui as aui
import wx.lib.scrolledpanel as scrolled
from pubsub import pub
import platform

from dump_json import JsonData
import update_package
from thread_with_return_value import ThreadWithReturnValue


class PanelOne(wx.Panel):
    def __init__(self, parent, screenSize, menu_bar, *args, **kwargs):
        super(PanelOne, self).__init__(parent=parent)
        self.width, self.height = screenSize
        self.menu_bar = menu_bar
        self.size = wx.Size(self.width*(0.8), self.height*(0.6)) # For video_panel
        
        self.config = args[0]
        ai_model_width = int(self.config.get_config_item("COMMON_SETTINGS", "ai_model_width"))
        ai_model_height = int(self.config.get_config_item("COMMON_SETTINGS", "ai_model_height"))
        self.ai_model_dimension = (ai_model_width, ai_model_height)
        #print(self.ai_model_dimension)
        self.roi_limit = int(self.config.get_config_item("COMMON_SETTINGS", "roi_limit"))
        #print(self.roi_limit)
        
        self.cwd = os.getcwd()
        self.video_path = "None.mp4" # Non-existent initial files
        self.image_path = "None.jpg" # Non-existent initial files
        self.init_flag = 0
        self.frame_count = 0
        
        # draw on opencv
        self.draw_flag = 0
        self.points_list = []
        
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
        roi_hbox = wx.BoxSizer(wx.HORIZONTAL)
        ai_hbox = wx.BoxSizer(wx.HORIZONTAL)
        item_vbox_2 = wx.BoxSizer(wx.VERTICAL)

        # define the buttons
        self.btn_video_load = wx.Button(self.scrolled_panel, label="Load video", size=(-1, 30))
        self.btn_video_load.Bind(wx.EVT_BUTTON, self.OnLoadVideoFile)
        self.btn_video_load.Enable()
        
        self.btn_image_load = wx.Button(self.scrolled_panel, label="Load image", size=(-1, 30))
        self.btn_image_load.Bind(wx.EVT_BUTTON, self.OnLoadImageFile)
        self.btn_image_load.Enable()
        
        # define the ROI choice box
        roi_text = wx.StaticText(self.scrolled_panel, label="ROI level: ", size=(-1, 30))
        roi_list = ["ROI1", "ROI2"]
        self.roi_choice = wx.Choice(self.scrolled_panel, -1, choices = roi_list, style = wx.CB_SORT)
        self.roi_choice.Disable()
        
        # define the AI choice box
        ai_text = wx.StaticText(self.scrolled_panel, label="AI model: ", size=(-1, 30))
        ai_list = ["BSD", "BSIS", "BSD_BSIS", "FCW"]
        self.ai_choice = wx.Choice(self.scrolled_panel, -1, choices = ai_list, style = wx.CB_SORT)
        self.ai_choice.Disable()
        
        # define the buttons
        self.btn_json = wx.Button(self.scrolled_panel, label="Dump json", size=(-1, 30))
        self.btn_json.Disable()
        
        self.btn_upload = wx.Button(self.scrolled_panel, label="Upload package", size=(-1, 30))
        self.btn_upload.Disable()
        
        # put to boxes
        item_vbox.Add(self.btn_video_load, 0, wx.ALL, 10) # Load video
        item_vbox.Add(self.btn_image_load, 0, wx.ALL, 10) # Load image
        roi_hbox.Add(roi_text, 0, wx.ALL, 10) # ROI level
        roi_hbox.Add(self.roi_choice, 0, wx.ALL, 10)
        ai_hbox.Add(ai_text, 0, wx.ALL, 10) # AI model
        ai_hbox.Add(self.ai_choice, 0, wx.ALL, 10)
        item_vbox_2.Add(self.btn_json, 0, wx.ALL, 10) # Dump json
        item_vbox_2.Add(self.btn_upload, 0, wx.ALL, 10) # Upload package
        
        button_vbox.Add(item_vbox, 0, wx.ALL, 10)
        button_vbox.Add(roi_hbox, 0, wx.ALL, 10)
        button_vbox.Add(ai_hbox, 0, wx.ALL, 10)
        button_vbox.Add(item_vbox_2, 0, wx.ALL, 10)
        
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
        self.img = self.img.Scale(self.client_size[0], self.client_size[1])
        """ 
        wxPyDeprecationWarning: Call to deprecated item BitmapFromImage. Use :class:`wx.Bitmap` instead 
        """
        # self.img = wx.StaticBitmap(self.video_panel, -1, wx.BitmapFromImage(self.img))
        self.img = wx.StaticBitmap(self.video_panel, -1, wx.Bitmap(self.img))
        
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
        self.slider = wx.Slider(self, id=-1, value=0, minValue=0, maxValue=100)
        self.slider.SetMinSize((100, -1))
        self.slider.Disable()
        
        video_vbox.Add(video_hbox, 1, wx.EXPAND)
        video_vbox.Add(self.slider, 1, wx.EXPAND)
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
        self.slider.SetValue(0)
        # self.slider.Disable()
        
        self.roi_choice.Bind(wx.EVT_CHOICE, self.onRoiChoice)
        self.roi_choice.Enable()
        
        self.ai_choice.Bind(wx.EVT_CHOICE, self.onAiChoice)
        self.ai_choice.Enable()
        
        self.btn_json.Bind(wx.EVT_BUTTON, self.OnDumpJson)
        
        self.btn_upload.Bind(wx.EVT_BUTTON, self.OnUploadPackage)
        
        self.cvVideo2wx_interface()
        
    def create_image_panel(self): # after trigger "Load image" btn
        # bind events
        self.btn_play.Disable()
        self.btn_pause.Disable()
        self.btn_stop.Disable()
        
        self.roi_choice.Bind(wx.EVT_CHOICE, self.onRoiChoice)
        self.roi_choice.Enable()
        
        self.ai_choice.Bind(wx.EVT_CHOICE, self.onAiChoice)
        self.ai_choice.Enable()
        
        self.btn_json.Bind(wx.EVT_BUTTON, self.OnDumpJson)
        
        self.btn_upload.Bind(wx.EVT_BUTTON, self.OnUploadPackage)
        
        self.cvImg2wx_interface()
                
    def cvVideo2wx_interface(self):
        # ---------- opencv to wxpython interface ---------- #
        # opencv information
        self.capture = cv2.VideoCapture(self.video_path)
        ret, self.frame = self.capture.read()
        self.frame_count += 1
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        #height, width = self.frame.shape[:2]
        #print(height, width)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        #print(self.fps)
        self.total_frame = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        #print(self.total_frame)
        
        if not ret:
            print("Video file error !!!")
            sys.exit(999)
            
        # resize the frame
        self.frame = self.rescaleFrame(self.frame)
        # draw on frame
        if self.draw_flag:
            self.cv_draw(self.frame)
        
        # create a wx bitmap
        self.bmp = wx.Bitmap.FromBuffer(self.client_size[0], self.client_size[1], self.frame)
        self.bitmap = wx.StaticBitmap(self.video_panel, bitmap=self.bmp)
        
        # set a timer to handle this event
        self.timer = wx.Timer(self)
        #self.timer.Start(1000./self.fps)
        self.timer.Stop()
        self.Bind(wx.EVT_TIMER, self.nextFrame)
        
        # avoid flicker (Note! Do not refresh the panel, refresh the bitmap !)
        #self.video_panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.bitmap.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.video_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
        # bind to mouse clicked event
        #print(self.video_panel.GetChildren())
        self.bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event: self.OnMouseClicked(self.frame, event))
        
        # avoid layout changes after zooming
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def cvImg2wx_interface(self):
        # ---------- opencv to wxpython interface ---------- #
        # opencv information
        self.cvImg = cv2.imread(self.image_path)
        self.cvImg = cv2.cvtColor(self.cvImg, cv2.COLOR_BGR2RGB)
        
        # resize the Img
        self.cvImg = self.rescaleFrame(self.cvImg)
        # draw on Img
        if self.draw_flag:
            self.cv_draw(self.cvImg)
            
        # create a wx bitmap
        self.bmp = wx.Bitmap.FromBuffer(self.client_size[0], self.client_size[1], self.cvImg)
        self.bitmap = wx.StaticBitmap(self.video_panel, bitmap=self.bmp)
        
        # avoid flicker (Note! Do not refresh the panel, refresh the bitmap !)
        self.bitmap.Bind(wx.EVT_PAINT, self.OnPaint)
        
        # bind to mouse clicked event
        self.bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event: self.OnMouseClicked(self.cvImg, event))
        
        # avoid layout changes after zooming
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    # ---------- Event Handler Start ---------- #
    def OnLoadVideoFile(self, event=None):
        if platform.system() == "Windows":
            wildcard = "Video (*.mp4; *.mov)|*.mp4; *.mov"
        # Linux have some bugs... cannot show multiple wildcard
        elif platform.system() == "Linux":
            wildcard = "Video (*.mp4)|*.mp4"
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
             
            self.frame_count = 0
            self.draw_flag = 0
            self.points_list = []
            
            # reload video
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
        self.draw_flag = 0
        self.points_list = []
        
        # reload video
        self.video_panel_refresh()
        
        self.btn_play.Enable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()
        
    # def OnSeek(self, event=None):
        # pass
        
    def OnPaint(self, event=None):
        try:
            dc = wx.BufferedPaintDC(self.bitmap)
            dc.DrawBitmap(self.bmp, 0, 0)
            
            event.Skip()
        except Exception as e:
            pass
        
    def OnEraseBackground(self, event=None):
        event.Skip()
        
    def OnSize(self, event=None):
        #print("zooming ...")
        self.Refresh()
        
    def OnMouseClicked(self, frame, event=None):
        #print(event.Position) # data type: wx.Point(X, Y)
        if len(self.points_list) < self.roi_limit:
            # print("Limit the number of points successfully !")
            self.draw_flag = 1
            self.points_list.append(tuple(event.Position))
            
            self.cv_draw(frame)
            #self.video_panel.Refresh()
            
            self.dump_json_conditions()
        
    def onRoiChoice(self, event=None):
        self.roi_result = self.roi_choice.GetStringSelection()
        # print(self.roi_result)
        
        self.dump_json_conditions()
        
    def onAiChoice(self, event=None):
        self.ai_result = self.ai_choice.GetStringSelection()
        # print(self.ai_result)
        
        self.dump_json_conditions()
        
    def OnDumpJson(self, event=None):
        #print("Dump json ...")
        #print(self.points_list)
        ai_points_list = self.to_AI_model_position()
        #print(ai_points_list)
        # print(self.ai_result)
        # print(self.roi_result)
        
        json_key = "%s_%s"%(self.ai_result, self.roi_result)
        #print(json_key.lower())
        
        # check json file exist
        json_data_path = "data/event_fusion.json"
        #print(os.path.abspath(json_data_path))
        
        if not os.path.isfile(json_data_path):
            self.showDialog("%s is not exist!\n Please check again..."%(os.path.abspath(json_data_path)))
            
        else:
            jsonData = JsonData(json_data_path, json_key.lower(), ai_points_list)
            jsonData.json_load()
            jsonData.json_data_process()
            jsonData.json_dump()
            
            file_update = jsonData.check_json_file_update()
            if file_update:
                msg = "json dump successfully!"
            else:
                msg = "json dump failed! Please try again..."
                
            self.showDialog(msg)
            
    def OnLoadImageFile(self, event=None):
        if platform.system() == "Windows":
            wildcard = "Image (*.jpg; *.png)|*.jpg; *.png"
        # Linux have some bugs... cannot show multiple wildcard
        elif platform.system() == "Linux":
            wildcard = "Image (*.png)|*.png"
        cwd = r""+self.cwd+"/images/"
        dialog = wx.FileDialog(None, "Select Image", cwd, "", wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.image_path = dialog.GetPath()    
            
            # First trigger event !
            if not self.init_flag:
                # delete image
                self.img.Destroy()
                del self.img

                self.init_flag = 1
             
            self.frame_count = 0
            self.draw_flag = 0
            self.points_list = []
            
            # reload image
            # if a timer exists, force delete it !!!
            try:
                del self.timer
            except AttributeError as e:
                #print(e)
                pass
            self.image_panel_refresh()
        
        dialog.Destroy()
        
    # ---------- Event Handler End ---------- # 
    
    def press_state(self):
        # disable others
        self.btn_json.Disable()
        self.btn_upload.Disable()
        
        self.btn_play.Disable()
        self.btn_pause.Disable()
        self.btn_stop.Disable()
        self.menu_bar.EnableTop(pos=0, enable=False)
        
        # scrolled_panel back to (0, 0)
        self.scrolled_panel.Scroll(0, 0)   
        
        # disable other tabs
        self.GetParent().EnableTab(0, False)
        
    def enable_state(self):
        # enable others
        self.btn_json.Enable()
        self.btn_upload.Enable()
        
        self.btn_play.Enable()
        self.btn_pause.Enable()
        self.btn_stop.Enable()
        self.menu_bar.EnableTop(pos=0, enable=True)  
        
        # disable other tabs
        self.GetParent().EnableTab(0, True)
        
    # ---------- opencv to wxpython interface ---------- #
    def nextFrame(self, event=None):
        # ---------- video part ---------- #
        ret, self.frame = self.capture.read()
        self.frame_count += 1
        #print(self.frame_count, self.total_frame)
        
        if (self.frame_count == self.total_frame):
            #self.OnStop()
            self.timer.Stop()
            
        if ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # resize the frame
            self.frame = self.rescaleFrame(self.frame)
            # draw on frame
            if self.draw_flag:
                self.cv_draw(self.frame)
                
            """ 
            In windows 10, you can update the screen with self.video_panel.Refresh().
            However, it doesn't work in ubuntu 1804.
            So use refresh bitmap instead.
            """
            # refresh the bitmap
            self.bmp.CopyFromBuffer(self.frame)
            self.bitmap.SetBitmap(self.bmp)
            
            #self.video_panel.Refresh()
            
        # ---------- slider part ---------- #
        offset = self.frame_count*100//self.total_frame
        self.slider.SetValue(offset)
            
    def rescaleFrame(self, frame):
        """ Rescale Images, Videos and Live Video """
        height, width = frame.shape[:2]
        dimensions = (self.client_size[0], self.client_size[1])
        
        if (height == self.client_size[1]) and (width == self.client_size[0]):
            return frame
        elif (height > self.client_size[1]) or (width > self.client_size[0]):
            method = cv2.INTER_AREA   
        else:
            method = cv2.INTER_CUBIC
            
        return cv2.resize(frame, dimensions, interpolation=method)
        
    # ---------- refresh panel ---------- #
    def video_panel_refresh(self):
        self.video_panel.Destroy()
        self.video_panel = wx.Panel(self, wx.ID_ANY, size=self.size, style=wx.BORDER_THEME)
        self.create_video_panel()
        
        self.btn_json.Disable()     
        self.btn_upload.Disable() 
        
    def image_panel_refresh(self):
        self.video_panel.Destroy()
        self.video_panel = wx.Panel(self, wx.ID_ANY, size=self.size, style=wx.BORDER_THEME)
        self.create_image_panel()
        
        self.btn_json.Disable()
        self.btn_upload.Disable() 
        
    def cv_draw(self, frame): # already BGR -> RGB
        color_table = self.config.get_config_item("COMMON_SETTINGS", "color_table")
        # (R, G, B)
        if color_table == "0":
            color = (0, 0, 0)
        elif color_table == "1":
            color = (255, 255, 255)
        elif color_table == "2":
            color = (255, 0, 0)
        elif color_table == "3":
            color = (0, 255, 0)
        elif color_table == "4":
            color = (0, 0, 255)
        else:
            color = (255, 255, 255)
            
        # draw point
        for point in self.points_list:
            cv2.circle(frame, tuple(point), 1, color, 5)
            
        # draw line 
        for i in range(len(self.points_list)):
            #print(i, self.points_list)
            if i > 0:
                cv2.line(frame, tuple(self.points_list[i-1]), tuple(self.points_list[i]), color, 2)
                
            if i == self.roi_limit-1:
                cv2.line(frame, tuple(self.points_list[i]), tuple(self.points_list[0]), color, 2)
                
        # refresh the bitmap
        self.bmp.CopyFromBuffer(frame)
        self.bitmap.SetBitmap(self.bmp)
        
    # ---------- dump json conditions ---------- #        
    def dump_json_conditions(self):
        try:
            if self.roi_result and self.ai_result and len(self.points_list) == self.roi_limit:
                self.btn_json.Enable()
                self.btn_upload.Enable()
                
        except AttributeError as e:
            #print("AttributeError !")
            self.btn_json.Disable()
            self.btn_upload.Disable()
            
    def to_AI_model_position(self):
        ai_points_list = []
    
        for i in range(len(self.points_list)):
            #print(self.points_list[i]) # GUI video coordinate (self.client_size)
            ai_x = int(self.points_list[i][0]*self.ai_model_dimension[0]/self.client_size[0])
            ai_y = int(self.points_list[i][1]*self.ai_model_dimension[1]/self.client_size[1])
            
            ai_points_list.append((ai_x, ai_y))
            
        #print(ai_points_list)
        return ai_points_list
        
        
    # ---------- show dialog ---------- #  
    def showDialog(self, msg, dlg_type="OK"):
        retCode = None

        if dlg_type == "OK":
            dlg = wx.MessageDialog(parent=None, message=msg,
                caption="Note",
                style = wx.OK|wx.ICON_WARNING|wx.STAY_ON_TOP)
                
            retCode = dlg.ShowModal()
            
            # release dialog
            dlg.Destroy()
            
        elif dlg_type == "YES_NO":
            dlg = wx.MessageDialog(parent=None, message=msg,
                caption="Question",
                style = wx.YES_NO|wx.ICON_QUESTION|wx.STAY_ON_TOP)
            
            retCode = dlg.ShowModal()
            
            # release dialog
            dlg.Destroy()
            
        return retCode
 # ---------- Show json helper line ---------- # 
    def to_UI_position(self, ai_pos):
        ui_x = int(ai_pos[0]*self.client_size[0]/self.ai_model_dimension[0])
        ui_y = int(ai_pos[1]*self.client_size[1]/self.ai_model_dimension[1])
        
        return (ui_x, ui_y)
    
    def json_line(self, json_key, frame): 
        json_data_path = "data/event_fusion.json"
        key_roi1 = "%s_roi1"%(json_key)
        key_roi2 = "%s_roi2"%(json_key)
        
        jsonData = JsonData(json_data_path, None, None)
        data = jsonData.json_load()
        # print(data)
        
        # print(data[key_roi1])
        # print(data[key_roi2])
        
        for key in [key_roi1, key_roi2]:
            #for i in range(len(data[key_roi1])):
            for i in range(self.roi_limit):
                #print(data[key]["p%d"%i])
                if i > 0:
                    drawDashLine(frame, self.to_UI_position((data[key]["p%d"%(i-1)]["x"], data[key]["p%d"%(i-1)]["y"])), \
                                        self.to_UI_position((data[key]["p%d"%(i)]["x"], data[key]["p%d"%(i)]["y"])))
                    
                if i == self.roi_limit-1:
                    drawDashLine(frame, self.to_UI_position((data[key]["p%d"%(i)]["x"], data[key]["p%d"%(i)]["y"])), \
                                        self.to_UI_position((data[key]["p%d"%(0)]["x"], data[key]["p%d"%(0)]["y"])))
                                        
        # refresh the bitmap
        self.bmp.CopyFromBuffer(frame)
        self.bitmap.SetBitmap(self.bmp)
        
    def OnUploadPackage(self, event=None):
        # get ip
        ip = self.config.get_config_item("COMMON_SETTINGS", "ip")   
        
        #self.press_state()
        wx.SafeYield()

        t = ThreadWithReturnValue(target=update_package.update_package, args=(ip, ))
        t.start()
        r = t.join()

        if r:
            msg = "upload package successfully!"
        else:
            msg = "upload package failed! Please check ip or net..."
            
        self.showDialog(msg)
        # Note! Back to the working directory...
        os.chdir(self.cwd)
        
""" opencv draws dashed lines:
    https://stackoverflow.com/questions/26690932/opencv-rectangle-with-dotted-or-dashed-lines
    example: drawDashLine(frame, (218, 188), (338, 217))
"""
def drawDashLine(img, pt1, pt2, color=(0, 0, 0), thickness=2, style="dotted", gap=10):
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in np.arange(0, dist, gap):
        r = i/dist
        x = int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y = int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x, y)
        pts.append(p)

    if style == "dotted":
        for p in pts:
            cv2.circle(img, p, thickness, color, -1)
    else:
        s = pts[0]
        e = pts[0]
        i = 0
        for p in pts:
            s = e
            e = p
            if i%2 == 1:
                cv2.line(img, s, e, color, thickness)
            i += 1