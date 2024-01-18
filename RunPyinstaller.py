import sys
from subprocess import call

system = sys.platform
print(system)
if system == 'darwin':
    print('MacOS')
    call(['pyinstaller', '-F', '-w', 'csimGPR/__main__.py', '-n', 'csimGPRapp', '-p', 'csimGPR/csimGPR.py',
            '--add-data', 'csimGPR/startGUIdat/*:csimGPR/startGUIdat/',
            '-i', 'csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns',
            '--hidden-import=Pmw', '--exclude-module=csimGPR/csimGPR/__main__.py'])
            #'--add-data', '/Users/zhiyuzhang/miniconda3/lib/python3.10/site-packages/Pmw:Pmw'])

elif system == 'linux':
    print('Linux')
    call(['pyinstaller', '-F', '-w', '__main__.py', '-n', 'csimGPRapp', '-p', 'csimGPR/csimGPR.py',
            '--add-data', 'csimGPR/startGUIdat/*:csimGPR/startGUIdat/',
            '-i', 'csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns',
            '--hidden-import=Pmw', '--exclude-module=csimGPR/csimGPR/__main__.py'])
            #'--add-data', '/Users/zhiyuzhang/miniconda3/lib/python3.10/site-packages/Pmw:Pmw'])

else:
    print('Windows')
    call(['pyinstaller', '-D', '-w', '__main__.py', '-n', 'csimGPRapp', '-p', 'csimGPR/csimGPR.py',
            '--add-data', 'csimGPR/startGUIdat/*;csimGPR/startGUIdat/',
            '-i', 'csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns',
            '--hidden-import=Pmw', '--exclude-module=csimGPR/csimGPR/__main__.py',
            '--add-data', 'examples\*;examples/'])
            # '--add-data', 'c:\users\zhangzhiyu\miniconda3\lib\site-packages\Pmw\;Pmw',





# ## question 1
# ### FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/nz/m3bx1d092tl_6x3ktkj67nxc0000gn/T/_MEIruL6Ek/csimGPR/startGUIdat/JLU.jpg
# # solution
# ### /csimGPR/toolbox/csimStartGUI.py  add :
# # def resource_path(relative_path):
# #     """ Get absolute path to resource, works for dev and for PyInstaller """
# #     base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
# #     return os.path.join(base_path, relative_path)
# ### and change the path to resource_path('csimGPR/startGUIdat/JLU.jpg')

# ## question 2
# ### ModuleNotFoundError: No module named 'Pmw'
# # solution
# ### pyinstaller --hidden-import=Pmw --exclude-module=__main__ --add-data "c:\users\zhangzhiyu\miniconda3\lib\site-packages\pmw\:Pmw"




# # Mac
# pyinstaller -F -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py \
#             --add-data "csimGPR/startGUIdat/*:csimGPR/startGUIdat/" \
#             -i csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns \
#             --hidden-import=Pmw --exclude-module=__main__ \
#             --add-data "/Users/zhiyuzhang/miniconda3/lib/python3.10/site-packages/Pmw:Pmw"


# # Windows
# pyinstaller -D -w __main__.py -n csimGPRapp -p csimGPR/csimGPR.py -p csimGPR/csimGPRGUI.py --add-data "csimGPR/startGUIdat/*;csimGPR/startGUIdat/" -i csimGPR/startGUIdat/AnyConv.com__csimGPR_logo.icns --hidden-import=Pmw --exclude-module=__main__ --add-data "c:\users\zhangzhiyu\miniconda3\lib\site-packages\Pmw\;Pmw" --add-data "examples\*;examples/"
    

# Path: RunPyinstaller.py