import numpy as np
import matplotlib.pyplot as plt
import allan_variance
import pandas as pd
import os
import scipy.signal as signal
name_t = []
signalType_l = []
freqDev_l = []
baseFreq_l = []
filesToCombine_l = []
dataColumn_l = []
removeSamplesHigherThan_l = []

'''
# Acquisition with voltmeter. All voltmeter acquisitions should 
# look the same, since the error signal doesn't have a drift, 
# only the redpitaya DAC has some. Anyway, it was acquired in 
# parallel with "18/10/25 Moku acquisition of non-normalized control"
name_t.append("18_10_25 voltmeter acquisition of non-normalized control")
signalType_l.append("V")
freqDev_l.append(11e6)
baseFreq_l.append(64e6)
filesToCombine_l.append(["D:/lastline/SignalHound/17_10/firstHour_voltage_readings2025-10-17__10_44_59_trimmed.csv",
				  "D:/lastline/SignalHound/17_10/voltage_readings2025-10-17__11_21_39_trimmed.csv",
				  "D:/lastline/SignalHound/17_10/voltage_readings2025-10-17 16_34_22_trimmed.csv"])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

'''
# Good acquisition of non-normalized peak. I managed to get 20 hours of acquisition
name_t.append("18_10_25 Moku acquisition of non-normalized control")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append(["D:/lastline/SignalHound/17_10/MokuPhasemeterData_20251017_112121.csv",
				  "D:/lastline/SignalHound/17_10/MokuPhasemeterData_20251017_132251.csv",
				  "D:/lastline/SignalHound/17_10/MokuPhasemeterData_20251017_163356.csv"])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# Good acquisition of normalized peak (with the same parameters as "18/10/25
# Moku acquisition of non-normalized control")
name_t.append("19_10_25 Moku acquisition of normalized control")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append(["D:/lastline/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251022_114221.csv",
				  "D:/lastline/SignalHound/22_10/MokuPhasemeterData_controlNormalized_1_20251022_134328.csv"])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''


'''
# Another normalized acquisition. Though the overall noise is way higher, 
# there aren't long term drifts (maybe because they're too covered by the high noise)
name_t.append("20_10_25 Moku acquisition of normalized control")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append(["D:/lastline/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251020_145315.csv", 
						"D:/lastline/SignalHound/22_10/MokuPhasemeterData_controlNormalized_20251020_155439.csv"])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''


'''
# short acquisition (3 hours), there are a few peaks due to the door opening
# (and with a slower control, they are more visible)
name_t.append("24_10_25 Moku acquisition of normalized control (again), slower PID")
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

'''
# tried to lower the scan frequency to diminish the drifts due 
# to filtering/nonlinearities of the ramp. But I managed to save 
# only a few hours, divided by many hours (the big gaps are 
# just due to the fact that I acquired in different days, so 
# don't trust the allan variance). Though, there's still less 
# of a 1MHz drift after 2 days, which is quite good, I assume
name_t.append("27_10_25 Moku acquisition of normalized control with slower scan frequency")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_7_20251024_194242trimmed.csv",
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_8_20251025_100606trimmed.csv",
	"d:/lastline/scanCavityMeasurements/27_10_25/MokuPhasemeterData_controlNormalized_8.5_20251027_115240trimmed.csv",
])
dataColumn_l.append(1)#2
removeSamplesHigherThan_l.append(None)#[8289, 5512, -1])
#'''

'''
# tried again with the lower scan frequency (14 hours). 
# between hours 8 and 10 there's a big change in frequency, 
# not sure due to what...
name_t.append("28_10_25 Moku acquisition of normalized control with slower scan frequency (with no saturations this time))")
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

'''
# trying to also lock the second peak (using the scan amplitude as the control signal)
name_t.append("28_10_25 Moku acquisition of extra-normalized control (fast scan)")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/28_10_25/MokuPhasemeterData_controlNormalized_12_noisy_20251028_140034.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# trying again to lock the second peak, this time I've got a longer acquisition
name_t.append("30_10_25 Moku acquisition of extra-normalized control (fast scan)")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	# "d:/lastline/scanCavityMeasurements/30_10_25/doubleReferenceLock_20251029_163823.csv",
	"d:/lastline/scanCavityMeasurements/31_10_25/doubleReferenceLock_20251030_183357.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with different scan frequencies, to see the peak-to-peak noise
