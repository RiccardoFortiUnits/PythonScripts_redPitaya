import tkinter as tk
import threading

import subprocess
from redPitayaInterface import ShellHandler
from datetime import datetime
import shutil
import time



connection = ShellHandler()
connected = False
elementListFile = "redPitayaController.cfg"
def connect():
    global connection, connected
    connection.standardConnection()
    connected = True

def disconnect():
    # Code to execute when the window is closed
    
    if not debug_waitForRedPitaya:
        if connection is not None:
            connection.close()
    root.destroy()
           
    
def setOnGrid(elements, row, column):
    elements = transformToList(elements) 
    for i in range(len(elements)):
        elements[i].grid(row = row, column = column + i, padx = 5, pady = 5)

def transformToList(Object):
    try:
        len(Object)
        return Object
    except:
        return [Object]

def readNumber(string):
    try:
        return float(string)
    except:
        return int(string, 0x10)

class fpgaValue:
    def __init__(self, name, fpgaAddresses, bitStartPositions, bitStringSizes):
        self.name = name
        try:
            len(fpgaAddresses)
        except:
            fpgaAddresses = [fpgaAddresses]
            bitStartPositions = [bitStartPositions]
            bitStringSizes = [bitStringSizes]
            
        self.fpgaAddresses = fpgaAddresses        
        self.bitStartPositions = bitStartPositions        
        self.bitStringSizes = bitStringSizes
        self.currentValues = [0]*len(fpgaAddresses)
        self.refreshValues()
        
    def refreshingFunction(self, *args):
        pass
    def updatingFunction(self, *args):
        pass
        
    def refreshValues(self):
        for i in range(len(self.fpgaAddresses)):
            if debug_waitForRedPitaya:
                self.currentValues[i] = 0
            else:
                self.currentValues[i] = connection.getBitString(self.fpgaAddresses[i], self.bitStartPositions[i], self.bitStringSizes[i])
        self.refreshingFunction()
        
    def update(self, newValues):
        newValues = transformToList(newValues)        
        for i in range(len(newValues)):
            if debug_waitForRedPitaya:
                pass
            else:
                connection.setBitString(self.fpgaAddresses[i], newValues[i], self.bitStartPositions[i], self.bitStringSizes[i])
            self.currentValues[i] = newValues[i]
        self.updatingFunction()
            
class fpgaToggle(fpgaValue):
    def __init__(self, name, fpgaAddress, bitStartPosition, gridRow = 0, gridColumnOffset = 0):
        super().__init__(name, fpgaAddress, bitStartPosition, 1)
        self.toggle = tk.IntVar()
        # Associate the variable with the Checkbutton
        self.checkbox = tk.Checkbutton(root, text= name, variable= self.toggle, command= lambda: self.update(self.toggle.get()))
        self.toggle.set(self.currentValues)
        setOnGrid(self.checkbox, gridRow, gridColumnOffset)
class fpgaReadToggle(fpgaValue):
    def __init__(self, name, fpgaAddress, bitStartPosition, gridRow = 0, gridColumnOffset = 0):
        super().__init__(name, fpgaAddress, bitStartPosition, 1)
        self.tag = tk.Label(root, text=name)        
        self.toggleButton = tk.Button(root, text="refresh")
        self.toggleButton.bind("<ButtonRelease-1>", lambda x: (self.refreshValues(), self.tag.config(text= self.name + ': ' + ('false' if self.currentValues[0] > 0 else 'true'))))
        self.tag.config(text= self.name + ': ' + ('false' if self.currentValues[0] > 0 else 'true'))
        setOnGrid([self.tag, self.toggleButton], gridRow, gridColumnOffset)
        
