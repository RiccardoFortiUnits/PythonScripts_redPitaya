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
    connection.modifiedConnection()
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
    if isinstance(Object,list):
        return Object
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
        
        
    def refreshValues(self):
        for i in range(len(self.fpgaAddresses)):
            if debug_waitForRedPitaya:
                self.currentValues[i] = 0
            else:
                self.currentValues[i] = connection.getBitString(self.fpgaAddresses[i], self.bitStartPositions[i], self.bitStringSizes[i])
        
    def update(self, newValues):
        newValues = transformToList(newValues)        
        for i in range(len(newValues)):
            if debug_waitForRedPitaya:
                pass
            else:
                connection.setBitString(self.fpgaAddresses[i], newValues[i], self.bitStartPositions[i], self.bitStringSizes[i])
            self.currentValues[i] = newValues[i]

class canvasElement:
    def place(self, gridRow = 0, gridColumnOffset = 0):
        setOnGrid(self.UI_elements, gridRow, gridColumnOffset)

class fpgaToggle(fpgaValue, canvasElement):
    def __init__(self, name, fpgaAddress, bitStartPosition):
        super().__init__(name, fpgaAddress, bitStartPosition, 1)
        self.toggle = tk.IntVar()
        # Associate the variable with the Checkbutton
        self.checkbox = tk.Checkbutton(root, text= name, variable= self.toggle, command= lambda: self.update(self.toggle.get()))
        self.toggle.set(self.currentValues)
        self.UI_elements = [self.checkbox]
class fpgaReadToggle(fpgaValue, canvasElement):
    def __init__(self, name, fpgaAddress, bitStartPosition):
        super().__init__(name, fpgaAddress, bitStartPosition, 1)
        self.tag = tk.Label(root, text=name)        
        self.toggleButton = tk.Button(root, text="refresh")
        self.toggleButton.bind("<ButtonRelease-1>", lambda x: (self.refreshValues(), self.tag.config(text= self.name + ': ' + ('false' if self.currentValues[0] > 0 else 'true'))))
        self.tag.config(text= self.name + ': ' + ('false' if self.currentValues[0] > 0 else 'true'))
        self.UI_elements = [self.tag, self.toggleButton]

def getSignedNumber(n, bitSize):
    if n>>(bitSize-1) == 1:#negative number?
        n = n | ~((1<<bitSize) - 1)
    return n
    
class fpgaNumber(fpgaValue, canvasElement):
    def __init__(self, name, fpgaAddress, bitStartPosition, bitSize, multiplier = None, initialValue = None):
        super().__init__(name, fpgaAddress, bitStartPosition, bitSize)
        # Associate the variable with the Checkbutton
        self.multiplier = multiplier
        self.tag = tk.Label(root, text=name)
        self.entry = tk.Entry(root)
        
        self.entry.bind("<KeyRelease>", lambda x: self.entry.config(bg="white" if x.keysym == 'Return' else "yellow"))
        if multiplier is None:
            if initialValue is None:
                initialValue = self.currentValues[0]
            self.entry.insert(0, hex(initialValue))
            self.entry.bind("<Return>", lambda x: (self.update(int(readNumber(self.entry.get()))), self.entry.config(bg="white")))
        else:
            if initialValue is None:
                initialValue = getSignedNumber(self.currentValues[0], bitSize) / self.multiplier
            self.entry.insert(0, str(initialValue))
            self.entry.bind("<Return>", lambda x: (self.update(int(readNumber(self.entry.get())*self.multiplier)), self.entry.config(bg="white")))
        self.UI_elements = [self.tag, self.entry]

class fpgaReadNumber(fpgaValue, canvasElement):
    def __init__(self, name, fpgaAddress, bitStartPosition, bitSize, multiplier = None):
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
            self.tag.config(text= self.name + ': ' + str(getSignedNumber(self.currentValues[0], bitSize) / multiplier))
        self.UI_elements = [self.tag, self.toggleButton]


class fpgaEnum(fpgaValue, canvasElement):
    def __init__(self, name, fpgaAddress, bitStartPosition, enumValues):
        super().__init__(name, fpgaAddress, bitStartPosition, (len(enumValues)-1).bit_length())
        self.tag = tk.Label(root, text=name)     
        self.enumValues = enumValues
        self.radioButtons = [None] * len(enumValues)
        #if an enum value is "", it means that the associated number does not have an associated 
            #enum state, and we shouldn't be able to set the enum to that value. Thus, we will only 
            #show the radioButtons for the available enums
        usedRadioButtons = [None] * len(enumValues)
        nOf_usedRadioButtons = 0
        
        # Create a variable to hold the selected option
        selected_option_var = tk.StringVar()
        
        for i, option in enumerate(enumValues):
            self.radioButtons[i] = tk.Radiobutton(root, text=option, variable=selected_option_var, value=option, 
                                 command=lambda: self.update(enumValues.index(selected_option_var.get())))
            if option != "":
                usedRadioButtons[nOf_usedRadioButtons] = self.radioButtons[i]
                nOf_usedRadioButtons = nOf_usedRadioButtons + 1
        
        # Set an initial value for the selected option
        selected_option_var.initialize(enumValues[self.currentValues[0]])
            
        self.UI_elements = [self.tag] + usedRadioButtons[:nOf_usedRadioButtons]
        

class divider(canvasElement):
    def __init__(self, color):        
        line = tk.Frame(root, height=2, width=100, bg=color)
        self.UI_elements = [line]
        

def getElementList(fileName, row, column): 
    firstRow = row
    with open(fileName, 'r') as file:
        elements = []
        maxCol = column
        for line in file:
            # Remove leading and trailing whitespaces
            line = line.strip()
    
            # Check if the line is not empty
            if line and line[0] != '#':
                # Evaluate the line to create the object
                obj = eval(line)
                if isinstance(obj, tuple):
                    c = column                
                    for o in obj:
                        o.place(row, c)
                        c = c + len(o.UI_elements)
                    maxCol = max(maxCol,c)
                else:
                    obj.place(row, column)
                    
                    
                row = row + 1
                if(row > 30):
                    column = maxCol + 5#let's add a few more columns, just in case
                    row = firstRow
    
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
    print("preparing UI")

getElementList(elementListFile, 2, 0)

    
root.protocol("WM_DELETE_WINDOW", disconnect)
# Avvio del loop principale
root.mainloop()
