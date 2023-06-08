#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 16:20:21 2021

@author: nephilim
"""

from matplotlib import pyplot,cm
import numpy as np
import numba
import skimage.transform

def Nonnegative_Matrix_Factorization(v,rank,max_iter=1000):
    w=np.random.rand(v.shape[0],rank)
    h=np.random.rand(rank,v.shape[1])
    for idx in range(max_iter):
        w=np.multiply(w,(np.dot(v,h.T)/(np.dot(w,np.dot(h,h.T))+1e-8)))
        h=np.multiply(h,(np.dot(w.T,v)/(np.dot(w.T,np.dot(w,h))+1e-8)))
            
    return w,h

def shrink(M,tau):
    return np.sign(M)*np.maximum((np.abs(M)-tau),np.zeros(M.shape))

def Updata_WH(X,S,w,h):
    w=np.multiply(w,(np.abs(np.dot(S-X,h.T))-np.dot(S-X,h.T))/(2*np.dot(w,np.dot(h,h.T))+1e-8))
    h=np.multiply(h,(np.abs(np.dot(w.T,S-X))-np.dot(w.T,S-X))/(2*np.dot(w.T,np.dot(w,h))+1e-8))
    norm_=np.sqrt(np.sum(w**2))
    w=w/norm_
    h=h*norm_
    return w,h

def Robust_NMF(X,lambda_=5e-2,max_iter=1000,rank=1):
    w,h=Nonnegative_Matrix_Factorization(X,rank)
    for idx in range(max_iter):
        S=X-np.dot(w,h)
        S=shrink(S,lambda_/2)
        w,h=Updata_WH(X,S,w,h)
    return w,h,S
        
def PreProcessGPR(X_data,lambda_,max_iter,rank):
    if np.min(X_data)<0:
        min_X_data=np.min(X_data)
    else:
        min_X_data=0
    X_data-=min_X_data
    w,h,S=Robust_NMF(X_data,lambda_=lambda_,max_iter=max_iter,rank=rank)
    X_data+=min_X_data
    RefData=X_data-S
    return RefData
