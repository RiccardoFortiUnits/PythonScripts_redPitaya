# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 13:23:29 2023

@author: lastline
"""
import numpy as np
import lecroyInterface
import matplotlib.pyplot as plt


fileName = "C:/Users/lastline/Documents/aom_acquisitions/C2--sin_+-1V.trc"
samplesToPlot = 100000

(data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(fileName)
(data1, samplingFreq1, time1) = lecroyInterface.getDataFromBinaryFile(fileName.replace("C2", "C3"))

plt.figure()
plt.title(fileName)
plt.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), data[0:samplesToPlot]*-100-5)
plt.plot(np.linspace(0,time*samplesToPlot/len(data),samplesToPlot), data1[0:samplesToPlot])