import numpy as np
# import numba as nb

# @nb.jit(nopython=True, cache=True)
def GPR_transmission_angles_v4(er, h, xa, ya, xq, yq, zq):
    xa = np.single(xa)
    ya = np.single(ya)
    xq = np.single(xq)
    yq = np.single(yq)
    
    max_n_steps = 50
    yq = yq - ya
    xq = xq - xa
    
    phi = np.arctan2(yq, xq)
    
    if phi < 0:
        phi = 2 * np.pi + phi
    
    xi = xq
    tol = 1e-4
    step = 2 * tol
    nsteps = 0
    
    while abs(step) > tol:
        # Calculate value of F'(xi)
        t_center = xi * (np.tan(phi)**2 + 1) / np.sqrt(xi**2 + (xi * np.tan(phi))**2 + h**2) - \
            np.sqrt(er) * (np.tan(phi) * (yq - xi * np.tan(phi)) + (xq - xi)) / np.sqrt((xq - xi)**2 + (yq - xi * np.tan(phi))**2 + zq**2)
        
        # Calculate value of F'(xi+delta)
        t_right = (xi + tol) * (np.tan(phi)**2 + 1) / np.sqrt((xi + tol)**2 + ((xi + tol) * np.tan(phi))**2 + h**2) - \
            np.sqrt(er) * (np.tan(phi) * (yq - (xi + tol) * np.tan(phi)) + (xq - (xi + tol))) / np.sqrt((xq - (xi + tol))**2 + (yq - (xi + tol) * np.tan(phi))**2 + zq**2)
        
        # Calculate step size as F'(xi)/F''(xi). /2 for stability
        step = -t_center / ((t_right - t_center) / tol) / 2
        
        # Update xi with step size
        xi = xi + step
        
        nsteps = nsteps + 1
        
        if nsteps > max_n_steps:
            xi = xq
            break
    
    theta_a = np.arccos(h / np.sqrt(xi**2 + (xi * np.tan(phi))**2 + h**2))
    theta_g = np.arccos(zq / np.sqrt((xq - xi)**2 + (yq - xi * np.tan(phi))**2 + zq**2))
    
    return theta_a, theta_g, phi
