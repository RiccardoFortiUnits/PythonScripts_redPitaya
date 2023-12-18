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
import csv

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
x0 = None
y0 = None
for path in folder_path:
    extension = os.path.splitext(path)[-1]
    if extension == '.txt':
        x, y = getSpectrumAnalysis_ltSpice(path)
    if extension == '.csv':
        x, y = getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm =50)
    if x0 is None:
        x0 = x
        y0 = y
    else:
        x0, y0 = sa.combineTraces(x0, y0, x, y)
    
finalName = filedialog.asksaveasfilename(filetypes=[("csv files", "*.csv")])
        
with open(finalName + "_mv.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(map(list, zip(*[x0, y0])))
    csvfile.close()
