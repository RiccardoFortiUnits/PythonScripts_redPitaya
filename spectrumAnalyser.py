# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:28 2023

@author: lastline
"""

import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np
import os
import pandas as pd
import csv

from scipy import signal
import scipy.integrate as integrate
from scipy.interpolate import InterpolatedUnivariateSpline
import copy
import os
import tkinter
from tkinter import filedialog
import lecroyInterface
import lecroyparser
import bisect

#dBm: measure of power read by the spectrum analyzer (on a certain input impedance)
    #V/√Hz: measure of rpm tension emitted by the source (on the sum of its output impedance 
    #and the input one of the spectrum analyzer)
def dBm_to_V_sqrtHz(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    return np.sqrt(10**(y / 10 - 3) * inputImpedance_Ohm) * \
        (outputImpedance_Ohm + inputImpedance_Ohm) / inputImpedance_Ohm
        
#V: tension erogated by the source (on the load outputImpedance + inputImpedance)
#dBm: power read on the load inputImpedance
def V_sqrtHz_to_dBm(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    yy = y * inputImpedance_Ohm / (outputImpedance_Ohm + inputImpedance_Ohm)
    return 10 * np.log10(yy ** 2 / inputImpedance_Ohm / 1e-3)

def V_sqrtHz_to_RIN(y, averageVoltage):
    return 10 * np.log10(measure.RINCoeff * (y / averageVoltage) ** 2)

def Volt_to_Ampere(y, Gain_Ohm):
    return y / Gain_Ohm

def Volt_to_LightPower(y, Gain_Ohm, responsivity):
    return y / Gain_Ohm / responsivity

def laserW_sqrtHz_to_RIN_dBc_Hz(y, basePower_W):
    return 10*np.log10(measure.RINCoeff*(y/basePower_W)**2)

#the data in the file is already in V/√Hz, and it doesn't need any adjustment (why 
    #can't every other tool do the same? It doesn't seem like a hard thing to ask, that 
    #what you measure is correct...)
def getSpectrumAnalysis_ltSpice(file_csv, isDataIndB = True):
    data = pd.read_csv(file_csv, low_memory=False, delimiter="\t")
    array = data.to_numpy()
    return array[:,0], array[:,1]

def getSignalFromCsv(file_csv):    
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    try:
        _ = int(data[0][0])
    except:
        data = pd.read_csv(file_csv, low_memory=False, header= 1)
    array = data.to_numpy()
    return (array[:,0],array[:,1])

#still not sure if the translation is correct...
    #anyway, the noise obtained by the Signal Hound (in dBm or mVrms, depending on the SH configuration) is 
    #converted in V/√Hz. To convert from mVrms, the file name must contain the string "mv"

    #Be aware of where you want to reference the noise to: there is always a voltage 
    #divider between the signal source and the analyzer (the input impedance of the SH is 50Ohm), 
    #and the SH compensates for that by assuming that the source has an output impedance of 50Ohm, 
    #thus multiplying the values it reads by 2. And so, the noise is referenced to the output of the 
    #source (i.e. "before" its output impedance)
    #This function lets you choose a different output source impedance (outputImpedance_Ohm)        
def getSpectrumAnalysis_signalHound(file_csv, isDataIndB = True, outputImpedance_Ohm = 50, inputInpedance = 50):
    if "_mv" in os.path.basename(file_csv).split('/')[-1]:
        isDataIndB = False
    x,y = getSignalFromCsv(file_csv)
    if(x[0] < 0):
        x -= 2 * x[0]
    binBand = 1 / (x[1] - x[0])
    # pg = 10*np.log10(len(array[:,0]))
    # print(binBand)
    # print("pg: " + str(pg) + "  | " + str(len(array[:,0])))    
    
    if isDataIndB:
        #multiply by the bin bandwidth, so that the output is normalized in frequency
        return x, \
            dBm_to_V_sqrtHz(y, outputImpedance_Ohm = outputImpedance_Ohm, inputImpedance_Ohm = inputInpedance)\
                                            * np.sqrt(binBand)
    else:
        return x, y

def getSpectrumAnalysis_lecroy(path, isDataIndB = True, outputImpedance_Ohm = 50, inputInpedance = 50):
    acquisitionInfo = lecroyparser.ScopeData(path)
    x,y = acquisitionInfo.x,acquisitionInfo.y
    if(x[0] <= 0):
        x += x[1] - 2 * x[0]
    binBand = 1 / (x[1] - x[0])
    
    if isDataIndB:
        #multiply by the bin bandwidth, so that the output is normalized in frequency
        return x, \
            dBm_to_V_sqrtHz(y, outputImpedance_Ohm = outputImpedance_Ohm, inputImpedance_Ohm = inputInpedance)\
                                            * np.sqrt(binBand)
    else:
        return x, y
      
def getSpectrumAnalysis_matlabNoise(file_csv):
    data = pd.read_csv(file_csv, low_memory=False, header= None)
    array = data.to_numpy()
    # freq, psd = getNSD(array[:,1], 1/(array[1,0] - array[0,0]))
    # return freq, psd
    return array[:,0], array[:,1]

#NSD from a time-domain data acquisition.
def getNSD(noise, samplingFrequency):
    noise = noise - np.mean(noise)
        
    frequencies = np.fft.fftfreq(len(noise), 1.0 / samplingFrequency)

    window = np.hanning(len(noise))
    
    noise_windowed = noise * window
    
    #divide for the integral of the window (for hanning window, sum = nOfSamples / 2)
    noise_fft = abs(np.fft.fft(noise_windowed)) * 2/len(noise)
    
    #we'll show only the positive frequencies (half of the obtained values)
    plotLength = int(len(noise_fft) / 2) - 1
    
    # multiply the spectrum by 2, since half of its energy is in the negative frequencies
    return frequencies[:plotLength], noise_fft[:plotLength] * 2
    
def getRMS(y, minFreq = -1, maxFreq = -1, x = None):
    if minFreq == -1 or maxFreq == -1 or x is None:
        start = 0
        end = len(y)
        dx = 1
    else:
        start = next(i for i in range(len(y)) if x[i] >= minFreq)
        end = next(i for i in range(len(y) - 1, -1, -1) if x[i] <= maxFreq)
        dx = (x[1] - x[0])
    sq = y[start : end] ** 2 * dx
    
    return np.sqrt(np.sum(sq))
        

def plotNSD(frequencies, spectrum, paths = None, axisDimensions = "V/√Hz", legendPosition = "upper right", logPlot = True, linearX=False, linearY=False, showAverageLines = False):
    
    #let's work with a list of curves to plot
    if frequencies.__class__ != list:
        frequencies = [frequencies]
        spectrum = [spectrum]
        if paths is not None:
            paths = [paths]
    
    if paths is None:
        paths = list(map(str, list(range(len(frequencies)))))    
    
    plt.figure(figsize=(15, 10))
    for j in range(len(frequencies)):
    # for j in range(len(frequencies)-1,-1,-1): 
        label = os.path.basename(paths[j]).split('/')[-1].replace('.csv', '')
        plt.plot(frequencies[j], spectrum[j], alpha=0.7, label = label)
       
    if showAverageLines:
        for j in range(len(frequencies)):
            plt.plot(np.array([frequencies[j][0], frequencies[j][-1]]), np.ones(2)*np.mean(spectrum[j]), 
                     alpha=1, label = os.path.basename(paths[j]).split('/')[-1] + " avg")
        

    plt.legend(loc=legendPosition)            
    if not linearX:
        plt.xscale('log')
    if not linearY:
        plt.yscale('log')
    if isinstance(axisDimensions, list):
        plt.xlabel(axisDimensions[0])
        plt.ylabel(axisDimensions[1])
    else:
        plt.xlabel("Hz")
        plt.ylabel(axisDimensions)
    
    # plt.show()
def plotSignal(x, y, paths = None):
    plotNSD(x, y, paths=paths, axisDimensions = "V", linearX=True, linearY=True)
    
#for sweeps in different frequency ranges and different binWidth
def combineTraces(x1, y1, x2, y2):
    if x1[0] < x2[0]:
        x_primo = x1
        x_secondo = x2
        y_primo = y1
        y_secondo = y2
    else:
        x_primo = x2
        x_secondo = x1
        y_primo = y2
        y_secondo = y1
    
    index = next(i for i in range(len(x_secondo)) if x_secondo[i] > x_primo[-1])
    x_secondo = x_secondo[index:]
    y_secondo = y_secondo[index:]
    
    X = np.concatenate([x_primo, x_secondo])
    Y = np.concatenate([y_primo, y_secondo])
    
    return X, Y
    
def saveTrace(x, y, fileName):
    with open(fileName, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(map(list, zip(*[x, y])))
        csvfile.close()


# def getSpikes(y, windowSize):
#     allSpikeIndexes = [i for i in range(1, len(y) - 1, 1) if y[i] >= np.max(y[i - 1 : i + 1])]
#     allSpikes = y[allSpikeIndexes]
#     return allSpikeIndexes
    
    
    
    
def transformToList(Object):
    if isinstance(Object,list):
        return Object
    return [Object]

def extractNumberFromFileName(fileName, stringsToFind):
    # Find the position of the substring "setpoint"
    stringsToFind = transformToList(stringsToFind)
    for stringToFind in stringsToFind:#["setpoint", "laserPower"]:
        setpoint_index = fileName.find(stringToFind)
        
        # If the string is found, extract the substring starting from the position after the string
        if setpoint_index != -1:
            setpoint_substring = fileName[setpoint_index + len(stringToFind):].strip()
            
            # Extract the numeric part (excluding any non-numeric characters)
            setpoint_number = ""
            for char in setpoint_substring:
                if char.isdigit() or char == "." or char == "-":
                    setpoint_number += char
                else:
                    break  # Stop when encountering a non-numeric character
            
            if setpoint_number:
                return float(setpoint_number), stringToFind  # Convert to a float if needed
            else:
                return -1, stringToFind
    return -1, "None"

def decimateByAveraging(V, q):
    # Reshape V into a 2D matrix with q columns
    mod = len(V)%q
    if mod != 0:
        V = np.append(V,np.ones(q-mod)*np.mean(V[-mod:-1]))
    matrix = np.array(V).reshape(-1, q)
    
    # Calculate the mean along each column   
    return np.mean(matrix, axis=1)


def first_index(val, arr):
    index = bisect.bisect_right(arr, val)
    return index if index < len(arr) else -1

class measure:
    defaultInitVals = {
        "InputImpedance_Ohm" : 50,
        "OutputImpedance_Ohm" : 50,
        "isDataIndB" : True,
        }
    dataInsideFileName = {
        "tiaVersion":["AT4v3","AT4_39k","AT4_16k","AT4_160k"],
        "controlType":["no mixer","nomixer","mixer&attenuator","mixer"],
        "usesPid":["no PID", "PID"],
        }
    numericDataInFileName = {
        "laserPower":["laserPower", "setpoint"],
        }
    
    RINCoeff = 2# 1# I'm not sure if I have to multiply by 2 when going from a PSD to the RIN (RIN = 2*PSD/Pow^2, right?)
                                #anyway, with this, I can add and remove this multiplier more easily
    
    rho_shotNoise = 1.26577e-9# √(2*e*photodiodeResponsivity)
    photodiodeResponsivity = 0.2# A/W
    maxSetpoint = 1.8# V
    stage1Saturation = 3.5# V
    
    def setGainsFromTiaVersion(self):
        try:
            nameList = measure.dataInsideFileName["tiaVersion"]
            index = nameList.index(self.tiaVersion)
            if index <= nameList.index("AT4_39k"):
                g1 = 25500
                g2 = 49000 / 2700
                maxPower = 750e-6
            elif index <= nameList.index("AT4_16k"):
                g1 = 25500
                g2 = 15800 / 2700
                maxPower = 750e-6
            elif index <= nameList.index("AT4_160k"):
                g1 = 25500
                g2 = 162000 / 2700
                maxPower = 750e-6
            self.g1, self.g2, self.maxPower = g1, g2, maxPower
        except:
            pass
        
    def setLaserPower(self):
        if self.laserPower_type == "setpoint":
            self.laserPower = self.maxPower * self.laserPower / measure.maxSetpoint
        if self.laserPower_type == "laserPower":
            self.laserPower *= 1e-3
        
    
    def isSystemControlled(self):
        nameList = measure.dataInsideFileName["controlType"]
        index = nameList.index(self.controlType)
        return index > nameList.index("nomixer") and self.usesPid == "PID"
    
    def frequencies(self):
        return self.__freq
    
    def tiaTensionV_sqrtHz(self):
        return self.__tensionV_sqrtHz
    
    def tiaPSD_dBm_Hz(self):
        inputImpedance_Ohm = self.InputImpedance_Ohm
        outputImpedance_Ohm = self.OutputImpedance_Ohm
        return V_sqrtHz_to_dBm(self.__tensionV_sqrtHz, inputImpedance_Ohm = inputImpedance_Ohm, outputImpedance_Ohm = outputImpedance_Ohm)

    def laserPower_W_sqrtHz(self):
        return self.__tensionV_sqrtHz / (self.g1 * self.g2 * measure.photodiodeResponsivity)
    
    def laserPSD_W2_Hz(self):
        return self.laserPower_W_sqrtHz()**2
    
    def unshiftedVoltage(self):
        return self.laserPower * self.g1 * self.g2 * measure.photodiodeResponsivity
    
    def voltageRIN_dBc_Hz(self):
        return V_sqrtHz_to_RIN(self.__tensionV_sqrtHz, self.unshiftedVoltage())
    
    def laserPowerRIN_dBc_Hz(self):
        return laserW_sqrtHz_to_RIN_dBc_Hz(self.laserPower_W_sqrtHz(), self.laserPower)
    
    def laserPowerRIN_1_Hz(self):
        return 10**(self.laserPowerRIN_dBc_Hz()/10)
    
    def shotNoisePower_W_sqrtHz(self):
        return measure.rho_shotNoise * np.sqrt(self.laserPower)
    
    def shotNoiseForPlots_W_sqrtHz(self):
        return [self.__freq[0],self.__freq[-1]], [self.shotNoisePower_W_sqrtHz()] * 2
    def shotNoiseForPlotsRIN_dBc_Hz(self):
        return [self.__freq[0],self.__freq[-1]], [laserW_sqrtHz_to_RIN_dBc_Hz(self.shotNoisePower_W_sqrtHz(), self.laserPower)] * 2
    def shotNoiseMeasure(self):
        sn = copy.deepcopy(self)
        sn.__freq = np.array([self.__freq[0],self.__freq[-1]])
        sn.__tensionV_sqrtHz = np.ones(2) * (self.shotNoisePower_W_sqrtHz() * (self.g1 * self.g2 * measure.photodiodeResponsivity))
        return sn
   
    # @staticmethod
    # def experimentLaserNoiseRIN_dBc_Hz(openLoop, closedLoop, experimentLaserPower):
    #     #we assume that the noise of the open loop is all generator noise, not shot noise
    #     eta_generator = openLoop.laserPower_W_sqrtHz() / openLoop.laserPower
    #     H = 1 - closedLoop.__tensionV_sqrtHz / openLoop.__tensionV_sqrtHz
    #     Rin = (1-H)**2 * eta_generator**2 + measure.rho_shotNoise**2 * (1 + experimentLaserPower / openLoop.laserPower * H**2) / experimentLaserPower
    #     return 10 * np.log10(Rin)
    
    @staticmethod
    def experimentLaserNoiseMeasure(openLoop, closedLoop, experimentLaserPower):
        #we assume that the noise of the open loop is all generator noise, not shot noise
        eta_generator = openLoop.laserPower_W_sqrtHz() / openLoop.laserPower
        H = 1-closedLoop.__tensionV_sqrtHz / openLoop.__tensionV_sqrtHz
        laserNoise_W_sqrtHz = np.sqrt((1-H)**2 * eta_generator**2 * experimentLaserPower**2 + measure.rho_shotNoise**2 * (1 + experimentLaserPower / openLoop.laserPower * H**2) * experimentLaserPower)
        newMeasure = copy.deepcopy(openLoop)
        newMeasure.__tensionV_sqrtHz = laserNoise_W_sqrtHz * (newMeasure.g1 * newMeasure.g2 * measure.photodiodeResponsivity)
        newMeasure.laserPower = experimentLaserPower
        return newMeasure
        
    
    def energy_e_foldingTime_s(self):#also returns the frequency vector. Be careful!
        halfFrequencies = self.__freq / 2
        return halfFrequencies, 1 / (np.pi ** 2 * halfFrequencies ** 2 * self.laserPowerRIN_1_Hz())
    
    def changeLaserPower(self, newLaserPower):
        #assume you changed the base power of the laser and changed the tia circuit accordingly, so 
        #that you would get the same voltage noise as before
        self.g1 *= self.laserPower / newLaserPower
        self.laserPower = newLaserPower
    
    
    def reduceFrequencyRange(self, newStartFrequency = None, newEndFrequency = None):
        if newEndFrequency is None:
            newEndFrequency = self.__freq[-1]
        if newStartFrequency is None:
            newStartFrequency = self.__freq[0]
        startIdx = first_index(newStartFrequency, self.__freq)
        endIdx = first_index(newEndFrequency, self.__freq)            
        
        if endIdx - startIdx < 1:
            if startIdx > 0:    
                prevVal = self.__tensionV_sqrtHz[startIdx-1] + \
                    (newStartFrequency-self.__freq[startIdx-1]) / (self.__freq[startIdx]-self.__freq[startIdx-1]) * \
                    (self.__tensionV_sqrtHz[startIdx] - self.__tensionV_sqrtHz[startIdx-1])
            else:
                prevVal = self.__tensionV_sqrtHz[startIdx]
                
            if endIdx < len(self.__freq) - 1:    
                nextVal = self.__tensionV_sqrtHz[startIdx+1] + \
                    (newEndFrequency-self.__freq[startIdx+1]) / (self.__freq[startIdx]-self.__freq[startIdx+1]) * \
                    (self.__tensionV_sqrtHz[startIdx] - self.__tensionV_sqrtHz[startIdx+1])
            else:
                nextVal = self.__tensionV_sqrtHz[endIdx]
                
        self.__freq = self.__freq[startIdx:endIdx]
        self.__tensionV_sqrtHz = self.__tensionV_sqrtHz[startIdx:endIdx]
        
        if endIdx - startIdx < 1:
            self.__freq = np.array([newStartFrequency] + list(self.__freq) + [newEndFrequency])
            self.__tensionV_sqrtHz = np.array([prevVal] + list(self.__tensionV_sqrtHz) + [nextVal])
    
    def decimateLinearly(self, decimationRatio):
        self.__tensionV_sqrtHz = decimateByAveraging(self.__tensionV_sqrtHz, decimationRatio)
        self.__freq = decimateByAveraging(self.__freq, decimationRatio)
        
    def decimateLogarithmically(self, q):
        #this function will decimate the data on a logarithmic scale, meaning that at higher __freq, where there are more samples, the decimation will be greater
        
        sections = np.ceil(np.log(self.__freq) / np.log(q))
        indexes = sorted(list(set(sections)), key=float)
        newVs = np.zeros(len(indexes))
        
        for i in range(len(indexes)):
            currSection = indexes[i]
            allVoltages = self.__tensionV_sqrtHz[sections == currSection]
            newVs[i] = np.mean(allVoltages)
            
        self.__tensionV_sqrtHz = newVs
        self.__freq = q ** np.array(indexes)
        

    def __init__(self, filePath, **kwargs):
        
        for key, value in measure.defaultInitVals.items():
            kwargs[key] = kwargs.get(key, value)
        
        if filePath is not None:
            extension = os.path.splitext(filePath)[-1]
            plt.plot()
            name = os.path.basename(filePath)        
            if extension == '.txt':
                x, y = getSpectrumAnalysis_ltSpice(filePath)
            if extension == '.csv':
                x, y = getSpectrumAnalysis_signalHound(filePath, outputImpedance_Ohm = kwargs["OutputImpedance_Ohm"])
            if extension == '.mcsv':#csv obtained from Matlab
                x, y = getSpectrumAnalysis_matlabNoise(filePath)    
            if extension == '.trc':
                (data, samplingFreq, time) = lecroyInterface.getDataFromBinaryFile(filePath)
                x,y=getNSD(data, samplingFreq)
            if extension == '.log':
                x, y = lecroyInterface.getDataFromMultimeterLogFile(filePath)   
                x,y = getNSD(y, 1/(x[1]-x[0]))
        
        for key, value in measure.dataInsideFileName.items():
            _, string = extractNumberFromFileName(name, value)
            if string is not None:
                setattr(self,key,string)
        for key, value in measure.numericDataInFileName.items():
            number, string = extractNumberFromFileName(name, value)
            if number is not None:
                setattr(self,key,number)
                setattr(self,key+"_type",string)
            
        self.name = name
        self.__freq = x
        self.__tensionV_sqrtHz = y
        for key, value in kwargs.items():
            setattr(self,key,value)
            
        if not hasattr(self, "tiaVersion"):
            setattr(self, "tiaVersion", measure.dataInsideFileName["tiaVersion"][0])
            print(f"setting default tia version {self.tiaVersion}")
        self.setGainsFromTiaVersion()
        self.setLaserPower()
        
    @staticmethod
    def getListFromFileExplorer():
        root = tkinter.Tk()
        root.withdraw() # prevents an empty tkinter window from appearing
        root.grab_set()  # Make the root window modal
        folder_path = filedialog.askopenfilenames(filetypes=[("csv files", "*.*")])
        # Release the grab to allow interaction with other windows
        root.grab_release()
        if len(folder_path) < 1:
            print("procedure stopped")
            return []
        return [measure(path) for path in folder_path]
    
    @staticmethod
    def plotList(measureList, plotType = "dB", x_and_y_tuples = ("frequencies", "laserPowerRIN_dBc_Hz"), **kwargs):
        #x_and_y_tuples: list of strings or 2-tuples of strings that represent the function to get the x and y of the various curves
        #a single element of x_and_y_tuples should refer to a function that returns a tuple (x,y), otherwise an element that is a 
        #tuple will refer to 2 functions, that will return respectively x and y
        #example: x_and_y_tuples = [("frequencies", "laserPowerRIN_dBc_Hz"), "shotNoiseForPlotsRIN_dBc_Hz"]
        #   for each measure m of the list, the curves represented by (m.frequencies(), m.laserPowerRIN_dBc_Hz()) and
        #   m.shotNoiseForPlotsRIN_dBc_Hz() (wich returns 2 arrays) will be shown
        x_and_y_tuples = transformToList(x_and_y_tuples)
        X=[]
        Y=[]
        for funcs in x_and_y_tuples:
            for meas in measureList:
                if isinstance(funcs, tuple):
                    x = getattr(meas,funcs[0])()
                    y = getattr(meas,funcs[1])()
                else:
                    x, y = getattr(meas,funcs)()
                X.append(x)
                Y.append(y)
        if plotType == "dB":
            plotNSD(X,Y,**kwargs, linearY=True)
        elif plotType == "exp":
            plotNSD(X,Y,**kwargs, linearY=False)
            
            
        
# a=measure('C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 spectral noise, laserPower .400mW (high res).csv')
# b=measure('C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 controlled spectral noise, laserPower .400mW (high res).csv')
# newControlLaserPower = 1e-3

# a.changeLaserPower(newControlLaserPower)
# b.changeLaserPower(newControlLaserPower)

# experimentPower = a.laserPower*10
# c = measure.experimentLaserNoiseMeasure(a,b,experimentPower)
# H = b.tiaTensionV_sqrtHz() / a.tiaTensionV_sqrtHz()
# plotNSD(a.frequencies(), 10*np.log10(H), linearY = True, axisDimensions="|1-H(f)|")

# measure.plotList([a,b])

# l = [a,b,c]
# measure.plotList(l,"dB",[("frequencies", "laserPowerRIN_dBc_Hz"), "shotNoiseForPlotsRIN_dBc_Hz"])
# # X=[]
# # Y=[]
# # for meas in l:
# #     x,y = meas.energy_e_foldingTime_s()
# #     # x,y = (meas.__freq, meas.laserPowerRIN_dBc_Hz())
# #     X.append(x)
# #     Y.append(y)

# # # for meas in l:
# # #     x,y = meas.shotNoiseForPlotsRIN_dBc_Hz()
# # #     X.append(x)
# # #     Y.append(y)


# # plotNSD(X,Y,legendPosition="upper left", axisDimensions='s')#, linearY=True)
    