# Copyright (c) 2013, James Davidheiser
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution. 

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.



import os
import wx
import time
from wx.lib.mixins.listctrl import ColumnSorterMixin
import matplot
import sys
from DataFileReader import DataFileReader
using_win32api = True
try:
	from win32api import GetLogicalDriveStrings
except:
	using_win32api = False
import CustomGrid
from configobj import ConfigObj
import numpy as npy

class FileListCtrl(wx.ListCtrl,ColumnSorterMixin):
# File list control is a custom list control that acts as an explorer file list
# it shows directories and files, and allows navigation by double-clicking
# on directories, or .. to go up one directory
# it can be futher embedded in more elaborate panels to provide a fully featured
# file explorer implemented from the ground up in Python


	def __init__(self, parent, id=wx.ID_ANY,extension_list = None):
		#print 'MyListCtrl init called'
		self.parent = parent
		wx.ListCtrl.__init__(self, parent, id, style=wx.BORDER_RAISED|wx.LC_REPORT)
		
		if extension_list==None:
			raise Exception('extension list not specified')
			
		self.extension_list = extension_list
		
		numcolstosort=4
		ColumnSorterMixin.__init__(self,numcolstosort)
		
		#images = ['images/empty.png', 'images/folder.png', 'images/source_py.png', 'images/image.png', 'images/pdf.png', 'images/up16.png']
		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Ext')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Modified')

		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 70)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 420)

		# self.il = wx.ImageList(16, 16)
		# for i in images:
			# self.il.Add(wx.Bitmap(i))
		#self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.all_results_list = []
		self.update()
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDoubleClick, id=id)
#		self.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.FileSelect, id=id)
		
	
#	def FileSelect(self,event):
#		event.Skip()

	# Always secondary sort on the first column, except if that one is sorted, then sort on
	# the second column
	# see http://wxpython-users.1045709.n5.nabble.com/Secondary-sorting-of-a-ListCtrl-td4941409.html
	def GetSecondarySortValues(self, col, key1, key2):
		
		sscol = 1 if col == 0 else 0
		def ss(key):
			return self.itemDataMap[key][sscol]
		return (ss(key1), ss(key2))
	#\todo - fix sorting on size column
		
		
	def GetListCtrl(self):
		return self

	def SetExtensionList(self,extension_list):
		self.extension_list = extension_list
		self.update()
		
	def update(self,current_dir = None):
	
		if current_dir:
			# if we are specifying a directory to switch to, and it's the same as our current
			# directory, we don't want to refresh it, since it takes forever. 
			if current_dir.upper() == os.getcwd().upper():
				return
			else:
				os.chdir(current_dir)
				
		self.DeleteAllItems()
		id = self.GetId()

		files = os.listdir('.')
		self.itemDataMap = {}
		
		j = 1
		index = self.InsertStringItem(0, '..')
		self.itemDataMap[0] = ('..','','','')
		self.SetItemData(index,0)
		#self.SetItemImage(0, 4)

		#  This will hide any files that are not explicitly configured for plotting.  This leads to a cleaner
		#  interaction if you're usig the panel for nothing but data exploration
		#  for use as a more general file explorer, this could be modified significantly.
		for i in files:
			if os.path.isdir(i):
				name = i
				ext = ""
			else:
				(name, ext) = os.path.splitext(i)
			ex = ext[1:]
			if ex in self.extension_list or os.path.isdir(i):
			#if ex in ['wfm','txt'] or os.path.isdir(i):
				size = os.path.getsize(i)
				sec = os.path.getmtime(i)
				index = self.InsertStringItem(j, name)
				self.SetStringItem(j, 1, ex)
				self.SetStringItem(j, 2, str(size) + ' B')
				self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))

				self.SetItemData(index,j)
				self.itemDataMap[j] = (name, ex, str(size) + 'B', time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)) )
				# if os.path.isdir(i):
					# self.SetItemImage(j, 4)
				# elif ex == 'wfm':
					# self.SetItemImage(j, 3)
				# elif ex == 'xcn':
					# self.SetItemImage(j, 2)
				# elif ex == 'rst':
					# self.SetItemImage(j, 1)
				# else:
					# self.SetItemImage(j, 5)

				#if (j % 2) == 0:
				#	self.SetItemBackgroundColour(j, '#e6f1f5')
				j += 1

	
	def OnDoubleClick(self,event):
		
		item = event.GetItem()
		item_name = item.GetText().encode('ascii')
		#print "Item selected:", item_name
		if os.path.isdir(item_name):
			current_dir = os.getcwd()
			
			os.chdir(os.path.join(current_dir,item_name))
			
			self.update()
		event.Skip()
	
