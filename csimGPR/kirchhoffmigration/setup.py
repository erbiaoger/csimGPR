from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy as np

## 创建了一个名为 mod_cyMigrate 的扩展模块，其中传入的参数 "mod_cyMigrate.pyx" 表示扩展模块的源文件名
## include_dirs=[np.get_include()] 表示需要包含 NumPy 库的头文件，以便在 Cython 源代码中使用 NumPy 数组
ext = Extension("mod_cyMigrate", ["mod_cyMigrate.pyx"],
    include_dirs = [np.get_include()])
                
## Cython.Distutils.build_ext 类是用于构建 Cython 扩展模块的工具，
## 用于将 Cython 代码 (.pyx) 编译成 C 代码 (.c)，并将其与可执行的 C 代码一起编译成最终的扩展模块。
setup(ext_modules=[ext],
      cmdclass = {'build_ext': build_ext})
