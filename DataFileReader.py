import numpy as npy
##
#  Contains a generic data file reader class.  The class can be instantiated once, and then called
#  repeatedly to read in different data files, rather than creating a new class for every read.
#  data is read from a provided file name, and palced in self.data, and headers are read into self.header
class DataFileReader():
	##
	#
	#
	def __init__(self):
		self.header = []
		self.data = []
		
	##
	#   read the data from a provided filename.  If headerlines is provided, skip lines at the beginning of
	#   a file before reading data, assuming that there is some header information provided there
	#   if delimiter is provided, use a different character as a delimiter, other than tab.
	def read_from_file(self, filename,headerlines=0,delimiter="\t"):
		#re-initialize header and data every time we do a read, to make sure we aren't overlapping any data
		self.header = []
		self.data = []
		self.headerlines = headerlines
		self.delimiter = delimiter
		f = open(filename)
		for i in range(self.headerlines):
			self.header.append(f.readline().rstrip().split(self.delimiter))
		lines = f.readlines()
		f.close()
		for l in lines:
			# convert data to float values
			# uses list comprehension to cycle through each element in the list which describes the delimited values on a single line		
			self.data.append([float(x) for x in l.rstrip().split(self.delimiter)])
		
