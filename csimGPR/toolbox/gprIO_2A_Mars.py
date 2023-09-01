import numpy as np
import os
from glob import glob

file = f'C:\\Users\\erbia\\Desktop\\csimGPR\\examples\\HX1-Ro_GRAS_RoPeR-HF-HH_SCI_N_20210525042001_20210525043243_00011_A.2B'


def readMars2A(filename=None):
    # 设置读取的精度
    precision4 = 'f'  # 单精度浮点数，对应于MATLAB中的single
    skip4 = 69


    # 初始化列表以存放数据
    D_all = []
    E_all = []


    with open(filename, 'rb') as fid:
        # 首先跳过文件开始的18个字节
        fid.seek(18)
        
        # 读取科学数据
        while True:
            # 从当前位置读取数据，不跳过任何字节
            D = np.fromfile(fid, dtype='float32', count=4096)
            if D.size != 4096:  # 如果读取的数据量不正确，就停止循环
                break
            D_all.append(D)
            
            # 读取完当前块后，跳过69个字节
            current_pos = fid.tell()  # 获取当前文件位置
            fid.seek(current_pos + skip4)  # 移动文件指针，跳过字节

    # 将列表转换为numpy数组并调整形状
    D_all = np.array(D_all)
    D_all = D_all.reshape((-1, 4096)).T

    DS1 = D_all[::2, :]
    DX1 = D_all[1::2, :]

    print(D_all.shape)
    
    return DS1, DX1



