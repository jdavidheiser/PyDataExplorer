# use wxPython's wx.lib.sheet.CSheet widget
# to create a simple spread sheet

import wx
import wx.lib.sheet
import string


class GenericTable(wx.grid.PyGridTableBase):

	def __init__(self, data, rowLabels=None, colLabels=None):
		wx.grid.PyGridTableBase.__init__(self)
		self.data = data
		self.rowLabels = rowLabels
		self.colLabels = colLabels
		self.currentRows = self.GetNumberRows()
		self.currentColumns = self.GetNumberCols()
		
	def GetNumberRows(self):
		if self.data:
			return len(self.data)
		else:
			return 0

	def GetNumberCols(self):
		numcols = 0
		if self.data:
			for row in self.data:
				tmp = len(row)
				if tmp > numcols:
					numcols = tmp
		
		return numcols

	def GetColLabelValue(self, col):
		if self.colLabels and col < len(self.colLabels):
			return self.colLabels[col]
		else:
			counter = 1
			while col >= 26:
				col = col-26
				counter+=1
			return string.uppercase[col]*counter	
				
		
	def GetRowLabelValue(self, row):
		if self.rowLabels and row < len(self.rowLabels):
			return self.rowLabels[row]
		else:
			return str(row)
		
	def IsEmptyCell(self, row, col):
		return False

	def GetValue(self, row, col):
		try:
			return self.data[row][col]
		except:
			return ""

	def SetValue(self, row, col, value):
		pass         
	
	def IsEmptyCell(self, row, col):
		"""Return True if the cell is empty"""
		return False

	def GetTypeName(self, row, col):
		"""Return the name of the data type of the value in the cell"""
		return None
	
	def DeleteRows(self,currentrows,newrows):
		pass
		
	def AppendCols(self,numcols):
		pass

		
	def SetData(self,data):
		self.data = data
		self.ResetView()
		self.currentRows = self.GetNumberRows()
		self.currentColumns = self.GetNumberCols()
		#self.UpdateValues()

	
	
	def getGrid(self):
		return wx.grid.PyGridTableBase.GetView(self)
	
	def UpdateValues( self ):
		"""Update all displayed values"""
		msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
