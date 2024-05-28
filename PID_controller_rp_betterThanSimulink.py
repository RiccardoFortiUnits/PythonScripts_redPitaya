# -*- coding: utf-8 -*-
"""
Created on Thu May  9 10:03:38 2024

@author: lastline
"""

import tkinter as tk
import threading

import subprocess
from redPitayaInterface import ShellHandler
from datetime import datetime
import shutil

connection = ShellHandler()

def connect():
    global connection
    connection.modifiedConnection()
    B_setPidValues["state"] = "active"
    B_updateFpga["state"] = "active"
    canvas.itemconfig(indicatore, fill='green')

def disconnect():
    # Code to execute when the window is closed
    if connection is not None:
        connection.close()
    finestra.destroy()

isPIDenabled = False
compile_n_sendFpga = False

def togglePID():
    global isPIDenabled
    global B_setPidValues
    if not isPIDenabled:
        connection.pidDisableIntegral()
        for key, el in elements.items():
            el.callFunction(connection)
        connection.pidEnableIntegral()
        B_setPidValues.config(text="Disable PID")
    else:
        connection.pidDisableIntegral()
        connection.pidSetProportional(0)
        connection.pidSetIntegral(0)
        connection.pidSetDerivative(0)
        B_setPidValues.config(text="Enable PID")
    isPIDenabled = not isPIDenabled
    

def change_compile_n_sendFpga(*args):
    global compile_n_sendFpga
    compile_n_sendFpga = not compile_n_sendFpga
    
def loadNewFpga():
    global compile_n_sendFpga
    
    newFpgaName = T_FpgaName.get()
    
    if compile_n_sendFpga:
        newFpgaName = newFpgaName + datetime.now().strftime(" %d_%m_%Y %H_%M")+".bit.bin"
        
        backupSaveFolder = "C:/Users/lastline/Documents/backupFpgaBinaries/"
    
        #execute the batch that converts the bitstream to one usable by the redPitaya
        batFilePath="C:/Xilinx/Vivado/2020.1/bin/create_RP_binFile.bat"
        p = subprocess.Popen(batFilePath, shell=True, stdout = subprocess.PIPE)
        stdout, stderr = p.communicate()
    
        #save a backup of the newly created binary
        shutil.copyfile("C:/Git/redPitayaFpga/prj/v0.94/project/redpitaya.runs/impl_1/red_pitaya_top.bit.bin", 
                        backupSaveFolder + newFpgaName)
    
        #open an ssh connection, send the selected binary and execute it
        connection.copyFile(backupSaveFolder + newFpgaName, newFpgaName)
        
    connection.execute("/opt/redpitaya/bin/fpgautil -b '"+newFpgaName.replace(" ","\ ")+"'")

class element:
    def __init__(self, name, settingFunction, initialValue = 0.):
        self.name = name
        self.settingFunction = settingFunction
        self.tag = tk.Label(finestra, text=name)
        self.entry = tk.Entry(finestra)
        
        self.entry.insert(0, str(initialValue))
        self.entry.bind("<Return>", self.callFunction)
        # self.scale.bind("<ButtonRelease-1>", self.updateEntryFromScale)
        self.graficElements = [self.tag, self.entry]
        # .grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        # .grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)
        
    def callFunction(self, connection):
        val = float(self.entry.get())
        self.settingFunction(val)

class toggle:
    def __init__(self, name, settingFunction, useAdditionalVal = False, initialValue = False, additionalInitialValue = 0.):
        self.useAdditionalVal = useAdditionalVal
        self.settingFunction = settingFunction
        self.name = name
        self.currentVal = initialValue
        self.toggleButton = tk.Button(finestra)        
        # self.toggleButton.grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        self.toggleButton.bind("<ButtonRelease-1>", self.toggle_n_callFunction)
        if useAdditionalVal:
            self.entry = tk.Entry(finestra)
            self.entry.insert(0, additionalInitialValue)
            # self.entry.grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)
            self.entry.bind("<Return>", self.callFunction)
            self.graficElements = [self.toggleButton, self.entry]
        else:
            self.entry = None    
            self.graficElements = [self.toggleButton]
        self.updateButtonText()
    
    def updateButtonText(self):
        if self.currentVal:
            self.toggleButton.config(text="Disabilita " + self.name)
        else:
            self.toggleButton.config(text="Abilita " + self.name)
    
    def toggle_n_callFunction(self, connection):
        self.currentVal = not self.currentVal
        self.callFunction(connection) 
        self.updateButtonText()
        
    def callFunction(self, connection):
        if self.useAdditionalVal:
            try:
                val = float(self.entry.get())
                self.settingFunction(self.currentVal, val)
            except:
                self.settingFunction(self.currentVal, self.entry.get())
        else:
            self.settingFunction(self.currentVal)
       
