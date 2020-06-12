import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
from PyQt5.QtWidgets import (QWidget, QToolTip, QMainWindow, )
from ColorMap import (cmap_cyclic_spectrum, cmap_jet_extended, cmap_vge, cmap_vge_hdr,
                      cmap_albula, cmap_albula_r,cmap_hdr_goldish , color_map_dict )      
import matplotlib.pyplot as plt
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


                             
plot_curve_type = [ 'curve', 'g2', 'qiq', 'plot_stack', 'mat_curve' ]   # some particular format for curve plot 
plot_image_type = ['image', 'c12']           # some particular format  for image plot
plot_surface_type = ['surface']           # some particular format  for surfce plot

    
        
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
             print('the color string is: %s.'%self.mainWin.colormap_string)
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
                self.mainWin.canvas = FigureCanvas(self.mainWin.testplot)
                self.mainWin.grid.addWidget( self.mainWin.canvas, 
			self.mainWin.testplot_grid_fromRow, self.mainWin.testplot_grid_fromColumn,
			self.mainWin.testplot_grid_rowSpan, self.mainWin.testplot_grid_columnSpan)
            #try:
            #    self.mainWin.imageCrossHair.clear() 
            #except:
            #    pass
            self.mainWin.image_plot_count=0
            
        elif plot_type in plot_image_type: 
            self.get_colormap(  self.mainWin )  
            if self.mainWin.image_plot_count==0:
                self.mainWin.testplot = Figure()
                self.mainWin.canvas = FigureCanvas(self.mainWin.testplot)
                self.mainWin.grid.addWidget( self.mainWin.canvas, 
		    self.mainWin.testplot_grid_fromRow, self.mainWin.testplot_grid_fromColumn,
		    self.mainWin.testplot_grid_rowSpan, self.mainWin.testplot_grid_columnSpan)
            self.mainWin.testplot_count=0              
            try:
                self.mainWin.CurCrossHair.clear() 
            except:
                pass                
            
        elif plot_type  in plot_surface_type:
            self.get_colormap(  self.mainWin )     
            self.mainWin.testplot = Figure()
            self.mainWin.canvas = FigureCanvas(self.mainWin.testplot)
            self.mainWin.grid.addWidget( self.mainWin.canvas, 
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
        #print( self.uid, self.legends )
        ##################
        symbolSize = 6
        ##########################
        
        #print('here 333333333333')
        #print( self.mainWin.value.shape )
            
        self.mainWin.setX_Special_flag = False    ##if self.mainWin.setX_flag is True, self.mainWin.X is not None,
        sami = 1
        ys=0
        if plot_type =='qiq':
            Special_Plot( self.mainWin ).plot_mat_qiq( )              
        elif  plot_type =='g2':
            Special_Plot( self.mainWin ).plot_mat_g2( ) 
        elif plot_type == 'plot_stack' :
            sami = self.mainWin.vstack_sampling
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
                   #####################################################NEW
                    ax = self.mainWin.testplot.add_subplot(111)
                    ax.clear()
                    ax.plot(X, Y, '*-')
                    self.mainWin.canvas.draw()
                   #####################################################
                    j += 1
                    self.mainWin.testplot_count += 1
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
                #####################################################NEW
                ax = self.mainWin.testplot.add_subplot(111)
                data = [random.random() for i in range(10)]
                ax.clear()
                ax.plot(X, Y, '*-')
                self.mainWin.canvas.draw()
                self.mainWin.testplot_count += 1
                #####################################################               
   

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
        print(  self.uid , self.legends )
        self.title =  self.uid + '-' +  '%s'%self.legends 
        if plot_type == 'c12':
            Special_Plot( self.mainWin ).plot_c12( ) 
        elif plot_type == 'image': 
            #print('Should plot image here...###')
            nan_mask = ~np.isnan( self.mainWin.value )            
            image_min, image_max = np.min( self.mainWin.value[nan_mask] ), np.max( self.mainWin.value[nan_mask] )
            self.mainWin.min,self.mainWin.max=image_min, image_max
            pos=[ 0, 0  ]
            if self.mainWin.colorscale_string == 'log':
                if image_min<=0:
                    image_min = 0.1*np.mean(np.abs( self.mainWin.value[nan_mask] ))
                tmpData=np.where(self.mainWin.value<=0,1,self.mainWin.value)
                self.mainWin.testplot.setImage(np.log10(tmpData),
                                      levels=(np.log10( image_min),np.log10( image_max)),
                                      pos=pos,
                                      autoRange=True)
            else:
                self.mainWin.testplot.setImage( self.mainWin.value ,
                                       levels=( image_min, image_max),
                                       pos=pos,
                                       autoRange=True)
            #print( self.mainWin.colorscale_string   )
            self.mainWin.plt.setLabels( left = 'Y', bottom='X')
            ax = self.mainWin.plt.getAxis('bottom')
            ax2 = self.mainWin.plt.getAxis('left')
            pos = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 ))
            tick = np.int_(np.linspace(0, self.mainWin.value.shape[0], 5 ))
            dx = [(pos[i], '%i'%(tick[i])) for i in range( len(pos ))   ]
            ax.setTicks([dx, []])
            ax2.setTicks([dx, []] )
        self.mainWin.testplot.setColorMap( self.mainWin.cmap )
        self.mainWin.plt.setTitle( title = self.title )
        self.mainWin.testplot.getView().invertY(False)
        self.mainWin.image_plot_count += 1

    def plot_surface(self):
        '''TODOLIST'''
        print( 'here plot the surface...')
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
        
    


    def plot_mat_curve( self ):  
        try:
            print( 'mat def curve here ------>')     
            return self.plot_generic_curve( 'mat_curve' )
        except:
            pass
    def plot_mat_stack( self ):          
        try:
            print( 'stack plot here ------>')      
            return self.plot_generic_curve( 'plot_stack' )
        except:
            pass        
    def plot_mat_g2( self ):          
        try:
            print( 'g2 here ------>')      
            return self.plot_generic_curve( 'g2' )
        except:
            pass
    def plot_mat_qiq( self ):
        
        try:
            print( 'qiq here ------>') 
            return self.plot_generic_curve( 'qiq' )
        except:
            pass
    def plot_image( self ):
        
        try:
            print( 'image here ------>') 
            self.plot_generic_image( 'image')
        except:
            pass
    def plot_C12( self ):
        
        try:
            print( 'C12 here ------>') 
            return self.plot_generic_image( 'c12' )
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

