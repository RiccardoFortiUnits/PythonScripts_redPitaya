# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 16:09:59 2024

@author: lastline
"""
import spectrumAnalyser as sa
import lecroyInterface
import os
import tkinter
from tkinter import filedialog
import numpy as np

X = list()
Y = list()
root = tkinter.Tk()
root.withdraw() # prevents an empty tkinter window from appearing
root.grab_set()  # Make the root window modal
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
# Release the grab to allow interaction with other windows
root.grab_release()
if len(folder_path) < 1:
    print("procedure stopped")
else:    
    for path in folder_path:
        extension = os.path.splitext(path)[-1]
        name = os.path.basename(path)
        outputImpedance = 50#100 if ("floor" in os.path.basename(path)) else 50
        if extension == '.trc':
            (data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(path)
        elif extension == '.csv':
            (x, y) = sa.getSignalFromCsv(path)
            data = y
            time = x[-1]
        else:
            raise Exception("only .trc extension supported")
        
        Y.append(data)
        X.append(np.linspace(0, time, len(data)))
        
    sa.plotSignal(X,Y, paths = folder_path)
