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

def decimateAndReduceToMaxes(y, sampleFreq, finalSampleFreq):
    #if the signal is a modulated sinusoidal, make sure that the final sample frequency is lower than the signal frequency
    decimation = int(np.ceil(sampleFreq / finalSampleFreq))
    out = np.zeros(int(len(y) * finalSampleFreq / sampleFreq))
    y=np.abs(y)
    for i in range(len(out)):
        startIndex = int(i * len(y) / len(out))
        out[i] = np.max(y[startIndex : startIndex + decimation])
    return out

# import spectrumAnalyser as sa
# fs = 20000
# ffs = fs // 600
# x=np.linspace(0, 1,fs)
# y = np.sin(x*2*np.pi*50)+np.tanh(x)
# x2=np.linspace(0, 1,ffs)
# y2 = decimateAndReduceToMaxes(y, fs, ffs)

# sa.plotSignal([x,x2],[y,y2])

