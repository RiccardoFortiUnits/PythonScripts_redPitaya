# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 10:23:47 2024

@author: lastline
"""

import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
from spectrumAnalyser import getSpectrumAnalysis_matlabNoise
import os
import numpy as np
import csv

nOfAcquisitions = 49
startName = "C:/Users/lastline/Downloads/spectrumSignal (1).csv"
finalName = "C:/Users/lastline/Downloads/spectrumSignal"
x = [None] * nOfAcquisitions
y = [None] * nOfAcquisitions
for i in range(nOfAcquisitions):
    x[i], y[i] = getSpectrumAnalysis_signalHound(startName.replace("(1)", "("+str(nOfAcquisitions+1)+")"), outputImpedance_Ohm = 50)

meany = 0

for i in range(nOfAcquisitions):
    meany = meany + y[i]**2
    
meany = np.sqrt(meany / nOfAcquisitions)



with open(finalName + "_mv.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(map(list, zip(*[x[0], meany])))
    csvfile.close()
