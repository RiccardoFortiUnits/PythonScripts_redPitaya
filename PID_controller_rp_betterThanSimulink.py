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

    connection.reset(connection)
    for el in elements:
        el.callFunction(connection)
    connection.enableIntegral(connection)
       
    
def stop_pid():
    output_text.delete("1.0", tk.END)
    # connection.reset(connection)
    connection.setProportional(connection, 0)
    connection.setIntegral(connection, 0)
    connection.setDerivative(connection, 0)
    # connection.setSetPoint(connection, 0)

class element:
    def __init__(self, name, settingFunction, gridRow, initialValue):
        self.name = name
        self.settingFunction = settingFunction
        self.tag = tk.Label(finestra, text=name)
        self.entry = tk.Entry(finestra)
        self.scale = tk.Scale(finestra, from_=0.5, to=2,resolution=0.25, orient=tk.HORIZONTAL)
        self.entry.insert(0, str(initialValue))
        self.scale.set(1)
        self.scale.bind("<ButtonRelease-1>", self.updateEntryFromScale)
        self.tag.grid(row = gridRow, column = 0, padx = 5, pady = 5)
        self.entry.grid(row = gridRow, column = 1, padx = 5, pady = 5)
        self.scale.grid(row = gridRow, column = 2, padx = 5, pady = 5)
        
    def updateEntryFromScale(self, event):
        val = float(self.entry.get())
        self.entry.delete(0, tk.END)
        print(self.scale.get())
        self.entry.insert(0, str(val * float(self.scale.get())))
        self.callFunction(connection)
    
    def callFunction(self, connection):
        val = float(self.entry.get())
        output_text.insert(tk.END, f"{self.name}: {val}\n")
        self.settingFunction(connection, val)

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("red pitaya PID")

# Creazione dell'etichetta
title = tk.Label(finestra, text="Controllo PID")


# Creazione dell'indicatore
canvas = tk.Canvas(finestra, width=25, height=20)
indicatore = canvas.create_oval(5,5,15,15, fill='red')

# Creazione del setPidValues
setPidValues = tk.Button(finestra, text="Imposta PID", command=sendToPID)
disablePid = tk.Button(finestra, text="Disabilita PID", command=stop_pid)

# Creazione della casella di testo per l'output
output_text = tk.Text(finestra, height=5, width=30)


# Posizionamento degli elementi nella finestra
title.grid(row = 0, columnspan=3,padx=5,pady=5)

elements = [\
    element("Kp", connection.pidSetProportional, 1, 0.1),\
    element("Ki", connection.pidSetIntegral, 2, 0.02),\
    element("Kd", connection.pidSetDerivative, 3, 0.01),\
    element("set point (V)", connection.pidSetSetPoint, 4, 0.3),\
    ]

setPidValues.grid(row = 5 ,column =1,padx=5,pady=5,sticky=tk.W)
canvas.grid(row = 5, column =0 ,padx=5,pady=5)
disablePid.grid(row = 6 ,column =1,padx=5,pady=5,sticky=tk.W)

output_text.grid(row = 7, columnspan=3, pady=5)
setPidValues["state"] = "disable"
disablePid["state"] = "disable"
# Avvio del loop principale
x = threading.Thread(target=connect)
x.start()
finestra.mainloop()

connection.__del__()