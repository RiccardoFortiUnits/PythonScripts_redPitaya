# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 09:16:23 2024

@author: lastline
"""

import socket
import time as t

self_ip = "192.168.1.100"
fpga_ip = "192.168.1.12"
parameterPort = 2047
parameterSock = None
dataPort = 2048
dataSock = None
def setupReception(selfIP, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((selfIP, port))
    return sock

def setupParameterReception():
    global parameterSock
    parameterSock = setupReception(self_ip, parameterPort)
    return parameterSock
def setupDataReception():
    global dataSock
    dataSock = setupReception(self_ip, dataPort)
    return dataSock
    
def closeParameterReception():
    global parameterSock
    parameterSock.close()
    parameterSock = None
def closeDataReception():
    global dataSock
    dataSock.close()
    dataSock = None
    
def transmitCommand(command, waitForResponse = True):
    global parameterSock
    if(isinstance(command, str)):
        command = command.encode()
    parameterSock.sendto(command, (fpga_ip, parameterPort))    
    if(waitForResponse):
        return receive()    
    
def receive():
    received, address = parameterSock.recvfrom(parameterPort)
    print("Received from", address, ":", received)
    return received

datas = ["pid out", "x", "y", "z", "x^2", "y^2", "z^2"]
def receiveData(time = 5):
    retData = {}
    for name in datas:
        retData[name] = []
    retData["times"] = []
    retData["packetCounter"] = []
    endTime = t.time() + time
    startTime = t.time()
    while t.time() < endTime:
        received, address = dataSock.recvfrom(2048)
        retData["times"].append(t.time() - startTime)
        retData["packetCounter"].append(received[0])
        byteIdx = 1
        for name in datas:
            val = int(received[byteIdx] << 8) + int(received[byteIdx+1])
            if(val >= 0x8000):
                val = -65536 + val
            retData[name].append(val * pow(2, -7))
            byteIdx += 2
    return retData
      
def sendAllCommands():
    for i in range(len(longRegisters)):
        fixedPointVal = int(longRegisters[i] * pow(2, longRegistersShift[i])) & 0xffffffff
        idx = 1 + i * 2
        transmitCommand(b"CPAR"+idx.to_bytes(1,'big')+b"\0"+(fixedPointVal >> 16).to_bytes(2,'big'))
        idx += 1
        transmitCommand(b"CPAR"+idx.to_bytes(1,'big')+b"\0"+(fixedPointVal & 0xffff).to_bytes(2,'big'))
        
    for i in range(len(shortRegisters)):
        fixedPointVal = int(shortRegisters[i] * pow(2, shortRegistersShift[i])) & 0xffff
        idx = 1 + len(longRegisters) * 2 + i
        transmitCommand(b"CPAR"+idx.to_bytes(1,'big')+b"\0"+(fixedPointVal).to_bytes(2,'big'))
          
with setupParameterReception() as qqq:

    kp = 0.9
    ki = 0.0
    setpoint = 0.0
    limitLow = -0.9
    limitHigh = 0.9
    
    longRegistersShift = [25, 25,25]
    longRegisters =      [kp, ki,0]
    
    shortRegistersShift = [15,       15,       15, 15]
    shortRegisters =      [0.2,setpoint, limitLow, limitHigh]
    sendAllCommands() 
    
    transmitCommand("PICL0001")
    transmitCommand("PIEN0001")
    transmitCommand("PICL0000")

# closeParameterReception()

with setupDataReception() as qqq:

    q=receiveData(5)

# closeDataReception()

import matplotlib.pyplot as plt
import numpy as np

# Example dictionary of vectors

# Extract the keys and values from the dictionary
x=np.linspace(0,len(q["times"])-1, len(q["times"]))
# x=q["times"]
# q["counter"] = ((np.array(q["counter"])) * pow(2, 7) % 256)
q["packetCounter"] = np.array(q["packetCounter"])
# datas += ["packetCounter"]
plt.figure()
for name in datas:
    plt.plot(x, q[name], label=name, alpha=0.7)

# plt.yscale('log')
# Add legend
plt.legend()

