# I've scaled the control with the scanning frequency, so that all the acquisitions 
# would have a similar effect from the disturbances given by the cavity control. 
# The control was a Integrator with values -15,60 and 240, dev scan 10MHz 
ff = [
#careful: it's written I-2.4e2, but the integral coefficient was actually 1.6e2
	"d:/lastline/scanCavityMeasurements/31_10_25/doubleReferenceLock_period16ms_20251031_092531.csv",
	"d:/lastline/scanCavityMeasurements/31_10_25/doubleReferenceLock_period4ms_I-6e1_20251031_100138.csv",
	"d:/lastline/scanCavityMeasurements/31_10_25/doubleReferenceLock_period1ms_I-2.4e2_20251031_103713.csv",
]
nn = ["32", "8", "2"]
for f, n in zip(ff, nn):
	name_t.append(f"31/10/25 acquisitions with scan period {n}ms")
	signalType_l.append("f")
	freqDev_l.append(None)
	baseFreq_l.append(None)
	filesToCombine_l.append([f])
	dataColumn_l.append(2)
	removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with different scan amplitudes
# I've not scaled the control with the scanning amplitude, even though it should matter. Even though you 
# might expect the larger amplitudes to have more noise (because they have more gain, the intermediated 
# amplitudes have less noise compared to the extremes. So, there might be an optimum in amplitude)
ff = [
#careful: it's written I-2.4e2, but the integral coefficient was actually 1.6e2
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.2_period2ms_I-2.4e2_20251101_161440.csv", 
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.4_period2ms_I-2.4e2_20251101_165347.csv", 
"d:/lastline/scanCavityMeasurements/10_11_25/doubleLocked_duration2ms_amplitude.5_I-1.6e2_20251105_113903.csv",
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.6_period2ms_I-2.4e2_20251101_172828.csv", 
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.8_period2ms_I-2.4e2_20251101_180147.csv", 
]
nn = [".2", ".4", ".5", ".6", ".8", ]
for f, n in zip(ff, nn):
	name_t.append(f"31/10/25 acquisitions with FSR/scan amplitude = {n}")
	signalType_l.append("f")
	freqDev_l.append(None)
	baseFreq_l.append(None)
	filesToCombine_l.append([f])
	dataColumn_l.append(2)
	removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with large scan frequency FSR/scan=.2. compare it 
# with acquisition 30/10/25 Moku acquisition of extra-normalized control (fast scan),
# even though it has different scan frequency and PID speed. you can clearly see that 
# the actual drift is better
name_t.append("31_10_25 long acquisitions with large amplitude")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.2_period2ms_I-4e1_20251101_191122.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with a ramp on the laser frequency, 
# which means the scan offset is gradually changing. Let's see if there's 
# periodic components in the drifts of this acquisition. Laser scan 
# period: 100s
name_t.append("04_11_25 acquisition with slow laser scan")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_cavityOffsetSweep_2ms_I-4e1_laserScan10mHz_20251104_120034.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with different PID intensities. It also contains some acquisitions of other sets
ff = [
#careful: it's written I-2.4e2, but the integral coefficient was actually 1.6e2
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_cavityOffsetSweep_2ms_I-4e1_laserScan10mHz_20251104_120034.csv",
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.4_period2ms_I-8e1_20251101_183836.csv",
"d:/lastline/scanCavityMeasurements/3_11_25/doubleReferenceLock_amplitude.4_period2ms_I-2.4e2_20251101_165347.csv",]
nn = ["40", "80", "160"]
for f, n in zip(ff, nn):
	name_t.append(f"1/11/25 acquisition with integral {n}")
	signalType_l.append("f")
	freqDev_l.append(None)
	baseFreq_l.append(None)
	filesToCombine_l.append([f])
	dataColumn_l.append(2)
	removeSamplesHigherThan_l.append(None)
#'''

'''
# acquisitions (extra-normalized) with amplitude.5
name_t.append("04_11_25 acquisition with slow laser scan")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/3_11_25/doubleLocked_duration2ms_amplitude.5_I-1.6e2_20251104_135535.csv",
	# "d:/lastline/scanCavityMeasurements/3_11_25/doubleLocked_duration2ms_amplitude.5_I-1.6e2_20251104_141348.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append([588])#, 393])
#'''

'''
# first beatnote between ULE and precilaser. The PLL wasn't very stable, so I had to trim a lot of data... Not much time, but the data sure looks nice
name_t.append("22_11_25 first ULE beatnote")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([	
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_044937.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_045109.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_045211.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_045431.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_053719.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_055053.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_055119.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_055210.csv",
"d:/lastline/scanCavityMeasurements/22_12_25/beatnote11.5MHz_doubleNormalized_20251122_061837.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(np.array([6170, 200, 3950, 8900, 64480, 300, 3580, 40310, 3360, ])*0.008388608)
#'''