class fpgaNumber(fpgaValue):
    def __init__(self, name, fpgaAddress, bitStartPosition, bitSize, multiplier = None, initialValue = None, gridRow = 0, gridColumnOffset = 0):
        super().__init__(name, fpgaAddress, bitStartPosition, bitSize)
        # Associate the variable with the Checkbutton
        self.multiplier = multiplier
        self.tag = tk.Label(root, text=name)
        self.entry = tk.Entry(root)
        if initialValue is None:
            initialValue = self.currentValues[0]
        
        if multiplier is None:
            self.entry.insert(0, hex(initialValue))
            self.entry.bind("<Return>", lambda x: self.update(int(readNumber(self.entry.get()))))
        else:
            self.entry.insert(0, str(initialValue*self.multiplier))
            self.entry.bind("<Return>", lambda x: self.update(int(readNumber(self.entry.get())*self.multiplier)))
        setOnGrid([self.tag, self.entry], gridRow, gridColumnOffset)

class fpgaReadNumber(fpgaValue):
    def __init__(self, name, fpgaAddress, bitStartPosition, bitSize, multiplier = None, gridRow = 0, gridColumnOffset = 0):
        super().__init__(name, fpgaAddress, bitStartPosition, bitSize)
        # Associate the variable with the Checkbutton
        self.multiplier = multiplier
        self.tag = tk.Label(root, text=name)        
        self.toggleButton = tk.Button(root, text="refresh")
        if multiplier is None:
            self.toggleButton.bind("<ButtonRelease-1>", lambda x: (self.refreshValues(), self.tag.config(text= self.name + ': ' + hex(self.currentValues[0]))))
            self.tag.config(text= self.name + ': ' + hex(self.currentValues[0]))
        else:
            self.toggleButton.bind("<ButtonRelease-1>", lambda x: (self.refreshValues(), self.tag.config(text= self.name + ': ' + str(self.currentValues[0]/multiplier))))
            self.tag.config(text= self.name + ': ' + str(self.currentValues[0]/multiplier))
        setOnGrid([self.tag, self.toggleButton], gridRow, gridColumnOffset)


class fpgaEnum(fpgaValue):
    def __init__(self, name, fpgaAddress, bitStartPosition, enumValues, gridRow = 0, gridColumnOffset = 0):
        super().__init__(name, fpgaAddress, bitStartPosition, len(enumValues).bit_length())
        self.tag = tk.Label(root, text=name)     
        self.enumValues = enumValues
        self.radioButtons = [None] * len(enumValues)
        
        # Create a variable to hold the selected option
        selected_option_var = tk.StringVar()
        
        # Set an initial value for the selected option
        selected_option_var.initialize(enumValues[self.currentValues[0]])
        
        for i, option in enumerate(enumValues):
            self.radioButtons[i] = tk.Radiobutton(root, text=option, variable=selected_option_var, value=option, 
                                 command=lambda: self.update(enumValues.index(selected_option_var.get())))
            
        setOnGrid([self.tag] + self.radioButtons, gridRow, gridColumnOffset)
        

def getElementList(fileName, row, column):    
    with open(fileName, 'r') as file:
        elements = []
        for line in file:
            # Remove leading and trailing whitespaces
            line = line.strip()
    
            # Check if the line is not empty
            if line:
                lineWithRows = line.replace(')',', gridRow= '+str(row)+', gridColumnOffset='+str(column)+')')
                row = row + 1
                # Evaluate the line to create the object
                obj = eval(lineWithRows)
    
                # Append the created object to the list
                elements.append(obj)    

# ______________________________________________


debug_waitForRedPitaya = False

# Creazione della root principale
root = tk.Tk()
root.title("Red Pitaya Controller")


# Creazione dell'indicatore
canvas = tk.Canvas(root, width=25, height=25)

if not debug_waitForRedPitaya:
    print("waiting for ssh connection")
    connect()
    time.sleep(0.3)
    print("ready")

getElementList(elementListFile, 2, 0)

    
root.protocol("WM_DELETE_WINDOW", disconnect)
# Avvio del loop principale
root.mainloop()
