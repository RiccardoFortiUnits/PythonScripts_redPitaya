# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:28 2023

@author: lastline
"""

import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np

import pandas as pd
def getSpectrumAnalysis(file_csv, gain_dB = 0):
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    return array[:,0], 10**((array[:,1] - gain_dB) / 10) * 0.001

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
    if(logPlot):
        plt.figure(figsize=(15, 10))
        if(frequencies.__class__ == list):
            for i in range(len(frequencies)):
                plt.plot(frequencies[i], spectrum[i], alpha=0.7)   
        else:
            plt.plot(frequencies, spectrum)
        # plt.ylim(1*10**(-8), 1*10**(-2))
        plt.xscale('log')
        plt.yscale('log')
        plt.ylabel("V/sqrt(Hz)")
        plt.xlabel("Hz")
    
    if(linearPlot):
        plt.figure(figsize=(15, 10))
        
        if(frequencies.__class__ == list):
            for i in range(len(frequencies)):
                plt.plot(frequencies[i], spectrum[i], alpha=0.7)   
        else:
            plt.plot(frequencies, spectrum)
        # plt.ylim(0, 25*10**(-6))
        plt.ylabel("V/sqrt(Hz)")
        plt.xlabel("Hz")
    
