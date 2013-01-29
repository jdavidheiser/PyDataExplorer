import matplotlib
from matplotlib.figure import Figure
from numpy import arange, sin, pi
import pylab
import math

import wx
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.backends.backend_wx import FigureCanvasWx

from mpl_toolkits.mplot3d import Axes3D
import numpy as npy
import matplotlib.cm as cm
import traceback

error_checking = True	

#matplotlib.use('WXAgg')

''' Contains plotting routines

NOTE:  Plotting routines expect data to be passed as transposed - ie each "column"
is actually a row - this is to enable us to reference the data as:
data[column] - eliminating need to use numpy arrays or for loops to access the specific chunk
of data we want'''

def scaleaxislims(x, y):
	# strip out any None's we've padded with, because they break min and max
	x = filter(None, x)
	y = filter(None, y)
	x_min = min(x)
	x_max = max(x)
	# round these values to no more than 3 decimal places so we can get some reasonable limits on the plot!

	x_span = x_max - x_min
		
	y_min = min(y)
	y_max = max(y)

	# round these values to no more than 3 decimal places so we can get some reasonable limits on the plot!
	y_span = y_max - y_min
	
	if x_span < 0.1:
		x_span = 0.1
	if y_span < 0.1:
		y_span = 0.1
	#print 'before', x_max,  x_min,  y_max,  y_min
	x_min -= 0.2 * x_span
	x_max += 0.2 * x_span
	
	y_min -= 0.2 * y_span
	y_max += 0.2 * y_span
	#print 'after', x_max,  x_min,  y_max,  y_min
	return [x_min, x_max, y_min,  y_max]

def default_axes_setup(axes):
	# Add any universal axes options you would like to see in all plots to this function.
	# it will turn on those options for all of the main plot types defined here, with the exception of 3d plots.
	axes.grid(True)
	


def compute_3d_coordinates(z_data,x_end,y_end):
	# assume that Z data is passed as a 2d array X by Y in size, and get the number of points from that
	
	(num_x_points,num_y_points) = npy.shape(z_data)
	x_values = npy.linspace(0,x_end,num_x_points)
	y_values = npy.linspace(0,y_end,num_y_points)
	# meshgrid wants arguments in the form of y,x - even though we use x,y everywhere else. 
	y_data,x_data = npy.meshgrid(y_values,x_values)
	return x_data,y_data

