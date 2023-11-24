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

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.txt':
        x, y = getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm = 0)
            
    X.append(x)
    Y.append(y)
    
sa.plotNSD(X,Y, linearX=False, linearY=False)
