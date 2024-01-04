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
        self.pidSetValue(0x40300010, (2**13) - 1, value) 
        
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
    def pidSetFilter(self, enable, coefficient = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 12) | (enable << 12)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        self.pidSetValue(0x40300008, 2**14, coefficient)
    def pidSetDelay(self, enable, delay = 0):
        ShellHandler.configValValue = ShellHandler.configValValue & ~((1 << 1) | (0x3FF << 2)) | (enable << 1) | (int(delay) << 2)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
    def pidSetFeedback(self, enable):
        ShellHandler.configValValue = ShellHandler.configValValue & ~(1 << 0) | (enable << 0)
        self.pidSetValue(0x40300004, 1, ShellHandler.configValValue)
        
        
        
        
        
        