class ExplorerPanel(wx.Panel):
	'''Explorer Panel is a fully featured plot-focused data file explorer, which embeds both the file
	list control and the Python directory tree controle, with matplotlib graphing.
	All of these GUI elements are laid out with splitter windows, so that they can be resized by
	the user
	
	It reads configuration options from a config file config.cfg
	'''
	def __init__(self, parent,id=wx.ID_ANY):
		
		wx.Panel.__init__(self,parent,-1)
		
		master_splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
		# wxpython behaves strangely if we set the minimum pane size too small, and it resizes the windows to an obnoxiously
		# small size - by setting the minimum to 100, wxpython will, by default, split the windows evenly in half, with the option
		# to resize them down as small as 100 pixels wide.
		master_splitter.SetMinimumPaneSize(100)
		top_splitter = wx.SplitterWindow(master_splitter, -1, style=wx.SP_3D)
		top_splitter.SetMinimumPaneSize(100)
		
		self.dir = wx.GenericDirCtrl(top_splitter, -1, dir='/home/', style=wx.DIRCTRL_DIR_ONLY|wx.BORDER_RAISED)
		self.dir.SetPath(os.getcwd())
		
		# set up the config file
		self.config = ConfigObj('config.cfg')

		
		# get the list of possible extensions from the config file
		extension_list = self.config['Extensions'].keys()
		
		self.FileList = FileListCtrl(top_splitter,-1,extension_list=extension_list)

		
		self.bottom_panel = wx.Panel(master_splitter)
		self.bottom_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.plot = matplot.plot(self.bottom_panel)
		self.bottom_panel_sizer.Add(self.plot,1,wx.EXPAND)
	
		#self.textbox = wx.TextCtrl(self.bottom_panel,-1,style=wx.TE_MULTILINE|wx.HSCROLL)
		#self.bottom_panel_sizer.Add(self.textbox,1,wx.EXPAND)

		self.spreadsheet = CustomGrid.SpreadSheet(self.bottom_panel)
		self.bottom_panel_sizer.Add(self.spreadsheet,1,wx.EXPAND)
		
		self.bottom_panel.SetSizer(self.bottom_panel_sizer)
		
		#self.textbox.WriteText('**************************************************')
		self.tree = self.dir.GetTreeCtrl()
		
		
		master_splitter.SplitHorizontally(top_splitter, self.bottom_panel)
		top_splitter.SplitVertically(self.dir, self.FileList,300)
				
		sizer = wx.BoxSizer(wx.VERTICAL)
		


		# add combo box for text representation of current directory
		if using_win32api:
			drives = GetLogicalDriveStrings()
			drives = drives.split('\000')[:-1]
		else:
			drives = []
		self.combobox = wx.ComboBox(self,choices=drives,size=(800,25),style=wx.TE_PROCESS_ENTER)
		
		self.Bind(wx.EVT_COMBOBOX,self.OnComboboxSelect,id=self.combobox.GetId())
		self.Bind(wx.EVT_TEXT_ENTER,self.OnComboboxSelect,id=self.combobox.GetId())
		sizer.Add(self.combobox,0)
		# add the master splitter window AFTER the text input box for directory
		sizer.Add(master_splitter, 1, wx.ALL|wx.EXPAND, 5)
		
		self.SetSizer(sizer)

		#bind event for when user clicks on an item in the tree
		wx.EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.OnDirTreeSelect)
		#self.FileSelect(0)
		wx.EVT_LIST_ITEM_SELECTED(self,self.FileList.GetId(),self.FileSelect)
		wx.EVT_LIST_ITEM_ACTIVATED(self, self.FileList.GetId(),self.OnDoubleClick)
		#self.plot.dummy_plot()
		self.OnDirTreeSelect(0)
		self.header = None
		
	def __del__(self):
		'''cleanup functions for when the class is destroyed - especially useful for saving the config file
		if, for example, the panel is being called from another part of the GUI, and being repeatedly created
		and destroyed, such as when being used as a file open dialog (see DataFileOpenDialog)'''
		
		# this ensures that any changes to the config file (ie, current directory information) have been saved
		# it also ensures that, if the panel is destroyed and re-opened, it is able to read the config file again.
		self.config.write()
		wx.Panel.__del__(self)

		
	def ChangeDirectory(self,path):
		
		self.dir.SetPath(path)
		self.FileList.update()
		
	def OnDoubleClick(self,event):
		# This catches the double click event from the file list window.
		# When you double click on a file in the file list window, it should change
		# the directory for that file list.
		# this is handled in the file list panel
		# it should also update the tree control to display the current directory.
		# this is handled here
		#self.dir.SetPath(os.getcwd())
		self.dir.ExpandPath(os.getcwd())
		event.Skip()
	
	

	def OnDirTreeSelect(self, event):
		# draws list of items defined by files in current directory (upper right window)
		self.FileList.update(self.dir.GetPath())
		if event:
			event.Skip()
		#make sure the event can be seen by higher level windows
		#list = os.listdir(self.dir.GetPath())
		self.UpdateCombobox(event)

		
	def GetFirstSelectedFilename(self):
		
		index = self.FileList.GetFirstSelected()
		if index == -1:
			return None
		else:
			item = self.FileList.GetItem(index,0)
			filename = item.GetText().encode('ascii')
			item = self.FileList.GetItem(index,1)
			extension = item.GetText().encode('ascii')
			if extension:
				filename = filename + '.' + extension
			return filename

	def FileSelect(self,event):
		''' this routine will plot and display the data when a file is selected'''
		# get the filename and extension of the first selected filename
		(filename, ext) = os.path.splitext(self.GetFirstSelectedFilename())
		ext=ext[1:]
		
		if ext in self.config['Extensions'].keys():
			# get the config for this particular extension
			cfg = self.config['Extensions'][ext]
			reader = DataFileReader()
			if cfg.has_key('headerlines'):
				headerlines = int(cfg['headerlines'])
			else:
				headerlines = 0
			reader.read_from_file(filename+'.'+ext, headerlines)
			plot_function = getattr(self.plot,cfg['plot_type'])
			# use map to transpose the data and pad any lines that are shorter than the rest with Nones
			# this allows us to reference 'rows' instead of 'columns' in the plotting routines
			# pass a reference to the dictionary of all options read from the config file
			plot_function(map(None,*reader.data),**cfg['options'])
			
		#\todo Update this to show the data AND the header
		# in previous usage, the header contained values derived from the raw data - this is not going to be
		# true for all generic use cases.
			self.spreadsheet.SetData( reader.header + reader.data )
		
		else:
			#this isn't one of our defined data types
			self.spreadsheet.SetData([])

		event.Skip()
	def UpdateCombobox(self,event):
		path = os.getcwd()
		self.combobox.SetValue(path)
		if not path in self.combobox.GetStrings():
			self.combobox.Insert(path,0)
		
	
	def OnComboboxSelect(self,event):
		
		value = self.combobox.GetValue()
		self.ChangeDirectory(value)

