#!/usr/bin/env pythoncolsp
# @file:           csimGPRGUI.py
# @author:         Zhiyu Zhang
# @Institution:    JiLin University
# @Email:          erbiaoger@gmail.com
# @url:            erbiaoger.site
# @date:           2023-07-18 21:10:10
# @Description     界面部分：用于csimGPR的图形用户界面
# @version:        v1.0.0


import sys
import os
import Pmw
import numpy as np
import scipy.interpolate as interp
from scipy.interpolate import interp1d

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import messagebox as mesbox

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
mpl.use('TkAgg')

from csimGPR import csimGPR
from csimGPR.toolbox import csimStartGUI



class GPRPyApp:
    '''
    GPRPy class for graphical user interface for GPR profile data
    '''

    def __init__(self,master, colsp=2, rightcol=9, halfwid=6, figrowsp=21+1, figcolsp=9):
        self.window = master

        self.colsp = colsp
        self.rightcol = rightcol
        self.halfwid = halfwid
        self.figrowsp = figrowsp
        self.figcolsp = figcolsp
        
        # Set up for high-resolution screens
        normscrwidt=1280 #1024
        normscrhigt=720 #768
        # 获取屏幕宽度，高度
        scrwidt=master.winfo_screenwidth()
        scrhigt=master.winfo_screenheight()
        # These to use if operating system doesn't automatically adjust
        #self.widfac=scrwidt/normscrwidt
        #self.highfac=scrhigt/normscrhigt
        self.widfac=normscrwidt/normscrhigt
        self.highfac=1
        #fontfac=(normscrwidt/normscrhigt)/(scrwidt/scrhigt)
        fontfac=1
        
        # Set some default choices
        self.hypx = 0
        self.hypt = 0
        self.hypv = 0.1
        
        master.title("CSIM - 月球及火星次表层结构解译")
        
        # Variables specific to GUI
        self.balloon = Pmw.Balloon()
        #self.balloon = tk.Label(master, text="balloon", height = 1, width = 2*self.halfwid)
        self.picking = False
        self.delimiter = None
        self.grid = False

        # Initialize the gprpy
        proj = csimGPR.gprpyProfile()

        # Show csimGPR screen
        #fig=Figure(figsize=(8*self.widfac,5*self.highfac))
        fig=Figure(figsize=(self.widfac,self.highfac))
        a=fig.add_subplot(111)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        csimStartGUI.showcsimGPR(a,dir_path,self.widfac,self.highfac,fontfac)

        # Set font size for screen res
        mpl.rcParams.update({'font.size': mpl.rcParams['font.size']*self.widfac})
        a.tick_params(direction='out',length=6*self.widfac,width=self.highfac)
        
        a.get_xaxis().set_visible(False)
        a.get_yaxis().set_visible(False)
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().grid(row=2,column=0,columnspan=self.figcolsp,rowspan=self.figrowsp,sticky='nsew')

        canvas.draw() 

        self.initLoadData(proj)
        #self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)
               
        self.curves = {}
        self.leijia = 0

        ## Visualization Buttons              

        # Undo Button
        undoButton = tk.Button(
            text="撤回",
            command=lambda : [self.resetYrng(proj),
                              self.undo(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        undoButton.config(height = 1, width = 2*self.halfwid)
        undoButton.grid(row=0, column=0, sticky='nsew',rowspan=2)
        self.balloon.bind(undoButton,
                          "“撤消”最近的处理步骤并\n"
                           "将数据设置回其先前的状态。\n"
                           "这也删除了最近的处理\n"
                           "从历史中走出来。 不恢复\n"
                           "可视化设置，例如“设置 x 范围”\n"
                           "等。")

        # Full view
        FullButton = tk.Button(
            text="全视图", fg="black",
            command=lambda : [self.setFullView(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        FullButton.config(height = 1, width = 2*self.halfwid)         
        FullButton.grid(row=0, column=1, sticky='nsew',rowspan=1)
        self.balloon.bind(FullButton,"将 x 轴和 y 轴限制重置为完整数据。")

        # Refreshing plot
        plotButton = tk.Button(
            text="刷新绘图",
            command=lambda : self.plotProfileData(proj,fig=fig,a=a,canvas=canvas))
        plotButton.config(height = 1, width = 2*self.halfwid)
        plotButton.grid(row=1, column=1, sticky='nsew',rowspan=1)
        self.balloon.bind(plotButton,
                          "修改后刷新图形\n"
                           "在可视化设置中。另外\n"
                           "删除任何绘制的双曲线。")
        
        # Grid button
        GridButton = tk.Button(
            text="网格", fg="black",
            command=lambda : [self.toggleGrid(),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        GridButton.config(height = 1, width = 2*self.halfwid)         
        GridButton.grid(row=0, column=2, sticky='nsew',rowspan=1)
        self.balloon.bind(GridButton,"打开/关闭网格。")

        # Aspect
        AspButton = tk.Button(
            text="纵横比", fg="black",
            command=lambda : [self.setAspect(),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])                              
        AspButton.config(height = 1, width = 2*self.halfwid)         
        AspButton.grid(row=1, column=2, sticky='nsew',rowspan=1)
        self.balloon.bind(AspButton, "设置 x 轴和 y 轴之间的纵横比。")
        
        # X range
        XrngButton = tk.Button(
            text="设置 x 轴范围", fg="black",
            command=lambda : [self.setXrng(),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        XrngButton.config(height = 1, width = 2*self.halfwid)         
        XrngButton.grid(row=0, column=3, sticky='nsew',rowspan=1)
        self.balloon.bind(XrngButton,"设置 x 轴显示限制。")
        
        # Y range
        YrngButton = tk.Button(
            text="设置 y 轴范围", fg="black",
            command=lambda : [self.setYrng(),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        YrngButton.config(height = 1, width = 2*self.halfwid)         
        YrngButton.grid(row=1, column=3, sticky='nsew',rowspan=1)
        self.balloon.bind(YrngButton,"设置 y 轴显示限制。")

        # Contrast
        contrtext = tk.StringVar()
        contrtext.set("对比")
        contrlabel = tk.Label(master, textvariable=contrtext,height = 1,width = 2*self.halfwid)
        contrlabel.grid(row=0, column=4, sticky='nsew')
        self.balloon.bind(contrlabel,"设置色彩饱和度")
        self.contrast = tk.DoubleVar()
        contrbox = tk.Entry(master, textvariable=self.contrast, width=2*self.halfwid)
        contrbox.grid(row=1, column=4, sticky='nsew')
        #contr.set("1.0")
        self.contrast.set("1.0")

        
        # Mode switch for figure color
        self.color=tk.StringVar()
        self.color.set("gray")
        colswitch = tk.OptionMenu(master,self.color,"gray","bwr")
        colswitch.grid(row=0, column=5, sticky='nsew',rowspan=2)
        self.balloon.bind(colswitch,
                          "在灰度之间选择\n"
                            "和蓝白红（bwr）\n" 
                           "数据表示。")
        # 单道绘图 
        signaltraceButton = tk.Button(
            text="单道绘图", fg="black",
            command=lambda : self.plotProfileData_new_windows_oneplus(proj))
        signaltraceButton.config(height = 1, width = 2*self.halfwid)         
        signaltraceButton.grid(row=0, column=6, sticky='nsew',rowspan=1)

        # 带通滤波 
        filterButton = tk.Button(
            text="带通滤波", fg="black",
            command = lambda : [self.filter(proj),
                                self.plotProfileData(proj,fig=fig,a=a,canvas=canvas),
                                print('Done')])
        filterButton.config(height = 1, width = 2*self.halfwid)
        filterButton.grid(row=1, column=6, sticky='nsew',rowspan=1)       

        # Export to VTK
        VTKButton = tk.Button(
            text="export to VTK", fg="black",
            command = lambda : self.exportVTK(proj))
        VTKButton.config(height = 1, width = 2*self.halfwid)
        VTKButton.grid(row=0, column=7, sticky='nsew',rowspan=1)
        self.balloon.bind(VTKButton,
                          "Exports the processed figure to a\n"
                          "VTK format, that can be read by\n" 
                          "Paraview or similar 3D programs.")
        
        # Write script
        HistButton = tk.Button(
            text="write script", fg="black",
            command=lambda : self.writeHistory(proj))
        HistButton.config(height = 1, width = 2*self.halfwid)         
        HistButton.grid(row=1, column=7, sticky='nsew',rowspan=1)
        self.balloon.bind(HistButton,
                          'Writes a python script to reproduce the \n'
                          'current status.\n'
                          '\n'
                          'If the current data is from a .gpr file, \n'  
                          'then the python script will contain all \n'
                          'steps going back to the raw data. \n'
                          '\n'
                          'The script will not contain visualization \n'
                          'settings such as x-range settings, unless \n'
                          'the "print figure" command was used. ')
        
        # 去噪
        signaltraceButton = tk.Button(
            text="去噪", fg="black",
            command=lambda : [self.noiseCC(proj),
                            self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        signaltraceButton.config(height = 1, width = 2*self.halfwid)         
        signaltraceButton.grid(row=0, column=8, sticky='nsew',rowspan=1)

        # st谱
        stspectrumButton = tk.Button(
            text="st谱", fg="black",
            command=lambda : [self.stspectrum(proj)])
        stspectrumButton.config(height = 1, width = 2*self.halfwid)
        stspectrumButton.grid(row=1, column=8, sticky='nsew',rowspan=1)


        ## Methods buttons
        
        # Load data
        LoadButton = tk.Button(
            text="导入数据", fg="red",
            command=lambda : [self.loadData(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        LoadButton.config(height = 1, width = 2*self.halfwid)         
        LoadButton.grid(row=0, column=self.rightcol, sticky='nsew',columnspan=self.colsp,rowspan=2)
        self.balloon.bind(LoadButton,"加载 .2A、.2B、.gpr、.DT1 或 .DZT 数据。")

        
        # Adjust profile length; if trigger wheel is not good
        AdjProfileButton = tk.Button(
            text="剖面适应", fg="black",
            command=lambda : [self.adjProfile(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        AdjProfileButton.config(height = 1, width = 2*self.halfwid)         
        AdjProfileButton.grid(row=2, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(AdjProfileButton,
                          "将配置文件长度调整为 \n"
                           "已知的开始和结束位置\n"
                           "和/或水平翻转配置文件\n"
                           "（左到右）。")

        
        # Set new zero time
        SetZeroTimeButton = tk.Button(
            text="设置零时刻", fg="black",
            command=lambda : [self.setZeroTime(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        SetZeroTimeButton.config(height = 1, width = 2*self.halfwid)         
        SetZeroTimeButton.grid(row=3, column=self.rightcol, sticky='nsew',columnspan=self.colsp)    
        self.balloon.bind(SetZeroTimeButton,
                          "设置行程时间\n"
                           "对应地表。")



        # TimeZero Adjust = align traces
        TrAlignButton = tk.Button(
            text="道对齐", fg="black",
            command=lambda : [proj.alignTraces(),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        TrAlignButton.config(height = 1, width = 2*self.halfwid)         
        TrAlignButton.grid(row=4, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(TrAlignButton,
                         '自动向上或向下移动每条迹线，\n'
                         '使各个迹线的最大幅度对齐。 \n'
                         '当最大值不在空气波中时会导致问题。\n'
                         '如果结果不好，请使用“撤消”按钮。')

        

        # truncate Y
        truncYButton = tk.Button(
            text="Y方向裁剪", fg="black",
            command=lambda : [self.truncateY(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        truncYButton.config(height = 1, width = 2*self.halfwid)         
        truncYButton.grid(row=5, column=self.rightcol+1, sticky='nsew')
        self.balloon.bind(truncYButton,
                          '删除到达时间晚于所选值的数据点。\n'
                           '如果给定速度：删除深度大于所选值的数据点.')   
 


        # Cut
        cutButton = tk.Button(
            text="X方向裁剪", fg="black",
            command=lambda : [self.cut(proj),
                              self.setFullView(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        cutButton.config(height = 1, width = 2*self.halfwid)         
        cutButton.grid(row=5, column=self.rightcol, sticky='nsew')
        self.balloon.bind(cutButton,
                          "将数据修剪到所需的沿剖面范围。") 

        # # kirchhoffmigration
        # kfmigrationButton = tk.Button(
        #     text="科希霍夫偏移", fg="black",
        #     # command=lambda : [self.kirchhoffmigration(proj),
        #     #                   self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        #     command=lambda : [])
        # kfmigrationButton.config(height = 1, width = 2*self.halfwid)         
        # kfmigrationButton.grid(row=6, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        # self.balloon.bind(kfmigrationButton,
        #                   "Trace-wise 低切滤波器。 \n"
        #                   "从每个轨迹中删除所选窗口宽度的运行平均值。")
        
        kirchhoffmigrationButton = tk.Button(
            text="科希霍夫偏移", fg="black",
            command=lambda : [self.kirchhoffmigration(proj),
                            self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        kirchhoffmigrationButton.config(height = 1, width = 2*self.halfwid)
        kirchhoffmigrationButton.grid(row=6, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(kirchhoffmigrationButton,
                            "绘制曲线。")
        
        # Dewow
        DewowButton = tk.Button(
            text="dewow", fg="black",
            command=lambda : [self.dewow(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        DewowButton.config(height = 1, width = 2*self.halfwid)         
        DewowButton.grid(row=7, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(DewowButton,
                          "Trace-wise 低切滤波器。 \n"
                          "从每个轨迹中删除所选窗口宽度的运行平均值。")

        
        # Rem mean trace
        remMeanTraceButton = tk.Button(
            text="去平均", fg="black",
            command=lambda : [self.remMeanTrace(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        remMeanTraceButton.config(height = 1, width = 2*self.halfwid)         
        remMeanTraceButton.grid(row=8, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(remMeanTraceButton,
                          "从每条轨迹中删除平均值\n"
                           "它周围的痕迹。这可以是\n"
                           "可用于去除空气波，地面\n"
                           "波浪，或水平特征。")
        

        # Smooth 
        SmoothButton = tk.Button(
            text="光滑 (temp)", fg="black",
            command=lambda : [self.smooth(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        SmoothButton.config(height = 1, width = 2*self.halfwid)         
        SmoothButton.grid(row=9, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(SmoothButton,
                          "Trace-wise 高切滤波器。\n"
                          "用所选窗口宽度的运行平均值替换轨迹中的每个样本。")

        

        

        # profile Smoothing Button
        profSmButton = tk.Button(
            text="剖面平滑", fg="black",
            command=lambda : [self.profileSmooth(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        profSmButton.config(height = 1, width = 2*self.halfwid)         
        profSmButton.grid(row=10, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(profSmButton,
                          "首先对配置文件进行过采样（制作每个轨迹的“n”个副本），\n"
                          "然后用其相邻“m”个轨迹的平均值替换每个轨迹。")
        

        
        # Gain
        tpowButton = tk.Button(
            text="t-功率增益", fg="black",
            command=lambda : [self.tpowGain(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        tpowButton.config(height=1, width=self.halfwid)
        tpowButton.grid(row=11, column=self.rightcol, sticky='nsew')
        self.balloon.bind(tpowButton,
                          "t-功率增益。 将信号的功率增加（行程时间）^p 倍，\n"
                          "其中用户提供 p。 这种增益往往不如 agc 激进。")

        
        agcButton = tk.Button(
            text="自动增益控制",fg="black",
            command=lambda : [self.agcGain(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        agcButton.config(height=1, width=self.halfwid)
        agcButton.grid(row=11, column=self.rightcol+1, sticky='nsew')
        self.balloon.bind(agcButton,
                          "自动增益控制。沿着每个道，\n"
                          "规范化信号的功率给定样本窗口。")

        # show hyperbola
        hypButton = tk.Button(
            text="绘制双曲线", fg="black",
            command=lambda : [self.showHyp(proj,a), canvas.draw()])
        hypButton.config(height = 1, width = 2*self.halfwid)
        hypButton.grid(row=12, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(hypButton,
                          "根据剖面位置、走时和估计速度绘制双曲线。\n"
                          "当数据中出现双曲线时，这可以用于找到地下速度。\n"
                          "刷新图像后，绘制的双曲线将消失。")

        

        # Set Velocity
        setVelButton = tk.Button(
            text="设置速度", fg="black",
            command=lambda : [self.setVelocity(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        setVelButton.config(height = 1, width = 2*self.halfwid)         
        setVelButton.grid(row=13, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(setVelButton,
                          "设置已知的地下雷达速度。这将将y轴从\n"
                          "走时转换为深度。这一步是进行地形校正所必需的。")


        
        # Correct for antenna separation
        antennaSepButton = tk.Button(
            text="天线偏移校正", fg="black",
            command=lambda : [self.antennaSep(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        antennaSepButton.config(height = 1, width = 2*self.halfwid)         
        antennaSepButton.grid(row=14, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(antennaSepButton,                        
                          "如果提供了天线偏移量，则纠正由于发射\n"
                          "和接收天线之间的分离而导致的接收时间扭曲。\n"
                          "此项功能需要选择空气波的第一个到达时间，\n"
                          "并设置速度。")
        

        # Migration Button # TODO
        migButton = tk.Button(
            text="fk 偏移", fg="black",
            command=lambda : [self.fkMigration(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        migButton.config(height = 1, width = 2*self.halfwid)         
        migButton.grid(row=15, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(migButton,
                          "使用最初为CREWES软件包编写的Matlab代码\n"
                          "进行Stolt的fk偏移。由Nat Wilson翻译成Python 2。")     

        
        
        # Topo Correct
        topoCorrectButton = tk.Button(
            text="地形校正", fg="black",
            command=lambda : [self.topoCorrect(proj),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        topoCorrectButton.config(height = 1, width = 2*self.halfwid)
        topoCorrectButton.grid(row=16, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(topoCorrectButton,
                          "读取一个逗号或制表符分隔的文件，\n"
                          "其中包含3列（东坐标、北坐标、高程）\n"
                          "或两列（剖面位置、高程）的数据。\n"
                          "所有坐标以米为单位。")                                                      
                     

       
        startPickButton = tk.Button(
            text="start pick", fg="black",
            command=lambda : self.startPicking(proj,fig=fig,a=a,canvas=canvas))        
        startPickButton.config(height = 1, width = self.halfwid)
        startPickButton.grid(row=17, column=self.rightcol, sticky='nsew',columnspan=1)
        self.balloon.bind(startPickButton,
                          "Start collecting location information\n" 
                          "by clicking on the profile.")  
        

        stopPickButton = tk.Button(
            text="stop pick", fg="black",
            command=lambda : [self.stopPicking(proj,canvas),
                              self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)])
        
        stopPickButton.config(height = 1, width = self.halfwid)
        stopPickButton.grid(row=17, column=self.rightcol+1, sticky='nsew',columnspan=1)
        self.balloon.bind(stopPickButton,
                          "Stop collecting location information\n"
                          "and save the locations you collected\n"
                          "in a text file.")
        
        # Save data
        SaveButton = tk.Button(
            text="保存数据", fg="black",
            command=lambda : self.saveData(proj))
        SaveButton.config(height = 1, width = 2*self.halfwid)         
        SaveButton.grid(row=18, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(SaveButton,
                          "将处理后的数据以及处理历史保存在一个 .gpr 文件中。\n"
                          "生成的文件将包含所使用数据和地形文件的绝对路径名。\n"
                          "可视化设置如“设置 x 范围”或“对比度”将不会保存。")

        
        
        # Print Figure
        PrintButton = tk.Button(
            text="保存图片", fg="black",
            command=lambda : self.printProfileFig(proj=proj,fig=fig))
        PrintButton.config(height = 1, width = 2*self.halfwid)         
        PrintButton.grid(row=19, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(PrintButton,
                          "以选择的分辨率将当前可见的图形保存为 PDF。\n"
                          "如果当前图形上有双曲线，则双曲线也会出现在\n"
                          "打印的图形上。")
        
        # getPoint
        getPointButton = tk.Button(
            text="getPoint", fg="black",
            command=lambda : self.getPoint(proj, fig,a,canvas))
        getPointButton.config(height = 1, width = 2*self.halfwid)
        getPointButton.grid(row=20, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(getPointButton,
                            "使用Diffrapy软件包进行处理。")
        
        plotCurvesButton = tk.Button(
            text="plot curves", fg="black",
            command=lambda : self.plotCurves(proj,a,canvas))
        plotCurvesButton.config(height = 1, width = 2*self.halfwid)
        plotCurvesButton.grid(row=21, column=self.rightcol, sticky='nsew',columnspan=self.colsp)
        self.balloon.bind(plotCurvesButton,
                            "绘制曲线。")

    def stspectrum(self, proj):
        
        print("\nDoing stspectrum...")
        f_min = sd.askfloat("输入","s变换滤波器的下截止频率 [MHz]")
        f_max = sd.askfloat("输入","s变换滤波器的上截止频率 [MHz]")

        newroot = tk.Tk(); newroot.columnconfigure(1, weight=1); newroot.rowconfigure(1, weight=1); newroot.title('st 时频谱')
        fig = Figure(figsize=(12, 10)); fig.clear(); a = fig.add_subplot(111); a.clear()
        a = proj.stspectrum(a, f_min, f_max)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=newroot)
        canvas.get_tk_widget().grid(row=1, column=1, columnspan=10, rowspan=8, sticky='nsew')
        canvas.draw()
        print("stspectrum Done.\n")



    def noiseCC(self, proj):
        print("\nDoing NoiseCC...")
        proj.noiseCC()
        print("NoiseCC Done.\n")


    def kirchhoffmigration(self, proj):
        print("\nDoing Kirchhoffmigration...")
        proj.kirchhoffmigration()
        print("Kirchhoffmigration Done.\n")


    def plotProfileData_new_windows_oneplus(self, proj):
        trace = sd.askfloat("输入","道坐标")
        t, tracedata, xf, yf, fs, sf = proj.signaltrace(trace)
        newroot = tk.Tk(); newroot.columnconfigure(1, weight=1); newroot.rowconfigure(1, weight=1); newroot.title('坐标 '+ str(trace) + '单道图')
        fig = Figure(figsize=(12, 10)); fig.clear(); 

        a = fig.add_subplot(221); a.clear()
        a.plot(t, tracedata)
        a.set_xlabel("Time [ns]"); a.set_ylabel("Amplitude"); a.set_title("Single-channel signal diagram")

        b = fig.add_subplot(222); b.clear()
        b.plot(xf, yf)
        b.set_xlabel("Frequency [MHz]"); b.set_ylabel("Amplitude"); b.set_title("frequency graph")

        c = fig.add_subplot(223); c.clear()
        
        # 绘制谱图
        #f_sp, t_sp, Sxx = signal.spectrogram(tracedata, fs)
        #c.pcolormesh(t_sp, f_sp, Sxx)
        #print(np.max(f_sp), f_sp.shape, np.max(t_sp), t_sp.shape)
        c.specgram(tracedata, Fs=fs, cmap='jet')
        c.set_xlabel('Time [s]'); c.set_ylabel('Frequency [Hz]'); c.set_title('Time-Frequency Diagram')

        d = fig.add_subplot(224); d.clear()
        d.imshow(sf, extent=[0, np.max(t), np.max(xf), 0], aspect='auto', cmap='jet')
        d.set_xlabel('Time [ns]'); d.set_ylabel('Frequency [MHz]'); d.set_title('st time-frequency diagram')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=newroot)
        canvas.get_tk_widget().grid(row=1, column=1, columnspan=10, rowspan=8, sticky='nsew')
        canvas.draw()

    def filter(self, proj):
        f_min = sd.askfloat("输入","带通滤波器的下截止频率 [MHz]")
        f_max = sd.askfloat("输入","带通滤波器的上截止频率 [MHz]")
        proj.filter(f_min*1e6, f_max*1e6)
        

    def undo(self,proj):
        if self.picking:
            self.picked=self.picked[0:-1,:]
        else:
            proj.undo()                        
        
      
    def setYrng(self):
        ylow = sd.askfloat("Input","Min Y value",initialvalue=self.yrng[0])
        if ylow is not None:            
            yhigh = sd.askfloat("Input","Max Y value",initialvalue=self.yrng[1])
            if yhigh is not None:
                self.prevyrng=self.yrng
                self.yrng=[ylow,yhigh]
        

    def resetYrng(self,proj):
        # Only needed in undo, and only if what you want to
        # undo changed the y axis
        if ("setVelocity" in proj.history[-1]) or ("topoCorrect" in proj.history[-1]): 
            self.yrng=self.prevyrng


    def setAspect(self):
        self.asp = sd.askfloat("Input","Plotting aspect ratio", initialvalue=self.asp)
        

    def setFullView(self,proj):    
        self.xrng=[np.min(proj.profilePos),np.max(proj.profilePos)]
        if proj.velocity is None:
            self.yrng=[np.min(proj.twtt),np.max(proj.twtt)]
        elif proj.maxTopo is None:
            self.yrng=[np.min(proj.depth),np.max(proj.depth)]
        else:
            self.yrng=[proj.minTopo-np.max(proj.depth),proj.maxTopo-np.min(proj.depth)]

            
    def toggleGrid(self):
        self.grid = not self.grid
            
            
    def setXrng(self):
        xlow = sd.askfloat("Input","Min X value",initialvalue=self.xrng[0])
        if xlow is not None:
            xhigh = sd.askfloat("Input","Max X value",initialvalue=self.xrng[1])
            if xhigh is not None:
                self.xrng=[xlow,xhigh]
        

    def adjProfile(self,proj):
        flipit = mesbox.askyesno("Question","Flip the profile (left to right)?")
        if flipit:
            proj.flipProfile()        
        minPos = sd.askfloat("Input","Start x coordinate",initialvalue=self.xrng[0])
        if minPos is not None:
            maxPos = sd.askfloat("Input","End x coordinate",initialvalue=self.xrng[1])
            if maxPos is not None:
                proj.adjProfile(minPos=minPos,maxPos=maxPos)
                self.xrng=[minPos,maxPos]

                
    def setZeroTime(self,proj):
        newZeroTime = sd.askfloat("Input","New zero time")
        if newZeroTime is not None:
            proj.setZeroTime(newZeroTime=newZeroTime)
        
        
    def dewow(self,proj):
        window = sd.askinteger("Input","Dewow window width (number of samples)")
        if window is not None:
            proj.dewow(window=window)


    def smooth(self,proj):
        window = sd.askinteger("Input","Smoothing window width (number of samples)")
        if window is not None:
            proj.smooth(window=window)
            

    def remMeanTrace(self,proj):
        ntraces = sd.askinteger("Input","Remove mean over how many traces?")
        if ntraces is not None:
            proj.remMeanTrace(ntraces=ntraces)


    def tpowGain(self,proj):
        power = sd.askfloat("Input","Power for tpow gain?")
        if power is not None:
            proj.tpowGain(power=power)
        

    def agcGain(self,proj):
        window = sd.askinteger("Input","Window length for AGC?")
        if window is not None:
            proj.agcGain(window=window)

    def truncateY(self,proj):
        maxY = sd.askfloat("Input","Truncate at what y value\n" 
                           "(travel time or depth)")
        if maxY is not None:
            proj.truncateY(maxY)
        
    def cut(self,proj):
        minX = sd.askfloat("输入","最小剖面位置")
        if minX is not None:
            maxX = sd.askfloat("输入","最大剖面位置")
            if maxX is not None:
                proj.cut1(minX,maxX)
            
    def setVelocity(self,proj):
        velocity =  sd.askfloat("Input","Radar wave velocity [m/ns]?")        
        if velocity is not None:
            proj.setVelocity(velocity)
            self.prevyrng=self.yrng
            self.yrng=[0,np.max(proj.depth)]

    def antennaSep(self,proj):
        if proj.velocity is None:
            mesbox.showinfo("Antenna Sep Error","You have to set the velocity first")
        proj.antennaSep()

            
    def fkMigration(self,proj):
        if proj.velocity is None:
            mesbox.showinfo("Migration Error","You have to set the velocity first")
        proj.fkMigration()


    def profileSmooth(self,proj):
        ntraces = sd.askinteger("Input","Smooth over how many traces (m)")
        if ntraces is not None:
            noversample = sd.askinteger("Input","Make how many copies of each trace (n).\nRecommended: Same as number of traces to be smoothed.")
            if noversample is not None:
                proj.profileSmooth(ntraces,noversample)
        
            
    def topoCorrect(self,proj):
        if proj.velocity is None:
            mesbox.showinfo("Topo Correct Error","You have to set the velocity first")
            return
        topofile = fd.askopenfilename()
        if topofile != '':
            out = self.getDelimiter()    
            proj.topoCorrect(topofile,self.delimiter)
            self.prevyrng=self.yrng
            self.yrng=[proj.minTopo-np.max(proj.depth),proj.maxTopo]


   

    def startPicking(self,proj,fig,a,canvas):
        self.picking = True
        self.picked = np.asmatrix(np.empty((0,2)))
        print("Picking mode on")
        def addPoint(event):
            self.picked = np.append(self.picked,np.asmatrix([event.xdata,event.ydata]),axis=0)
            self.plotProfileData(proj,fig=fig,a=a,canvas=canvas)
            print(self.picked)
        self.pick_cid = canvas.mpl_connect('button_press_event', addPoint)

            

    def stopPicking(self,proj,canvas):
        filename = fd.asksaveasfilename()
        if filename != '':
            self.picking = False
            canvas.mpl_disconnect(self.pick_cid)
            print("Picking mode off")
            np.savetxt(filename+'_profile.txt',self.picked,delimiter='\t')
            print('saved picked file as "%s"' %(filename+'_profile.txt'))
            # If we have 3D info, also plot it as 3D points
            if proj.threeD is not None:
                # First calculate along-track points
                topoVal = proj.threeD[:,2]
                npos = proj.threeD.shape[0]
                steplen = np.sqrt(
                    np.power( proj.threeD[1:npos,0]-proj.threeD[0:npos-1,0] ,2.0) + 
                    np.power( proj.threeD[1:npos,1]-proj.threeD[0:npos-1,1] ,2.0) +
                    np.power( proj.threeD[1:npos,2]-proj.threeD[0:npos-1,2] ,2.0)
                )
                alongdist = np.cumsum(steplen)
                topoPos = np.append(0,alongdist)
                pick3D = np.zeros((self.picked.shape[0],3))
                # If profile is adjusted, need to start the picked at zero.
                pickProfileShifted = self.picked[:,0] - np.min(proj.profilePos)
                #for i in range(0,3):
                for i in range(0,2):
                    pick3D[:,i] = interp.pchip_interpolate(topoPos,
                                                           proj.threeD[:,i],
                                                           pickProfileShifted).squeeze()
                                                           #self.picked[:,0]).squeeze()
            
                pick3D[:,2] = self.picked[:,1].squeeze()
                    
                np.savetxt(filename+'_3D.txt',pick3D,delimiter='\t')
                print('saved picked file as "%s"' %(filename+'_3D.txt'))              
                
        
    def loadData(self,proj):
        filename = fd.askopenfilename( filetypes= (("All", "*.*"),
                                                   ('mat', '*.mat'),
                                                   ('2A', '*.2A'),
                                                   ('2B', '*.2B'),
                                                   ("GPRPy (.gpr)", "*.gpr"),
                                                   ("Sensors and Software (.DT1)", "*.DT1"),
                                                   ("GSSI (.DZT)", "*.DZT"),
                                                   ("BSQ header","*.GPRhdr"),
                                                   ("MALA header","*.rad")))
        if filename:
            proj.importdata(filename=filename)
            self.xrng = [np.min(proj.profilePos),np.max(proj.profilePos)]
            if proj.depth is None:
                self.yrng = [0,np.max(proj.twtt)]
            else:
                if proj.maxTopo is None:
                    self.yrng = [0,np.max(proj.depth)]
                else:
                    self.yrng = [proj.maxTopo-np.max(proj.depth), proj.maxTopo]
            self.asp=None
            # Just in case someone presses undo before changing yrange        
            self.prevyrng=self.yrng    
            print("导入 " + filename + " 成功")
            
    def loadDataMars(self,proj):
        filename = fd.askopenfilename( filetypes= (("All", "*.*"),
                                                   ('mat', '*.mat'),
                                                   ('2A', '*.2A'),
                                                   ('2B', '*.2B'),
                                                   ("GPRPy (.gpr)", "*.gpr"),
                                                   ("Sensors and Software (.DT1)", "*.DT1"),
                                                   ("GSSI (.DZT)", "*.DZT"),
                                                   ("BSQ header","*.GPRhdr"),
                                                   ("MALA header","*.rad")))
        if filename:
            proj.importdataMars(filename=filename)
            self.xrng = [np.min(proj.profilePos),np.max(proj.profilePos)]
            if proj.depth is None:
                self.yrng = [0,np.max(proj.twtt)]
            else:
                if proj.maxTopo is None:
                    self.yrng = [0,np.max(proj.depth)]
                else:
                    self.yrng = [proj.maxTopo-np.max(proj.depth), proj.maxTopo]
            self.asp=None
            # Just in case someone presses undo before changing yrange        
            self.prevyrng=self.yrng    
            print("导入 " + filename + " 成功")

    def initLoadData(self,proj):
        filename = 'examples/CE4_GRAS_LPR-2A_SCI_N_20190104004000_20190109213900_0001_A.2A'
        proj.importdata(filename=filename)
        self.xrng = [np.min(proj.profilePos),np.max(proj.profilePos)]
        if proj.depth is None:
            self.yrng = [0,np.max(proj.twtt)]
        else:
            if proj.maxTopo is None:
                self.yrng = [0,np.max(proj.depth)]
            else:
                self.yrng = [proj.maxTopo-np.max(proj.depth), proj.maxTopo]
        self.asp=None
        # Just in case someone presses undo before changing yrange        
        self.prevyrng=self.yrng    


    def initLoadData(self,proj):
        filename = 'examples/CE4_GRAS_LPR-2A_SCI_N_20190104004000_20190109213900_0001_A.2A'
        proj.importdata(filename=filename)
        self.xrng = [np.min(proj.profilePos),np.max(proj.profilePos)]
        if proj.depth is None:
            self.yrng = [0,np.max(proj.twtt)]
        else:
            if proj.maxTopo is None:
                self.yrng = [0,np.max(proj.depth)]
            else:
                self.yrng = [proj.maxTopo-np.max(proj.depth), proj.maxTopo]
        self.asp=None
        # Just in case someone presses undo before changing yrange        
        self.prevyrng=self.yrng    


        
    def saveData(self,proj):        
        filename = fd.asksaveasfilename(defaultextension=".gpr")
        if filename != '':
            proj.save(filename)


    def exportVTK(self,proj):                    
        outfile = fd.asksaveasfilename()
        if outfile != '':
            #thickness = sd.askfloat("Input","Profile thickness [m]")
            thickness = 0
            if self.asp is None:
                aspect = 1.0
            else:
                aspect = self.asp
            
            if proj.threeD is None:
                gpyes = mesbox.askyesno("Question","Do you have topography data for this profile?")
                if gpyes:
                    filename = fd.askopenfilename()
                    self.getDelimiter()
                    proj.exportVTK(outfile,gpsinfo=filename,thickness=thickness,delimiter=self.delimiter,aspect=aspect)
            else:
                proj.exportVTK(outfile,gpsinfo=proj.threeD,thickness=thickness,delimiter=self.delimiter,aspect=aspect)
            print('... done with exporting to VTK.')
                
    def writeHistory(self,proj):        
        filename = fd.asksaveasfilename(defaultextension=".py")
        if filename != '':
            proj.writeHistory(filename)
            print("Wrote script to " + filename)

    def plotProfileData(self,proj,fig,a,canvas):
        # Clear cursor coordinate cid if if exists to avoid multiple instances
        print('\nDoing plotProfileData ...')
        if 'self.cursor_cid' in locals():
            canvas.mpl_disconnect(self.cursor_cid)            
        dx=proj.profilePos[3]-proj.profilePos[2]
        dt=proj.twtt[3]-proj.twtt[2]
        a.clear()        
        print("plotProfileData shape: ", proj.data.shape)
        stdcont = np.nanmax(np.abs(proj.data)[:])        
        if proj.velocity is None:
            a.imshow(proj.data,cmap=self.color.get(),extent=[min(proj.profilePos)-dx/2.0,
                                                             max(proj.profilePos)+dx/2.0,
                                                             max(proj.twtt)+dt/2.0,
                                                             min(proj.twtt)-dt/2.0],
                     aspect="auto",
                     vmin=-stdcont/self.contrast.get(), vmax=stdcont/self.contrast.get())
            a.set_ylim(self.yrng)
            a.set_xlim(self.xrng)
            a.set_ylabel("time [ns]", fontsize=mpl.rcParams['font.size'])
            a.invert_yaxis()
        elif proj.maxTopo is None:
            dy=dt*proj.velocity
            a.imshow(proj.data,cmap=self.color.get(),extent=[min(proj.profilePos)-dx/2.0,
                                                             max(proj.profilePos)+dx/2.0,
                                                             max(proj.depth)+dy/2.0,
                                                             min(proj.depth)-dy/2.0],
                     aspect="auto",
                     vmin=-stdcont/self.contrast.get(), vmax=stdcont/self.contrast.get())
            a.set_ylabel("depth [m]", fontsize=mpl.rcParams['font.size'])
            a.set_ylim(self.yrng)
            a.set_xlim(self.xrng)
            a.invert_yaxis()
        else:
            dy=dt*proj.velocity
            a.imshow(proj.data,cmap=self.color.get(),extent=[min(proj.profilePos)-dx/2.0,
                                                             max(proj.profilePos)+dx/2.0,
                                                             proj.minTopo-max(proj.depth)-dy/2.0,
                                                             proj.maxTopo-min(proj.depth)+dy/2.0],
                     aspect="auto",
                     vmin=-stdcont/self.contrast.get(), vmax=stdcont/self.contrast.get())
            a.set_ylabel("elevation [m]", fontsize=mpl.rcParams['font.size'])
            a.set_ylim(self.yrng)
            a.set_xlim(self.xrng)

        a.get_xaxis().set_visible(True)
        a.get_yaxis().set_visible(True)                    
        a.set_xlabel("profile position [m]", fontsize=mpl.rcParams['font.size'])
        a.xaxis.tick_top()
        a.xaxis.set_label_position('top')
        if self.asp is not None:
            a.set_aspect(self.asp)
        print('plotProfileData Done.\n')

        # Set grid
        a.grid(self.grid)
            
        # In case you are picking
        if self.picking:
            a.plot(self.picked[:,0],self.picked[:,1],'-x',color='yellow',linewidth=3*self.highfac) 
            a.plot(self.picked[:,0],self.picked[:,1],'-x',color='black',linewidth=2*self.highfac)                               
        
        # Allow for cursor coordinates being displayed        
        def moved(event):
            if event.xdata is not None and event.ydata is not None:
                canvas.get_tk_widget().itemconfigure(tag, text="(x = %5.5g, y = %5.5g)" % (event.xdata, event.ydata))
                
        self.cursor_cid = canvas.mpl_connect('button_press_event', moved)
        tag = canvas.get_tk_widget().create_text(20, 20, text="", anchor="nw")

        canvas.get_tk_widget().grid(row=2,column=0,columnspan=self.figcolsp, rowspan=self.figrowsp, sticky='nsew')
        canvas.draw()
        

    # Show hyperbola
    def showHyp(self,proj,a):
        x0 = sd.askfloat("Input","Hyperbola center on profile [m]", initialvalue=self.hypx)
        if x0 is not None:
            t0 = sd.askfloat("Input","Hyperbola apex location (time [ns])", initialvalue=self.hypt)
            if t0 is not None:
                v  = sd.askfloat("Input","Estimated velocity [m/ns]", initialvalue=self.hypv)
                if v is not None:
                    y=proj.profilePos-x0
                    d=v*t0/2.0
                    k=np.sqrt(d**2 + np.power(y,2))
                    t2=2*k/v
                    a.plot(proj.profilePos,t2,'--c',linewidth=3)
                    self.hypx = x0
                    self.hypt = t0
                    self.hypv = v
        

    def printProfileFig(self,proj,fig):
        figname = fd.asksaveasfilename(defaultextension=".pdf")
        if figname != '':
            dpi = sd.askinteger("Input","Resolution in dots per inch? (Recommended: 600)")
            if dpi is not None:
                fig.savefig(figname, format='pdf', dpi=dpi)        
                # Put what you did in history
                if self.asp is None:
                    histstr = "mygpr.printProfile('%s', color='%s', contrast=%g, yrng=[%g,%g], xrng=[%g,%g], dpi=%d)" %(figname,self.color.get(),self.contrast.get(),self.yrng[0],self.yrng[1],self.xrng[0],self.xrng[1],dpi)
                else:
                    histstr = "mygpr.printProfile('%s', color='%s', contrast=%g, yrng=[%g,%g], xrng=[%g,%g], asp=%g, dpi=%d)" %(figname,self.color.get(),self.contrast.get(),self.yrng[0],self.yrng[1],self.xrng[0],self.xrng[1],self.asp,dpi)
                proj.history.append(histstr)
        print("Saved figure as %s" %(figname+'.pdf'))



    def getDelimiter(self):                
        commaQuery = tk.Toplevel(self.window)
        commaQuery.title("Comma or tab separated?")     
        text = tk.Label(commaQuery,text="Is this a comma- or tab-separated file?",fg='red')
        text.pack(padx=10,pady=10)
        commaButton = tk.Button(commaQuery,text="comma",width=10,
                                command = lambda: [self.setComma(),
                                                   commaQuery.destroy()])
        commaButton.pack(side="left")
        tabButton = tk.Button(commaQuery,text="tab",width=10,
                              command = lambda: [self.setTab(),
                                                 commaQuery.destroy()])
        tabButton.pack(side="right")
        #self.window.frame().tansient(self.window)
        #self.window.frame().grab_set()
        self.window.wait_window(commaQuery)        
    def setComma(self):
        self.delimiter = ','
        print("Delimiter set to comma")
    def setTab(self):
        self.delimiter = '\t'
        print("Delimiter set to tab")

    def getPoint(self, proj, fig,a,canvas):
        self.points = []
        self.curve = []
        # 连接鼠标点击事件和回调函数
        canvas.mpl_connect('button_press_event', lambda event: self.on_canvas_click(event, a, canvas))
        #self.points = np.array(points)
        
        self.leijia += 1

    def on_canvas_click(self, event,a,canvas):

        # 当鼠标点击时，获取点击的坐标
        x = event.xdata
        y = event.ydata
        points = self.points
        points.append([x, y])
        point = np.array(points)

        colors = ['r', 'g', 'b', 'y', 'c', 'm', 'k']
        sc_Colors = ['c', 'm', 'y', 'k', 'r', 'g', 'b']
        a.scatter(point[:, 0], point[:, 1], s=10, color=sc_Colors[self.leijia], marker='x')
        a.plot(point[:, 0], point[:, 1], color=colors[self.leijia], linewidth=1)
        canvas.draw()
        self.curves[str(self.leijia)] = point
        
    def plotCurves(self, proj, a, canvas):

        newroot = tk.Tk(); newroot.columnconfigure(1, weight=1); newroot.rowconfigure(1, weight=1)
        newroot.title('地质解释图')
        fig = Figure(figsize=(12, 10)); fig.clear(); 
        a = fig.add_subplot(111); a.clear()

        x_min =proj.profilePos[0]
        x_max = proj.profilePos[-1]

        curves = self.curves
        curve_max = []
        curve_min = []
        for key, curve in curves.items():
            start = (x_min, curve[0, 1])
            end = (x_max, curve[-1, 1])
            curves[key] = np.vstack((start, curve, end))

        xx = np.linspace(x_min, x_max, 1000)
        
        hatchs = ['.', '\?', 'o', '*', '/','+', 'x', '\\', '|', '-']
        colors = ['k', 'k', 'k', 'k', 'c', 'm', 'k']
        f_colors = ['#cccccc', '#acacac', '#c4c4c4', '#acacac', 'm', 'k', 'r']
        b_colors = ['k', 'k', 'k', 'k', 'k', 'r', 'g']
        for i, (key, curve) in enumerate(curves.items()):
            #print(curve)
            x1 = curve[:, 0]
            y1 = curve[:, 1]
            # 创建插值函数
            f = interp1d(x1, y1)
            yy = f(xx)
            curves[key] = np.vstack((xx, yy)).T
            a.plot(xx, yy, color=colors[i], linewidth=1)

        f = interp1d(proj.profilePos, np.zeros_like(proj.profilePos))
        yy = f(xx)
        curves['0'] = np.vstack((xx, yy)).T
        print('curves', len(curves))
        f = interp1d(proj.profilePos, np.max(proj.twtt)*np.ones_like(proj.profilePos))
        yy = f(xx)
        curves[str(len(curves))] = np.vstack((xx, yy)).T

        curves = dict(sorted(curves.items(), key=lambda x: x[0]))
        # print(curves)

        print('curves', len(curves))
        for i in range(len(curves)-1):
            a.fill_between(xx, curves[str(i)][:, 1], curves[str(i+1)][:, 1], hatch=hatchs[i], \
                           facecolor=f_colors[i], edgecolor=b_colors[i], alpha=1.0, \
                           label='layer'+str(i))
        a.invert_yaxis()
        # 添加图例
        fig.legend()
        # 反转y轴
        #a.invert_yaxis()
        a.set_xlabel("profile position [m]", fontsize=mpl.rcParams['font.size'])
        a.set_ylabel("depth [m]", fontsize=mpl.rcParams['font.size'])
        a.xaxis.set_ticks_position('top')
        a.xaxis.set_label_position('top')
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=newroot)
        canvas.get_tk_widget().grid(row=1, column=1, columnspan=10, rowspan=8, sticky='nsew')
        canvas.draw()

    def kirchhoffmigration(self, proj):
        print("\nDoing Kirchhoffmigration...")
        proj.kirchhoffmigration()
        print("Kirchhoffmigration Done.\n")
