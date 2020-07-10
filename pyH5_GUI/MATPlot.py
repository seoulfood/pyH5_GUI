import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from PyQt5.QtWidgets import * #(QWidget, QToolTip, QMainWindow, QRadioButton)
from ColorMap import (cmap_cyclic_spectrum, cmap_jet_extended, cmap_vge, cmap_vge_hdr,
                      cmap_albula, cmap_albula_r,cmap_hdr_goldish , color_map_dict )      
import matplotlib.pyplot as plt
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import Slider
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PIL import Image
import h5py

                             
plot_curve_type = [ 'curve', 'g2', 'qiq', 'plot_stack', 'stack_across' ]   # some particular format for curve plot 
plot_image_type = ['image', 'c12']           # some particular format  for image plot
plot_surface_type = ['surface']           # some particular format  for surfce plot
image_colors = ['jet', 'viridis', 'plasma', 'inferno', 'magma', 'cividis']
    
        
class MATPlotWidget(   ):
    def __init__(self, mainWin ):
        #print('Connect to mainWin here')
        self.mainWin= mainWin
        self.resizeEvent = self.mainWin.onresize

    def generatePgColormap(self, cmap ):
        colors = [cmap(i) for i in range(cmap.N)]
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        return pgMap
    
    def get_colormap( self, mainWin ):
        #print( self.colormap_string )
        if self.mainWin.colormap_string == 'default':
            pos = np.array([0., 1., 0.5, 0.25, 0.75])
            color = np.array([[0, 0, 255, 255], [255, 0, 0, 255], [0, 255, 0, 255], (0, 255, 255, 255), (255, 255, 0, 255)],
                 dtype=np.ubyte)
            cmap = pg.ColorMap(pos, color)
            self.mainWin.colormap = cmap
        elif self.mainWin.colormap_string in [ "jet", 'jet_extended', 'albula', 'albula_r',
                                      'goldish', "viridis", 'spectrum', 'vge', 'vge_hdr',]:
             self.mainWin.colormap =  color_map_dict[self.mainWin.colormap_string]
             cmap = self.generatePgColormap(  self.mainWin.colormap   )
             #print('the color string is: %s.'%self.mainWin.colormap_string)
        else:
            pass
        self.mainWin.cmap = cmap
        return cmap
    
    def configure_plot_title( self, plot_type ): 
        if plot_type in plot_curve_type :
            self.uid =  self.mainWin.current_base_filename  
            legend_heads = self.mainWin.current_item_path
            legend_cols = list(  range(self.mainWin.min_col+1, self.mainWin.max_col+2) )
            self.legends =  [  legend_heads + '-%s'%s for s in legend_cols ]             
            if self.mainWin.current_dataset_type =='CHX':   
                try:                    
                    if not self.mainWin.group_data:
                        self.legends = self.mainWin.get_dict_from_qval_dict(  )
                    self.uid =  'uid=%s'%self.mainWin.current_hdf5['md'].attrs[ 'uid' ][:6]
                except:
                    pass                
            elif self.mainWin.current_dataset_type =='CFN': 
                try:
                    lab_path =  '/'.join( legend_heads.split('/')[:-1] ) + '/label'
                    legend_cols =  self.mainWin.current_hdf5[ lab_path ][:]                     
                    self.legends =  legend_cols
                except:
                    pass   
                #print('Here conf plot title')  
                #print( self.uid, lab_path, self.legends  )
                
        elif plot_type in plot_image_type:             
            if self.mainWin.current_dataset_type =='CHX':   
                try:
                    self.uid =  'uid=%s-'%self.mainWin.current_hdf5['md'].attrs[ 'uid' ][:6]
                    self.legends =   self.mainWin.current_item_name                    
                except:
                    pass
            elif self.mainWin.current_dataset_type =='CFN': 
                legend_heads = self.mainWin.current_item_path  
                #print( legend_heads)
                self.use_extent = True
                try:
                    xdim_path = '/'.join(legend_heads.split('/')[:-1]) + '/x/data'
                    ydim_path = '/'.join(legend_heads.split('/')[:-1]) + '/y/data'
                    self.actual_xdim = self.mainWin.current_hdf5[xdim_path][:]
                    self.actual_ydim = self.mainWin.current_hdf5[ydim_path][:]
                except:
                    self.use_extent = False
                try:
                    lab_path =  '/'.join( legend_heads.split('/')[:-1] ) + '/label'
                    self.legends =    self.mainWin.current_hdf5[ lab_path ][:]
                    self.uid = self.mainWin.current_base_filename
                    #self.title =  self.uid + '-' +  self.legends                    
                except:                     
                    self.legends =    legend_heads
                    self.uid = self.mainWin.current_base_filename        
    
    def  configure_plot_type(self, plot_type ):
        self.mainWin.plot_type = plot_type
        if plot_type in plot_curve_type :
            if self.mainWin.testplot_count==0:
                self.mainWin.testplot = Figure()
                self.mainWin.ax = self.mainWin.testplot.add_subplot(111)
                self.mainWin.canvas = FigureCanvas(self.mainWin.testplot)
                self.mainWin.toolbar = NavigationToolbar(self.mainWin.canvas, self.mainWin)
                self.mainWin.grid.addWidget(self.mainWin.toolbar, 5, 1, 1, 7)
                self.mainWin.grid.addWidget( self.mainWin.canvas, 
			self.mainWin.testplot_grid_fromRow, self.mainWin.testplot_grid_fromColumn,
			self.mainWin.testplot_grid_rowSpan, self.mainWin.testplot_grid_columnSpan)
            #try:
            #    self.mainWin.imageCrossHair.clear() 
            #except:
            #    pass
            self.mainWin.image_plot_count=0
            
        elif plot_type in plot_image_type: 
            if self.mainWin.image_plot_count==0:
                self.mainWin.testplot = plt.figure()
                self.mainWin.ax = self.mainWin.testplot.add_subplot(111)
                self.mainWin.canvas = FigureCanvas(self.mainWin.testplot)
                self.add_image_color_options()
                self.mainWin.toolbar = NavigationToolbar(self.mainWin.canvas, self.mainWin)
                self.mainWin.grid.addWidget(self.mainWin.toolbar, 5, 1, 1, 7)
                self.mainWin.grid.addWidget( self.mainWin.canvas, 
		    self.mainWin.testplot_grid_fromRow, self.mainWin.testplot_grid_fromColumn,
		    self.mainWin.testplot_grid_rowSpan, self.mainWin.testplot_grid_columnSpan)
            self.mainWin.testplot_count=0              
            
        elif plot_type  in plot_surface_type:
            #self.get_colormap(  self.mainWin )     
            self.mainWin.testplot = gl.GLViewWidget()
            self.mainWin.grid.addWidget( self.mainWin.testplot, 
		self.mainWin.testplot_grid_fromRow, self.mainWin.testplot_grid_fromColumn,
		self.mainWin.testplot_grid_rowSpan, self.mainWin.testplot_grid_columnSpan)
            self.mainWin.image_plot_count=0
            self.mainWin.testplot_count=0  
        
    def plot_generic_curve(self, plot_type ):        
        self.configure_plot_type( plot_type )
        self.mainWin.get_selected_row_col(  ) 
        #self.mainWin.legend =   self.mainWin.testplot.legend() 
        shape = np.shape(self.mainWin.value)
        Ns = len(shape) 
        self.configure_plot_title(   plot_type )    
        self.mainWin.testplot_count += 1
        #print( self.uid, self.legends )
        #print( self.mainWin.value.shape )
            
        self.mainWin.setX_Special_flag = False    ##if self.mainWin.setX_flag is True, self.mainWin.X is not None,
        sami = 1
        ys=0
        if plot_type =='qiq':
            Special_Plot( self.mainWin ).plot_mat_qiq( )              
        elif  plot_type =='g2':
            Special_Plot( self.mainWin ).plot_mat_g2( ) 
        elif plot_type == 'plot_stack' or plot_type == 'stack_across' :
            #sami = self.mainWin.vstack_sampling #something is wrong with the sampling
            ys =   self.mainWin.vstack_yshift
        else:
            self.mainWin.setX_Special_flag = False
            
        #try: 
        #    self.mainWin.testplot.scene().sigMouseMoved.connect(self.curve_mouseMoved)            
        #except:
        #    pass
        if len(self.mainWin.value) > 0:     
            if self.mainWin.X is not None:# and len(self.mainWin.X)==self.mainWin.max_row-self.mainWin.min_row:
                X = self.mainWin.X[self.mainWin.min_row:self.mainWin.max_row] 
            else:
                X = self.mainWin.value[self.mainWin.min_row:self.mainWin.max_row, 0]               
            if   self.mainWin.max_col - self.mainWin.min_col   > 1: # for 2d data each plot col by col
                j = 0
                #print( 'here for debug plot ...')    
                #print(   X[0], X[-1]    )
                for i in range(self.mainWin.min_col, self.mainWin.max_col, sami):
                    Y = self.mainWin.value[self.mainWin.min_row:self.mainWin.max_row, i ] + ys * (i-self.mainWin.min_col)
                    try:
                        leg = self.legends[   i  ]
                    except:
                        leg = self.legends[ i - self.mainWin.min_col ]
                    if isinstance(leg, list):
                        leg = leg[:]
                    if plot_type == 'stack_across':
                        Y = Y + (ys * self.stacked_num * (self.mainWin.max_col - self.mainWin.min_col)) 
                        leg = str(leg) + ":" + str(self.current_acr_filename)
                   #####################################################NEW
                    self.mainWin.ax.plot(X, Y, '*-', label=leg)
                  #####################################################
                    j += 1
                self.mainWin.ax.set_xlabel(self.legends[0])
                self.mainWin.ax.legend()
                self.mainWin.canvas.draw()
                self.mainWin.canvas.hide()##This and the line below are required to
                self.mainWin.canvas.show()##circumvent maxOS incompatibilities with pyqt5
            else: # for 1d data we plot a row
                if Ns > 1:
                    Y = self.mainWin.value[ self.mainWin.min_row:self.mainWin.max_row, self.mainWin.min_col ]
                else:
                    Y = self.mainWin.value[ self.mainWin.min_row:self.mainWin.max_row  ]
                try:
                    leg = self.legends[ self.mainWin.min_col  ]
                except:
                    leg = self.legends[ self.mainWin.min_col - self.mainWin.min_col]
                if isinstance(leg, list):
                    leg = leg[:]
                #print(X.shape, Y.shape, leg )

                if plot_type == 'stack_across':
                    Y = Y + (ys * self.stacked_num)
                    self.mainWin.ax.plot(X, Y, '*-', label = self.current_acr_filename)
                else:
                    self.mainWin.ax.plot(X, Y, '*-', label=self.uid)
                self.mainWin.ax.set_xlabel(self.legends[0])
                self.mainWin.ax.set_ylabel(leg)
                self.mainWin.ax.legend()
                self.mainWin.canvas.draw()
                self.mainWin.canvas.hide()##This and the line below are required to
                self.mainWin.canvas.show()##circumvent maxOS incompatibilities with pyqt5

    def plot_generic_image( self, plot_type ):
        self.configure_plot_type( plot_type  )
        shape = (self.mainWin.value.T).shape
        self.mainWin.hor_Npt= shape[0]
        self.mainWin.ver_Npt= shape[1]
        self.mainWin.xmin,self.mainWin.xmax,self.mainWin.ymin,self.mainWin.ymax=0,shape[0],0,shape[1]
        try:
            self.mainWin.testplot.getView().vb.scene().sigMouseMoved.connect(  self.image_mouseMoved   )
        except:
            pass  
        #self.mainWin.legend =   self.mainWin.testplot.addLegend()
        #title = self.mainWin.current_base_filename + '-' + self.mainWin.current_item_path
        self.configure_plot_title(plot_type )  
        #print(  self.uid , self.legends )
        #self.title =  self.uid + '-' +  '%s'%self.legends 
        if plot_type == 'c12':
            Special_Plot( self.mainWin ).plot_c12( ) 
        elif plot_type in plot_image_type: 
            #print('Should plot image here...###')
            nan_mask = ~np.isnan( self.mainWin.value )            
            image_min, image_max = np.min( self.mainWin.value[nan_mask] ), np.max( self.mainWin.value[nan_mask] )
            self.mainWin.min,self.mainWin.max=image_min, image_max
            pos=[ 0, 0  ]
            if self.mainWin.colorscale_string == 'log':
                if image_min<=0:
                    image_min = 0.1*np.mean(np.abs( self.mainWin.value[nan_mask] ))
                tmpData=np.where(self.mainWin.value<=0,1,self.mainWin.value)
                self.mainWin.ax.clear()
                if self.use_extent:
                    self.cax = self.mainWin.ax.imshow(np.log10(self.mainWin.value),cmap=self.mainWin.colormap_string, extent=[self.actual_xdim[0], self.actual_xdim[-1], self.actual_ydim[0], self.actual_ydim[-1]], origin="lower") 
                else:
                    self.cax = self.mainWin.ax.imshow(np.log10(self.mainWin.value),cmap=self.mainWin.colormap_string, origin="lower") 
                   
                self.colorbar = self.mainWin.testplot.colorbar(self.cax, orientation='vertical')
                self.mainWin.canvas.draw()
                self.mainWin.canvas.hide()
                self.mainWin.canvas.show()
            else:
                self.mainWin.ax.clear()
                if self.use_extent:
                    self.cax = self.mainWin.ax.imshow(self.mainWin.value, cmap=self.mainWin.colormap_string, extent=[self.actual_xdim[0], self.actual_xdim[-1], self.actual_ydim[0], self.actual_ydim[-1]], origin="lower") 
                else:
                    self.cax = self.mainWin.ax.imshow(self.mainWin.value, cmap=self.mainWin.colormap_string, origin="lower") 

                self.colorbar = self.mainWin.testplot.colorbar(self.cax, orientation='vertical')
                self.mainWin.canvas.draw()
                self.mainWin.canvas.hide()
                self.mainWin.canvas.show()

    def plot_surface(self):
        plot_type = 'surface'
        self.configure_plot_type(  plot_type  )
        title = self.mainWin.current_base_filename + '-' + self.mainWin.current_item_path
        if self.mainWin.current_dataset_type =='CHX':   
            try:
                uid =  'uid=%s-'%self.mainWin.current_hdf5['md'].attrs[ 'uid' ][:6]
                title = uid  + self.mainWin.current_item_name
            except:
                pass         
        image_min, image_max = np.min( self.mainWin.value.T ), np.max( self.mainWin.value.T )
        self.mainWin.min,self.mainWin.max=image_min, image_max
        pos=[ 0, 0  ]
        if self.mainWin.colorscale_string == 'log':
            if image_min<=0:#np.any(self.mainWin.imageData<=0):
                image_min = 0.1*np.mean(np.abs( self.mainWin.value.T ))
            tmpData=np.where(self.mainWin.value.T<=0,1,self.mainWin.value.T)
            z=  np.log10(tmpData)
        else:
            z = self.mainWin.value.T
        minZ= np.min(z)
        maxZ= np.max(z)        
        #cmap = self.mainWin.cmap
        try:
            cmap = plt.get_cmap(  self.colormap_string)
        except:
            cmap = plt.get_cmap('jet') 
        rgba_img =  cmap((z-minZ)/(maxZ -minZ))
        p = gl.GLSurfacePlotItem(   z=z,
                                    colors = rgba_img,
                                  )
        try:
            sx,sy = self.mainWin.value.T.shape
            cx,cy = sx//2, sy//2
            p.translate(-cx,-cy,0)
        except:
            pass
        self.mainWin.testplot.addItem( p )

    def stack_across(self, plot_type): 
        saved_value = self.mainWin.value
        #print("There are", self.mainWin.file_items_list.tree.topLevelItemCount(), "item(s)")
        #for i in range(self.mainWin.file_items_list.tree.topLevelItemCount()):
        #    print("\t", self.mainWin.file_items_list.tree.topLevelItem(i))
        #print("This is the current item path:", self.mainWin.current_item_path)
        #print("This is self.item", self.mainWin.item)
        #leaf = self.mainW.file_items_list.file_array[0]
        full_path = '/'.join(self.mainWin.current_full_filename.split('/')[0:-1])
        self.stacked_num = 0
        for f in self.mainWin.file_items_list.file_array:
            self.current_acr_filename = f
            path_name = full_path + '/' + f
            print(path_name)
            try:
                current_hdf5 = h5py.File(path_name, 'r')
                current_hdf5_item = current_hdf5[self.mainWin.current_item_path]
                self.mainWin.value = current_hdf5_item[:]
                self.plot_generic_curve('stack_across')
                self.stacked_num += 1
            except:
                pass
        self.mainWin.value = saved_value #resets for future plotting

    def curve_mouseMoved( self, pos): 
        """
        Shows the mouse position of horizontal cut plot on its crosshair label
        """
        #print('Should show cross hair here.')
        try:
            if self.mainWin.testplot.sceneBoundingRect().contains(pos):
                point = self.mainWin.testplot.plotItem.vb.mapSceneToView(pos)
                x,y=point.x(),point.y()
                #print( x, y )
                if self.mainWin.logX_plot:
                    x=10**x
                if self.mainWin.logY_plot:
                    y=10**y
                self.mainWin.CurCrossHair.setText('X=%.6f, Y=%.3e'%(x,y))
            else:
                self.mainWin.CurCrossHair.clear()        
        except:
            pass        
        
    def image_mouseMoved(self, pos):
        """
        Shows the mouse position of 2D Image on its crosshair label
        """        
        try:
            pointer=self.mainWin.testplot.getView().vb.mapSceneToView(pos)
            x,y=pointer.x(),pointer.y()
            ang = np.degrees( np.arctan2(y,x))
            if (x>self.mainWin.xmin) and (x<self.mainWin.xmax) and (y>self.mainWin.ymin) and (y<self.mainWin.ymax):
                I =  self.mainWin.value.T[ int((x-self.mainWin.xmin)*self.mainWin.hor_Npt/(self.mainWin.xmax-self.mainWin.xmin)),int((y-self.mainWin.ymin)*self.mainWin.ver_Npt/(self.mainWin.ymax-self.mainWin.ymin)) ]                
                #self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, Ang=%0.2f, I=%.5e"%(x,y,ang, I) )
                self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, I=%.5e"%(x,y, I) )
            else:
                self.mainWin.imageCrossHair.setText(  'X=%0.4f, Y=%0.4f, I=%.5e'%(x,y, 0))
                #self.mainWin.imageCrossHair.setText("X=%0.4f, Y=%0.4f, Ang=%0.2f, I=%.5e"%(x,y,ang, I) )
        except:
            pass
        
    

    def plot_curve( self ):  
        try:
            print( 'plot curve here ------>')     
            self.mainWin.plot_clear()
            return self.plot_generic_curve( 'curve' )
        except:
            pass
    def plot_stack( self ):          
        try:
            #print( 'stack plot here ------>')      
            return self.plot_generic_curve( 'plot_stack' )
        except:
            pass        
    def plot_mat_g2( self ):          
        try:
            #print( 'g2 here ------>')      
            return self.plot_generic_curve( 'g2' )
        except:
            pass
    def plot_mat_qiq( self ):
        
        try:
            #print( 'qiq here ------>') 
            return self.plot_generic_curve( 'qiq' )
        except:
            pass
    def plot_image( self ):
        
        try:
            #print( 'image here ------>') 
            self.plot_generic_image( 'image')
        except:
            pass
    def plot_C12( self ):
        
        try:
            #print( 'C12 here ------>') 
            return self.plot_generic_image( 'c12' )
        except:
            pass       
    def plot_across( self ):
        try:
            print('plotting across datasets here -------->')
            return self.stack_across( 'curve' )
        except:
            pass
        
        
    def bstring_to_string( bstring ):
        '''Y.G., Dev@CFN Nov 20, 2019 convert a btring to string
        
        Parameters
        ----------
            bstring: bstring or list of bstring 
        Returns
        -------  
            string:    
        '''
        s =  np.array( bstring )
        if not len(s.shape):
            s=s.reshape( 1, )
            return s
            #return s[0].decode('utf-8')
        else:
            return np.char.decode( s )        

    def add_image_color_options(self):
        self.cb = QComboBox()
        self.cb.setPlaceholderText('Color Scheme')
        self.cb.addItems(image_colors)
        self.cb.currentIndexChanged.connect(self.colorClick)
        self.mainWin.cbWidget = self.mainWin.grid.addWidget(self.cb, 5, 8, 1, 1)


    def colorClick(self):
        self.mainWin.colormap_string = image_colors[self.cb.currentIndex()]
        #self.mainWin.plot_clear()
        #self.plot_image()
        self.mainWin.ax.clear()
        if self.mainWin.colorscale_string == 'log':
            self.cax = self.mainWin.ax.imshow(np.log10(self.mainWin.value), cmap=self.mainWin.colormap_string, origin='lower')
            self.colorbar.remove()
            self.colorbar = self.mainWin.testplot.colorbar(self.cax)
        else:            
            self.cax = self.mainWin.ax.imshow(self.mainWin.value, cmap=self.mainWin.colormap_string, origin='lower')
            self.colorbar.remove()
            self.colorbar = self.mainWin.testplot.colorbar(self.cax)
        # refresh canvas
        self.mainWin.canvas.draw()
        self.mainWin.canvas.hide()
        self.mainWin.canvas.show()