class ToggledExplorerPanel(wx.Panel):
	# This is an example that adds toggle buttons to the standard explorer panel - these buttons allow the user to disable
	# the plot and/or spreadsheet window views.  This is extremely handy if you want to, for example, only examine the plots
	# because you can recover the space used by the spreadsheet view.
	def __init__(self, parent,id=wx.ID_ANY,extension_list = None):
		wx.Panel.__init__(self,parent,-1)
	
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.ExplorerPanel = ExplorerPanel(self)
		sizer.Add(self.ExplorerPanel,1,wx.EXPAND)
		
		self.togglebutton1 = wx.ToggleButton(self,-1,"Hide Plot Window",(20,25))
		self.togglebutton2 = wx.ToggleButton(self, 1, 'Hide Spreadsheet Window', (20, 25))
	
		togglesizer = wx.BoxSizer(wx.HORIZONTAL)
		togglesizer.Add(self.togglebutton1,0)
		togglesizer.Add(self.togglebutton2,0)
		self.Bind(wx.EVT_TOGGLEBUTTON, self.Toggle1, id=self.togglebutton1.GetId())
		self.Bind(wx.EVT_TOGGLEBUTTON, self.Toggle2, id=self.togglebutton2.GetId())
		sizer.Add(togglesizer,0)
		wx.EVT_LIST_ITEM_ACTIVATED(self, self.ExplorerPanel.FileList.GetId(),self.OnDoubleClick)
		self.SetSizer(sizer)
		
	def Toggle1(self,event):
		if self.ExplorerPanel.plot.IsShown():
			self.ExplorerPanel.plot.Hide()
			self.togglebutton1.SetLabel("Show Plot Window")
		else:
			self.ExplorerPanel.plot.Show()
			self.togglebutton1.SetLabel("Hide Plot Window")
			
		self.ExplorerPanel.bottom_panel_sizer.Layout()

		
	def Toggle2(self,event):
		if self.ExplorerPanel.spreadsheet.IsShown():
			self.ExplorerPanel.spreadsheet.Hide()
			self.togglebutton2.SetLabel("Show Spreadsheet Window")

		else:
			self.ExplorerPanel.spreadsheet.Show()
			self.togglebutton2.SetLabel("Hide Spreadsheet Window")
		
		self.ExplorerPanel.bottom_panel_sizer.Layout()
		
	def OnDoubleClick(self, event):
		
		file = self.ExplorerPanel.GetFirstSelectedFilename()
		#print "Item selected:", item_name
		if file:
			os.startfile(file)
			