class enumToggle:
    def __init__(self, name, states, settingFunction):
        self.settingFunction = settingFunction
        self.name = name
        self.states = states
        self.currentVal = 0
        self.toggleButton = tk.Button(finestra, text=name)
        # self.toggleButton.grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        self.toggleButton.bind("<ButtonRelease-1>", self.callFunction)
        self.tag = tk.Label(finestra, text=states[0])
        # self.tag.grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)  
        self.graficElements = [self.toggleButton, self.tag]   
    
    def callFunction(self, connection):
        self.currentVal = (self.currentVal + 1) % len(self.states)
        self.tag.config(text=self.states[self.currentVal])
        self.settingFunction(self.currentVal)
        

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Red Pitaya PID Control")

# Creazione dell'indicatore
canvas = tk.Canvas(finestra, width=25, height=25)
indicatore = canvas.create_oval(5,5,20,20, fill='red')

# Creazione del setPidValues
B_setPidValues = tk.Button(finestra, text="Enable PID", command=togglePID)

#creazione dei gestori dell'update FPGA
B_updateFpga = tk.Button(finestra, text="Aggiorna FPGA", command=loadNewFpga)
T_FpgaName = tk.Entry(finestra)
T_FpgaName.insert(0, "digPinRamp 23_05_2024 11_27.bit.bin")

def elListToDictionary(elList):
    d = {}
    for el in elList:
        d[el.name] = el
    return d

elements = elListToDictionary([\
    element("Kp", connection.pidSetProportional, -0.01),\
    element("Ki", connection.pidSetIntegral, -0.001),\
    element("Kd", connection.pidSetDerivative, 0.00),\
    element("setpoint", connection.pidSetSetPoint, 0.0),\
    ])
toggles = elListToDictionary([\
    toggle("PWM delay", lambda x,y,z: print("not implemented yet"),True,False, 20),\
    toggle("PWM offset", connection.pidSetPwmSetpoint,True,False, 0),\
    toggle("PWM ramp", connection.pidSetPWMRamp,True,False, "[0,1.8,4e-3,0]"),\
    toggle("PWM linearizer", connection.pidSetPWMLinearizer, True,False, "[0,0.15,0.75,1][0,1,1,0]"),\
    # toggle("DAC1 ramp", lambda x,y,z: print("not implemented yet"),True,False, "[0,1.8,4e-3]"),\
    toggle("ADC0 filter", connection.pidSetGenFilter,True,False, "[0.01,0][1,0.99]"),\
    toggle("DAC0 linearizer", connection.pidSetLinearizer, True,False, "[-1,0.019283939731896,0.032590515583281,0.190926157824052,0.704166283061034,0.861064754066206,0.965351031553027,1][0,0,0.125017474264530,0.278875411577059,0.610845691806975,0.739630993553370,0.871737897932114,1]"),\
    toggle("DAC0 offset", connection.asgSetOffset, True, False,  1),\
    # toggle("DAC1 offset", connection.asgSetOffset2, True, False,  1),\
    toggle("common mode", connection.pidSetCommonModeReject,False),\
    ])
enumToggles = elListToDictionary([\
    enumToggle("feedback", ["no feedback", "PWM negative feedback", "PWM positive feedback", "no feedback, negated output"], connection.pidSetFeedback),\
    enumToggle("safeSwitch", ["disabled", "stopAtSaturation", "resetAtSaturation"], connection.pidSetSafeSwitch),\
    enumToggle("load/send FPGA", \
                   ["compile new & send", "load existing"] if compile_n_sendFpga else ["load existing", "compile new &send"], \
                   change_compile_n_sendFpga),\
    ])
    
def placeInGrid(totalGrid):
    for r in range(len(totalGrid)):
        row = totalGrid[r]
        for e in range(len(row)):
            el = row[e]
            if el is not None:
                if hasattr(el, "graficElements"):
                    for i in range(len(el.graficElements)):
                        el.graficElements[i].grid(row = r, column = e * 3 + i, padx = 5, pady = 5)
                elif hasattr(el, "grid"):
                    el.grid(row = r, column = e * 3, padx = 5, pady = 5)
   
totalGrid = \
[
    [elements["Kp"],        toggles["DAC0 offset"],         toggles["PWM offset"]        ],
    [elements["Ki"],        toggles["DAC0 linearizer"],     toggles["PWM linearizer"]    ],
    [elements["Kd"],        toggles["ADC0 filter"],         toggles["PWM ramp"]          ],
    [elements["setpoint"],  None,                           None                         ],
    [B_setPidValues,        None,                           None                         ],
    [B_updateFpga,          T_FpgaName,                     enumToggles["load/send FPGA"]],
    [indicatore],
]
placeInGrid(totalGrid)

# setPidValues.grid(row = 5 ,column =1,padx=5,pady=5)
# canvas.grid(row = 5, column =0 ,padx=0,pady=0)
# disablePid.grid(row = 6 ,column =1,padx=5,pady=5)
# B_updateFpga.grid(row = 7 ,column =1,padx=5,pady=5)
# T_FpgaName.grid(row = 7 ,column =0,padx=5,pady=5)

B_setPidValues["state"] = "disable"
B_updateFpga["state"] = "disable"

    
finestra.protocol("WM_DELETE_WINDOW", disconnect)
print("connecting...")
connect()
print("connected...")
finestra.mainloop()
