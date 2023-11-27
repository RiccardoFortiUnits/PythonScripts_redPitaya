# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 15:37:17 2023

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
from spectrumAnalyser import combineTraces
import os
import tkinter
from tkinter import filedialog

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing
X = list()
Y = list()
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
secondFolder = "C:\\Users\\lastline\\Documents\\SignalHound\\1-10kHz\\"
for path in folder_path:
    extension = os.path.splitext(path)[-1]
    name = os.path.basename(path).split('/')[-1]
    print(name)
    if extension == '.txt':
        x, y = getSpectrumAnalysis_ltSpice(path)
        x2, y2 = getSpectrumAnalysis_ltSpice(secondFolder + name)
        x, y = combineTraces(x, y, x2, y2)
    if extension == '.csv':
        x, y =  getSpectrumAnalysis_signalHound(path, outputImpedance_Ohm =50)
        x2, y2 =  getSpectrumAnalysis_signalHound(secondFolder + name, outputImpedance_Ohm =50)
        x, y = combineTraces(x, y, x2, y2)
    #if extension == '.ini':
        #do nothing
            
    X.append(x)
    Y.append(y)
    
sa.plotNSD(X,Y, paths = folder_path)#, linearX=True, linearY=True)