'''
# second beatnote between ULE and precilaser. Even though the beatnote is at about 11MHz, after unlocking the phasemeter would go to around 12MHz and settle. Since the settling frequency seems to be correlated to the actual beatnote frequency, I tried to do a long measurement even if the phasemeter got unlocked. Of course, after a few minutes, this new "lock" got unlocked again, so no luck here...
# aand... this acquisition sucks very bad. Don't use it
name_t.append("27_11_25 second ULE beatnote")
signalType_l.append("f")
freqDev_l.append(None)
baseFreq_l.append(None)
filesToCombine_l.append([	
	"d:/lastline/scanCavityMeasurements/22_12_25/beatnote8.5MHz_doubleNormalized_20251122_015514.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)#np.array([6170, 200, 3950, 8900, 64480, 300, 3580, 40310, 3360, ])*0.008388608)
#'''

tab = chr(9)#backslash-t I don't want to have a backslash in the code
ret = chr(10)#backslash-n
totalSignal_l = []
fileIntersections_l = []
dt_l = []
for (name, signalType, freqDev, baseFreq, filesToCombine, dataColumn, removeSamplesHigherThan) in zip(name_t, signalType_l, freqDev_l, baseFreq_l, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l):
	file_size_sum = 0
	for fp in filesToCombine:
		file_size_sum += os.path.getsize(fp)
	print(f"{name}: {file_size_sum} bytes ({file_size_sum/1024/1024:.2f} MB)")
	# continue
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
		xsorted = np.sort(x)
		peakRejectionRatio = .05
		peakToPeak = xsorted[int((1-peakRejectionRatio)*len(x))] - xsorted[int(peakRejectionRatio*len(x))]
		print(np.mean(x), np.var(x), peakToPeak, xsorted[-1] - xsorted[0])
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

	plt.plot(t/60/60, x*1e-6, label=name, alpha=.5)
	pd.DataFrame({'t (s)': t, 'frequency (Hz)': x}).to_csv(f"{os.path.dirname(file_path)}/{name}_raw.csv", index=False)
	plt.scatter(t[fileIntersections]/60/60, x[fileIntersections]*1e-6, c="orange")
	# plt.title(name)
	totalSignal_l.append(totalSignal)
	fileIntersections_l.append(fileIntersections)
	dt_l.append(dt)
plt.xlabel("time, hours")
plt.ylabel("beatnote frequency, MHz")
plt.legend()
plt.show()

tau_t = []
avar_t = []
for name, x, dt in zip(name_t, totalSignal_l, dt_l):
	tau, avar = allan_variance.compute_avar(x, dt, input_type="integral", tau_min = dt)

	plt.loglog(tau, avar, '.', label=name)
	tau_t.append(tau)
	avar_t.append(avar)
	tau, avar = allan_variance.compute_avar(x, dt, input_type="mean", tau_min = dt)

	plt.loglog(tau, avar, '.', label=name)
plt.xlabel("Averaging time, s")
plt.ylabel("AVAR")
plt.legend()
plt.show()
# for name, tau, avar in zip(name_t, tau_t, avar_t):
# 	params, avar_pred = allan_variance.estimate_parameters(tau, avar)
# 	params

# 	plt.loglog(tau, avar, '.', label = name)
# 	def remove_last_line(input_string):
# 		all_lines = input_string.split(ret)
# 		all_lines_except_last = all_lines[:-1]
# 		result_string = ret.join(all_lines_except_last)    
# 		return result_string

# 	strParams = str(params)
# 	plt.loglog(tau, avar_pred, label='estimated params:'+remove_last_line(strParams))
# plt.legend()
# plt.xlabel("Averaging time, s")
# plt.ylabel("AVAR")
# plt.show()

for name, x, dt in zip(name_t, totalSignal_l, dt_l):
	fs = 1.0 / dt
	x = np.asarray(x)
	x_d = x - np.mean(x)

	nperseg = min(8192, len(x))
	f, Pxx = signal.welch(x_d, fs=fs, window='hann', nperseg=nperseg, detrend='constant', scaling='density')

	plt.figure("PSD")
	plt.loglog(f, Pxx, label=name, alpha=0.7)
plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD (Hz^2/Hz)")
plt.grid(True, which="both", ls=":", alpha=0.3)
plt.legend()
plt.show()