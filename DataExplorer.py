#!/usr/bin/env python
import os
import wx
import sys, inspect

import DataExplorerGui

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1024,768))
        
        expPanel = DataExplorerGui.ExplorerPanel(self)
        self.Show(True)

        # Open the dialog instead of loading as a frame
##        dia = DataExplorerGui.DataFileOpenDialog(self, -1, 'Open a file')
##        retval = dia.ShowModal()
##        self.Close(True)

app = wx.App(False)
frame = MainFrame(None, "PyDataExplorer File Browser")
app.MainLoop()
