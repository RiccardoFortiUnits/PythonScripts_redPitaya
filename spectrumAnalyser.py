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
    #V: measure of rpm tension emitted by the source (on the sum of its output impedance 
    #and the input one of the spectrum analyzer)
def dBm_to_V_sqrtHz(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    return np.sqrt(10**(y / 10 - 3) * inputImpedance_Ohm) / 2 * \
        (outputImpedance_Ohm + inputImpedance_Ohm) / inputImpedance_Ohm

def Volt_to_Ampere(y, Gain_Ohm):
    return y / Gain_Ohm

#the data in the file is already in V/sqrt(Hz), and it doesn't need any adjustment (why 
    #can't every other tool do the same? It doesn't seem like a hard thing to ask, that 
    #what you measure is correct...)
def getSpectrumAnalysis_ltSpice(file_csv, isDataIndB = True):
    data = pd.read_csv(file_csv, low_memory=False, delimiter="\t")
    array = data.to_numpy()
    return array[:,0], array[:,1]

#still not sure how to properly translate the analyzer readings to the correct levels...
def getSpectrumAnalysis_signalHound(file_csv, isDataIndB = True, outputImpedance_Ohm = 50):
    if "mv" in file_csv:
        isDataIndB = False
    
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    binBand = 1/(array[1,0] - array[0,0])
    pg = 10*np.log10(len(array[:,0]))
    print(binBand)
    print("pg: " + str(pg) + "  | " + str(len(array[:,0])))
    
    
    if isDataIndB:
        #return array[:,0], dBm_to_V_sqrtHz(array[:,1] + pg, outputImpedance_Ohm = outputImpedance_Ohm)
        return array[:,0], dBm_to_V_sqrtHz(array[:,1], outputImpedance_Ohm = outputImpedance_Ohm) * np.sqrt(binBand)
    else:
        print("controlla")
        return array[:,0], array[:,1] * 0.001 / binBand


def getNSD(noise, fs, durata):
    noise = noise - np.mean(noise)
        
    frequencies = np.fft.fftfreq(len(noise), 1.0 / fs)

    window = np.hanning(len(noise))
    
    noise_windowed = noise * window
    
    #divide for the integral of the window (for hanning window, sum = nOfSamples / 2)
    noise_fft = abs(np.fft.fft(noise_windowed)) * 2/len(noise)
    
    #we'll show only the positive frequencies (half of the obtained values)
    plotLength = int(len(noise_fft) / 2) - 1
    
    # multiply the spectrum by 2, since half of its energy is in the negative frequencies
    return frequencies[:plotLength], noise_fft[:plotLength] * 2
    
def plotNSD(frequencies, spectrum, paths = None, logPlot = True, linearX=False, linearY=False):
    
    #let's work with a list of curves to plot
    if frequencies.__class__ != list:
        frequencies = [frequencies]
        spectrum = [spectrum]
    
    if paths == None:
        paths = list(map(str, list(range(len(frequencies)))))
    # for j in range(len(frequencies)):
    #     f2 = InterpolatedUnivariateSpline(frequencies[j], spectrum[j]**2, k=1)
    #     result4 = np.sqrt(f2.integral(frequencies[j][0], frequencies[j][-1]))
    #     # non serve moltiplicare *2 a causa della partizione tra i 50Ohm, è già fatta internamente
    #     print("V_rms " + str(j) +": " + str(result4))
    
    
    plt.figure(figsize=(15, 10))
    for j in range(len(frequencies)):
        plt.plot(frequencies[j], spectrum[j], alpha=0.7, label = os.path.basename(paths[j]).split('/')[-1])

    plt.legend(loc="upper right")            
    if not linearX:
        plt.xscale('log')
    if not linearY:
        plt.yscale('log')
    plt.ylabel("V/sqrt(Hz)")
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
    
    index = [i for i in range(len(x_secondo)) if x_secondo[i] < x_primo[-1]][-1]
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