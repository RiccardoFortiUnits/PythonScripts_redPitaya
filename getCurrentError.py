# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 14:09:59 2023

@author: lastline
"""

import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
import os
import tkinter
from tkinter import filedialog
from scipy.interpolate import InterpolatedUnivariateSpline
import numpy as np

path = "C:\\Users\\lastline\\Documents\\SignalHound\\1-200kHz\\"

#floor
xf, yf = getSpectrumAnalysis(path + "floor.csv")

#tot
xt, yt = getSpectrumAnalysis(path + "diode_light.csv")
yt = InterpolatedUnivariateSpline(xt,yt, k=1)

#tia simulated
xtia, ytia = getSpectrumAnalysis_ltSpice(path + "tia_noise.txt")
ytia = InterpolatedUnivariateSpline(xtia,ytia, k=1)

#resistor Rf
eRF = np.sqrt(4 * 1.38*10**(-23) * 300 * 10*10**(3))
yrf = InterpolatedUnivariateSpline([0,10*9], [eRF, eRF], k=1)

x = xtia
yt = yt(x)**2
ytia = ytia(x)**2
yrf = yrf(x)**2

yi = np.sqrt(yt-ytia-yrf)


sa.plotPowerSpectrum([xf,x,x,x,x],[yf, np.sqrt(yt),np.sqrt(ytia),np.sqrt(yrf),yi], linearX=True, linearY=True)

