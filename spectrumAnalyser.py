# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:28 2023

@author: lastline
"""

import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np

import pandas as pd
def getSpectrumAnalysis(file_csv, isDataIndB = True, inputImpedance_Ohm = 50):
    if "mv" in file_csv:
        isDataIndB = False
    
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    if isDataIndB:
        return array[:,0], np.sqrt(10**((array[:,1]) / 10 - 3) * inputImpedance_Ohm)
    else:
        return array[:,0], array[:,1] * 0.001

def getPowerSpectrum(noise, fs, durata):
    noise = noise - np.mean(noise)
    
    # noise = noise ** 2    
    
    frequencies = np.fft.fftfreq(len(noise), 1.0 / fs)

    window = np.hanning(len(noise))
    
    noise_windowed = noise * window
    
    noise_fft = abs(np.fft.fft(noise_windowed))*2/len(noise)
    
    plotLength = int(len(noise_fft) /2) - 1
    
    # multiply the spectrum by 2, since half of its energy is in the negative frequencies
    return frequencies[:plotLength], noise_fft[:plotLength] * 2
    
def plotPowerSpectrum(frequencies, spectrum, logPlot = True, linearPlot = True):
    bools = [logPlot, linearPlot]
    setLogScale = [True, False]
    
    for i in range(len(bools)):
        if bools[i]:
            plt.figure(figsize=(15, 10))
            if(frequencies.__class__ == list):
                print(frequencies[0][0:10])
                for j in range(len(frequencies)):
                    plt.plot(frequencies[j], spectrum[j], alpha=0.7)   
            else:
                plt.plot(frequencies, spectrum)
            # plt.ylim(1*10**(-8), 1*10**(-2))
            if setLogScale[i]:
                plt.xscale('log')
                plt.yscale('log')
            plt.ylabel("V/sqrt(Hz)")
            plt.xlabel("Hz")
            