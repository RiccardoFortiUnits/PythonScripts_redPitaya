# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:23:29 2023

@author: lastline
"""
import numpy as np
import lecroyInterface
import matplotlib.pyplot as plt


fileName = "C:/Users/lastline/Documents/aom_acquisitions/C2--square_0-1V.trc"
samplesToPlot = 100000

(data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(fileName)
(data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C2", "C3"))




# plt.figure()
plt.title(fileName)

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

plt.xlim([0.00081,0.00082])


fileName = "C:/Users/lastline/Documents/aom_acquisitions/C2--triangle.trc"
samplesToPlot = 100000000

(data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(fileName)
(data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C2", "C3"))

fig, ax1 = plt.subplots()

# Plot the first graph on the primary y-axis
ax1.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), -data[0:samplesToPlot], color='tab:blue', label='Risposta')
ax1.set_xlabel('t')
ax1.set_ylabel('V_aom')
ax1.tick_params('y', colors='tab:blue')

# Create a secondary y-axis
ax2 = ax1.twinx()
ax2.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), data1[0:samplesToPlot], color='tab:red', label='Ingresso')
ax2.set_ylabel('V_ramp')
ax2.tick_params('y', colors='tab:red')

plt.xlim([0.787,1.3])

