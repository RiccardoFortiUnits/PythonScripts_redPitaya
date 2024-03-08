from redPitayaInterface import ShellHandler

import sys
import os

# sys.argv[0] is the script name itself
filePath = sys.argv[1]
fileName_withExtension =  os.path.basename(filePath)
fileName =  os.path.splitext(fileName_withExtension)[0]

connection = ShellHandler()
connection.standardConnection()

connection.copyFile(filePath, "C/"+fileName_withExtension)

connection.execute("cd C")
print("building file")
response = connection.execute("make " + fileName, 6)
print(response)
response = connection.execute("./" + fileName, 2)
print(response)
connection.close()
           