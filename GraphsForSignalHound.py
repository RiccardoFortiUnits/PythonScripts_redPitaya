# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

@author: lastline
"""
import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
import os
import tkinter
from tkinter import filedialog

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
folder_path = filedialog.askopenfilenames(initialdir = "C:/Documenti/SignalHound", filetypes=[("csv files", "*.*")])
for path in folder_path:
    x, y = getSpectrumAnalysis(path)
    # if i >= 0:
    #     x, y = getSpectrumAnalysis(path)
    # else:
    #     x, y = getSpectrumAnalysis_ltSpice(path)
    X.append(x)
    Y.append(y)
    
sa.plotPowerSpectrum(X,Y, linearX=True, linearY=False)
