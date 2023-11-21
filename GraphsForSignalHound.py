# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:29:48 2023

@author: lastline
"""
import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis
import os
import tkinter
from tkinter import filedialog

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
for i in range(4):
    folder_path = filedialog.askopenfilename(initialdir = "C:/Documenti/SignalHound", filetypes=[("csv files", "*.csv")])
    x, y = getSpectrumAnalysis(folder_path, gain_dB= -20)
    X.append(x)
    Y.append(y)
sa.plotPowerSpectrum(X,Y, linearPlot=False)
