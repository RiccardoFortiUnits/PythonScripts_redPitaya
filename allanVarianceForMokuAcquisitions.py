import numpy as np
import matplotlib.pyplot as plt
import allan_variance
import pandas as pd
signalType_l = []
freqDev_l = []
baseFreq_l = []
filesToCombine_l = []
dataColumn_l = []
removeSamplesHigherThan_l = []
'''18/10/25 voltmeter acquisition of non-normalized control
signalType_l.append("V")
freqDev_l.append(11e6)
baseFreq_l.append(64e6)
filesToCombine_l.append(["c:/Users/lastline/Documents/SignalHound/17_10/firstHour_voltage_readings2025-10-17__10_44_59_trimmed.csv",
				  "c:/Users/lastline/Documents/SignalHound/17_10/voltage_readings2025-10-17__11_21_39_trimmed.csv",
				  "c:/Users/lastline/Documents/SignalHound/17_10/voltage_readings2025-10-17 16_34_22_trimmed.csv"])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

# '''18/10/25 Moku acquisition of non-normalized control
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append(["c:/Users/lastline/Documents/SignalHound/17_10/MokuPhasemeterData_20251017_112121.csv",
				  "c:/Users/lastline/Documents/SignalHound/17_10/MokuPhasemeterData_20251017_132251.csv",
				  "c:/Users/lastline/Documents/SignalHound/17_10/MokuPhasemeterData_20251017_163356.csv"])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

# '''19/10/25 Moku acquisition of normalized control
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
# filesToCombine_l.append(["c:/Users/lastline/Documents/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251020_145315.csv",
# 				  "c:/Users/lastline/Documents/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251020_155439.csv"])
filesToCombine_l.append(["c:/Users/lastline/Documents/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251022_114221.csv",
				  "c:/Users/lastline/Documents/SignalHound/22_10/MokuPhasemeterData_controlNormalized_1_20251022_134328.csv"])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''24/10/25 Moku acquisition of normalized control (again), slower PID)
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_4_20251024_104247trimmed.csv",
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_5_20251024_124440trimmed.csv",
])
dataColumn_l.append(1)#2
removeSamplesHigherThan_l.append(None)#[-1, 4396])
#'''

'''27/10/25 Moku acquisition of normalized control with slower scan frequency)
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_7_20251024_194242trimmed.csv",
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_8_20251025_100606trimmed.csv",
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_8.5_20251027_115240trimmed.csv",
])
dataColumn_l.append(1)#2
# removeSamplesHigherThan_l.append(None)#[8289, 5512, -1])
#'''

'''28/10/25 Moku acquisition of normalized control with slower scan frequency (with no saturations this time))
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/28_10_25/MokuPhasemeterData_controlNormalized_9_20251027_185258.csv",
	"d:/lastline/scanCavityMeasurements/28_10_25/MokuPhasemeterData_controlNormalized_10_20251028_092923.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

tab = chr(9)#backslash-t I don't want to have a backslash in the code
ret = chr(10)#backslash-n
totalSignal_l = []
fileIntersections_l = []
dt_l = []
for (signalType, freqDev, baseFreq, filesToCombine, dataColumn, removeSamplesHigherThan) in zip(signalType_l, freqDev_l, baseFreq_l, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l):
	totalSignal = None
	fileIntersections = []
	for file_path in filesToCombine:
		with open(file_path, 'r') as file:
			print(f"opening file {file_path}")
			lines = file.readlines()
			i = 1
			while lines[i][0] == "%":
				i += 1
			if tab in lines[1]:
				delimiter = tab
			else:
				delimiter = ','
			num_columns = len(lines[1].strip().split(delimiter))

			# Load the .csv file into a DataFrame, specifying the number of columns
			# Find the header line (last line starting with %)
			header_line_idx = None
			for idx, line in enumerate(lines):
				if line.lstrip().startswith('%'):
					header_line_idx = idx
				else:
					break  # Stop at first non-comment line

			# The header is the last comment line (strip the % and whitespace)
			if header_line_idx is not None:
				header = lines[header_line_idx].lstrip('%').strip().split(delimiter)
				num_columns = len(header)

		# Read the CSV, skipping comment lines, using the correct header and column count
		if header_line_idx is not None:
			df = pd.read_csv(
				file_path,
				names = header,
				header = None,
				delimiter = delimiter,
				usecols = range(num_columns),
				comment = '%',
				skipinitialspace = True
			)
		else:
			df = pd.read_csv(file_path, delimiter=delimiter, header=0, usecols=range(num_columns))
		t = df[df.columns[0]]
		if removeSamplesHigherThan is not None:
			rsht = removeSamplesHigherThan[len(fileIntersections)]
			if rsht != -1:
				limit = np.where(t > rsht)[0][0]
			else:
				limit = rsht
		else:
			limit = -1
		x = df[df.columns[dataColumn]]
		if limit != -1:
			x = x[:limit]
			t = t[:limit]

		# if (removeSamplesHigherThan is not None):
		# 	# Save t and x columns to a new CSV file
		# 	output_file = file_path.replace(".csv", "trimmed.csv")
		# 	pd.DataFrame({'t (s)': t, 'frequency (Hz)': x}).to_csv(output_file, index=False)
		
		if totalSignal is None:
			dt = t[1]-t[0]
			totalSignal = x
		else:
			totalSignal = np.concatenate((totalSignal,x))
		fileIntersections.append(len(totalSignal))
	fileIntersections = fileIntersections[:-1]
	#remove the first 20 minutes, in which the redPitaya is heating up
	# y=y[int(20*60/dt):]
	x=totalSignal
	t = np.linspace(0,len(x)*dt,len(x),endpoint=False)
	if signalType == "V":
		VtoHz = freqDev / 5
		x = 2 * (baseFreq + x * VtoHz)

	plt.figure()
	plt.plot(t, x)
	plt.xlabel("time, s")
	plt.ylabel("laser Variation, MHz")
	plt.scatter(t[fileIntersections], x[fileIntersections], c="orange")
	plt.show()
	totalSignal_l.append(totalSignal)
	fileIntersections_l.append(fileIntersections)
	dt_l.append(dt)

tau_t = []
avar_t = []
for x, dt in zip(totalSignal_l, dt_l):
	tau, avar = allan_variance.compute_avar(x, dt, input_type="integral")

	def removeFirstUpwardsSlope(t,x):
		dx = x[1:] - x[:-1]
		firstMaxIndex = np.where(dx <= 0)[0][0]
		return t[firstMaxIndex:], x[firstMaxIndex:]

	plt.loglog(tau, avar, '.')
	tau_t.append(tau)
	avar_t.append(avar)
plt.xlabel("Averaging time, s")
plt.ylabel("AVAR")
plt.show()
for tau, avar in zip(tau_t, avar_t):
	params, avar_pred = allan_variance.estimate_parameters(tau, avar)
	params

	plt.loglog(tau, avar, '.', label='Computed variance')
	def remove_last_line(input_string):
		all_lines = input_string.split(ret)
		all_lines_except_last = all_lines[:-1]
		result_string = ret.join(all_lines_except_last)    
		return result_string

	strParams = str(params)
	plt.loglog(tau, avar_pred, label='Modeled with estimated parameters:ret'+remove_last_line(strParams))
plt.legend()
plt.xlabel("Averaging time, s")
plt.ylabel("AVAR")
plt.show()