# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:23:29 2023

@author: lastline
"""
import numpy as np
import lecroyInterface
import matplotlib.pyplot as plt
from scipy.signal import decimate
import scipy
import tkinter
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw() # prevents an empty tkinter window from appearing
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])

fileName = folder_path[0]

(data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(fileName)
if "C3" in fileName:
    (data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C3", "C2"))    
else:
    (data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C2", "C3"))



decimation = 50
if decimation is not None:
    data1 = scipy.signal.decimate(data1, decimation)
    data = scipy.signal.decimate(data, decimation)

samplesToPlot = len(data)

# def smallCorrelation(x,y,nSamples):
#     res = np.zeros(nSamples)
#     for i in range(nSamples):
#         res[i] = np.correlate(x[:len(x)-i], y[i:]) / (len(x)-i)
#     return res

# decimation = 1
# samplesToPlot = int(samplesToPlot/decimation)
# data = decimate(data, decimation)
# data1 = decimate(data1, decimation)

# cross_corr = smallCorrelation(abs(data), data1, 5000)
# plt.figure()
# plt.plot(cross_corr)
# print(np.argmax(cross_corr)*decimation/samplingFreq)


fig, ax1 = plt.subplots()

# Plot the first graph on the primary y-axis
ax1.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), -data[0:samplesToPlot], color='tab:blue', label='Risposta')
ax1.set_xlabel('t')
ax1.set_ylabel('V_aom')
ax1.tick_params('y', colors='tab:blue')

# Create a secondary y-axis
ax2 = ax1.twinx()
ax2.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), data1[0:samplesToPlot], color='tab:red', label='Ingresso')
ax2.set_ylabel('V_step')
ax2.tick_params('y', colors='tab:red')

# plt.xlim([0.00081,0.00082])


# fileName = "C:/Users/lastline/Documents/aom_acquisitions/C2--triangle.trc"
# samplesToPlot = 100000000

# (data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(fileName)
# (data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C2", "C3"))

# fig, ax1 = plt.subplots()

# # Plot the first graph on the primary y-axis
# ax1.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), -data[0:samplesToPlot], color='tab:blue', label='Risposta')
# ax1.set_xlabel('t')
# ax1.set_ylabel('V_aom')
# ax1.tick_params('y', colors='tab:blue')

# # Create a secondary y-axis
# ax2 = ax1.twinx()
# ax2.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), data1[0:samplesToPlot], color='tab:red', label='Ingresso')
# ax2.set_ylabel('V_ramp')
# ax2.tick_params('y', colors='tab:red')

# plt.xlim([0.787,1.3])

