import tkinter as tk
import threading

import subprocess
from redPitayaInterface import ShellHandler
from datetime import datetime
import shutil

connection = ShellHandler()

def connect():
    global connection
    connection.standardConnection()
    setPidValues["state"] = "active"
    disablePid["state"] = "active"
    updateFpga["state"] = "active"
    canvas.itemconfig(indicatore, fill='green')

def disconnect():
    # Code to execute when the window is closed
    if connection is not None:
        connection.close()
    finestra.destroy()
    
def sendToPID():
    # Pulisce il contenuto corrente della casella di testo
    output_text.delete("1.0", tk.END)

    connection.pidDisableIntegral()
    for el in elements:
        el.callFunction(connection)
    connection.pidEnableIntegral()
       
    
def stop_pid():
    output_text.delete("1.0", tk.END)
    connection.pidDisableIntegral()
    connection.pidSetProportional(0)
    connection.pidSetIntegral(0)
    connection.pidSetDerivative(0)
    # connection.setSetPoint(connection, 0)

def loadNewFpga():
    
    newFpgaName = newFpgaName_text.get()
        
    # newFpgaName = newFpgaName + datetime.now().strftime(" %d_%m_%Y %H_%M")+".bit.bin"
    
    # # newFpgaName = newFpgaName.replace(" ", "\\ ")
    
    # backupSaveFolder = "C:/Users/lastline/Documents/backupFpgaBinaries/"

    # #execute the batch that converts the bitstream to one usable by the redPitaya
    # batFilePath="C:/Xilinx/Vivado/2020.1/bin/create_RP_binFile.bat"
    # p = subprocess.Popen(batFilePath, shell=True, stdout = subprocess.PIPE)
    # stdout, stderr = p.communicate()

    # #save a backup of the newly created binary
    # shutil.copyfile("C:/Git/redPitayaFpga/prj/v0.94/project/redpitaya.runs/impl_1/red_pitaya_top.bit.bin", 
    #                backupSaveFolder + newFpgaName)

    # #open an ssh connection, send the selected binary and execute it
    # connection.copyFile(backupSaveFolder + newFpgaName, newFpgaName)
    connection.execute("/opt/redpitaya/bin/fpgautil -b '"+newFpgaName.replace(" ","\ ")+"'")

class element:
    def __init__(self, name, settingFunction, gridRow, initialValue = 0., gridColumnOffset = 0):
        self.name = name
        self.settingFunction = settingFunction
        self.tag = tk.Label(finestra, text=name)
        self.entry = tk.Entry(finestra)
        
        self.entry.insert(0, str(initialValue))
        # self.scale.bind("<ButtonRelease-1>", self.updateEntryFromScale)
        self.tag.grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        self.entry.grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)
        
        incrementers = [-0.001,-0.01,-0.1,0.1,0.01,0.001]
        self.incrementers = [None] * len(incrementers)
        for i in range(len(incrementers)):
            self.incrementers[i] = tk.Button(finestra,text=str(incrementers[i]))
            self.incrementers[i].grid(row = gridRow, column = gridColumnOffset + 2 + i, padx = 5, pady = 5)
            self.incrementers[i].bind("<ButtonRelease-1>", self.updateEntryFromIncrementer)
        
    def updateEntryFromIncrementer(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        buttonValue = float(event.widget.cget("text"))
        self.entry.insert(0, str(round(val + buttonValue,5)))
        self.callFunction(connection)
        
    def callFunction(self, connection):
        val = float(self.entry.get())
        output_text.insert(tk.END, f"{self.name}: {val}\n")
        self.settingFunction(val)

class toggle:
    def __init__(self, name, settingFunction, gridRow, gridColumnOffset = 0, useAdditionalVal = False, initialValue = False, additionalInitialValue = 0.):
        self.useAdditionalVal = useAdditionalVal
        self.settingFunction = settingFunction
        self.name = name
        self.currentVal = initialValue
        self.toggleButton = tk.Button(finestra)
        self.toggleButton.grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        self.toggleButton.bind("<ButtonRelease-1>", self.callFunction)
        if useAdditionalVal:
            self.entry = tk.Entry(finestra)
            self.entry.insert(0, additionalInitialValue)
            self.entry.grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)            
        else:
            self.entry = None
        self.updateButtonText()
    
    def updateButtonText(self):
        if self.currentVal:
            self.toggleButton.config(text="Disabilita " + self.name)
        else:
            self.toggleButton.config(text="Abilita " + self.name)
    
    def callFunction(self, connection):
        self.currentVal = not self.currentVal
        if self.useAdditionalVal:
            val = float(self.entry.get())
            self.settingFunction(self.currentVal, val)
        else:
            self.settingFunction(self.currentVal)
        self.updateButtonText()
       
