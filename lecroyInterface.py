# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 16:20:28 2023

@author: lastline
"""
import lecroyparser
import numpy as np

def getDataFromBinaryFile(path):
    acquisitionInfo = lecroyparser.ScopeData(path)
    data = acquisitionInfo.y
    samplingFreq = np.ceil(1/(acquisitionInfo.x[1] - acquisitionInfo.x[0]))
    time = acquisitionInfo.x[-1] - acquisitionInfo.x[0]
    return (data, samplingFreq, time)