class plot(wx.Panel):
	# This is a generic plotting class which contains most of the various plots that will be created using matplotlib
	# the plot initiates a plotting panel with a figure inside of it, and that figure can then be configured by each of the various
	# individual plot commands.  This gives flexibility to create a single generic plot panel and plot different things within it, depending on conditions.
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, 1)
		
		self.fig = Figure((5,4), 75)
		
		self.fig.set_facecolor("white") 
		self.canvas = FigureCanvasWxAgg(self, 1, self.fig)
		#self.canvas = FigureCanvasWx(self, 1, self.fig)
		
		# Now put all into a sizer
		sizer = wx.BoxSizer(wx.VERTICAL)
		# This way of adding to sizer allows resizing
		sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
		self.SetSizer(sizer)
		self.Fit()
		
	def clear_figure(self):
		# This is an awful hack to work around a bug in matplot3d - it creates the axes in a wonky, confusing way, then when you try to clear 
		# the figure, it confuses the axes list when trying to delete them
		# the solution is to delete it twice so all the axes get removed, and catch the exception while we are at it.
		# It's probably a good idea to check whether this is still necessary, the next time the matplotlib team revs the code
		# this problem was first seen in matplotlib versions 1.1
		
		try:
			self.fig.clear()
		except:
			self.fig.clear()
			pass
		
	def plot_2d(self, data = None, x_column = None, y_column = None, title = None,x_axis_label = 'X', y_axis_label='Y'):
		# plots simple two dimensional data, x vs y
		if data == None:
			raise ImageException('data not specified')
		if x_column == None:
			raise ImageException('X data column not specified')
		if y_column == None:
			raise ImageException('Y data column not specified')
		x_data = data[int(x_column)]
		y_data = data[int(y_column)]
		self.clear_figure()
		axes = self.fig.add_subplot(111)
		axes.cla()
	
		self.fig.subplots_adjust(bottom = 0.2)
		if title:
			axes.set_title(title)			 
		axes.set_xlabel(x_axis_label)
		axes.set_ylabel(y_axis_label)
		axes.axis(scaleaxislims(x_data, y_data))
		
		axes.plot(x_data, y_data, '-', label='') 
		
		default_axes_setup(axes)
		#axes.grid(True)
		#axes.legend(numpoints=1)	
		self.canvas.draw()


	
	def plot_2d_double(self, data, x1_column,y1_column,x2_column,y2_column,title = None,x1_label='X1',y1_label='Y1',x2_label='X2',y2_label='Y2'):
		# this plots two sets of 2d data, one above the other, and is meant to serve as an example of how to use subplots
		# to combine more complicated plots together into a single panel.  Similar functions can be created for 
		# specialty plots for a specific data set type.
		# x1,y1 is plotted on top, and x2,y2 on the bottom
		
		#\todo - figure out what to do if these columns aren't the same length
		# numpy is not happy with trying to make an array out of two different-length plots
		x1_data = data[int(x1_column)]
		y1_data = data[int(y1_column)]
		x2_data = data[int(x2_column)]
		y2_data = data[int(y2_column)]

		self.clear_figure()
		axes = self.fig.add_subplot(211)
		axes.cla()
	
		self.fig.subplots_adjust(bottom = 0.2)
		if title:
			axes.set_title(title)			 
		axes.set_xlabel(x1_label)
		axes.set_ylabel(y1_label)
		axes.axis(scaleaxislims(x1_data, y1_data))
		
		axes.plot(x1_data, y1_data, '-', label='') 
		
		default_axes_setup(axes)
		
		axes2 = self.fig.add_subplot(212)
		axes2.set_xlabel(x2_label)
		axes2.set_ylabel(y2_label)
		axes2.axis(scaleaxislims(x2_data, y2_data))
		axes2.plot(x2_data, y2_data, '-', label='') 
		
		default_axes_setup(axes2)
		#axes.grid(True)
		#axes.legend(numpoints=1)	
		self.canvas.draw()
	
	
		
	def plot_3d(	self, z_data, x_coverage,y_coverage,title = None, x_axis_label = 'X', y_axis_label='Y', z_axis_label='Z'):
		# 3D plotting is sort of a pain in the neck, and heavily dependent on data formatting.  This routine assumes that you are
		# providing the z height data as a two dimensional array array, and that the overall X and Y spans are
		# given, so the routine can automatically compute arrays comprising the X and Y positions.  If your data files contain the X and Y
		# positions explicitly, this routine AND the data file reader will require heavy modification to ensure that the data gets
		# passed and plotted correctly.
	
		# takes Z data as an X by Y array of z values, and computes the X and Y arrays based on the "coverage" provided and the size
		# of the Z array
		
		#\todo design a better way of handling x and y coordinates
		# these might be passed as strings by the config parser, so ensure that they are recast as integers
		#\todo use configobj validators to handle this casting
		x_coverage = int(x_coverage)
		y_coverage = int(y_coverage)
		
		z_data = npy.array(z_data)
		self.clear_figure()
		# set up some borders
		# these borders never go away, and screw up the other plots - leave them out until a better way is found to elegently fix them
		#self.fig.subplots_adjust(left=0.05)
		#self.fig.subplots_adjust(right=0.95)
		#self.fig.subplots_adjust(top=0.97)
		#self.fig.subplots_adjust(bottom = 0.03)
		axes = self.fig.add_subplot(111, projection='3d')
		
		# allow us to use the mouse to spin the 3d plot around
		Axes3D.mouse_init(axes)
		
		(x_data,y_data)=compute_3d_coordinates(z_data,x_coverage,y_coverage)

		axes.plot_wireframe(x_data, y_data, z_data)
		
		if title:
			axes.set_title(title)
		axes.set_xlabel(x_axis_label)
		axes.set_ylabel(y_axis_label)
		axes.set_zlabel(z_axis_label)
		
		self.canvas.draw()

	

	def dummy_plot(self):
		#axes = self.fig.add_subplot(111)
		
		# this will allow us to make sure the axes are only set once.  If we don't use self.axes, a new axes object will be created
		# each time we plot does this replace the current one?  This is not strictly necessary and was done here for experimental
		# purposes
		
		try: 
			self.axes
		except:
			self.axes = self.fig.add_axes([0.1, 0.3,0.8, 0.6]) 
			print "updating axes"

		self.axes.cla()
		self.axes.set_ylabel('test plot $\lambda ^2$')
		
		t = arange(0.0,3.0,0.01)
		s = sin(2*pi*t)
		self.axes.plot(t,s,'*',  label = 'plot one')
		self.axes.plot(t, s+1, '.', label = 'plot 2')
		self.axes.plot(t-0.5, s, '^', label = 'plot 3')
		self.axes.plot(t, s-1, label = 'plot 4')
		from time import gmtime, strftime
		currtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		print currtime
		self.axes.set_title(currtime)
		self.axes.legend(bbox_to_anchor=(0., -0.1, 1., -0.1), loc=1 , 
								ncol=2, mode="expand", borderaxespad=0., numpoints=1)
		self.fig.text(0.8, 0.8, 'test text')
		self.fig.text(0.8, 0.75, 'test text 2', color='blue')
		self.canvas.draw()
		

	def onEraseBackground(self, evt):
		# this is supposed to prevent redraw flicker on some X servers...
		pass





