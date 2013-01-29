#!/usr/bin/env python
import os
import wx
import sys, inspect

import DataExplorerGui

		
class MyPanel(wx.Panel):
		def __init__(self, parent, id, title):
			wx.Panel.__init__(self, parent, id)
			sizer = wx.BoxSizer(wx.VERTICAL)
			mybutton = wx.Button(self, 1, 'Read File Contents', (100,100))
			self.Bind (wx.EVT_BUTTON, self.OnShowCustomDialog, id=1)
			sizer.Add(mybutton,0,wx.ALIGN_CENTER,5)
			self.textbox = wx.TextCtrl(self,-1,style=wx.TE_MULTILINE|wx.HSCROLL)
			sizer.Add(self.textbox,1,wx.EXPAND)
			
			# use a lambda function to pass data through the wx event - see http://stackoverflow.com/questions/173687/is-it-possible-to-pass-arguments-into-event-bindings
			# see also : http://wiki.wxpython.org/Passing%20Arguments%20to%20Callbacks

			file_button = wx.Button(self,label = "Read File Name")
			self.filename_box = wx.TextCtrl(self,size=wx.Size(600,25))
			file_button.Bind(wx.EVT_BUTTON,  lambda event: self.open_data_files(event, "1", 
			self.filename_box ) )
			sizer.Add(file_button)
			sizer.Add(self.filename_box)
			self.SetSizer(sizer)
			
		def OnShowCustomDialog(self, event):
			dia = DataExplorerGui.DataFileOpenDialog(self, -1, 'buttons')
			retval = dia.ShowModal()
			if retval == wx.ID_OK:
					filename = dia.GetFilename()
					
					f = open(filename)
					self.textbox.WriteText(f.read())        
					self.textbox.SetInsertionPoint(0)
			#else:
			#       print "canceled"
			
			dia.Destroy()
	
		
		def open_data_files(self, event,  probe_number, filename_box):
			dia = DataExplorerGui.DataFileOpenDialog(self, -1, 
					'Select Data File for Probe %s'  %(probe_number) )
			
			retval = dia.ShowModal()
			if retval == wx.ID_OK:
				#print dia.GetFilename()
				filename_box.SetValue(dia.GetFilename())					
			else:
				print "canceled"
			
			dia.Destroy()
			
			
		def OnDestroy(self,event):
			print "panel has been destroyed"

class MainFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(1024,768))
		panel = MyPanel(self,-1,title)
##        panel.Layout()
		self.Show(True)
		
		# Open the dialog instead of loading as a frame
##        dia = AMS_File_Dialog.AMSDataFileOpenDialog(self, -1, 'helloAcertara')
##        retval = dia.ShowModal()
##        self.Close(True)

app = wx.App(False)
frame = MainFrame(None, "Python Browser")
app.MainLoop()
