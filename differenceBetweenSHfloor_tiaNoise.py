# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 09:53:16 2023

@author: lastline
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

script that compares the spectral density of 
    the analyzer noise floor
    the measurement of the tia circuit (done with the same analyzer)
    the expected NSD calculated in spice
    
be sure that these 3 measuerements are done on the same frequency range

the spice simulation we were using is not the best, so we manually added some elements to this noise

@author: lastline
"""
import spectrumAnalyser as sa
import spectrumAnalyser
import os
import tkinter
from tkinter import filedialog
import numpy as np
import lecroyInterface

#-----------------------------MODIFY------------------------

noiseFloorPath      = "C:/Users/lastline/Documents/SignalHound/new tia circuit/new_tia_no 2nd gain - diode_light.csv"
tiaNoisePath        = "C:/Users/lastline/Documents/SignalHound/new tia circuit/old_tia - diode_light.csv"
simulatedNoisePath  = "C:\\Users\\lastline\\Documents\\SignalHound\\199950-200k\\tia_noise.txt"

folder_path = [noiseFloorPath, tiaNoisePath]#, simulatedNoisePath]

#feedback resistor    
tiaGain_Ohm = 5600

#in which metrics should the output be? V/√Hz (voltage), A/√Hz (current), W/√Hz (NEP)
outputDimensions                =          "voltage"     #"NEP" # "current" # "voltage"

diodeResponsitivity = 0.2

#noise to add to the spice simulation (expressed in V/√Hz)
simulationAddictions_V_sqrtHz = [
    (7e-9),                                             #input current of the OPA656
    np.sqrt(2 * 1.602e-19 * 0.35e-9) * tiaGain_Ohm      #photodiode shot noise (multiplied by the gain, so that it is in V/√Hz)
    ]

#----------------------------KEEP AS IS--------------------

def nextDoneRight(expression, returnIfExpressionIsEmpty = None):
    try:
        return next(expression)
    except StopIteration:
        return returnIfExpressionIsEmpty

tkinter.Tk().withdraw()
X = list()
Y = list()
RMS = list()

for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.txt':
        x, y = sa.getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = sa.getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm = 50)
    if extension == '.trc':
        data, samplingFreq, time = lecroyInterface.getDataFromBinaryFile(path)
        x,y = sa.getNSD(data, samplingFreq, time)
            
    if path == simulatedNoisePath:
        #add some other noise
        squareNoiseToAdd = sum(el **2 for el in simulationAddictions_V_sqrtHz)
        y = np.sqrt(y ** 2 + squareNoiseToAdd)
        
        #remove data before and after the frequency range
        indMax = nextDoneRight((i for i in range(len(x)) if x[i] > X[0][-1]), len(x))
        indMin = nextDoneRight((i for i in range(len(x) -1, -1, -1) if x[i] < X[0][0]), -1)
        x = x[indMin + 1 : indMax-1]
        y = y[indMin + 1 : indMax-1]
    
    if outputDimensions == "NEP":
        y = sa.Volt_to_LightPower(y, tiaGain_Ohm, diodeResponsitivity)
    if outputDimensions == "current":
        y = sa.Volt_to_Ampere(y, tiaGain_Ohm)
    #if outputDimensions == "voltage":
        #do nothing
    
    X.append(x)
    Y.append(y)
    RMS.append(sa.getRMS(y, x = x, minFreq=X[0][0], maxFreq=X[0][-1]))
    print(os.path.basename(path).split('/')[-1] + "\t\tRMS: " + str(RMS[-1]))

#let's calculate the difference between the measured tia noise and the analyzer floor noise
try:
    difference = np.sqrt(np.maximum(1e-18,(Y[1] **2 - Y[0] **2)))#this is just an indicative value, some data could be negative/undefined
    
    X.append(X[0])
    Y.append(difference)
    folder_path.append("difference")
    RMS.append(np.sqrt(RMS[1] **2 - RMS[0] **2))
    print(folder_path[-1] + "\t\tRMS: " + str(RMS[-1]))
except:
    print("WARNING: failed to make difference signal")

sa.plotNSD(X,Y, paths = folder_path)#, showAverageLines = True)#, linearX=True, linearY=True)
print("RMS calculated between " + str(X[0][0]) + "Hz and " + str(X[0][-1]))


