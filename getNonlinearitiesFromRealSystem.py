# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:16:33 2024

@author: lastline
"""

from redPitayaInterface import ShellHandler
import numpy as np
import time

proportional = 0.01
integral = 0.0001
nOfPoints = 6
waitTime = 0.1
nOfReadsPerPoint = 5 #average current value on multiple points


connection = ShellHandler()
connection.standardConnection()

connection.pidDisableIntegral()
connection.pidSetProportional(proportional)
connection.pidSetIntegral(integral)

x = np.linspace(0, 1.8, nOfPoints)
y = np.zeros(len(x))

for i in range(len(x)):
    connection.pidSetPwmSetpoint(True, x[i])
    connection.pidEnableIntegral()
    time.sleep(waitTime)
    v = 0
    for _ in range(nOfReadsPerPoint):
        v = v + connection.getBitString(0x40300050, 0, 14, True)
    y[i] = v / nOfReadsPerPoint / 2**13
    
    connection.pidDisableIntegral() 

connection.close()
    
    
    



