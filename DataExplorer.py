'''This is an extremely simple demo program, which will load up the Data Explorer as a standalone app.
Expansions upon the functionality of the Data Explorer could be contained here without modifying the core
Data Explorer GUI library in any way.'''


#!/usr/bin/env python
import os
import wx


import sys, inspect

import DataExplorerGui

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(1024,768))
		
		expPanel = DataExplorerGui.ToggledExplorerPanel(self)
		self.Show(True)


		
app = wx.App(False)
frame = MainFrame(None, "PyDataExplorer File Browser")
app.MainLoop()
