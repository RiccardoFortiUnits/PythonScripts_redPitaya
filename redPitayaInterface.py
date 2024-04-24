# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:02:49 2023

@author: lastline
"""

import paramiko
from base64 import decodebytes


import matplotlib.pyplot as plt
plt.rcParams['agg.path.chunksize'] = 10000
import numpy as np
import redpitaya_scpi as scpi
import time
from datetime import datetime, timedelta

#ask the device to read 16K samples. The function also returns the sample frequency and overall time
def getAcquisition(repeats = 1):  
    IP = 'rp-f0be3a.local'
    
    rp_s = scpi.scpi(IP)
    
    array = np.zeros(repeats * 0x4000)
        
    for i in range(repeats):
        rp_s.tx_txt('ACQ:RST')
        
        dec = 1
        
        # Function for configuring Acquisition
        rp_s.acq_set(dec)
        
        rp_s.tx_txt('ACQ:START')
        rp_s.tx_txt('ACQ:TRIG NOW')
        
        while 1:
            rp_s.tx_txt('ACQ:TRIG:STAT?')
            if rp_s.rx_txt() == 'TD':
                break
        
        while 1:
            rp_s.tx_txt('ACQ:TRIG:FILL?')
            if rp_s.rx_txt() == '1':
                break
        
        # function for Data Acquisition
        buff = rp_s.acq_data(1, convert= True)
        array[i * 0x4000 : (i + 1) * 0x4000] = np.array(buff)
        
        if i >= 10 and (i*10) // repeats != ((i-1)*10) // repeats:
            print(str(int(i / repeats * 100))+"%")
        
    
    rp_s.close()
    
    samplingFreq = 125*10**6
    time = len(buff) * 8*10**(-9) * repeats
    
    return (array, samplingFreq, time)

def find_line_starting_with_string(file_path, target_string):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(target_string):
                    return line.strip()  # Return the line without leading/trailing spaces
        return f"No line starting with '{target_string}' found in the file."
    except FileNotFoundError:
        return f"File '{file_path}' not found."

class ShellHandler:

    def __init__(self, host=None, user=None, psw=None, keyType=None, key=None):
        if host is not None:
            self.ssh = paramiko.SSHClient()
            self.ssh.get_host_keys().add(host, keyType, key)
            self.ssh.connect(host, username=user, password=psw)

            self.channel = self.ssh.invoke_shell()
            self.stdin = self.channel.makefile('wb')
            self.stdout = self.channel.makefile('r')

    def __del__(self):
        self.ssh.close()

    def close(self):
        self.ssh.close()
    known_hosts_file = "C:/Users/lastline/.ssh/known_hosts"
    def connect(self, ssh_siteAddress = "rp-xxxxxx.local"):
        #example of ssh_siteAddress: 
        keyData = find_line_starting_with_string(ShellHandler.known_hosts_file, ssh_siteAddress).split(" ")[2]
        # keyData = b"""AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBHTehAYPnnZWXRlnhr/4rgY/jiDpbEvyUv2JVCgHapqWm6N8mDwOV6XJxQr3gPRhGYBNi/rwfi/bkMGfIG/hpeI="""
        key = paramiko.ECDSAKey(data=decodebytes(bytes(keyData, "utf-8")))
        self.__init__(ssh_siteAddress, "root", "root", 'ecdsa-sha2-nistp256', key)
        self.execute("echo")
        
    def standardConnection(self):
        self.connect("rp-f0be3a.local")        

    def modifiedConnection(self):
        self.connect("rp-f0be72.local")

    def execute(self, cmd, delayTime = 0.05):
        response = self.roughCommand(cmd,delayTime=delayTime)
        
        # Remove the command and prompt lines from the response
        lines = response.splitlines()
        response = '\n'.join(lines[2:len(lines) - 1])
        
        return response
    
    
    def getCurrentFolder(self, cmd, delayTime = 0.05):
        response = self.roughCommand(cmd,delayTime=delayTime)
        
        # Remove the command and prompt lines from the response
        lines = response.splitlines()
        response = '\n'.join(lines[2:len(lines) - 1])
    
    def roughCommand(self, cmd, delayTime = 0.05):
        cmd = cmd.strip('\n')
        
        # Clear any pending data in the input and output streams
        while self.channel.recv_ready():
            self.channel.recv(1024)
        
        # Write the command to the input stream
        self.stdin.write(cmd + '\n')

        # Wait for the shell prompt
        time.sleep(delayTime)  # Adjust as needed

        # Set the channel to non-blocking
        self.channel.setblocking(0)

        response = ""
        while True:
            try:
                # Attempt to receive data
                data = self.channel.recv(1024)
                if not data:
                    break
                response += data.decode('utf-8')

                # Check for the shell prompt to indicate the end of the command response
                if response.endswith('# '):
                    break
            except paramiko.SSHException as e:
                # Break the loop on SSHException
                break
            except Exception as e:
                # Handle other exceptions if needed
                break

        # Set the channel back to blocking
        self.channel.setblocking(1)

        return response
    

    
    def copyFile(self, localpath, remotepath):
        sftp = self.ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
        
        
    #functions to set the values of the RAM, which will be read by the FPGA
    
    #generic function
    def pidSetValue(self, address, multiplier, value, shift=0):
        value_toFpgaNumber = int(value * multiplier) << shift
        self.execute("monitor "+ str(address) + " " + str(value_toFpgaNumber))
    
    
    # def setRegister(self, address, value):
    #     self.execute("monitor "+ str(address) + " " + str(value))
        
    def setBitString(self, address, value, startBit, stringSize):#the value isn't shifted yet
        value = int(value)
        prevRegValue = int(self.execute("monitor "+ str(address)), 0x10)
        bitMask = (((1 << stringSize) - 1) << startBit)
        prevRegValue = prevRegValue & ( -1 - bitMask)#remove previous value
        value_toFpgaNumber = prevRegValue | ((value << startBit) & bitMask)
        self.execute("monitor "+ str(address) + " " + str(value_toFpgaNumber))
        
    def setBit(self, address, value, bitPosition):
        self.setBitString(address, value, bitPosition, 1)
    
    @staticmethod
    def getSignedNumber(n, bitSize):
        if n>>(bitSize-1) == 1:#negative number?
            n = n | ~((1<<bitSize) - 1)
        return n
    
    def getBitString(self, address, startBit, stringSize, convertToSigned = False):
        register = int(self.execute("monitor "+ str(address)), 0x10)        
        bitMask = ((1 << stringSize) - 1)

        value =  (register >> startBit) & bitMask
        
        if convertToSigned:
            return ShellHandler.getSignedNumber(value, stringSize)
        else:
            return value
        
         
    def pidSetSetPoint(self, value):
        self.pidSetValue(0x40300010, (2**23) - 1, value) 
        
    def pidSetProportional(self, value):
        self.pidSetValue(0x40300014, 2**12, value)   
    def pidSetProportional2(self, value):
        self.pidSetValue(0x40300024, 2**12, value)   
        
    def pidSetIntegral(self, value):
        self.pidSetValue(0x40300018, 2**18, value)   
    def pidSetIntegral2(self, value):
        self.pidSetValue(0x40300028, 2**18, value)   
        
    def pidSetDerivative(self, value):
        self.pidSetValue(0x4030001c, 2**10, value)  
        
    def pidDisableIntegral(self):
       self. pidSetValue(0x40300000, 1, 0xf)    
       
    def pidEnableIntegral(self):
        self.pidSetValue(0x40300000, 1, 0xc)
    configValValue = 0
    def pidSetLpFilter(self, enable, coefficient = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 13) | (enable << 13)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        self.pidSetValue(0x40300008, 2**(30), coefficient)
    def pidSetDelay(self, enable, delay = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~((1 << 2) | (0x3FF << 3)) | (enable << 2) | (int(delay) << 3)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetPwmSetpoint(self, enable, value = 0):
        if not enable:
            value = 0
        self.setBitString(0x40400020, value * 255 / 1.8, 16, 8)
        
    def pidSetFeedback(self, enable):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x3 << 0) | (enable << 0)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetSafeSwitch(self, value):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x3 << 16) | (value << 16)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetCommonModeReject(self, enable):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x1 << 18) | (enable << 18)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        
    def pidSetGenFilter(self, enable, coefficientString):
        maxCoefficients = 8
        numbers, denNumSplit = extract_numbers_and_count(coefficientString)
        numbers, denNumSplit = convertToGenericFilterCoefficients(numbers, denNumSplit)
        if len(numbers) > maxCoefficients:
            raise Exception("too many coefficients!")
        
        numbers.extend([0] * (maxCoefficients - len(numbers)))
        
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 14) | (enable << 14)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        
        self.pidSetValue(0x40300060, 1, denNumSplit)
        for i in range(len(numbers)):
            self.pidSetValue(0x40300064 + i*4, 2**20, numbers[i])
    
    def asgSetOffset(self, enable, value=0):
        if not enable:
            value = 0
        self.pidSetValue(0x40200004, ((2**13)-1), value-1, 16)
    
    def pidSetLinearizer(self, enable, samplesString):
        maxSamples = 8
        numbers, denNumSplit = extract_numbers_and_count(samplesString)
        x = np.array(numbers[0:denNumSplit])
        y = np.array(numbers[denNumSplit:])
        if(len(x) > maxSamples+1 or len(y) != len(x)):
            raise Exception("incorrect number of samples!")
        
        (s,q,m) = segmentedCoefficient(x,y)
        
        s = np.append(s,[-1] * (maxSamples - len(m)))
        q = np.append(q,[0] * (maxSamples - len(m)))
        m = np.append(m,[0] * (maxSamples - len(m)))
        
        for i in range(maxSamples):
            self.setBitString(0x403000A0 + i*8, s[i]*(2**13-1), 0, 14)
            self.setBitString(0x403000A0 + i*8, q[i]*(2**13-1), 14, 14)
            self.setBitString(0x403000A4 + i*8, m[i]*(2**24-1), 0, 32)
            
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x1 << 15) | (enable << 15)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
            
    def pidSetRamp(self, enable, samplesString):
        numbers, _ = extract_numbers_and_count(samplesString)
        x = np.array(numbers)
        if(len(x)  != 3):
            raise Exception("incorrect number of samples!")
            
        startValue = int(x[0]*255/1.8)
        endValue = x[1]*255/1.8
        rampTime = x[2]/8e-9
        valueIncrementer = 1 if startValue < endValue else -1#let's always use the smallest incrementer possible, to have the highest resolution
            
        nOfSteps = valueIncrementer * (endValue - startValue)
        stepTime = int(rampTime / nOfSteps)
        if not enable:
            self.setBitString(0x40400020, 0x0, 0, 2)
                    
        self.setBitString(0x40400040, startValue	    , 0, 8)		#PWM0_ramp_startValue
        self.setBitString(0x40400040, valueIncrementer  , 8, 8)		#PWM0_ramp_valueIncrementer
        self.setBitString(0x40400050, stepTime	        , 0, 24)	#PWM0_ramp_stepTime
        self.setBitString(0x40400050, nOfSteps			, 24, 8)	#PWM0_ramp_nOfSteps
        
        if enable:
            self.setBitString(0x40400020, 0x1, 0, 2)
            self.setBitString(0x40400060, 0x1, 0, 2)
            

def segmentedCoefficient(x,y):
    a = x[0:len(x)-1]
    b = x[1:]
    c = y[0:len(y)-1]
    d = y[1:]
    
    m = (d-c) / (b-a)
    s = a
    q = c
    return (s,q,m)
        
import re

def extract_numbers_and_count(input_string):
    # Use regular expression to find sets of numbers in brackets
    matches = re.findall(r'\[([0-9eE., -]+)\]', input_string)

    # Extract numbers from the first set of brackets
    totalList = [float(num) for num in re.split(r'[,\s]+', matches[0]) if num.strip()]
    firstLength = len(totalList)
    for i in range(1,len(matches)):
        set_numbers = [float(num) for num in re.split(r'[,\s]+', matches[i]) if num.strip()]
        totalList += set_numbers

    return totalList, firstLength
 
 
def convertToGenericFilterCoefficients(numbers, denNumSplit):
    #y[n] = sum(ai*y[n-i])) + sum(bj*x[n-j]])
    #the generic filter cannot use y[n-1] (not fast to do it in one cycle), but we can still do everything:
    #y[n-1] = sum(ai*y(n-i-1])) + sum(bj*x[n-j-1]]) =>
    #y[n] = sum_{i!=1}(ai*y(n-i])) + sum(bj*x[n-j]]) + a1*(sum(ai*y(n-i-1])) + sum(bj*x[n-j-1]]))
    #the term y[n-1] can be done using the previous values of y and x
    #the structure of coefficients taken by the fpga will be [b0 b1...][a2 a3...]
    b = numbers[:denNumSplit]
    
    a = numbers[denNumSplit:] #"a0" should always be 1
    if len(a) >= 2:
        a1 = a[1]
        newA = np.array(a[2:] + [0]) + a1 * np.array(a[1:])
        newB = np.array(b + [0]) + np.array([0] + list(a1 * np.array(b)))
    else:
        # a1 = 0;
        newA = np.array([0])
        newB = np.array(b + [0])
    
    return list(newB) + list(newA), len(newB)
