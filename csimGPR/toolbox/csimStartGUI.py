# csimStartGUI.py 用于绘制csimGPR的启动界面

import csimGPR.csimGPR as gp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import os
import matplotlib.image as im
from scipy import signal

import sys
import os
 
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def showcsimGPR(a,dir_path,widfac,highfac,fontfac):
    '''
    Creates the csimGPR screen shown when starting csimGPR GUI for 
    common-offset profiles.
    '''
    try:
        filename=os.path.join(dir_path,'exampledata','SnS','ComOffs','XLINE00.DT1')
        snakeGPR = gp.gprpyProfile(filename)
        maxpoint=100;
        x=snakeGPR.twtt[0:maxpoint]
        y=snakeGPR.data[0:maxpoint,10]
        xshift=-7
    except:
        rick = signal.ricker(150, 4.0)
        x = np.linspace(0,85,100)
        y = rick[50:150]*25000
        xshift=0
        
    # Snake body
    lw=7#5
    a.plot(x,y,'k',linewidth=lw*widfac,solid_capstyle='round')
    # Snake head
    Path = mpath.Path
    headval=2000*widfac/highfac
    path_data = [
        (Path.MOVETO, [xshift,headval]),
        (Path.CURVE3, [-20+xshift,0]),
        (Path.LINETO, [xshift,-headval]),
        (Path.CURVE3, [10+xshift,0]),
        (Path.LINETO, [xshift,headval]),
        (Path.CLOSEPOLY, [xshift,headval])]
    codes, verts = zip(*path_data)
    path = mpath.Path(verts, codes)
    patch = mpatches.PathPatch(path)
    patch.set_facecolor('black')
    a.add_patch(patch)
    # Eyes
    eye1 = mpatches.Ellipse([-2+xshift,1000], 3, 1000)
    eye2 = mpatches.Ellipse([-2+xshift,-1000], 3, 1000)
    eye1.set_facecolor('white')
    eye2.set_facecolor('white')
    a.add_patch(eye1)
    a.add_patch(eye2)
    # Tongue
    x, y = np.array([[-10+xshift, -13+xshift, -15+xshift], [0.0, 0.0, 600]])
    line1 = mlines.Line2D(x, y, lw=2*widfac, color='black')
    x, y = np.array([[-10+xshift, -13+xshift, -15+xshift], [0.0, 0.0, -600]])
    line2 = mlines.Line2D(x, y, lw=2*widfac, color='black')
    a.add_line(line1)
    a.add_line(line2)
    # Axis setup
    a.set_xlim([-25,90])
    a.set_ylim([-28000,12000])
    a.axis('off')
    # Text
    font = {'family': 'DejaVu Sans',
        'color':  'black',
        'weight': 'bold',
        'style': 'italic',
        'size': 60*fontfac
        #'size': 45.6
        }
#    a.text(35,-10000,'csimGPR',fontdict=font)
    a.text(50,-10000,'csimGPR',fontdict=font)

    fontver = {'family': 'DejaVu Sans',
        'color':  'black',
        'style': 'italic',
        'size': 13.5*fontfac
        #'size': 45.6
        }
    a.text(50,-12000,'Version 1.0.0',fontdict=fontver)
   
    # add UA logo
    filename1=os.path.join(dir_path,'startGUIdat',
                           'JLU.jpg')
    ua = im.imread(resource_path(filename1))
    #yanchor = -24500
    #yheight = 10000*0.9
    yanchor = -24000
    yheight = 10000*0.8
    xanchor = -20
    figsize = a.figure.get_size_inches()
    figratio = figsize[0]/figsize[1]
    ratio = a.get_data_ratio()*figratio
    xwidth = yheight/ratio
    a.imshow(ua, aspect='auto', extent=(xanchor, xanchor+xwidth,
                                        yanchor, yanchor+yheight),
             interpolation='spline36')

    # # add UA words
    # filename1=os.path.join(dir_path,'startGUIdat',
    #                         'UA-StackedNameplate.png')
    # ua = im.imread(filename1)
    # #yanchor = -24500
    # #yheight = 10000*0.9
    # yanchor = -24000
    # yheight = 10000*0.4
    # xanchor = -10
    # figsize = a.figure.get_size_inches()
    # figratio = figsize[0]/figsize[1]
    # ratio = a.get_data_ratio()*figratio
    # xwidth = 5*yheight/ratio
    # a.imshow(ua, aspect='auto', extent=(xanchor, xanchor+xwidth,
    #                                     yanchor, yanchor+yheight),
    #          interpolation='spline36')
    
    
    # Add NSF logo
    filename2=os.path.join(dir_path,'startGUIdat',
                           'ditan.jpeg')
    nsf = im.imread(resource_path(filename2))
    yanchor = -25000
    yheight = 10000
    xanchor = -5
    figsize = a.figure.get_size_inches()
    figratio = figsize[0]/figsize[1]
    ratio = a.get_data_ratio()*figratio
    xwidth = yheight/ratio 
    a.imshow(nsf, aspect=0.0016,extent=(xanchor, xanchor+xwidth,  #aspect='auto'
                                         yanchor, yanchor+yheight),
             interpolation='spline36')
    font2 = {'family': 'DejaVu Sans',
             'color':  'black',
             'size': 12*fontfac}
			 #'size': 10.26}
    #a.text(-5,-27000,'EAR-1550732',fontdict=font2)
    #a.text(-5,-29000,'EAR-2022671',fontdict=font2)

    a.text(30,-29000,'Please cite https://erbiaoger.site',fontdict=font2)
    a.set_url(['https://doi.org'])

    
    # Add name/email
    font3 = {'family': 'DejaVu Sans',
             'color':  'gray',
             'size': 12*fontfac}
			 #'size' : 10.26}
    a.text(59,-22000,'Zhiyu Zhang',fontdict=font3)
    a.text(59,-24000,'erbiaoger@gmail.com',fontdict=font3)