import struct
import numpy as np
import os

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
   
def read2A(filename=None):
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

# def read2A(filename=None):
#     ScanNum = 1063
#     RecLen = 8283
#     SampleNum = 2048
#     RecOffset = 90
#     LabNum = 0
#     DatclonNum = ScanNum - 1  # LabNum + DatclonNum = ScanNum


#     data = np.fromfile(filename, dtype=np.float32)
#     data = data.reshape((ScanNum+1+RecOffset, RecLen))
#     return np.asmatrix(data[1:, RecOffset+1:RecOffset+SampleNum+1].T)


# def read2A(filename=None):
#     import numpy as np
#     import os

#     ScanNum = 1063
#     RecLen = 8283
#     SampleNum = 2048
#     RecOffset = 90
#     LabNum = 0
#     DatclonNum = ScanNum - 1  # LabNum + DatclonNum = ScanNum

#     path = os.getcwd()
#     fin = open(filename, 'rb')
#     fin.seek(RecOffset + RecLen * LabNum)
#     data = np.fromfile(fin, dtype=np.float32)#, count=SampleNum * DatclonNum)
#     print(data.shape)
#     data = data.reshape((SampleNum, DatclonNum+1), order='F')
#     fin.close()
#     print(data.shape)
#     return np.asmatrix(data)
