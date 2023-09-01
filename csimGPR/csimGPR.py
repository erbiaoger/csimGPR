# csimGPR.py 用于处理GPR数据

import os
import time
import numpy as np
import matplotlib.pyplot as plt
import pickle
import skimage.transform
import scipy.io as io
from scipy import fft

import csimGPR.toolbox.gprIO_2A as gprIO_2A
import csimGPR.toolbox.gprIO_DT1 as gprIO_DT1
import csimGPR.toolbox.gprIO_DZT as gprIO_DZT
import csimGPR.toolbox.gprIO_BSQ as gprIO_BSQ
import csimGPR.toolbox.gprIO_MALA as gprIO_MALA
import csimGPR.toolbox.gprpyTools as tools
import csimGPR.toolbox.Robust_NMF as Robust_NMF
from csimGPR.toolbox.my_stran import st
from csimGPR.toolbox.filters import butterworth
#from csimGPR.kirchhoffmigration.kirchhoffmigration import full_migration, taper

try:
    import csimGPR.irlib.external.mig_fk as mig_fk
except:
    print("Install fk migration if needed")
import copy
import scipy.interpolate as interp
from pyevtk.hl import gridToVTK

class gprpyProfile:
    '''
    Ground penetrating radar data processing and visualization class 
    for common-offset profiles.
    '''

    def __init__(self,filename=None):
        '''
        Initialization for a gprpyProfile object. Initialization can be 
        empty or with a provided filename for the GPR data.

        INPUT:
        filename     data file name. Currently supported formats:
                     .gpr (GPRPy), .DT1 (SnS), .DZT (GSSI), .rd3 (MALA),
                     and ENVI standard BSQ.
        '''
        
        self.history = ["mygpr = gp.gprpyProfile()"]

        # Initialize previous for undo
        self.previous = {}
        
        if filename is not None:
            self.importdata(filename)                 
        
    def importdata(self,filename):
        '''
        Loads .gpr (native GPRPy), .DT1 (Sensors and Software),
        .DZT (GSSI), .GPRhdr (ENVI standard BSQ), .rad (MALA)
        data files and populates all the gprpyProfile fields.

        INPUT: 
        filename  name of the .gpr, .DT1, dt1, .DZT, .GPRhdr, dat, 
                  rd3, or .rad file you want to import.
                  The header file name and the data file name 
                  have to be the same!
        '''
        
        file_name, file_ext = os.path.splitext(filename)
        
        if file_ext == ".mat":
            self.data = io.loadmat(file_name + '.mat')['field'].T
            dx = 0.050000; dt = 0.3125
            self.profilePos = np.arange(0, self.data.shape[1]*dx, dx)
            self.twtt = np.arange(0, self.data.shape[0]*dt, dt) #np.linspace(0,self.info["rhf_range"],self.info["rh_nsamp"])

            self.info = None
            self.antsep = 0
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)

        if file_ext == ".2A":
            self.data = gprIO_2A.read2A(file_name + '.2A')
            dx = 0.50000; dt = 0.3125
            self.profilePos = np.arange(0, self.data.shape[1]*dx, dx)
            self.twtt = np.arange(0, self.data.shape[0]*dt, dt) #np.linspace(0,self.info["rhf_range"],self.info["rh_nsamp"])

            self.info = None
            self.antsep = 0
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)

        
        if file_ext==".DT1" or file_ext==".HD" or file_ext==".dt1" or file_ext==".hd":

            if file_ext==".DT1" or  file_ext==".HD":
                self.data=gprIO_DT1.readdt1(file_name + ".DT1")
                self.info=gprIO_DT1.readdt1Header(file_name + ".HD")  
            else:
                self.data=gprIO_DT1.readdt1(file_name + ".dt1")
                self.info=gprIO_DT1.readdt1Header(file_name + ".hd")
            
            self.profilePos = np.linspace(self.info["Start_pos"],
                                          self.info["Final_pos"],
                                          self.info["N_traces"])

            #self.twtt = np.linspace(self.info["TZ_at_pt"],
            #                        self.info["Total_time_window"],
            #                        self.info["N_pts_per_trace"])

            sec_per_samp = self.info["Total_time_window"]/self.info["N_pts_per_trace"]
            tshift = self.info["TZ_at_pt"]*sec_per_samp
            
            self.twtt = np.linspace(0,self.info["Total_time_window"],
                                    self.info["N_pts_per_trace"]) - tshift

            self.antsep = self.info["Antenna_sep"] # Set to m in the loading routine 
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)                                
            
        elif file_ext==".DZT":

            self.data, self.info = gprIO_DZT.readdzt(filename)

            if self.info["rhf_spm"] != 0:
                self.profilePos = self.info["rhf_position"]+np.linspace(0.0,
                                                                        self.data.shape[1]/self.info["rhf_spm"],
                                                                        self.data.shape[1])
            else:
                self.profilePos = self.info["rhf_position"]+np.linspace(0.0,
                                                                        self.data.shape[1]/self.info["rhf_sps"],
                                                                        self.data.shape[1])
                
            self.twtt = np.linspace(0,self.info["rhf_range"],self.info["rh_nsamp"])

            
            self.antsep = 0
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)
    
        

        elif file_ext==".GPRhdr" or file_ext==".dat":
            # ENVI standard BSQ file
            self.data, self.info = gprIO_BSQ.readBSQ(file_name)

            self.profilePos = float(self.info["dx"])*np.arange(0,int(self.info["columns"]))
            self.twtt = np.linspace(0,float(self.info["time_window"]),int(self.info["lines"]))

            self.antsep = 0
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)       


        elif file_ext==".rad" or file_ext==".rd3" or file_ext==".rd7":
            self.data, self.info = gprIO_MALA.readMALA(file_name)

            self.twtt = np.linspace(0,float(self.info["TIMEWINDOW"]),int(self.info["SAMPLES"]))
            self.profilePos = float(self.info["DISTANCE INTERVAL"])*np.arange(0,self.data.shape[1])

            self.antsep = self.info["ANTENNA SEPARATION"]
            self.velocity = None
            self.depth = None
            self.maxTopo = None
            self.minTopo = None
            self.threeD = None
            self.data_pretopo = None
            self.twtt_pretopo = None
            # Initialize previous
            self.initPrevious()
            
            # Put what you did in history
            histstr = "mygpr.importdata('%s')" %(filename)
            self.history.append(histstr)
            
            

        elif file_ext==".gpr":
            ## Getting back the objects:
            with open(filename, 'rb') as f:
                data, info, profilePos, twtt, history, antsep, velocity, depth, maxTopo, minTopo, threeD, data_pretopo, twtt_pretopo = pickle.load(f)
            self.data = data
            self.info = info
            self.profilePos = profilePos
            self.twtt = twtt
            self.history = history
            self.antsep = antsep
            self.velocity = velocity
            self.depth = depth
            self.maxTopo = maxTopo
            self.minTopo = minTopo
            self.threeD = threeD
            self.data_pretopo = data_pretopo
            self.twtt_pretopo = twtt_pretopo
            
            # Initialize previous
            self.initPrevious()
            
        else:
            print("可读取 2A 2B dt1, DT1, hd, HD, DZT, dat, GPRhdr, rad, rd3, rd7, and gpr 文件.", '\n')
        print(self.data.shape, type(self.data))

    def showHistory(self):
        '''
        Prints out processing and visualization history of a data set. 
        '''
        for i in range(0,len(self.history)):
            print(self.history[i])

    def writeHistory(self,outfilename="myhistory.py"):
        '''
        Turns the processing and visualization history into a Python script.
        The full path names are saved in the Python script. You can edit the
        Python script after saving to remove the full path names.

        INPUT:
        outfilename        filename for Python script
        '''
        with open(outfilename,"w") as outfile:
            outfile.write("# Automatically generated by GPRPy\nimport gprpy.gprpy as gp\n")
            for i in range(0,len(self.history)):
                outfile.write(self.history[i] + "\n")
                
    def undo(self):
        '''
        Undoes the last processing step and removes that step fromt he history.
        '''
        self.data = self.previous["data"]
        self.twtt = self.previous["twtt"]
        self.info = self.previous["info"]
        self.profilePos = self.previous["profilePos"]
        self.velocity = self.previous["velocity"]
        self.depth = self.previous["depth"]
        self.maxTopo = self.previous["maxTopo"]
        self.minTopo = self.previous["minTopo"]
        self.threeD = self.previous["threeD"]
        self.data_pretopo = self.previous["data_pretopo"]
        self.twtt_pretopo = self.previous["twtt_pretopo"]
        # Make sure to not keep deleting history
        # when applying undo several times. 
        histsav = copy.copy(self.previous["history"])
        del histsav[-1]
        self.history = histsav
        print("undo")

        
    def initPrevious(self):
        '''
        Initialization of data strucure that contains the step 
        before the most recent action.
        '''
        self.previous["data"] = self.data
        self.previous["twtt"] = self.twtt 
        self.previous["info"] = self.info
        self.previous["profilePos"] = self.profilePos
        self.previous["velocity"] = self.velocity
        self.previous["depth"] = self.depth
        self.previous["maxTopo"] = self.maxTopo
        self.previous["minTopo"] = self.minTopo
        self.previous["threeD"] = self.threeD
        self.previous["data_pretopo"] = self.data_pretopo
        self.previous["twtt_pretopo"] = self.twtt_pretopo
        histsav = copy.copy(self.history)
        self.previous["history"] = histsav

        

    def save(self,filename):
        '''
        Saves the processed data together with the processing and visualization
        history. Warning: The history stored in this file will contain the full 
        path to the file.

        INPUT:
        filename       name for .gpr file
        '''
        # Saving the objects:
        # Want to force the file name .gpr
        file_name, file_ext = os.path.splitext(filename)
        if not(file_ext=='.gpr'):
            filename = filename + '.gpr'
        with open(filename, 'wb') as f:  
            pickle.dump([self.data, self.info, self.profilePos, self.twtt,
                         self.history, self.antsep, self.velocity, self.depth,
                         self.maxTopo, self.minTopo, self.threeD, self.data_pretopo,
                         self.twtt_pretopo], f)            
        print("Saved " + filename)
        # Add to history string
        histstr = "mygpr.save('%s')" %(filename)
        self.history.append(histstr)

    
    # This is a helper function
    def prepProfileFig(self, color="gray", contrast=1.0, yrng=None, xrng=None, asp=None):
        '''
        This is a helper function.
        It prepares the plot showing the processed profile data.
        
        INPUT:
        color        "gray", or "bwr" for blue-white-red,
                     or any other Matplotlib color map [default: "gray"]
        contrast     Factor to increase contrast by reducing color range.
                     [default = 1.0]
        yrng         y-axis range to show [default: None, meaning "everything"]
        xrng         x-axis range to show [default: None, meaning "everything"]
        asp          aspect ratio [default: None, meaning automatic]

        OUTPUT:
        contrast     contrast value used to prepare the figure
        color        color value used to prepare the figure
        yrng         yrng value used to prepare the figure
        xrng         xrng value used to prepare the figure
        asp          asp value used to prepare the figure

        '''
        dx=self.profilePos[3]-self.profilePos[2]
        dt=self.twtt[3]-self.twtt[2]
        stdcont = np.nanmax(np.abs(self.data)[:])       
        
        if self.velocity is None:
            plt.imshow(self.data,cmap=color,extent=[min(self.profilePos)-dx/2.0,
                                                    max(self.profilePos)+dx/2.0,
                                                    max(self.twtt)+dt/2.0,
                                                    min(self.twtt)-dt/2.0],
                       aspect="auto",vmin=-stdcont/contrast, vmax=stdcont/contrast)
            plt.gca().set_ylabel("time [ns]")
            plt.gca().invert_yaxis()
            if yrng is not None:
                yrng=[np.max(yrng),np.min(yrng)]
            else:
                yrng=[np.max(self.twtt),np.min(self.twtt)]
            
        elif self.maxTopo is None:
            dy=dt*self.velocity
            plt.imshow(self.data,cmap=color,extent=[min(self.profilePos)-dx/2.0,
                                                    max(self.profilePos)+dx/2.0,
                                                    max(self.depth)+dy/2.0,
                                                    min(self.depth)-dy/2.0],
                       aspect="auto",vmin=-stdcont/contrast, vmax=stdcont/contrast)
            plt.gca().set_ylabel("depth [m]")
            plt.gca().invert_yaxis()
            if yrng is not None:
                yrng=[np.max(yrng),np.min(yrng)]
            else:
                yrng=[np.max(self.depth),np.min(self.depth)]
                
        else:
            dy=dt*self.velocity
            plt.imshow(self.data,cmap=color,extent=[min(self.profilePos)-dx/2.0,
                                                    max(self.profilePos)+dx/2.0,
                                                    self.minTopo-max(self.depth)-dy/2.0,
                                                    self.maxTopo-min(self.depth)+dy/2.0],
                    aspect="auto",vmin=-stdcont/contrast, vmax=stdcont/contrast)            
            plt.gca().set_ylabel("elevation [m]")
            if yrng is None:
                yrng=[self.minTopo-np.max(self.depth),self.maxTopo-np.min(self.depth)]
            

        if xrng is None:
            xrng=[min(self.profilePos),max(self.profilePos)]       
                
        if yrng is not None:
            plt.ylim(yrng)
            
        if xrng is not None:
            plt.xlim(xrng)

        if asp is not None:
            plt.gca().set_aspect(asp)

        plt.gca().get_xaxis().set_visible(True)
        plt.gca().get_yaxis().set_visible(True)                
        plt.gca().set_xlabel("profile position [m]")
        plt.gca().xaxis.tick_top()
        plt.gca().xaxis.set_label_position('top')
        
        return contrast, color, yrng, xrng, asp
       
    
    def showProfile(self, **kwargs):
        '''
        Plots the profile using Matplotlib. 
        You need to run .show() afterward to show it 
        
        INPUT:
        color        "gray", or "bwr" for blue-white-red,
                     or any other Matplotlib color map [default: "gray"]
        contrast     Factor to increase contrast by reducing color range.
                     [default = 1.0]
        yrng         y-axis range to show [default: None, meaning "everything"]
        xrng         x-axis range to show [default: None, meaning "everything"]
        asp          aspect ratio [default: None, meaning automatic]

        '''
        self.prepProfileFig(**kwargs)
        plt.show(block=False)


    def printProfile(self, figname, dpi=600, **kwargs):
        '''
        Creates a pdf of the profile. 
        
        INPUT:
        figname      file name for the pdf
        dpi          dots per inch resolution [default: 600 dpi]
        color        "gray", or "bwr" for blue-white-red,
                     or any other Matplotlib color map [default: "gray"]
        contrast     Factor to increase contrast by reducing color range.
                     [default = 1.0]
        yrng         y-axis range to show [default: None, meaning "everything"]
        xrng         x-axis range to show [default: None, meaning "everything"]
        asp          aspect ratio [default: None, meaning automatic]

        '''
        contrast, color, yrng, xrng, asp = self.prepProfileFig(**kwargs)
        plt.savefig(figname, format='pdf', dpi=dpi)
        plt.close('all')
        # Put what you did in history
        if asp is None:
            histstr = "mygpr.printProfile('%s', color='%s', contrast=%g, yrng=[%g,%g], xrng=[%g,%g], dpi=%d)" %(figname,color,contrast,yrng[0],yrng[1],xrng[0],xrng[1],dpi)
        else:
            histstr = "mygpr.printProfile('%s', color='%s', contrast=%g, yrng=[%g,%g], xrng=[%g,%g], asp=%g, dpi=%d)" %(figname,color,contrast,yrng[0],yrng[1],xrng[0],xrng[1],asp,dpi)
        self.history.append(histstr)
        

    ####### Processing #######
    
    def adjProfile(self,minPos,maxPos):
        '''
        Adjusts the length of the profile.

        INPUT:
        minPos      starting position of the profile
        maxpos      end position of the profile
        '''
        # Store previous state for undo
        self.storePrevious()
        # set new profile positions
        self.profilePos = np.linspace(minPos,maxPos,len(self.profilePos))       
        # Put what you did in history
        histstr = "mygpr.adjProfile(%g,%g)" %(minPos,maxPos)
        self.history.append(histstr)

    
    def flipProfile(self):
        '''
        Flips the profile left-to-right (start to end)
        '''
        # Flips the profile left to right (start to end)
        self.storePrevious()
        self.data=np.flip(self.data,1)
        if self.data_pretopo is not None:
            self.data_pretopo = np.flip(self.data_pretopo,1)
        histstr = "mygpr.flipProfile()"
        self.history.append(histstr)
        

    def alignTraces(self):
        '''
        Aligns the traces in the profile such that their maximum 
        amplitudes align at the average travel time of the 
        maximum amplitudes.
        '''
        # Store previous state for undo
        self.storePrevious()        
        self.data = tools.alignTraces(self.data)      
        # Put what you did in history
        histstr = "mygpr.alignTraces()"
        self.history.append(histstr)



    def cut(self,minPos,maxPos):
        '''
        Removes all data outside of the profile positions between
        minPos and maxPos.

        INPUT:
        minPos      starting position of data to keep
        maxPos      end position of data to keep
        '''
        # Store previous state for undo
        self.storePrevious()
        zeroind = np.abs(self.profilePos - minPos).argmin()
        maxind = np.abs(self.profilePos - maxPos).argmin()
        self.data = self.data[:,zeroind:(maxind+1)]
        self.profilePos=self.profilePos[zeroind:(maxind+1)]
        if self.data_pretopo is not None:
            self.data_pretopo = self.data_pretopo[:,zeroind:(maxind+1)]
        # Put into history string
        histstr = "mygpr.cut(%g,%g)" %(minPos,maxPos)
        self.history.append(histstr)
        
    def cut1(self,minPos,maxPos):
        # Store previous state for undo
        self.storePrevious()
        zeroind = np.abs(self.profilePos - minPos).argmin()
        maxind = np.abs(self.profilePos - maxPos).argmin()
        self.data = np.concatenate((self.data[:, 0:zeroind], self.data[:, (maxind+1):]), axis=1)
        idx = len(self.profilePos) - (maxind - zeroind + 1)
        self.profilePos=self.profilePos[0:(idx+1)]
        if self.data_pretopo is not None:
            self.data_pretopo = np.concatenate((self.data_pretopo[0:zeroind], self.data_pretopo[(maxind+1):]))
        # Put into history string
        histstr = "mygpr.cut1(%g,%g)" %(minPos,maxPos)
        self.history.append(histstr)
        
    def setZeroTime(self,newZeroTime):
        '''
        Deletes all data recorded before newZeroTime and 
        sets newZeroTime to zero.

        INPUT:
        newZeroTime     The new zero-time
        '''
        # Store previous state for undo
        self.storePrevious()
        # Find index of value that is nearest to newZeroTime
        zeroind = np.abs(self.twtt - newZeroTime).argmin()
        print(zeroind) 
        # Cut out everything before
        self.twtt = self.twtt[zeroind:] - newZeroTime
        # Set first value to 0
        self.twtt[0] = 0
        self.data = self.data[zeroind:,:]
        print(self.data.shape)
        # Put what you did in history
        histstr = "mygpr.setZeroTime(%g)" %(newZeroTime)
        self.history.append(histstr)  

        
    def dewow(self,window):
        '''
        Subtracts from each sample along each trace an 
        along-time moving average.

        Can be used as a low-cut filter.

        INPUT:
        window     length of moving average window 
                   [in "number of samples"]
        '''
        # Store previous state for undo
        self.storePrevious()
        self.data = tools.dewow(self.data,window)
        # Put in history
        histstr = "mygpr.dewow(%d)" %(window)
        self.history.append(histstr)


    def smooth(self,window):
        '''
        Replaces each sample along each trace with an 
        along-time moving average.

        Can be used as high-cut filter.

        INPUT: 
        window     length of moving average window
                   [in "number of samples"]
        '''
        # Store previous state for undo
        self.storePrevious()
        self.data = tools.smooth(self.data,window)
        # Put in history
        histstr = "mygpr.smooth(%d)" %(window)
        self.history.append(histstr)

        
    def remMeanTrace(self,ntraces):
        '''
        Subtracts from each trace the average trace over
        a moving average window.

        Can be used to remove horizontal arrivals, 
        such as the airwave.

        INPUT:
        ntraces     window width; over how many traces 
                    to take the moving average. 
        '''
        # Store previous state for undo
        self.storePrevious()
        # apply
        self.data = tools.remMeanTrace(self.data,ntraces)        
        # Put in history
        histstr = "mygpr.remMeanTrace(%d)" %(ntraces)
        self.history.append(histstr)


    def profileSmooth(self,ntraces,noversample):
        '''
        First creates copies of each trace and appends the copies 
        next to each trace, then replaces each trace with the 
        average trace over a moving average window.

        Can be used to smooth-out noisy reflectors appearing 
        in neighboring traces, or simply to increase the along-profile 
        resolution by interpolating between the traces.

        For example: To increase the along-profile resolution smoothly 
        by a factor of 4: use

        mygpr.profileSmooth(4,4)

        INPUT:
        ntraces         window width [in "number of samples"]; 
                        over how many traces to take the moving average. 
        noversample     how many copies of each trace
        '''
        # Store previous state for undo
        self.storePrevious()
        self.data,self.profilePos = tools.profileSmooth(self.data,self.profilePos,
                                                        ntraces,noversample)
        # Put in history
        histstr = "mygpr.profileSmooth(%d,%d)" %(ntraces,noversample)
        self.history.append(histstr)

        
    def tpowGain(self,power=0.0):
        '''
        Apply a t-power gain to each trace with the given exponent.

        INPUT:
        power     exponent
        '''
        # Store previous state for undo
        self.storePrevious()
        # apply tpowGain
        self.data = tools.tpowGain(self.data,self.twtt,power)
        # Put in history
        histstr = "mygpr.tpowGain(%g)" %(power)
        self.history.append(histstr)

    def agcGain(self,window=10):
        '''
        Apply automated gain controll (AGC) by normalizing the energy
        of the signal over a given window width in each trace

        INPUT:
        window     window width [in "number of samples"]
        '''
        # Store previous state for undo
        self.storePrevious()
        # apply agcGain
        self.data = tools.agcGain(self.data,window)
        # Put in history
        histstr = "mygpr.agcGain(%d)" %(float(window))
        self.history.append(histstr)
        

    def setVelocity(self,velocity):
        '''
        Provide the subsurface RMS radar velocity

        INPUT:
        velocity      subsurface RMS velocity [in m/ns]
        '''
        # Store previous state for undo
        self.storePrevious()

        self.velocity = velocity
        self.depth = self.twtt * velocity/2.0
        
        # Put in history
        histstr = "mygpr.setVelocity(%g)" %(velocity)
        self.history.append(histstr)


    def antennaSep(self):
        ''' 
        Corrects for distortions of arrival times caused by the
        separation of the antennae.

        For this to work properly, you must have set the velocity
        and you must have set the zero time to the beginning of the 
        arrival of the airwave.

        '''

        # Store previous state for undo
        self.storePrevious()

        # Take into account that the airwave first break
        # is after the airwave has already traveled the
        # antenna separation with the speed of light 0.3 m/ns.
        # And we only look at half the
        # two-way travel time. Hence divide by two
        t0 = self.twtt/2 + self.antsep/(2*0.3)

        # t0 is when the waves left the transmitter antenna.
        # To be able to calculate the depth time from the
        # single-way travel time we need to shift the time reference
        # frame. Lets set it "arriving at midpoint time", so
        ta = t0 + self.antsep/(2*self.velocity)
        # Later we will need to undo this reference frame transformation

        # Now use the pythagorean relationship between single-way travel
        # time to the depth point and the depth time td
        tad = np.sqrt( ta**2 - (self.antsep/(2*self.velocity))**2 )

        # We are still in the "arriving at midpoint" time frame ta
        # To transform ta into depth time td, we need to shift it back
        # by the time it took for the ground wave to get to the midpoint.
        # This makes sense because the times before the groundwave got to the
        # midpoint will not actually be underground in the sense of:
        # No travel into depth has been recorded at the receiver.
        # These "arrivals" will just be shifted into "negative arrival times"
        # and hence "negative depth"
        td = tad - self.antsep/(2*self.velocity)

        # Finally, translate time into depth
        self.depth = td*self.velocity

        # And update the two-way travel time
        self.twtt = td
        
        # Put in history
        histstr = "mygpr.antennaSep()"
        self.history.append(histstr)

        
    def fkMigration(self):
        '''
        Apply Stolt's f-k migration to the profile. Requires the 
        velocity to be set.

        This is a wrapper function for the migration code
        imported from Nat Wilson's irlib software.
        '''
        # Store previous state for undo
        self.storePrevious()
        # apply migration
        dt=self.twtt[3]-self.twtt[2]
        #dx=self.profilePos[1]-self.profilePos[0]
        dx=(self.profilePos[-1]-self.profilePos[0])/(len(self.profilePos)-1)
        # fkmig sets x profile to start at zero but resamples
        self.data,self.twtt,migProfilePos=mig_fk.fkmig(self.data,dt,dx,self.velocity)
        self.profilePos = migProfilePos + self.profilePos[0]
        
        # Put in history
        histstr = "mygpr.fkMigration()"
        self.history.append(histstr)
        
        
    def truncateY(self,maxY):
        '''
        Delete all data after y-axis position maxY.

        INPUT:
        maxY    maximum y-axis position for data to be kept
        '''
        # Store previous state for undo
        self.storePrevious()
        if self.velocity is None:
            maxtwtt = maxY
            maxind = np.argmin( np.abs(self.twtt-maxY) )
            self.twtt = self.twtt[0:maxind]
            # Set the last value to maxY
            self.twtt[-1] = maxY
            self.data = self.data[0:maxind,:]
        else:
            maxtwtt = maxY*2.0/self.velocity
            maxind = np.argmin( np.abs(self.twtt-maxtwtt) )
            self.twtt = self.twtt[0:maxind]
            # Set the last value to maxtwtt
            self.twtt[-1] = maxtwtt
            self.data = self.data[0:maxind,:]
            self.depth = self.depth[0:maxind]
            self.depth[-1] = maxY
        # Put in history
        histstr = "mygpr.truncateY(%g)" %(maxY)
        self.history.append(histstr)


        
    def topoCorrect(self,topofile,delimiter=','):
        '''
        Correct for topography along the profile by shifting each 
        Trace up or down depending on a provided ASCII text file
        containing topography information.

        The topography data file can either have 
        two columns: profile position and topography,
        or three columns: X, Y, and topography, or Easting, Northing, topography
        
        In the topo text file, units of profile position (or northing and easting)
        and of the topography (or elevation) need to be in meters!

        Requires the velocity to be set.

        INPUT:
        topofile      file name for ASCII text topography information
        delimiter     how the entries are delimited (by comma, or by tab)
                      [default: ',']. To set tab: delimiter='\t'
        '''
        if self.velocity is None:
            print("First need to set velocity!")
            return
        # Store previous state for undo
        self.storePrevious()
        self.data_pretopo = self.data
        self.twtt_pretopo = self.twtt
        topoPos, topoVal, self.threeD = tools.prepTopo(topofile,delimiter,self.profilePos[0])
        self.data, self.twtt, self.maxTopo, self.minTopo = tools.correctTopo(self.data,
                                                                             velocity=self.velocity,
                                                                             profilePos=self.profilePos,
                                                                             topoPos=topoPos,
                                                                             topoVal=topoVal,
                                                                             twtt=self.twtt)
        # Put in history
        if delimiter == ',':
            histstr = "mygpr.topoCorrect('%s')" %(topofile)
        else:
            histstr = "mygpr.topoCorrect('%s',delimiter='\\t')" %(topofile)
        self.history.append(histstr)
        


    def exportVTK(self,outfile,gpsinfo,delimiter=',',thickness=0,aspect=1.0,smooth=True, win_length=51, porder=3):
        '''
        Turn processed profile into a VTK file that can be imported in 
        Paraview or MayaVi or other VTK processing and visualization tools.

        If three-dimensional topo information is provided (X,Y,Z or 
        Easting, Northing, Elevation), then the profile will be exported 
        in its three-dimensional shape.

        INPUT:
        outfile       file name for the VTK file
        gpsinfo       EITHER: n x 3 matrix containing x, y, and z or 
                              Easting, Northing, Elevation information
                      OR: file name for ASCII text file containing this
                          information
        delimiter     if topo file is provided: delimiter (by comma, or by tab)
                      [default: ',']. To set tab: delimiter='\t' 
        thickness     If you want your profile to be exported as a 
                      three-dimensional band with thickness, enter thickness
                      in meters [default: 0]
        aspect        aspect ratio in case you want to exaggerate z-axis.
                      default = 1. I recommend leaving this at 1 and using 
                      your VTK visualization software to set the aspect for
                      the representation.
        smooth        Want to smooth the profile's three-dimensional alignment
                      instead of piecewise linear? [Default: True]
        win_length    If smoothing, the window length for 
                      scipy.signal.savgol_filter [default: 51]
        porder        If smoothing, the polynomial order for
                      scipy.signal.savgol_filter [default: 3]
        '''
        # If gpsmat is a filename, we first need to load the file:
        if type(gpsinfo) is str:
            gpsmat = np.loadtxt(gpsinfo,delimiter=delimiter)
        else:
            gpsmat = gpsinfo
            
        # First get the x,y,z positions of our data points
        x,y,z = tools.prepVTK(self.profilePos,gpsmat,smooth,win_length,porder)        
        z = z*aspect     
        if self.velocity is None:
            downward = self.twtt*aspect
        else:
            downward = self.depth*aspect                        
        Z = np.reshape(z,(len(z),1)) - np.reshape(downward,(1,len(downward)))

        
        if thickness:
            ZZ = np.tile(np.reshape(Z, (1,Z.shape[0],Z.shape[1])), (2,1,1))
        else:
            ZZ = np.tile(np.reshape(Z, (1,Z.shape[0],Z.shape[1])), (1,1,1))
        
        # This is if we want everything on the x axis.
        #X = np.tile(np.reshape(self.profilePos,(len(self.profilePos),1)),(1,len(downward)))
        #XX = np.tile(np.reshape(X, (X.shape[0],1,X.shape[1])), (1,2,1))
        #YY = np.tile(np.reshape([-thickness/2,thickness/2],(1,2,1)), (len(x),1,len(downward)))

        # To create a 3D grid with a width, calculate the perpendicular direction,
        # normalize it, and add it to xvals and yvals as below.
        # To figure this out, just drar the profile point-by-point, and at each point,
        # draw the perpendicular to the segment and place a grid point in each perpendicular
        # direction
        #
        #          x[0]-px[0], x[1]-px[1], x[2]-px[2], ..... 
        # xvals =     x[0]   ,    x[1]   ,     x[2]  , .....   
        #          x[0]+px[0], x[1]+px[1], x[2]+px[2], .....
        #  
        #          y[0]+py[0], y[1]+py[1], y[2]+py[2], .....
        # yvals =     y[0]   ,    y[1]   ,    y[2]   , .....
        #          y[0]-py[0], y[1]-py[1], y[2]-py[2], .....
        #
        # Here, the [px[i],py[i]] vector needs to be normalized by the thickness
        if thickness:
            pvec = np.asarray([(y[0:-1]-y[1:]).squeeze(), (x[1:]-x[0:-1]).squeeze()])
            pvec = np.divide(pvec, np.linalg.norm(pvec,axis=0)) * thickness/2.0
            # We can't calculate the perpendicular direction at the last point
            # let's just set it to the same as for the second-to-last point
            pvec = np.append(pvec, np.expand_dims(pvec[:,-1],axis=1) ,axis=1)
            X = np.asarray([(x.squeeze()-pvec[0,:]).squeeze(), (x.squeeze()+pvec[0,:]).squeeze()])
            Y = np.asarray([(y.squeeze()+pvec[1,:]).squeeze(), (y.squeeze()-pvec[1,:]).squeeze()])
        else:
            X = np.asarray([x.squeeze()])
            Y = np.asarray([y.squeeze()])
        
        # Copy-paste the same X and Y positions for each depth
        XX = np.tile(np.reshape(X, (X.shape[0],X.shape[1],1)), (1,1,ZZ.shape[2]))
        YY = np.tile(np.reshape(Y, (Y.shape[0],Y.shape[1],1)), (1,1,ZZ.shape[2]))
        
        if self.maxTopo is None:
            data=self.data.transpose()
        else:
            data=self.data_pretopo.transpose()       

        data = np.asarray(data)
        data = np.reshape(data,(1,data.shape[0],data.shape[1]))                 
        data = np.tile(data, (2,1,1))
        
        # Remove the last row and column to turn it into a cell
        # instead of point values 
        data = data[0:-1,0:-1,0:-1]

        nx=2-1
        ny=len(x)-1
        nz=len(downward)-1
        datarray = np.zeros(nx*ny*nz).reshape(nx,ny,nz)
        datarray[:,:,:] = data
        
        gridToVTK(outfile,XX,YY,ZZ, cellData ={'gpr': datarray})
 
        # Put in history
        if gpsinfo is None:
            histstr = "mygpr.exportVTK('%s',aspect=%g)" %(outfile,aspect)
        else:
            if type(gpsinfo) is str:            
                if delimiter == ',':
                    histstr = "mygpr.exportVTK('%s',gpsinfo='%s',thickness=%g,delimiter=',',aspect=%g,smooth=%r, win_length=%d, porder=%d)" %(outfile,gpsinfo,thickness,aspect,smooth,win_length,porder)
                else:
                    histstr = "mygpr.exportVTK('%s',gpsinfo='%s',thickness=%g,delimiter='\\t',aspect=%g,smooth=%r, win_length=%d, porder=%d)" %(outfile,gpsinfo,thickness,aspect,smooth,win_length,porder)
            else:
                if delimiter == ',':
                    histstr = "mygpr.exportVTK('%s',gpsinfo=mygpr.threeD,thickness=%g,delimiter=',',aspect=%g,smooth=%r, win_length=%d, porder=%d)" %(outfile,thickness,aspect,smooth,win_length,porder)
                else:
                    histstr = "mygpr.exportVTK('%s',gpsinfo=mygpr.threeD,thickness=%g,delimiter='\\t',aspect=%g,smooth=%r, win_length=%d, porder=%d)" %(outfile,thickness,aspect,smooth,win_length,porder)
                    
        self.history.append(histstr)       
        
    def storePrevious(self):
        '''
        Stores the current state of the profile and history in the 
        "previous" variable to be able to apply undo.
        '''
        self.previous["data"] = self.data
        self.previous["twtt"] = self.twtt
        self.previous["info"] = self.info
        self.previous["profilePos"] = self.profilePos
        self.previous["history"] = self.history
        self.previous["velocity"] = self.velocity
        self.previous["depth"] = self.depth
        self.previous["maxTopo"] = self.maxTopo
        self.previous["threeD"] = self.threeD
        self.previous["data_pretopo"] = self.data_pretopo
        self.previous["twtt_pretopo"] = self.twtt_pretopo
        
    def signaltrace(self, trace):
        idx = np.abs(self.profilePos - trace).argmin()
        self.data = np.array(self.data)
        data = self.data[:,idx]

        delta = (self.twtt[3] - self.twtt[2])*1e-9
        npts = len(data) 
        print('ntps: ', npts)
        x = delta * np.arange(npts)
        xf = fft.fftfreq(npts, delta)
        yf = fft.fft(data)
        sf = st(data)

        return x*1e9, data, np.abs(xf)*1e-6, np.abs(yf), 1/delta, np.abs(sf)
     
    def filter(self, f_min, f_max):
        data = self.data
        cutoff = [f_min, f_max]
        fs = 1 / (self.twtt[3] - self.twtt[2]) * 1e9
        print("\nfs = ", fs)
        self.data = butterworth(data, cutoff, fs, order=6, btype="bandpass", axis=0)


    def kirchhoffmigration(self):
        start_time=time.time()
        data = np.array(self.data.T)
        noff = 2
        nx, nt = data.shape
        print("data shape: ", data.shape)
        newdata = data.reshape((noff, nx//noff, nt), order='F')
        newdata = newdata.astype(np.float32)
        print("new data shape: ", newdata.shape)

        noff, nx, nt = newdata.shape
        dx = self.profilePos[3] - self.profilePos[2]
        dt = (self.twtt[3] - self.twtt[2])*1e-9 
        ntrc = nx
        nz = nt
        dz = V*dt/2
        dcdp = dx


        print("Waiting...")
        kfdata = full_migration(data=newdata, 
                                nx=nx, nz=nz, noff=noff, ntrc=nx, nsmp=nt,
                                dx=dx, dz=dz, dt=dt, dcdp=dcdp, 
                                offsets=np.arange(0, noff*ntrc*dx, ntrc*dx).astype(np.float32), 
                                V=self.velocity * 1e9)
        #kfdata = full_migration(newdata, nx=nx, nz=nz, noff=noff, dt=dt, dx=dx, dz=dx, dcdp=dx, V=self.velocity, offsets=np.array([0, 500]))
        print("data shape after kirchhoffmigration: ", kfdata.shape)
        self.data = kfdata.reshape(nx*noff, nt).T
        print("所用时间：", time.time()-start_time, " s")

    def noiseCC(self):
        start_time=time.time()
        X_data = self.data.T
        size = X_data.shape
        X_data=skimage.transform.resize(X_data, size, mode='edge')
        print("Waiting...")
        RefData=Robust_NMF.PreProcessGPR(X_data,lambda_=5e-3,max_iter=2000,rank=2)
        self.data = (X_data - RefData).T
        print("所用时间：", time.time()-start_time, " s")


    def stspectrum(self, ax, fmin, fmax):   
        start_time=time.time()
        datas = np.array(self.data)
        delta = (self.twtt[3] - self.twtt[2])*1e-9
        npts = datas.shape[0]
        t = delta * np.arange(npts)*1e9
        print('ntps: ', npts)
        xf = np.abs(fft.fftfreq(npts, delta))
        dx = self.profilePos[3] - self.profilePos[2]
        print("xf: ", xf.shape, np.max(xf))
        idex_min = np.abs(xf - fmin*1e6).argmin()
        idex_max = np.abs(xf - fmax*1e6).argmin()
        print(idex_min, idex_max)

        print("Waiting...")
        nt, nx = datas.shape

        
        for ix in range(nx):
            
            data_st = st(datas[:,ix])
            data_st_one_trace = np.zeros_like(data_st[0, :])
            #print('data_st: ', data_st.shape)
            for j in range(idex_min, idex_max):
                data_st_one_trace += np.abs(data_st[j, :])
            datas[:, ix] = data_st_one_trace

        ax.imshow(datas, extent=[0, nx*dx, np.max(t), 0], aspect='auto', cmap='jet', )
        ax.set_ylabel("Time [ns]"); ax.set_xlabel("trace")

        print("所用时间：", time.time()-start_time, " s")
        return ax