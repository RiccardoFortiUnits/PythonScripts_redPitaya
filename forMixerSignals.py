# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:40:41 2024

@author: lastline
"""


import spectrumAnalyser as sa
import numpy as np
import lecroyInterface
import matplotlib.pyplot as plt
from scipy.signal import decimate
import tkinter
from tkinter import filedialog

(data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile("C:/Users/lastline/Documents/mixerMeasures/C2--LO1V_IF800mV.trc")


finalSamplingFreq = 40e6

y = lecroyInterface.decimateAndReduceToMaxes(data, samplingFreq, finalSamplingFreq)

from scipy.signal import decimate
decimated_signal = decimate(y, q=1000, zero_phase=True)

# sa.plotSignal(np.linspace(0,1,len(decimated_signal)), decimated_signal)
y = decimated_signal[30:51]
sa.saveTrace(np.linspace(-.8, .8, len(y)), y, "C:/Users/lastline/Documents/mixerMeasures/mixerResponse.csv")
