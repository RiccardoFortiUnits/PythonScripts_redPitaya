# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:28 2023

@author: lastline
"""

import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np

import pandas as pd

import scipy.integrate as integrate
from scipy.interpolate import InterpolatedUnivariateSpline


def dBm_to_V(y, inputImpedance_Ohm = 50):
    return np.sqrt(10**(y / 10 - 3) * inputImpedance_Ohm)


def getSpectrumAnalysis_ltSpice(file_csv, isDataIndB = True, inputImpedance_Ohm = 50):
    data = pd.read_csv(file_csv, low_memory=False, delimiter="\t")
    array = data.to_numpy()
    return array[:,0], array[:,1]

def getSpectrumAnalysis(file_csv, isDataIndB = True, inputImpedance_Ohm = 50):
    if "mv" in file_csv:
        isDataIndB = False
    
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    binBand = 1/(array[1,0] - array[0,0])
    pg = 10*np.log10(len(array[:,0]))
    print(binBand)
    print("pg: " + str(pg) + "  | " + str(len(array[:,0])))
    
    
    if isDataIndB:
        # return array[:,0], dBm_to_V(array[:,1] + pg, inputImpedance_Ohm)
        return array[:,0], dBm_to_V(array[:,1], inputImpedance_Ohm) * np.sqrt(binBand)
    else:
        print("controlla")
        return array[:,0], array[:,1] * 0.001 / binBand

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
    
def plotPowerSpectrum(frequencies, spectrum, logPlot = True, linearX=False, linearY=False):
    
    if frequencies.__class__ != list:
        frequencies = [frequencies]
        spectrum = [spectrum]
    
    for j in range(len(frequencies)):
        f2 = InterpolatedUnivariateSpline(frequencies[j], spectrum[j]**2, k=1)
        result4 = np.sqrt(f2.integral(1e3, 1e6))
        # non serve moltiplicare *2 a causa della partizione tra i 50Ohm, è già fatta internamente
        print("V_rms " + str(j) +": " + str(result4))
    
    
    plt.figure(figsize=(15, 10))
    for j in range(len(frequencies)):
        plt.plot(frequencies[j], spectrum[j], alpha=0.7) 
            
    if not linearX:
        plt.xscale('log')
    if not linearY:
        plt.yscale('log')
    plt.ylabel("V/sqrt(Hz)")
    plt.xlabel("Hz")
    
    plt.show()
            