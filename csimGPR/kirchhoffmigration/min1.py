import numpy as np

def min1(t, M):
    # t is sorted with variation along dim3
    # M is the object to match to
    Np = len(t)-1
    lo = 0
    hi = Np
    
    while lo < hi:
        mid = np.int(np.floor((lo + hi) / 2))
        tq = t[mid]
        
        if tq == M:
            break
        elif tq > M:
            hi = mid - 1
        else:
            lo = mid + 1

    return np.uint32(mid)
