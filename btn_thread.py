# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
from threading import Thread
import wx
from pubsub import pub

from thread_with_return_value import ThreadWithReturnValue


class BtnThread(Thread):
    """
    Button Worker Thread
    """
    def __init__(self, *args, **kwargs):	   
        super(BtnThread, self).__init__()
        
        self.config = args[0]
        self.btn_task = args[1]
        self.DoLoadFile = args[2]
        self.init = args[3]
        
        self.cwd = os.getcwd()

        self.setDaemon(True)
        self.start() # start the thread
        
    def run(self):
        """
        Run Worker Thread
        """        
        # ---------- Check device start ---------- #
        # pub.sendMessage("log", msg="Check device existence")

        t = Thread(target=self.start_btn_task, args=(self.btn_task, ))
        t.start()
        t.join()
        # ---------- Check device end ---------- #
        
    def start_btn_task(self, item):
        try:
            if item == "LOAD_VIDEO":
                # step 1: select video path
                wildcard = "Video (*.mp4)|*.mp4"
                cwd = r""+self.cwd+"/videos/"
                #print(cwd)
                dialog = wx.FileDialog(None, "Select Video", cwd, "", wildcard, wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
                if dialog.ShowModal() == wx.ID_OK:
                    #print(dialog.GetPath())
                    video_path = dialog.GetPath()
                    dialog.Destroy()
                    
                    # step 2: prepare the task
                    wx.CallAfter(self.DoLoadFile, video_path)
                
                else:
                    # back to main thread
                    dialog.Destroy()
                
            else:
                print("Thread item does not exist.")
                sys.exit(999)

        except Exception as e:
            print(e)
            
        finally:
            wx.CallAfter(self.init)