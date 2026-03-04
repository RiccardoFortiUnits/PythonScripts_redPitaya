import numpy as np
import matplotlib.pyplot as plt
import allan_variance
import pandas as pd
import os
from numpy.lib.stride_tricks import sliding_window_view
from numpy.lib.stride_tricks import as_strided
import scipy.signal as signal
name_t = []
filesToCombine_l = []
dataColumn_l = []
removeSamplesHigherThan_l = []

'''
# noisy beatnote at around 11MHz. I made these measures while the experiments were running (and the ULE would also unlock sometimes), so don't treat these as perfect measurements
name_t.append("5_12_25 double green (unstable)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/5_12_25/peaks2025_12_05 09_19_49.csv",
	"d:/lastline/scanCavityMeasurements/5_12_25/peaks2025_12_04 13_35_53.csv",
	"d:/lastline/scanCavityMeasurements/5_12_25/peaks2025_12_04 15_37_50.csv",
	"d:/lastline/scanCavityMeasurements/5_12_25/peaks2025_12_04 20_34_58.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# noisy beatnote at around 11MHz. These acquisitions are cleaned a bit
name_t.append("5_12_25 double green (unstable)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/5_12_25/peaks2025_12_04 13_35_53.csv"
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# clean beatnote at around 11MHz.
name_t.append("closed loop, piezo scan")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/6_12_25/peaks2025_12_06 09_22_28trimmed.csv",
	"d:/lastline/scanCavityMeasurements/6_12_25/peaks2025_12_06 21_58_38trimmed.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#first file:
rangesToRemoveFromTotal = [[831, 1485], [1898, 1904], [2821, 2898], [3378, 3398], [4037, 4068], [5328, 5433], [5545, 5681], [5808, 5843], [5945, 6032], [6331, 6446], [7190, 8503]]
lims = [1.42e7, 1.48e7]
#second file
# rangesToRemoveFromTotal = [[4108, 4579], [6048, 6813], [6942, 6967], [7169, 7542]]
# lims = [1.42e7, 1.48e7]
#'''

# '''
# open loop
name_t.append("open loop")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/11_12_25/peaks2025_12_10 22_09_30.csv",
	"d:/lastline/scanCavityMeasurements/11_12_25/peaks2025_12_10 22_34_20.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''

'''
# AOM scan, while another experiment was running
name_t.append("noisy AOM scan")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/16_12_25/peaks2025_12_16 13_50_00.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)
#'''


'''
# 18/12/25 PSD beatnote frequency with different scan methods and samplings
ff = [
"d:/lastline/scanCavityMeasurements/18_12_25/AOM scan_peaks2025_12_18 13_36_10.csv",
"d:/lastline/scanCavityMeasurements/18_12_25/AOM scan_peaks2025_12_18 13_48_09.csv",
"d:/lastline/scanCavityMeasurements/18_12_25/AOM scan_peaks2025_12_18 16_44_15.csv",
"d:/lastline/scanCavityMeasurements/18_12_25/piezo scan_peaks2025_12_18 13_58_15.csv",
"d:/lastline/scanCavityMeasurements/18_12_25/piezo scan_peaks2025_12_18 14_59_46.csv",
"d:/lastline/scanCavityMeasurements/18_12_25/piezo scan_peaks2025_12_18 15_02_29.csv",
]
nn = ["AOM scan, sampling 1Hz", "AOM scan, sampling 5Hz", "AOM scan, sampling 8Hz", 
	   "piezo scan, sampling 1Hz", "piezo scan, sampling 5Hz", "piezo scan, sampling 5Hz", ]
removeSamples = [None, None, [.021*60*60], [30*60], None, None]
for f, n, rs in zip(ff, nn, removeSamples):
	name_t.append(f"18/12/25 {n}")
	filesToCombine_l.append([f])
	dataColumn_l.append(2)
	removeSamplesHigherThan_l.append(rs)
#'''

'''
# 18/12/25 AOM scan. It looks way better, but I couldn't measure it with the phasemeter (implying that the instantaneous noise is quite bad). Not sure what to do of this measuremnt
name_t.append("closed loop, AOM scan")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/18_12_25/AOM scan_peaks2025_12_18 13_48_09.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append(None)#[.021*60*60])
#'''


'''
# 23/12/25 AOM scan, with stable reference. Couldn't get a very long acquisition, but it looks good nonetheless
name_t.append("closed loop, AOM scan")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/23_12_25/AOM_scan_peaks2025_12_23-08_06_30.csv",
])
dataColumn_l.append(2)
removeSamplesHigherThan_l.append([1559])
#'''


