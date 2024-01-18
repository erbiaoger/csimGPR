#!/usr/bin/env python
# @file:           gprIO_2A.py
# @author:         Zhiyu Zhang
# @Institution:    JiLin University
# @Email:          erbiaoger@gmail.com
# @url:            erbiaoger.site
# @date:           2023-07-18 20:46:54
# @Description     用于读取2A格式的数据
# @version:        v1.0.0

import struct
import numpy as np
import os

def read2A(filename=None):
    """csimGPR/toolbox/gprIO_2A.py made by Zhiyu Zhang JiLin University in 2023-07-18 15h.
    Parameters
    ----------
    data : numpy array
        Array shape N,D
    cutoff : float or tuple of float
        Cutoff frequency for the filter
        A float for a lowpass and a highpass filters
        A tuple (lower, upper) for a bandpass and bandstop filters
    fs : float
        Sampling frequency
    order : int
        Filter order
    btype : {'lowpass', ‘highpass’, ‘bandpass’, ‘bandstop’}, optional
        A type of a filter.
        Default is lowpass
    axis : int, optional
        Axis to which the filter is applied.
        Default is 0

    Returns
    -------
    y : ndarray
        The filtered output from the `sosfiltfilt`-function

    """

    ScanNum = 1063
    RecLen = 8283
    SampleNum = 2048
    RecOffset = 90
    LabNum = 0
    DatclonNum = ScanNum - 1  # LabNum + DatclonNum = ScanNum

    fin = open(filename, 'rb')
    datalist = []
    for i in range(1, ScanNum - LabNum + 1):
        fin.seek(RecOffset + RecLen * (i + LabNum - 1))
        A = struct.unpack('f'*SampleNum, fin.read(4*SampleNum))
        datalist.append(A)       
    
    fin.close()
    return np.asmatrix(np.array(datalist).T)



# def read2A(filename='./LPR_data/First/4 LPR/2A/CE4_GRAS_LPR-2B_SCI_N_20190104004000_20190109213900_0001_A.2A'):
#     # 设置参数
#     scan_num = 1063
#     rec_len = 8283
#     sample_num = 2048
#     rec_offset = 90
#     lab_num = 0
#     datclon_num = scan_num - lab_num

#     datalist = []
#     # 打开输入文件和输出文件
#     with open(filename, 'rb') as fin:
#         # 循环读取数据
#         for i in range(datclon_num):
#             # 定位到文件位置
#             pos = rec_offset + (i + lab_num + 1) * rec_len
#             fin.seek(pos)

#             # 读取数据
#             data = fin.read(rec_len)
#             # samples = struct.unpack("<" + "f" * sample_num, data[0:sample_num * 4])
#             samples = struct.unpack('f'* sample_num, fin.read(4*sample_num))
#             linedata = np.array(samples[:])
#             # np.nan_to_num(linedata, copy=False, nan=0.0)
#             datalist.append(linedata)

#     return np.array(datalist)