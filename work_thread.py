# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import wx
from pubsub import pub
from threading import Thread

from thread_with_return_value import ThreadWithReturnValue
import update_package


class WorkThread(Thread):
    """
    Long Tasks Thread
    """
    def __init__(self, *args, **kwargs):	   
        super(WorkThread, self).__init__()
        
        self.ip = args[0]
        
        # Some information
        self.cwd = os.getcwd()
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        self.setDaemon(True)
        self.start() # start the thread
        
    def run(self):
        """
        Run Worker Thread
        """
        t = ThreadWithReturnValue(target=update_package.update_package, args=(self.ip, ))
        t.start()
        pub.sendMessage("updateStatusBar", msg="Running ROI package update...")
        r = t.join()

        if r:
            msg = "Upload package successfully!"
        else:
            msg = "Upload package failed! Please check ip or net..."

        # process after task
        pub.sendMessage("updateStatusBar", msg="Program Idle...")
        
        wx.CallAfter(pub.sendMessage, "showDialog", msg=msg)
        wx.CallAfter(pub.sendMessage, "changeDirectory")
        wx.CallAfter(pub.sendMessage, "enable_state")
        