# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 11:09:04 2024

@author: lastline
"""
import numpy as np
import socket
import time as t

def setupReception(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    return sock

def transmitCommand(sock, ip, port, command, waitForResponse = False):
    if(isinstance(command, str)):
        command = command.encode()
    sock.sendto(command, (ip, port))    
    if(waitForResponse):
        return receive(sock, port)        

def receive(sock, port, printReception = False):
    received, address = sock.recvfrom(port)
    if(printReception):
        print("Received from", address, ":", received)
    return received
    
class fpgaRegister:
    def __init__(self, bitSize, norm, offset = 0, command = None):
        self.bitSize = bitSize
        self.norm = norm
        self.offset = offset
        if command is None:
            self.command = [-1] * ((bitSize + 15) // 16)
        else: 
            self.command = command
        
    def floatToFixedPoint(self, floatValue):
        val = int((floatValue - self.offset) * self.norm)
        if(np.abs(val) >= (1 << (self.bitSize-1))):
            print(f"warning: value too high! Max value = +-{(1 << (self.bitSize-1) - 1)/ self.norm + self.offset}" )
        if(len(self.command) > 1):
            return [val >> 16, val & 0xffff]
        return [val]
    
    def fixedPointToFloat(self, intValue):
        if(len(self.command) > 1):
            intValue = intValue[0] << 16 + intValue[1]
        return intValue / self.norm + self.offset

class segmented_function:
    def __init__(self, x,y):
        self.x = x
        self.y = y
    def valueAt(self, t):
        if t <= self.x[0]:
            return self.y[0]
        elif t >= self.x[-1]:
            return self.y[-1]
        
        for i in range(len(self.x) - 1):
            if self.x[i] <= t <= self.x[i + 1]:
                # Linear interpolation
                slope = (self.y[i + 1] - self.y[i]) / (self.x[i + 1] - self.x[i])
                return self.y[i] + slope * (t - self.x[i])
        
class fpgaHandler:
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        #test the connection
        version = self.sendCommand("VER?")
        print("fpga version: ", version)
        
        #setup the command idx of each fpga register
        self.setupFpgaCommandIndexes()        
    
    #UDP connection
    self_ip = "192.168.1.100"
    fpga_ip = "192.168.1.12"
    parameterPort = 2047
    dataPort = 2048
    
    dataValuesFromFPGA = {
        "data read from the fpga stream"    : fpgaRegister(16 , 2 ** 15),
    }
    
    ParametersForFPGA = {
        #large parameters
        "parameter larger than 16 bits"     : fpgaRegister(26 , 2 ** 24),
        
        #small parameters
        "parameter with max 16 bits"        : fpgaRegister(16 , 2 ** 15),
    }
    
    
    def setupFpgaCommandIndexes(self):
        offset = 1
        for (key,value) in self.ParametersForFPGA.items():
            for j in range(len(value.command)):
                value.command[j] = offset
                offset += 1
                
    def setParameters(self, **kwargs):
        (parameters, values) = list(kwargs.keys()), list(kwargs.values())
        commandList = []
        for i in range(len(parameters)):
            register = self.ParametersForFPGA[parameters[i]]
            paramVals = register.floatToFixedPoint(values[i])
            for j in range(len(register.command)-1,-1,-1):    
                commandList.append(b"CPAR"+register.command[j].to_bytes(1,'big')+b"\0"+\
                                   (paramVals[j]&0xffff).to_bytes(2,'big'))
        self.sendCommand(commandList)
            
        
    def sendCommand(self, commands, waitForResponse = True):
        with setupReception(self.self_ip, self.parameterPort) as sock:
            if isinstance(commands, list):
                responses = [None] * len(commands)
                for i, command in enumerate(commands):
                    responses[i] = transmitCommand(sock, self.fpga_ip, self.parameterPort, command, waitForResponse)
                return responses
            return transmitCommand(sock, self.fpga_ip, self.parameterPort, commands, waitForResponse)
    
    
    def getDataStream(self, time = 1):
        with setupReception(self.self_ip, self.dataPort) as sock:
            retData = {}
            for name in self.dataValuesFromFPGA.keys():
                retData[name] = []
            retData["times"] = []
            # retData["packetCounter"] = []
            endTime = t.time() + time
            startTime = t.time()
            while t.time() < endTime:
                received, address = sock.recvfrom(2048)
                retData["times"].append(t.time() - startTime)
                # retData["packetCounter"].append(received[0])
                byteIdx = 1
                for name, register in self.dataValuesFromFPGA.items():
                    val = int(received[byteIdx] << 8) + int(received[byteIdx+1])
                    if(val >= 0x8000):
                        val = -65536 + val
                    
                    retData[name].append(register.fixedPointToFloat(val))
                    byteIdx += 2
            return retData
        
class bioTweezerController(fpgaHandler):
    def __init__(self, **kwargs):
        
        self.dataValuesFromFPGA = {
            "pid out"          : fpgaRegister(16 , 2 ** 15 / (self._fpgaOutputToLaserPower(1) - self._fpgaOutputToLaserPower(0)), self._fpgaOutputToLaserPower(0)),    # W
            "x"                : fpgaRegister(16 , 2 ** 15 / self.range_x),    # m
            "y"                : fpgaRegister(16 , 2 ** 15 / self.range_y),    # m
            "z"                : fpgaRegister(16 , 2 ** 15 / self.range_y),    # m
            "x^2"              : fpgaRegister(16 , 2 ** 15 / (self.range_x ** 2)),    # m^2
            "y^2"              : fpgaRegister(16 , 2 ** 15 / (self.range_y ** 2)),    # m^2
            "z^2"              : fpgaRegister(16 , 2 ** 15 / (self.range_y ** 2)),    # m^2
        }
        
        self.ParametersForFPGA = {
            #large parameters
            "kp"               : fpgaRegister(26 , 2 ** 24),    # [adimensional]
            "ki"               : fpgaRegister(26 , 2 ** 24),    # [adimensional]
            "sum_multiplier"   : fpgaRegister(26 , 2 ** 24),    # [adimensional]
            
            #small parameters
            "outWhenPiDisabled": fpgaRegister(16 , 2 ** 15 / (self._fpgaOutputToLaserPower(1) - self._fpgaOutputToLaserPower(0)), self._fpgaOutputToLaserPower(0)),    # W
            "setpoint"         : fpgaRegister(16 , 2 ** 15),    # m
            "limitLow"         : fpgaRegister(16 , 2 ** 15 / (self._fpgaOutputToLaserPower(1) - self._fpgaOutputToLaserPower(0)), self._fpgaOutputToLaserPower(0)),    # W
            "limitHigh"        : fpgaRegister(16 , 2 ** 15 / (self._fpgaOutputToLaserPower(1) - self._fpgaOutputToLaserPower(0)), self._fpgaOutputToLaserPower(0)),    # W
        }
        super(bioTweezerController, self).__init__(**kwargs)
        self.reset()
        self.initiateTweezers()
        
    #gains of the ADC/DAC circuits
    ADC_xyAttenuation = 1 / 7.8                     # V/V
    ADC_sumAttenuation = 1 / 11                     # V/V
    DAC_gain = 10                                   # V/V
    ADC_voltageToFpgaInput = 1                      # 1/V
    DAC_fpgaOuputToVoltage = 2.5                    # V
    
    #parameters of the current generator (how does the control input voltage get translated into a current)
    currentGenerator_inputVtoI = 2e-3 / 10e-3       # A/V
    currentGenerator_baseCurrent = 100e-3           # A
    
    #parameters of the laser
    laser_currentToLaserPower = 340e-3 / 730e-3     # W/A
    # = segmented_function([0,730e-3], [0,340e-3])  
    
    #distance ranges
    range_x = range_y = 10e-6                       # m
    range_z = 10e-6                                 # m
    
    #calibration parameters
    calibration_laserPower = 200e-3                 # W
    calibration_time = 3                            # s
    
    #ray that we want to have during the control
    requestedRay = 3e-6                             # m
    #small ray at which the PID will get disabled (when we have small rays, it means that we haven't started the control, or that we lost the tethering)
    minRay = 1e-6                                   # m
    
    def _fpgaOutputToLaserPower(self, value):       # W/[adimensional]
        return ((value * self.DAC_fpgaOuputToVoltage * self.DAC_gain * self.currentGenerator_inputVtoI) + \
                self.currentGenerator_baseCurrent) * self.laser_currentToLaserPower
    
    
    def calcStiffness(self, time = 3, temperature = 300, directions = ["x", "y"]):
        self.initiateFpga()
        dataFromFPGA = self.getDataStream(time)
        kBoltzman = 1.3806504e-23
        stiffnesses = [0] * len(directions)
        for i,direction in enumerate(directions):
            l = dataFromFPGA[direction]
            l_squared = dataFromFPGA[direction+"^2"]
            variance = np.mean(l_squared) - np.mean(l)**2
            stiffnesses[i] = kBoltzman * self.temperature / variance
        return stiffnesses
    
    
    def initiateTweezers(self):
        self.setParameters(sum_multiplier = self.ADC_xyAttenuation / self.ADC_sumAttenuation)
    def calibrateTweezers(self):
        #set a constant output (=> constant laser power)        
        self.setConstantOutput(self.calibration_laserPower)
        [self.kx, self.ky] = self.calcStiffness(time=self.calibration_time, directions=["x","y"])
        self.laser_powerToStiffness = (self.kx+self.ky)/2 / self.calibration_laserPower
        
    def setReset(self, reset = 1):
        self.sendCommand([b"PICL\0\0\0"+reset.to_bytes(1, 'big')])
    def setPiEnable(self, enable = 1):
        self.sendCommand([b"PIEN\0\0\0"+enable.to_bytes(1, 'big')])
    def reset(self):
        self.sendCommand(["PICL0001", "PIEN0000"])
    def EnableConstantOutput(self, output):
        self.sendCommand(["PICL0001"])
        self.setParameters(outWhenPiDisabled = output)
        self.sendCommand(["PICL0000", "PIEN0000"])
    def EnablePI(self, kp = 0.1, ki = 0.001, **kwargs):
        self.sendCommand(["PICL0001"])
        self.setParameters(kp=kp, ki=ki, **kwargs)
        self.sendCommand(["PICL0000", "PIEN0001"])
        
    
q = bioTweezerController()
q.EnablePI(kp = 0.9, ki = 0.0, limitLow = -0.9, limitHigh = 0.1, setpoint = 0.0, outWhenPiDisabled = -0.2)

import matplotlib.pyplot as plt
import numpy as np

# Example dictionary of vectors

w = q.getDataStream(3)
plt.figure()
x=w["times"]
w.pop("pid out")
for key, value in w.items():
    if(key != "times"):
        plt.plot(x, value, label=key, alpha=0.7)

# plt.yscale('log')
# Add legend
plt.legend()