class enumToggle:
    def __init__(self, name, states, settingFunction, gridRow, gridColumnOffset = 0):
        self.settingFunction = settingFunction
        self.name = name
        self.states = states
        self.currentVal = 0
        self.toggleButton = tk.Button(finestra, text=name)
        self.toggleButton.grid(row = gridRow, column = gridColumnOffset, padx = 5, pady = 5)
        self.toggleButton.bind("<ButtonRelease-1>", self.callFunction)
        self.tag = tk.Label(finestra, text=states[0])
        self.tag.grid(row = gridRow, column = gridColumnOffset + 1, padx = 5, pady = 5)     
    
    def callFunction(self, connection):
        self.currentVal = (self.currentVal + 1) % len(self.states)
        self.tag.config(text=self.states[self.currentVal])
        self.settingFunction(self.currentVal)
        

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Red Pitaya PID Control")

# Creazione dell'etichetta
title = tk.Label(finestra, text="Controllo PID")

# Creazione dell'indicatore
canvas = tk.Canvas(finestra, width=25, height=25)
indicatore = canvas.create_oval(5,5,20,20, fill='red')

# Creazione del setPidValues
setPidValues = tk.Button(finestra, text="Imposta PID", command=sendToPID)
disablePid = tk.Button(finestra, text="Disabilita PID", command=stop_pid)

#creazione dei gestori dell'update FPGA
updateFpga = tk.Button(finestra, text="Aggiorna FPGA", command=loadNewFpga)
newFpgaName_text = tk.Entry(finestra)
newFpgaName_text.insert(0, "filterInMemory 04_01_2024 14_33.bit.bin")

# Creazione della casella di testo per l'output
output_text = tk.Text(finestra, height=5, width=30)


# Posizionamento degli elementi nella finestra
title.grid(row = 0, columnspan=8,padx=5,pady=5)

elements = [\
    element("Kp", connection.pidSetProportional, 1, 0.1),\
    element("Ki", connection.pidSetIntegral, 2, 0.00),\
    element("Kd", connection.pidSetDerivative, 3, 0.00),\
    element("set point (V)", connection.pidSetSetPoint, 4, 0.0),\
    ]
toggles = [\
    toggle("delay", connection.pidSetDelay, 2,8,True,False, 300),\
    toggle("filtro", connection.pidSetFilter, 3,8,True,False, 0.9),\
    ]
enumToggles = [\
    enumToggle("feedback", ["no feedback", "negative feedback", "positive feedback", "negative feedback, negated output"], connection.pidSetFeedback, 1,8),\
    ]
setPidValues.grid(row = 5 ,column =1,padx=5,pady=5)
canvas.grid(row = 5, column =0 ,padx=0,pady=0)
disablePid.grid(row = 6 ,column =1,padx=5,pady=5)
updateFpga.grid(row = 7 ,column =1,padx=5,pady=5)
newFpgaName_text.grid(row = 7 ,column =0,padx=5,pady=5)

output_text.grid(row = 5,column=2,rowspan=2, columnspan=6, pady=5)
setPidValues["state"] = "disable"
disablePid["state"] = "disable"
updateFpga["state"] = "disable"

    
finestra.protocol("WM_DELETE_WINDOW", disconnect)
# Avvio del loop principale
x = threading.Thread(target=connect)
x.start()
finestra.mainloop()
