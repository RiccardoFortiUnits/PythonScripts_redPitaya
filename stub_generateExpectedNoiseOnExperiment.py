# -*- coding: utf-8 -*-
"""
Created on Tue May  7 09:14:15 2024

@author: lastline
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May  4 11:09:34 2024

@author: lastline
"""
import numpy as np
import spectrumAnalyser as sa

import spectrumAnalyser as sa
from spectrumAnalyser import getSpectrumAnalysis_signalHound
from spectrumAnalyser import getSpectrumAnalysis_ltSpice
from spectrumAnalyser import getSpectrumAnalysis_matlabNoise
import lecroyInterface
import os
import numpy as np
import tkinter
from tkinter import filedialog
from tkinter import simpledialog

def extract_setpoint_number(input_string):
    # Find the position of the substring "setpoint"
    for stringToFind in ["setpoint", "laserPower"]:
        setpoint_index = input_string.find(stringToFind)
        
        # If "setpoint" is found, extract the substring starting from the position after "setpoint"
        if setpoint_index != -1:
            setpoint_substring = input_string[setpoint_index + len(stringToFind):].strip()
            
            # Extract the numeric part (excluding any non-numeric characters)
            setpoint_number = ""
            for char in setpoint_substring:
                if char.isdigit() or char == ".":
                    setpoint_number += char
                else:
                    break  # Stop when encountering a non-numeric character
            
            if setpoint_number:
                return float(setpoint_number), stringToFind  # Convert to a float if needed
            else:
                print(f"failed to convert string '{setpoint_number}' into a number")
                return -1
folder_path = ['C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 spectral noise, laserPower .400mW.csv',
 'C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 controlled spectral noise, laserPower .400mW.csv']
folder_path = ['C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 spectral noise, laserPower .400mW (high res).csv',
 'C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 controlled spectral noise, laserPower .400mW (high res).csv']

g1 = 25500#          V/A
g2 = 49000 / 2700#          V/V

maxPower = 750e-6#          W
maxSetPoint = 1.8#          V
photodiodeResponsivity = 0.2#          A/W
maxCurrent = maxPower * photodiodeResponsivity#          A

#let's 
maxVoltage = maxCurrent * g1 * g2#          V

usedSetpoints = {}

X = list()
Y = list()
# Release the grab to allow interaction with other windows
# root.grab_release()
minX = 1e100
maxX = 0
if len(folder_path) < 1:
    print("procedure stopped")
else:    
    for path in folder_path:
        extension = os.path.splitext(path)[-1]
        name = os.path.basename(path)
        
        extractedNumber, stringFound = extract_setpoint_number(name)
        if stringFound == "setpoint":
            currentSetpoint = extractedNumber#          V
            currentPower = maxPower * currentSetpoint / maxSetPoint#          W
            
        elif stringFound == "laserPower":
            currentPower = extractedNumber * 1e-3#laser power given in mW#          W
            currentSetpoint = maxSetPoint * currentPower / maxPower#          V
                
        currentVoltage = maxVoltage * currentSetpoint / maxSetPoint#          V
        
        baseVoltage_dBm = sa.V_sqrtHz_to_dBm(currentVoltage)#          dBm(V^2*Ohm/W)
        
        x, y = getSpectrumAnalysis_signalHound(path)#          V / sqrt(Hz)
        
        frequencyBand = x[1]-x[0]#          Hz
        minX = min(minX, x[0])
        maxX = max(maxX, x[-1])
        y = sa.V_sqrtHz_to_dBm(y)#          dBm(V^2*Ohm/W) / Hz
        y -= baseVoltage_dBm#          dBc / Hz
        X.append(x)
        Y.append(y)
        
        if currentPower not in usedSetpoints.keys():
            #add shot noise level for this setpoint
            shotNoiseCurrent = np.sqrt(2 * 1.6e-19 * currentPower * photodiodeResponsivity)#          A / sqrt(Hz)
            # shotNoiseCurrent *= np.sqrt(frequencyBand)#          A
            shotNoiseVoltage_dBm = sa.V_sqrtHz_to_dBm(shotNoiseCurrent * g1 * g2)#          dBm(V^2*Ohm/W) / Hz
            shotNoiseVoltage_dBm -= baseVoltage_dBm#          dBc / Hz
            # shotNoiseVoltage_dBm -= 10 * np.log10(frequencyBand)#          dBc / Hz
            usedSetpoints[currentPower] = shotNoiseVoltage_dBm
                
    for setPoint, shotNoise in usedSetpoints.items():
        X.append(np.array([minX, maxX]))
        Y.append(np.array([shotNoise, shotNoise]))
        folder_path.append(f"shot noise for power {setPoint*1e3 : .3f}mW")
            

print_1_minus_H = True
realX = X
realY = Y
ng = 10**(realY[0]/20)
ps = 8.64e-10
ng = ng ** 2
ps = ps ** 2
Pe = 1
initialNoise = ng*Pe**2+ps*Pe
idealNoise = ps*Pe

yy = (realY[1] - realY[0])
H = 1-10**(yy/10)

X=[]
Y=[]
Names = []
for Pc in (list(Pe / np.array([10,100,1000,10000,100000])) + [0]):
    if(Pc != 0):
        Se = ng * Pe**2 * (1 - H)**2 + ps * Pe * (1 + Pe / Pc * H**2)
        Names.append(f"Pe : Pc = {Pe / Pc : .0f}")
    else:
        Se = ng * Pe**2 * (1 - H)**2 + ps * Pe
        Names.append("Pe : Pc = 0")
        
    X.append(x)
    Y.append(10*np.log10(2*Se / Pe**2))
    
X.append(x)
Y.append(10*np.log10(2*initialNoise / Pe**2))
Names.append("generator + shot noise")
X.append([x[0],x[-1]])
Y.append([10*np.log10(2*idealNoise / Pe**2)]*2)
Names.append("shot noise")

sa.plotNSD(X,Y,legendPosition="upper left", paths=Names, axisDimensions=['Hz','dBc/Hz'], linearX=False, linearY=True)#, linearX=True)