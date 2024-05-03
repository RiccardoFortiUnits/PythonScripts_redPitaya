# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 14:14:19 2024

@author: lastline
"""
import tkinter as tk
import threading

import subprocess
from redPitayaInterface import ShellHandler
from datetime import datetime
import shutil
import time
import numpy as np

connection = ShellHandler()
# connection.standardConnection()
connection.modifiedConnection()

# connection.getLastModifiedFile("./root")

def segmentedCoefficient(x,y):
    a = x[0:len(x)-1]
    b = x[1:]
    c = y[0:len(y)-1]
    d = y[1:]
    
    m = (d-c) / (b-a)
    q = c
    return (q,m)

currentLinearizer = 'ADC';#'PWM

if currentLinearizer == 'ADC':
    fpgaAddress = 0x403000A0
elif currentLinearizer == 'PWM':
    fpgaAddress = 0x40400080


# x = np.linspace(-1, 1,9)
# y = (x**3-x**2+.5)*2/2.5#(np.tanh(x*4)*0.2)
y = np.array([0,0,0.125017474264530,0.278875411577059,0.610845691806975,0.739630993553370,0.871737897932114,1])
x = np.array([-1,0.019283939731896,0.032590515583281,0.190926157824052,0.704166283061034,0.861064754066206,0.965351031553027,1])

(q,m) = segmentedCoefficient(x, y)

time.sleep(1)
for i in range(len(q)):
    if currentLinearizer == 'ADC':
        connection.setBitString(fpgaAddress + i*8, x[i]*(2**13), 0, 15)
        connection.setBitString(fpgaAddress + i*8, q[i]*(2**13), 15, 15)
        connection.setBitString(fpgaAddress + i*8+4, m[i]*(2**24-1), 0, 32)
        
    elif currentLinearizer == 'PWM':
        connection.setBitString(fpgaAddress + i*4, x[i]*255, 0, 8)
        connection.setBitString(fpgaAddress + i*4, q[i]*255, 8, 8)
        connection.setBitString(fpgaAddress + i*4, m[i]*255, 16, 16)
    
connection.close()



















