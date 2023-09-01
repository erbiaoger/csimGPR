import numpy as np
from .GPR_transmission_angles_v4 import GPR_transmission_angles_v4
from .min1 import min1
import numba

# @numba.jit(nopython=False)
def Bscan_migration_v3(B, h, er, t, x, tx_pos, rx_pos, xQ, zQ, progress=True):
    c = 3e8
    NxQ = len(xQ)
    NzQ = len(zQ)
    x_lims = 0.5
    dx = x[1] - x[0]
    xc = np.arange(-x_lims, x_lims, dx)
    Nxc = len(xc)
    TTD_inds = np.zeros((Nxc, NzQ), dtype=np.uint32)

    for ii in range(Nxc):
        xc_q = xc[ii]

        for jj in range(NzQ):
            zQ_q = zQ[jj]
            # Calculate GPR angles for Tx
            theta_a_tx, theta_g_tx, phi_tx = GPR_transmission_angles_v4(er, 
                                                                        h, 
                                                                        tx_pos+xc_q, 
                                                                        0, 
                                                                        0, 
                                                                        0, 
                                                                        zQ_q)
            
            TTD_tx = (h / np.cos(theta_a_tx) + zQ_q / np.cos(theta_g_tx) * np.sqrt(er)) / c

            # Calculate GPR angles for Rx
            theta_a_rx, theta_g_rx, phi_rx = GPR_transmission_angles_v4(er, 
                                                                        h, 
                                                                        rx_pos+xc_q, 
                                                                        0, 
                                                                        0, 
                                                                        0, 
                                                                        zQ_q)

            TTD = (h / np.cos(theta_a_rx) + zQ_q / np.cos(theta_g_rx) * np.sqrt(er)) / c + TTD_tx
            TTD_inds[ii, jj] = min1(t, TTD)

    I = np.zeros((NzQ, NxQ), dtype=np.float32)

    for ii, xq in enumerate(xQ):
        #xq = xQ[ii]
        x0_ind = np.argmin(np.abs(x - xq))
        xa_lower = max(min(x), x[x0_ind] - x_lims)
        xa_upper = min(max(x), x[x0_ind] + x_lims)
        size_left = int(np.floor((x[x0_ind] - xa_lower) / dx))
        size_right = int(np.floor((xa_upper - x[x0_ind]) / dx))
        ind_left_TTD = int(np.floor(Nxc / 2) - size_left) - 1
        ind_right_TTD = int(np.floor(Nxc / 2) + size_right) - 1
        xa_lower_ind = np.argmin(np.abs(x - xa_lower))
        C11 = B[:, xa_lower_ind + np.arange(size_left + size_right + 1)]
        I2 = np.arange(0, size_left + size_right + 1)

        for jj in range(NzQ):
            TTD_mat = TTD_inds[ind_left_TTD:ind_right_TTD + 1, jj]
            linInds = np.ravel_multi_index((TTD_mat, I2), C11.shape)
            I[jj, ii] = np.sum(C11.flat[linInds])

        if progress:
            print(f'Progress: {ii + 1}/{NxQ}')

    I = np.abs(I)
    return I
