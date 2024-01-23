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

#ask the device to read 16K samples. The function also returns the sample frequency and overall time
def getAcquisition():  
    IP = 'rp-f0be3a.local'
    
    rp_s = scpi.scpi(IP)
    
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
    rp_s.close()
    
    samplingFreq = 125*10**6
    time = len(buff) * 8*10**(-9)
    
    return (np.array(buff), samplingFreq, time)

class ShellHandler:

    def __init__(self, host = None, user = None, psw = None, keyType = None, key = None):
        if host is not None:
            self.ssh = paramiko.SSHClient()
            self.ssh.get_host_keys().add(host, keyType, key)
            self.ssh.connect(host, username=user, password=psw)
    
            channel = self.ssh.invoke_shell()
            self.stdin = channel.makefile('wb')
            self.stdout = channel.makefile('r')
        

    def __del__(self):
        self.ssh.close()
        
    def close(self):
        self.ssh.close()

    #specific connection for my PC and redPitaya
    def standardConnection(self):
        keyData = b"""AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBOiejaPKiyP0XO9eK1ZxKts9fTyxJU8N+Grf2H8KTZvohiZ9ZHFi5ISqqgU5KwR1ir3apkoUTj4r+x3/bjpQgQA="""
        key = paramiko.ECDSAKey(data = decodebytes(keyData))
        self.__init__("rp-f0be3a.local", "root", "root", 'ecdsa-sha2-nistp256', key)

    #write a command to the redPitaya. Don't expect to read a response, or even an error. I can't be bothered to properly implement it...
    def execute(self, cmd):
        cmd = cmd.strip('\n')
        self.stdin.write(cmd + '\n')

    def copyFile(self, localpath, remotepath):
        sftp = self.ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
        
        
    #functions to set the values of the RAM, which will be read by the FPGA
    
    #generic function
    def pidSetValue(self, address, multiplier, value):
        value_toFpgaNumber = int(value * multiplier)
        self.execute("monitor "+ str(address) + " " + str(value_toFpgaNumber))
         
    def pidSetSetPoint(self, value):
        self.pidSetValue(0x40300010, (2**23) - 1, value) 
        
    def pidSetProportional(self, value):
        self.pidSetValue(0x40300014, 2**12, value)   
        
    def pidSetIntegral(self, value):
        self.pidSetValue(0x40300018, 2**18, value)   
        
    def pidSetDerivative(self, value):
        self.pidSetValue(0x4030001c, 2**10, value)  
        
    def pidDisableIntegral(self):
       self. pidSetValue(0x40300000, 1, 0xf)    
       
    def pidEnableIntegral(self):
        self.pidSetValue(0x40300000, 1, 0xe)
    configValValue = 0
    def pidSetLpFilter(self, enable, coefficient = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 13) | (enable << 13)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        self.pidSetValue(0x40300008, 2**(30), coefficient)
    def pidSetDelay(self, enable, delay = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~((1 << 2) | (0x3FF << 3)) | (enable << 2) | (int(delay) << 3)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetFeedback(self, enable):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x3 << 0) | (enable << 0)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetVoltageShifter(self, enable):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(0x1 << 15) | (enable << 15)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        
    def pidSetGenFilter(self, enable, coefficientString):
        maxCoefficients = 8
        numbers, denNumSplit = extract_numbers_and_count(coefficientString)
        if len(numbers) > maxCoefficients:
            raise Exception("too many coefficients!")
        
        numbers.extend([0] * (maxCoefficients - len(numbers)))
        
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 14) | (enable << 14)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        
        self.pidSetValue(0x40300060, 1, denNumSplit)
        for i in range(len(numbers)):
            self.pidSetValue(0x40300064 + i*4, 2**20, numbers[i])
            
        
import re

def extract_numbers_and_count(input_string):
    # Use regular expression to find sets of numbers in brackets
    matches = re.findall(r'\[([0-9eE., -]+)\]', input_string)

    if len(matches) < 2:
        return None  # Less than two sets found

    # Extract numbers from the first set of brackets
    first_set_numbers = [float(num) for num in re.split(r'[,\s]+', matches[0]) if num.strip()]

    # Extract numbers from the second set of brackets
    second_set_numbers = [float(num) for num in re.split(r'[,\s]+', matches[1]) if num.strip()]

    return first_set_numbers + second_set_numbers, len(first_set_numbers) 
 
 
 
 