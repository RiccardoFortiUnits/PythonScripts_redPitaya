# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

@author: lastline
"""
import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
from spectrumAnalyser import getSpectrumAnalysis_matlabNoise
import os
import tkinter
from tkinter import filedialog

X = list()
Y = list()
tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
if len(folder_path) < 1:
    print("procedure stopped")
else:    
    for path in folder_path:
        extension = os.path.splitext(path)[-1]
        name = os.path.basename(path)
        outputImpedance = 50#100 if ("floor" in os.path.basename(path)) else 50
        if extension == '.txt':
            x, y = getSpectrumAnalysis_ltSpice(path)
        if extension == '.csv':
            x, y = getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm = outputImpedance)
        if extension == '.mcsv':#csv obtained from Matlab
            x, y = getSpectrumAnalysis_matlabNoise(path)
        #if extension == '.ini':
            #do nothing
                
        X.append(x)
        Y.append(y)
        
    sa.plotNSD(X,Y, paths = folder_path)#, linearX=True)#, linearY=True)
