import numpy as np
from .Bscan_migration_v3 import Bscan_migration_v3

class Scan:
    def __init__(self, ScanData, xVec, tVec):
        if ScanData is not None:
            self.Data = ScanData        # 原始数据，时间作为行，x作为列
            self.x = xVec               # x坐标
            self.dx = xVec[1] - xVec[0] # x坐标间隔
            self.Kx = 1 / self.dx       # x波数
            self.Nx = len(xVec)         # x坐标点数
            self.kx = np.linspace(-self.Kx/2, self.Kx/2, self.Nx)   # x波数坐标

            self.t = tVec               # 时间坐标
            self.Ts = tVec[1] - tVec[0] # 时间坐标间隔
            self.Fs = 1 / self.Ts       # 时间波数
            self.Nt = len(tVec)         # 时间坐标点数
            self.f = np.linspace(-self.Fs/2, self.Fs/2, self.Nt)    # 时间波数坐标

        # Other properties initialization goes here

    def BKGR_PCA(self, L):
        """
        使用主成分分析进行背景去除

        Parameters
        ----------
        L : int
            要去除的奇异值数量，2 是最佳值，1 也可以
        U : ndarray
            奇异值分解的左奇异向量
        S : ndarray
            奇异值分解的奇异值
        V : ndarray
            奇异值分解的右奇异向量
        o : ndarray
            奇异值矩阵
        DataBKGR : ndarray
            去除背景后的数据
        """

        U, S, V = np.linalg.svd(self.Data, full_matrices=False)
        o = np.diag(S)
        self.DataBKGR = np.dot(U, np.dot(np.diag([0] * L + o[L:]), V))

    def envelope(self, useBKGR=False):
        """
        获取包络信号的函数

        Parameters
        ----------
        useBKGR : bool, optional
            是否使用去除背景后的数据，默认为 False
        DataENV : ndarray
            包络信号
        """

        if useBKGR:
            self.DataENV = np.abs(np.imag(self.DataBKGR))
        else:
            self.DataENV = np.abs(np.imag(self.Data))

    def BKGR_MEAN(self):
        self.DataBKGR = self.Data #- np.mean(self.Data, axis=1)[:, np.newaxis]

    def migrate(self, xC, zC, progress=True):
        self.Image = Bscan_migration_v3(self.DataBKGR, self.h, self.er, self.t, self.x, self.tx_pos, self.rx_pos, xC, zC, progress)
        self.xC = xC
        self.zC = zC

    def matched_filter(self, wfm, positive=False):
        # 匹配过滤器
        self.DataMF = np.zeros(self.DataBKGR.shape)
        for k in range(self.Nx):
            self.DataMF[:, k] = np.convolve(self.DataBKGR[:, k], np.flip(wfm), 'same')
        
        self.matchedWFM = wfm

        if positive:
            self.DataMF[self.DataMF < 0] = 0

    def migrateMF(self, xC, zC, progress=True):
        self.ImageMF = Bscan_migration_v3(self.DataMF, self.h, self.er, self.t, self.x, self.tx_pos, self.rx_pos, xC, zC, progress)
        self.xC = xC
        self.zC = zC

    def generate_FK(self, useBKGR=False):
        if useBKGR:
            temp = np.fft.fftshift(np.fft.fft(self.DataBKGR, axis=0), axes=0)
        else:
            temp = np.fft.fftshift(np.fft.fft(self.Data, axis=0), axes=0)

        self.DataFK = np.fft.fftshift(np.fft.fft(temp, axis=1), axes=1)
