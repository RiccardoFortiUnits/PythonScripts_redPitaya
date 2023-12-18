import tkinter as tk
import threading

from redPitayaInterface import ShellHandler

connection = ShellHandler()

def connect():
    global connection
    connection.standardConnection()
    setPidValues["state"] = "active"
    disablePid["state"] = "active"
    canvas.itemconfig(indicatore, fill='green')

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

class element:
    def __init__(self, name, settingFunction, gridRow, initialValue):
        self.name = name
        self.settingFunction = settingFunction
        self.tag = tk.Label(finestra, text=name)
        self.entry = tk.Entry(finestra)
        self.Button = tk.Button(finestra,text="+0.1")
        self.Button2 = tk.Button(finestra,text="+0.01")
        self.Button3 = tk.Button(finestra,text="+0.001")
        self.Buttonn = tk.Button(finestra,text="-0.1")
        self.Buttonn2 = tk.Button(finestra,text="-0.01")
        self.Buttonn3 = tk.Button(finestra,text="-0.001")
        self.entry.insert(0, str(initialValue))
        # self.scale.bind("<ButtonRelease-1>", self.updateEntryFromScale)
        self.tag.grid(row = gridRow, column = 0, padx = 5, pady = 5)
        self.entry.grid(row = gridRow, column = 1, padx = 5, pady = 5)
        self.Buttonn.grid(row = gridRow, column = 4, padx = 5, pady = 5)
        self.Buttonn2.grid(row = gridRow, column = 3, padx = 5, pady = 5)
        self.Buttonn3.grid(row = gridRow, column = 2, padx = 5, pady = 5)
        self.Button.grid(row = gridRow, column = 5, padx = 5, pady = 5)
        self.Button2.grid(row = gridRow, column = 6, padx = 5, pady = 5)
        self.Button3.grid(row = gridRow, column = 7, padx = 5, pady = 5)
        
        self.Button.bind("<ButtonRelease-1>", self.updateEntryFromButton1)
        self.Button2.bind("<ButtonRelease-1>", self.updateEntryFromButton2)
        self.Button3.bind("<ButtonRelease-1>", self.updateEntryFromButton3)
        self.Buttonn.bind("<ButtonRelease-1>", self.updateEntryFromButtonn1)
        self.Buttonn2.bind("<ButtonRelease-1>", self.updateEntryFromButtonn2)
        self.Buttonn3.bind("<ButtonRelease-1>", self.updateEntryFromButtonn3)
        
        
    def updateEntryFromButton1(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val + 0.1,5)))
        self.callFunction(connection)
        
    def updateEntryFromButton2(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val + 0.01,5)))
        self.callFunction(connection)
    
    def updateEntryFromButton3(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val + 0.001,5)))
        self.callFunction(connection)
    
    def updateEntryFromButtonn1(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val - 0.1,5)))
        self.callFunction(connection)
        
    def updateEntryFromButtonn2(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val - 0.01,5)))
        self.callFunction(connection)
    
    def updateEntryFromButtonn3(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        # print(self.scale.get())
        self.entry.insert(0, str(round(val - 0.001,5)))
        self.callFunction(connection)
    
    def callFunction(self, connection):
        val = float(self.entry.get())
        output_text.insert(tk.END, f"{self.name}: {val}\n")
        self.settingFunction(val)

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

setPidValues.grid(row = 5 ,column =1,padx=5,pady=5)
canvas.grid(row = 5, column =0 ,padx=0,pady=0)
disablePid.grid(row = 6 ,column =1,padx=5,pady=5)

output_text.grid(row = 5,column=2,rowspan=2, columnspan=6, pady=5)
setPidValues["state"] = "disable"
disablePid["state"] = "disable"
# Avvio del loop principale
x = threading.Thread(target=connect)
x.start()
finestra.mainloop()

connection.__del__()