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
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
import os
import tkinter
from tkinter import filedialog
import numpy as np

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
folder_path = ["C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\floor.csv",\
               "C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\tia_diode_5k_newer.csv",\
               "C:\\Users\\lastline\\Documents\\SignalHound\\1-25MHz_oldTIA\\tia_noise_5_6K.txt"]
for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.txt':
        x, y = getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm =50)
    #if extension == '.ini':
        #do nothing
            
    X.append(x)
    Y.append(y)
    
difference = np.sqrt(Y[1] **2 - Y[0] **2)

X.append(X[0])
Y.append(difference)
folder_path.append("difference")
sa.plotNSD(X,Y, paths = folder_path)#, linearX=True, linearY=True)