def removeOutliars(x, windowSize):
	x = np.asarray(x)
	if windowSize % 2 == 0:
		raise ValueError("windowSize must be odd")
	if x.size == 0:
		return x
	k = windowSize // 2
	xp = np.pad(x, k, mode='edge')
	try:
		windows = sliding_window_view(xp, window_shape=windowSize)
	except Exception:
		# fallback using as_strided
		shape = (x.size, windowSize)
		strides = (xp.strides[0], xp.strides[0])
		windows = as_strided(xp, shape=shape, strides=strides)
	centers = windows[:, k]
	mmax = windows.max(axis=1)
	mmin = windows.min(axis=1)
	keep = (centers != mmax) & (centers != mmin)
	return x[keep]


tab = chr(9)#backslash-t I don't want to have a backslash in the code
ret = chr(10)#backslash-n
totalSignal_l = []
fileIntersections_l = []
dt_l = []
for (name, filesToCombine, dataColumn, removeSamplesHigherThan) in zip(name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l):

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
		t = df[df.columns[dataColumn-1]]
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
		dt = (t[len(t)-1]-t[0]) / (len(t)-1)
		print(dt)
		# dt=5
		
		# list.reverse(rangesToRemoveFromTotal)
		# for min, max in rangesToRemoveFromTotal:
		# 	x = np.concatenate((x[:min], x[max:]))
		# 	t = np.concatenate((t[:min], t[max:]))
		# acceptableValues=np.logical_and(x>lims[0], x<lims[1])
		# x = x[acceptableValues]
		# t = t[acceptableValues]

		# if (removeSamplesHigherThan is not None):
		# 	# Save t and x columns to a new CSV file
		# 	output_file = file_path.replace(".csv", "trimmed.csv")
		# 	pd.DataFrame({'t (s)': t, 'frequency (Hz)': x}).to_csv(output_file, index=False)

		# v = df[df.columns[dataColumn+1]]
		# x = x[v > -60]

		xsorted = np.sort(x)
		peakRejectionRatio = .05
		peakToPeak = xsorted[int((1-peakRejectionRatio)*len(x))] - xsorted[int(peakRejectionRatio*len(x))]
		print(np.mean(x), np.var(x), peakToPeak, xsorted[-1] - xsorted[0])
		if totalSignal is None:
			totalSignal = x
		else:
			totalSignal = np.concatenate((totalSignal,x))
		fileIntersections.append(len(totalSignal))
	fileIntersections = fileIntersections[:-1]
	#remove the first 20 minutes, in which the redPitaya is heating up
	# y=y[int(20*60/dt):]
	x=totalSignal
	t = np.linspace(0,len(x)*dt,len(x),endpoint=False)
	if name == "open loop":
		h=t/60/60
		x = x[np.logical_and(h>.5,h<1.4)]
		t = t[np.logical_and(h>.5,h<1.4)]

	plt.plot(t/60/60, x*1e-6, label=name, alpha=.5)
	# pd.DataFrame({'t (s)': t, 'frequency (Hz)': x}).to_csv(f"{os.path.dirname(file_path)}/{name}_raw.csv", index=False)
	# plt.scatter(t[fileIntersections]/60/60, x[fileIntersections]*1e-6, c="orange")
	# plt.title(name)
	totalSignal_l.append(x)
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

	def removeFirstUpwardsSlope(t,x):
		dx = x[1:] - x[:-1]
		firstMaxIndex = np.where(dx <= 0)[0][0]
		return t[firstMaxIndex:], x[firstMaxIndex:]

	plt.loglog(tau, avar, '.', label=name)
	tau_t.append(tau)
	avar_t.append(avar)
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
	fft_result = np.fft.fft(x_d)
	freqs = np.fft.fftfreq(len(fft_result), d=dt)

	# Only keep the positive frequencies and their corresponding FFT values
	pos_mask = freqs > 0
	freqs = freqs[pos_mask]
	Pxx = (np.abs(fft_result[pos_mask]) ** 2) / len(x_d)

	plt.figure("PSD")
	plt.loglog(freqs, Pxx, label=name, alpha=0.7)

	# nperseg = min(8192, len(x))
	# f, Pxx = signal.welch(x_d, fs=fs, window='hann', nperseg=nperseg, detrend='constant', scaling='density')

	# plt.figure("PSD")
	# plt.loglog(f, Pxx, label=name, alpha=0.7)
plt.xlabel("Frequency (Hz)")
plt.ylabel("PSD (Hz^2/Hz)")
plt.grid(True, which="both", ls=":", alpha=0.3)
plt.legend()
plt.show()