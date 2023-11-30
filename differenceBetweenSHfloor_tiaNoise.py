# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 09:53:16 2023

@author: lastline
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

@author: lastline
"""
import spectrumAnalyser as sa
import spectrumAnalyser
import os
import tkinter
from tkinter import filedialog
import numpy as np
import lecroyInterface

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
# folder_path = ["C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\floor.csv",\
#                "C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\tia_diode_5k_newer.csv",\
#                "C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\tia_noise_5_6K.txt"]
folder_path = ["C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz\\floor_new.csv",\
               "C:\\Users\\lastline\\Documents\\SignalHound\\10-15 kHz\\tia_diode.csv",\
               "C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz\\tia_noise.txt"]
    
tiaGain_Ohm = 5600
outputDimensions                =          "voltage"     #"NEP" # "current" # "voltage"

for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.txt':
        x, y = sa.getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = sa.getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm =50)
    if extension == '.trc':
        data, samplingFreq, time = lecroyInterface.getDataFromBinaryFile(path)
        x,y = sa.getNSD(data, samplingFreq, time)
        
    #if extension == '.ini':
        #do nothing
            
    if path == "C:\\Users\\lastline\\Documents\\SignalHound\\10-15 kHz\\tia_noise.txt":
        y = np.sqrt(y ** 2 + (7e-9) ** 2 + 2 * 1.602e-19 * 0.35e-9 * 5600**2)
        ind = next(i for i in range(len(x)) if x[i] > 11000)
        x = x[:ind-1]
        y = y[:ind-1]
    
    if outputDimensions == "NEP":
        y = sa.Volt_to_LightPower(y, tiaGain_Ohm, 0.3)
    if outputDimensions == "current":
        y = sa.Volt_to_Ampere(y, tiaGain_Ohm)
    #if outputDimensions == "voltage":
        #do nothing
    
    X.append(x)
    Y.append(y)
    
    print(os.path.basename(path).split('/')[-1] + "\t\tRMS: " + str(sa.getRMS(y, x = x, minFreq=10000, maxFreq=100000)))
    
# difference = np.sqrt(np.maximum(Y[1] **2 - Y[0] **2, 1e-20))
difference = np.sqrt(np.abs((Y[1] **2 - Y[0] **2)))

X.append(X[0])
Y.append(difference)

print("difference\t\tRMS: " + str(np.sqrt(sa.getRMS(Y[1], x = X[1], minFreq=10000, maxFreq=100000) ** 2 - sa.getRMS(Y[0], x = X[0], minFreq=10000, maxFreq=100000) ** 2)))
folder_path.append("difference")
sa.plotNSD(X,Y, paths = folder_path)#, linearX=True, linearY=True)