#		self.getGrid().ProcessTableMessage(msg)
		self.getGrid().ProcessTableMessage(msg)
		
		# does this actually do anything?
		# \todo check if it does anything
		#wx.CallAfter(self.SendSizeEvent)
		self.getGrid().ForceRefresh()

		
	def ResetView(self):
				"""Trim/extend the control's rows and update all values"""
				self.getGrid().BeginBatch()
				for current, new, delmsg, addmsg in [
						(self.currentRows, self.GetNumberRows(), wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
						wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
						(self.currentColumns, self.GetNumberCols(), wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,
						wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
				]:
						#print 'new:',new,'current:',current
						if new < current:
								msg = wx.grid.GridTableMessage(
										self,
										delmsg,
										new,    # position
										current-new,
								)
								self.getGrid().ProcessTableMessage(msg)
						elif new > current:
								msg = wx.grid.GridTableMessage(
										self,
										addmsg,
										new-current
								)
								self.getGrid().ProcessTableMessage(msg)
				self.UpdateValues()
				self.getGrid().EndBatch()

				# The scroll bars aren't resized (at least on windows)
				# Jiggling the size of the window rescales the scrollbars
				#h,w = grid.GetSize()
				#grid.SetSize((h+1, w))
				#grid.SetSize((h, w))
				#grid.ForceRefresh()
#

		
	
                   
				   
class SpreadSheet(wx.lib.sheet.CSheet):
	instance = 0
	def __init__(self, parent, rows=None, cols=None, data_list=[[]]):
		wx.lib.sheet.CSheet.__init__(self, parent)
		self.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
		
		self.text = ''

		self.mytable = GenericTable(data_list)

#		mytable = GenericTable()
		self.SetTable(self.mytable)
		
		#source = data_list
		
		# set the rows and columns of the sheet
		#self.SetNumberRows(rows)
		#self.SetNumberCols(cols+10)

		# # set row height and column width
		# row_size = 20
		# for row in range(self.GetNumberRows()):
			# self.SetRowSize(row, row_size)
		# col_size = 60
		# for col in range(self.GetNumberCols()):
			# # make name and role columns wider
			# if col < 2:
				# self.SetColSize(col, col_size + 80)
			# else:
				# self.SetColSize(col, col_size)

		# # set column lable titles at the top
		# for ix, title in enumerate(data_list[0]):
			# self.SetColLabelValue(ix, title)

		# # create reusable attribute objects for all cells
		# self.attr = wx.grid.GridCellAttr()
		# self.attr.SetTextColour('black')
		# self.attr.SetBackgroundColour('yellow')
		# self.attr.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

		# # now load the data_list into the spread sheet cells
		#self.loadCells(data_list)

	def loadCells(self, data_list):
		# find rows and columns the data needs
		self.drows = len(data_list)
		self.dcols = len(data_list[0])
		# note that the title row=0 is taken
		for row in range(1, self.drows):
			# set cell attributes for the whole row
			self.SetRowAttr(row-1, self.attr)
			for col in range(self.dcols):
				value = data_list[row][col]
				#print row, col, value  # testing ...
				self.SetCellValue(row-1, col, value)
				# align numbers to the right
				if col > 1:
					self.SetCellAlignment(row-1, col,
						wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)

		# optional extra information at the end
		self.SetCellTextColour(row, 0, 'red')
		self.SetCellBackgroundColour(row, 0, 'white')
		# wx.Font(pointSize, family, style, weight, underline=false,
		#     faceName="", encoding=wx.FONTENCODING_DEFAULT)
		# family: wx.DEFAULT, wx.DECORATIVE, wx.ROMAN, wx.SCRIPT, wx.SWISS,
		#     wx.MODERN
		# style: wx.NORMAL, wx.SLANT or wx.ITALIC
		# weight: wx.NORMAL, wx.LIGHT or wx.BOLD
		font = wx.Font(8, wx.ROMAN, wx.ITALIC, wx.NORMAL)
		self.SetCellFont(row, 0, font)
		text = "The cast of Hallo Yankee Mama"
		self.SetCellValue(row, 0, text)

	def OnLeftClick(self, event):
		"""
		a CSheet method
		cell is left-clicked, get cell data
		"""
		

		r = event.GetRow()
		c = event.GetCol()
		#text = self.GetCellValue(r, c)
		#self.GetParent().SetTitle(text)  # test ...
		# move the cursor to the selected cell
		self.SetGridCursor(r, c)
				
	def SetData(self,data):
		self.mytable.SetData(data)


class MyFrame(wx.Frame):
	def __init__(self, parent, mytitle, mysize, data_list):
		wx.Frame.__init__(self, parent, wx.ID_ANY, mytitle, size=mysize)

		# create the spread sheet
		# give it enough rows and columns to fit all the data
		rows = 18
		cols = 4
		self.sheet1 = SpreadSheet(self, rows, cols, data_list)
		self.sheet1.SetFocus()
		
if __name__ == '__main__':
	# show a simple test demonstration of the spreadsheet window if it's called by itself
	# this data string could have been loaded from a file
	data_str = """\
	Name, Role, Age, Height
	Gladys Day, Mama, 55, 64
	Alfonso Day, Papa, 60, 67
	Doris Night, Neighbor, 51, 68
	Jonathan Summer, Neighbor, 60, 66
	Elke Winter, Sweety, 51, 70
	Frank Ferkel Day, Son, 25, 74
	Karl Arm, Friend, 32, 73
	Mark Marlboro, Thief, 26, 72
	Larry Lark, Policeman, 22, 69
	Gustav Gurgel, Pizzaman, 19, 61
	Monika Kleinbrust, Niece, 23, 62
	Paul Porkough, Council, 45, 58"""

	# create a data list from the data string
	# this makes it easier to load the spread sheet
	data_list = []
	for line in data_str.split('\n'):
		line_list = line.split(',')
		data_list.append(line_list)

	app = wx.App(0)
	mytitle = "a simple spread sheet"
	width = 450
	height = 380
	exampleFrame = MyFrame(None, mytitle, (width, height), data_list)
	exampleFrame.Show()

	app.MainLoop()
