# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:28 2023

@author: lastline
"""

import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np
import os
import pandas as pd

import scipy.integrate as integrate
from scipy.interpolate import InterpolatedUnivariateSpline

#dBm: measure of power read by the spectrum analyzer (on a certain input impedance)
    #V/√Hz: measure of rpm tension emitted by the source (on the sum of its output impedance 
    #and the input one of the spectrum analyzer)
def dBm_to_V_sqrtHz(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    return np.sqrt(10**(y / 10 - 3) * inputImpedance_Ohm) * \
        (outputImpedance_Ohm + inputImpedance_Ohm) / inputImpedance_Ohm
        
#V: tension erogated by the source (on the load outputImpedance + inputImpedance)
#dBm: power read on the load inputImpedance
def V_sqrtHz_to_dBm(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    y *= inputImpedance_Ohm / (outputImpedance_Ohm + inputImpedance_Ohm)
    return 10 * np.log10(y ** 2 / inputImpedance_Ohm)

def Volt_to_Ampere(y, Gain_Ohm):
    return y / Gain_Ohm

def Volt_to_LightPower(y, Gain_Ohm, responsivity):
    return y / Gain_Ohm / responsivity

#the data in the file is already in V/√Hz, and it doesn't need any adjustment (why 
    #can't every other tool do the same? It doesn't seem like a hard thing to ask, that 
    #what you measure is correct...)
def getSpectrumAnalysis_ltSpice(file_csv, isDataIndB = True):
    data = pd.read_csv(file_csv, low_memory=False, delimiter="\t")
    array = data.to_numpy()
    return array[:,0], array[:,1]

#still not sure if the translation is correct...
    #anyway, the noise obtained by the Signal Hound (in dBm or mVrms, depending on the SH configuration) is 
    #converted in V/√Hz. To convert from mVrms, the file name must contain the string "mv"

    #Be aware of where you want to reference the noise to: there is always a voltage 
    #divider between the signal source and the analyzer (the input impedance of the SH is 50Ohm), 
    #and the SH compensates for that by assuming that the source has an output impedance of 50Ohm, 
    #thus multiplying the values it reads by 2. And so, the noise is referenced to the output of the 
    #source (i.e. "before" its output impedance)
    #This function lets you choose a different output source impedance (outputImpedance_Ohm)        
def getSpectrumAnalysis_signalHound(file_csv, isDataIndB = True, outputImpedance_Ohm = 50):
    if "mv" in os.path.basename(file_csv).split('/')[-1]:
        isDataIndB = False
    
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    binBand = 1/(array[1,0] - array[0,0])
    # pg = 10*np.log10(len(array[:,0]))
    # print(binBand)
    # print("pg: " + str(pg) + "  | " + str(len(array[:,0])))    
    
    if isDataIndB:
        #multiply by the bin bandwidth, so that the output is normalized in frequency
        return array[:,0], dBm_to_V_sqrtHz(array[:,1], outputImpedance_Ohm = outputImpedance_Ohm) * np.sqrt(binBand)
    else:
        return array[:,0], array[:,1]

      
def getSpectrumAnalysis_matlabNoise(file_csv):
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    freq, psd = getNSD(array[:,1], 1/(array[1,0] - array[0,0]))
    return freq, psd

#NSD from a time-domain data acquisition.
def getNSD(noise, samplingFrequency):
    noise = noise - np.mean(noise)
        
    frequencies = np.fft.fftfreq(len(noise), 1.0 / samplingFrequency)

    window = np.hanning(len(noise))
    
    noise_windowed = noise * window
    
    #divide for the integral of the window (for hanning window, sum = nOfSamples / 2)
    noise_fft = abs(np.fft.fft(noise_windowed)) * 2/len(noise)
    
    #we'll show only the positive frequencies (half of the obtained values)
    plotLength = int(len(noise_fft) / 2) - 1
    
    # multiply the spectrum by 2, since half of its energy is in the negative frequencies
    return frequencies[:plotLength], noise_fft[:plotLength] * 2
    
def getRMS(y, minFreq = -1, maxFreq = -1, x = None):
    if minFreq == -1 or maxFreq == -1 or x is None:
        start = 0
        end = len(y)
        dx = 1
    else:
        start = next(i for i in range(len(y)) if x[i] >= minFreq)
        end = next(i for i in range(len(y) - 1, -1, -1) if x[i] <= maxFreq)
        dx = (x[1] - x[0])
    sq = y[start : end] ** 2 * dx
    
    return np.sqrt(np.sum(sq))
        

def plotNSD(frequencies, spectrum, paths = None, axisDimensions = "V/√Hz", logPlot = True, linearX=False, linearY=False, showAverageLines = False):
    
    #let's work with a list of curves to plot
    if frequencies.__class__ != list:
        frequencies = [frequencies]
        spectrum = [spectrum]
        if paths is not None:
            paths = [paths]
    
    if paths is None:
        paths = list(map(str, list(range(len(frequencies)))))    
    
    plt.figure(figsize=(15, 10))
    for j in range(len(frequencies)):
    # for j in range(len(frequencies)-1,-1,-1): 
        plt.plot(frequencies[j], spectrum[j], alpha=0.7, label = os.path.basename(paths[j]).split('/')[-1])
       
    if showAverageLines:
        for j in range(len(frequencies)):
            plt.plot(np.array([frequencies[j][0], frequencies[j][-1]]), np.ones(2)*np.mean(spectrum[j]), 
                     alpha=1, label = os.path.basename(paths[j]).split('/')[-1] + " avg")
        

    plt.legend(loc="upper right")            
    if not linearX:
        plt.xscale('log')
    if not linearY:
        plt.yscale('log')
    plt.ylabel(axisDimensions)
    plt.xlabel("Hz")
    
    # plt.show()
    
#for sweeps in different frequency ranges and different binWidth
def combineTraces(x1, y1, x2, y2):
    if x1[0] < x2[0]:
        x_primo = x1
        x_secondo = x2
        y_primo = y1
        y_secondo = y2
    else:
        x_primo = x2
        x_secondo = x1
        y_primo = y2
        y_secondo = y1
    
    index = next(i for i in range(len(x_secondo)) if x_secondo[i] > x_primo[-1])
    x_secondo = x_secondo[index:]
    y_secondo = y_secondo[index:]
    
    X = np.concatenate([x_primo, x_secondo])
    Y = np.concatenate([y_primo, y_secondo])
    
    return X, Y
    
# x1 = [0,1]
# y1 =  [3,4]
# x2 = [-1,4,5]
# y2 =  [0,2,2]
# x,y = combineTraces(x1, y1, x2, y2)
# plotNSD([x1,x2,x], [y1,y2,y], linearX=True, linearY=True)