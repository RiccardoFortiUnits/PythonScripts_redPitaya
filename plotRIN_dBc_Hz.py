# -*- coding: utf-8 -*-
"""
Created on Fri May  3 14:37:13 2024

@author: lastline
"""

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
    for stringToFind in ["laserPower", "setpoint"]:
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

root = tkinter.Tk()
root.withdraw() # prevents an empty tkinter window from appearing

# root.grab_set()  # Make the root window modal
folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
folder_path = list(folder_path)

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
        
        baseVoltage_dBm = sa.V_sqrtHz_to_dBm(currentVoltage) - 10*np.log10(2)#          dBm(V^2*Ohm/W)
        
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
            
        
    sa.plotNSD(X,Y,legendPosition="upper left", paths = folder_path, axisDimensions='dBc/Hz', linearY=True)#, linearX=True)





















