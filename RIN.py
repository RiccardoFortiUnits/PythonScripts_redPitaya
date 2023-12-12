# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 09:53:16 2023

script that obtains the Relative Intensity Noise (RIN) of a laser, given
    the PSD (in V/√Hz) of the transimpedance (tia) + "inactive" photodiode (with no input light)
    the input power and frequency/wavelength of the laser
    the PSD of the circuit with the laser as input
    the responsivity of the photodiode and gain of the tia
    
be sure that the 2 measurements are done on the same frequency range and same binwidth

@author: lastline
"""
import spectrumAnalyser as sa
import spectrumAnalyser
import os
import tkinter
import numpy as np
import lecroyInterface
import scipy.constants as cst

#-----------------------------MODIFY------------------------

tiaNoisePath        = "F:\\SignalHound\\noise_tia_1-100k.csv"
laserNoisePath      = "F:\\SignalHound\\laserNoise 1_100k 100Avg.csv"

#laser parameters
laserPower_W = 1e-3
laserLambda_m = 532e-9
laserFrequency_Hz = None#you can either set λ or f, the code will obtain the other value from the set one

#circuit parameters
tiaGain_Ohm = 5600
diodeResponsitivity = 0.2

#plot settings
plotIn_dB_Hz = True

#----------------------------KEEP AS IS--------------------

folder_path = [tiaNoisePath, laserNoisePath]

tkinter.Tk().withdraw()
X = list()
Y = list()

for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.csv':
        x, y = sa.getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm =50)
    if extension == '.trc':
        data, samplingFreq, time = lecroyInterface.getDataFromBinaryFile(path)
        x,y = sa.getNSD(data, samplingFreq, time)
            
    y = sa.Volt_to_LightPower(y, tiaGain_Ohm, diodeResponsitivity)
    
    X.append(x)
    Y.append(y)

#from the laser noise, we need to remove the circuit noise (tiaNoise) and the shot noise of the laser (√(2hcP/λ))
try:
    if laserLambda_m is None:
        laserLambda_m = cst.speed_of_light / laserFrequency_Hz
    
    #this is just an indicative signal, some data could be negative/undefined
    rin = (np.sqrt(np.abs((Y[1] **2 - Y[0] **2)))) / laserPower_W
    
    if(plotIn_dB_Hz):
        rin = 10 * np.log10(rin)
    
    dimensions = "dB" if plotIn_dB_Hz else "1/Hz"
    
    sa.plotNSD(X[0], rin, paths = "RIN", axisDimensions = dimensions, linearY= plotIn_dB_Hz)
except:
    print("WARNING: failed to make RIN signal")



