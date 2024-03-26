# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 08:59:54 2024

@author: lastline
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

@author: lastline
"""
import numpy as np
import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
from spectrumAnalyser import getSpectrumAnalysis_matlabNoise
import lecroyInterface
import os
import tkinter
from tkinter import filedialog

def getFromFile(path):
    extension = os.path.splitext(path)[-1]
    name = os.path.basename(path)
    outputImpedance = 50#100 if ("floor" in os.path.basename(path)) else 50
    if extension == '.txt':
        x, y = getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm = outputImpedance)
    if extension == '.mcsv':#csv obtained from Matlab
        x, y = getSpectrumAnalysis_matlabNoise(path)    
    if extension == '.trc':
        (data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(path)
        x,y=sa.getNSD(data, samplingFreq)
    return x,y

root = tkinter.Tk()
root.withdraw() # prevents an empty tkinter window from appearing
root.grab_set()  # Make the root window modal
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])


if len(folder_path) < 1:
    print("procedure stopped")
else:    
    
    x0, y0 = getFromFile(folder_path[0])
    
    X = list()
    Y = list()
    X.append(np.array([x0[0], x0[-1]]))
    Y.append(np.array([1,1]))
    folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])

    
    # Release the grab to allow interaction with other windows
    root.grab_release()
    if len(folder_path) < 1:
        print("procedure stopped")
    else:    
        for path in folder_path:
            x,y = getFromFile(path)
            
            y = y / y0
            
            X.append(x)
            Y.append(y)
            
        sa.plotNSD(X,Y, paths = ["0dB"] + list(folder_path) )# , linearY=True )# , linearY=True)