ERR_TOL = 1e-5 # floating point slop for peak-detection

class PlotPanel(wx.Panel):
  #THIS IS SIMPLY AN EXAMPLE OF HOW TO CREATE A PLOT PANEL - IT SERVES NO PURPOSE EXCEPT TESTING WXPYTHON TO MAKE SURE IT'S WORKING CORRECTLY.
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.fig = Figure((5,4), 75)
        self.canvas = FigureCanvasWxAgg(self, -1, self.fig)
        self.toolbar = Toolbar(self.canvas) #matplotlib toolbar
        self.toolbar.Realize()
        #self.toolbar.set_active([0,1])

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def init_plot_data(self):
        a = self.fig.add_subplot(111)

        x = npy.arange(120.0)*2*npy.pi/60.0
        y = npy.arange(100.0)*2*npy.pi/50.0
        self.x, self.y = npy.meshgrid(x, y)
        z = npy.sin(self.x) + npy.cos(self.y)
        self.im = a.imshow( z, cmap=cm.jet)#, interpolation='nearest')

        zmax = npy.amax(z) - ERR_TOL
        ymax_i, xmax_i = npy.nonzero(z >= zmax)
        if self.im.origin == 'upper':
            ymax_i = z.shape[0]-ymax_i
        self.lines = a.plot(xmax_i,ymax_i,'ko')

        self.toolbar.update() # Not sure why this is needed - ADS

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def OnWhiz(self,evt):
        self.x += npy.pi/15
        self.y += npy.pi/20
        z = npy.sin(self.x) + npy.cos(self.y)
        self.im.set_array(z)

        zmax = npy.amax(z) - ERR_TOL
        ymax_i, xmax_i = npy.nonzero(z >= zmax)
        if self.im.origin == 'upper':
            ymax_i = z.shape[0]-ymax_i
        self.lines[0].set_data(xmax_i,ymax_i)

        self.canvas.draw()

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

if __name__ == '__main__':

	class MainFrame(wx.Frame):
		def __init__(self, parent, title):
			wx.Frame.__init__(self, parent, title=title, size=(1024,768))
			
			Notebook = wx.Notebook(self)
			
			plot1 = plot(Notebook)
			x_data=[1,2,3,4,5,6]
			y_data = npy.random.random(6)
			data=npy.column_stack((x_data,y_data))
			plot1.plot_2d( data, x_column=0, y_column=1,title="test 2d plot")
			Notebook.AddPage(plot1, '2d plot - random data')
			
			plot2 = plot(Notebook)
			# 3d plot example - grab dummy data from mpl
			from mpl_toolkits.mplot3d import axes3d
			#discard X and Y data - we will provide coverage when we call plot_3d
			X, Y, Z = axes3d.get_test_data(0.5)
			plot2.plot_3d(title="test 3d plot", z_data = Z,x_coverage=5,y_coverage=10)
			Notebook.AddPage(plot2,'3d Plot')
			
			plot3 = plot(Notebook)
			x1 = npy.arange(-10,10,0.5)
			x2 = npy.arange(0,20,0.5)
			data=npy.column_stack((x1,x1**2,x2,x2**3))
			plot3.plot_2d_double(data,0,1,2,3)
			Notebook.AddPage(plot3,'double 2dplot')
			
	##        panel.Layout()
			self.Show(True)

	app = wx.App(False)
	frame = MainFrame(None, "Plot test")
	#frame = wx.Frame(None)
	app.MainLoop()
