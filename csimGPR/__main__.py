#!/usr/bin/env python
# @file:           __main__.py
# @author:         Zhiyu Zhang
# @Institution:    JiLin University
# @Email:          erbiaoger@gmail.com
# @url:            erbiaoger.site
# @date:           2023-08-18 21:21:35
# @Description     程序入口
# @version:        v1.0.0

import sys
import tkinter as tk

from csimGPR.csimGPRGUI import GPRPyApp

def main(args=None):
    rightcol=9
    figrowsp=19+1

    root = tk.Tk()

    for col in range(rightcol):
        root.columnconfigure(col, weight=1)
    for row in range(figrowsp):    
        root.rowconfigure(row, weight=1)
            
    app = GPRPyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
