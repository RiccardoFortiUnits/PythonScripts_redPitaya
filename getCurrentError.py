# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:09:59 2023

@author: lastline
"""

import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
import os
import tkinter
from tkinter import filedialog
from scipy.interpolate import InterpolatedUnivariateSpline
import numpy as np

path = "C:\\Users\\lastline\\Documents\\SignalHound\\1-200kHz\\"

#floor
xf, yf = getSpectrumAnalysis_signalHound(path + "floor.csv", outputImpedance_Ohm=0)

#tot
xt, yt = getSpectrumAnalysis_signalHound(path + "diode_light.csv", outputImpedance_Ohm=0)
yt = InterpolatedUnivariateSpline(xt,yt, k=1)

#tia simulated
xtia, ytia = getSpectrumAnalysis_ltSpice(path + "tia_noise.txt")
ytia = InterpolatedUnivariateSpline(xtia,ytia, k=1)


x = xtia
yt = yt(x)**2
ytia = ytia(x)**2

yi = np.sqrt(np.maximum(yt-ytia, 10**-18))


sa.plotNSD([xf,x,x,x],[yf, np.sqrt(yt),np.sqrt(ytia),yi], linearX=False, linearY=False)