class DataFileOpenDialog(wx.Dialog):
	''' Data File Open Dialog implements a custom file open dialog for Data files.
	It embeds the Explorer Panel, which includes a directory key, current directory list,
	and plot preview for the currently highlighted data file, along with Open and Cancel buttons
	to select a file.  In addition, double-clicking on a data file will select that file.'''
	def __init__(self, parent, id, title = "Select a data file to open"):
		wx.Dialog.__init__(self, parent, id, title=title,size=(1024,768),style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		
		self.filename = None

		vbox = wx.BoxSizer(wx.VERTICAL)
		panel = wx.Panel(self)
				
		self.exp_panel = ExplorerPanel(panel)


		vbox.Add(self.exp_panel,1,wx.EXPAND)

		bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
		open_button = wx.Button(panel,-1,"Open File")
		cancel_button = wx.Button(panel,-1,"Cancel")
		bottom_sizer.Add(cancel_button,1)
		bottom_sizer.Add(open_button,1)
		
		vbox.Add(bottom_sizer,0,wx.ALIGN_RIGHT)
		panel.SetSizer(vbox)
		borderbox = wx.BoxSizer(wx.VERTICAL)
		borderbox.Add(panel,1,wx.ALL|wx.EXPAND,border=10)
		self.SetSizer(borderbox)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, id=cancel_button.GetId())
		self.Bind(wx.EVT_BUTTON, self.OnOpen,id=open_button.GetId())
		wx.EVT_LIST_ITEM_ACTIVATED(self, self.exp_panel.FileList.GetId(),self.OnDoubleClick)

		
	
	def OnDoubleClick(self,event):
		#all the updating stuff is handled in the sub-classes of the explorer panel
		#the only thing we want to add here is, if the item selected is a file
		#we want to open it
		
		# we have already checked if it's a directory or not at this point, and changed directories if it is, so 
		# let's just call OnOpen()

		self.OnOpen()

	
	

	def OnCancel(self,event):
		#self.Close()
		self.EndModal(wx.ID_CANCEL)

	def OnOpen(self, event=None):
		# we don't care about the event, since we're using the getfirstselectedfilename functionality from the explorer panel
		# this is primarily because the extension is stored in a separate column from the filename.
		file = self.exp_panel.GetFirstSelectedFilename()
		if file:
			current_dir = os.getcwd()
			
			if os.path.isdir(file):
				pass
				# This should, theoretically, never be a directory, since the first thing that happens when we double-click a directory is that the explorer panel changes directories
				# and the window updates such that no item is currently selected
				
				# however, just in case it does somehow get to this point with a directory, due to a network read error or something, don't return the directory name, just quietly pass
				# the bound function and keep the dialog open.
				# 
			else:
				self.filename = os.path.join(current_dir, file)
				self.EndModal(wx.ID_OK)

	def GetFilename(self):
		return self.filename
