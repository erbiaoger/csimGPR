import numpy as np

def find_image_resolution_slices(I):
    """
    此函数将查找目标图像中的最大值并提取水平和垂直切片。

    参数：
    I - 图像

    返回值：
    vslice - 垂直切片
    hslice - 水平切片
    """
    # 查找图像的维度
    Nz, Nx = I.shape

    # 在计算之前，确定是否需要填充
    pad_vert = False
    pad_horz = False

    if Nx > Nz:
        pad_vert = True
    elif Nz > Nx:
        pad_horz = True

    # 查找图像的最大值
    max_ind = np.argmax(I)
    max_r, max_c = np.unravel_index(max_ind, I.shape)  # 最大值的索引为 I[max_r, max_c]

    vslice = I[:, max_c]
    hslice = I[max_r, :]

    if pad_vert:
        vslice = np.concatenate((vslice, np.nan * np.ones(Nx - Nz)))
    elif pad_horz:
        hslice = np.concatenate((hslice, np.nan * np.ones(Nz - Nx)))

    return vslice, hslice
