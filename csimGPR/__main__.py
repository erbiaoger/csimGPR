# import sys
# import tkinter as tk

# from csimGPR.csimGPRGUI import GPRPyApp

# def main(args=None):
# 		rightcol=9
# 		figrowsp=19+1

# 		root = tk.Tk()

# 		for col in range(rightcol):
# 			root.columnconfigure(col, weight=1)
# 		for row in range(figrowsp):    
# 			root.rowconfigure(row, weight=1)
			
# 		app = GPRPyApp(root)

# 		root.mainloop()

# if __name__ == "__main__":
# 	main()

# __main__.py 程序入口

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
