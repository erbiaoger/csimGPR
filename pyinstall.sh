pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*:csimGPR/startGUIdat/"


pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*:csimGPR/startGUIdat/" -i csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns --hidden-import=Pmw --exclude-module=__main__ --add-data "/Users/zhiyuzhang/miniconda3/lib/python3.10/site-packages/Pmw:Pmw"

pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*;csimGPR/startGUIdat/" -i .\csimGPR\startGUIdat\az9q7-log83-001.ico --hidden-import=Pmw 


 pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*;csimGPR/startGUIdat/" -i csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns --hidden-import=Pmw --exclude-module=__main__ --add-data "c:\users\zhangzhiyu\miniconda3\lib\site-packages\pmw\:Pmw"