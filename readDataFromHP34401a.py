
def install_and_import(package):
	import subprocess
	import sys
	try:
		__import__(package)
	except ImportError:
		try:
			subprocess.check_call([sys.executable, "-m", "pip", "install", f"py{package}"])
		except:
			subprocess.check_call([sys.executable, "-m", "pip", "install", package])
		__import__(package)
		
install_and_import("pyvisa")
install_and_import("serial")
import pyvisa
import time
import csv
from datetime import datetime
import numpy as np

# Configuration
resource_name = "GPIB0::23::INSTR"  # Change this to match your setup
interval = 1.0  # seconds between readings
duration = 10.0  # total acquisition time in seconds
output_csv = "voltage_readings.csv"
def acquire_voltage(resource_name, interval, duration):
	rm = pyvisa.ResourceManager()
	values = np.zeros(int(np.ceil(duration/interval)))
	ts = np.zeros(int(np.ceil(duration/interval)))
	try:
		instrument = rm.open_resource(resource_name)
		instrument.write("*IDN?")
		print("Connected to:", instrument.read())

		instrument.write("CONF:VOLT:DC")  # Configure for DC voltage measurement

		start_time = time.time()
		for i in range(len(values)):
			initialTime = time.time()
			voltage = instrument.query("READ?")
			timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			print(f"{timestamp} - Voltage: {voltage.strip()} V")
			currentTime = time.time()
			ts[i] = currentTime - start_time
			values[i] = voltage
			time.sleep(initialTime + interval - currentTime)

	except Exception as e:
		print("Error:", e)
	finally:
		with open(output_csv, mode='w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(['Time (s)', 'Voltage (V)'])
			for t, v in zip(ts, values):
				writer.writerow([t, v])
		instrument.close()
		rm.close()

# Run acquisition
acquire_voltage(resource_name, interval, duration)
