pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*:csimGPR/startGUIdat/"


pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*:csimGPR/startGUIdat/" -i csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns
