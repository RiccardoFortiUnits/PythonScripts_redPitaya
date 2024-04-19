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
    #if the signal is a modulated sinusoidal, make sure that the final sample frequency is lower 
    #than the signal frequency (so that the decimated signal takes at least one 
    #period of the original signal for each sample)
    decimation = int(np.ceil(sampleFreq / finalSampleFreq))
    out = np.zeros(int(len(y) * finalSampleFreq / sampleFreq))
    y=np.abs(y)
    for i in range(len(out)):
        startIndex = int(i * len(y) / len(out))
        out[i] = np.max(y[startIndex : startIndex + decimation])
    return out

from datetime import datetime

def getDataFromMultimeterLogFile(path):
    #not actually for a lecroy device, but I can't be bothered to create a new file just for this
    #read data from a file created in labview where each line has the format "yyy.mm.dd_hh.mm.ss\t\tvalue"
    with open(path, 'r') as file:
        timestamps = np.zeros(sum(1 for line in file))
        values = np.zeros(len(timestamps))
    
    with open(path, 'r') as file:
        i=0
        for line in file:
            parts = line.strip().split('\t\t')
            
            timestamp_str, value_str = parts
            timestamps[i] = int(datetime.strptime(timestamp_str, "%Y.%m.%d_%H.%M.%S").timestamp())
            values[i] = float(value_str)  # Assuming values are numeric (adjust as needed)
            
            i = i+1
        timestamps = timestamps - timestamps[0]
        return timestamps, values

# import spectrumAnalyser as sa
# (x,y)=getDataFromMultimeterLogFile("D:/2024.04.03_15.01.01_.log")
# sa.plotSignal([x],[y])


# import spectrumAnalyser as sa
# fs = 20000
# ffs = fs // 600
# x=np.linspace(0, 1,fs)
# y = np.sin(x*2*np.pi*50)+np.tanh(x)
# x2=np.linspace(0, 1,ffs)
# y2 = decimateAndReduceToMaxes(y, fs, ffs)

# sa.plotSignal([x,x2],[y,y2])

