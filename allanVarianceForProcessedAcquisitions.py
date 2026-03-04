import numpy as np
import matplotlib.pyplot as plt
import allan_variance
import allantools
import pandas as pd
import os
from numpy.lib.stride_tricks import sliding_window_view
from numpy.lib.stride_tricks import as_strided
import scipy.signal as signal
name_t = []
filesToCombine_l = []
dataColumn_l = []
removeSamplesHigherThan_l = []

# '''
# AOM beatnote (reference unstabilized)
# name_t.append("31/10/25 AOM beatnote (reference unstabilized)")
name_t.append("piezo scan system noise floor")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/3_11_25/31_10_25 long acquisitions with large amplitude_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

# '''
# non-normalized peaks, AOM beatnote (reference unstabilized)
# name_t.append("31/10/25 AOM beatnote (reference unstabilized)")
name_t.append("closed loop, peaks non-normalized (phasemeter)")
filesToCombine_l.append([
	"d:/lastline/SignalHound/17_10/18_10_25 Moku acquisition of non-normalized control_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''



# '''
# ULE-precilaser beatnote (reference stabilized)
# name_t.append("5/12/25 ULE-precilaser beatnote (reference stabilized)")
name_t.append("closed loop (spectrum peak)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/6_12_25/5_12_25 double green (stable)_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

# '''
# ULE-precilaser beatnote (reference stabilized, phasemeter)
# name_t.append("5/12/25 ULE-precilaser beatnote (reference stabilized, phasemeter)")
name_t.append("closed loop (phasemeter)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/22_12_25/22_11_25 first ULE beatnote_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''
# '''
# ULE-precilaser beatnote in open loop
# name_t.append("11/12/25 open loop (reference stabilized)")
name_t.append("open loop (spectrum peak)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/11_12_25/11_12_25 open loop (stable reference)_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

# '''
# ULE-precilaser beatnote AOM scan (jumping reference)
# name_t.append("ULE-precilaser beatnote with AOM scan (jumping reference)")
name_t.append("AOM-scan with jumping reference (spectrum peak)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/18_12_25/closed loop, AOM scan_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
#'''

# '''
# ULE-precilaser beatnote AOM scan (stable reference)
name_t.append("AOM-scan (spectrum peak)")
filesToCombine_l.append([
	"d:/lastline/scanCavityMeasurements/23_12_25/closed loop, AOM scan_raw.csv",
])
dataColumn_l.append(1)
removeSamplesHigherThan_l.append(None)
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

def smoothPDF(samples):
	x = np.sort(samples)
	y = np.linspace(0,1,len(x))
	unique = np.where(x[:-1] != x[1:])[0]
	maxPoints = 50
	if len(unique) > len(x) * .9:
		xq = ((x - x[0]) / (x[-1] - x[0]) * maxPoints).round() / maxPoints * (x[-1] - x[0]) + x[0]
		unique = np.where(xq[:-1] != xq[1:])[0]
	unique = np.concatenate(([0], unique + 1))
	x = x[unique]
	y = y[unique]
	y /= y[-1]
	y1 = np.diff(y) / np.diff(x)
	# filterSize = np.ceil(len(x) / 20)
	# y1 = np.convolve(y1, np.repeat((1./filterSize), filterSize), mode="same")
	# return x[:-1], y[:-1]
	return x[:-1], y1
def AllanVariance(f, dt, tau_max = None, nOfPoints = 50):
	tmin = dt
	f = np.array(f)
	if tau_max is None:
		tmax = dt * len(f) * .75
	else:
		tmax = tau_max
	points = np.logspace(0, np.log10(tmax / dt), num=nOfPoints).astype(int)
	points = np.unique(points)
	taus = points * dt
	avar = np.zeros_like(points, dtype=float)
	for i, k in enumerate(points):
		avar[i] = np.mean((f[k:]-f[:-k])**2)
	avar = .5 * avar# / taus**2 boh...
	return taus, avar
	

tab = chr(9)#backslash-t I don't want to have a backslash in the code
ret = chr(10)#backslash-n

def execOnSubset(subset, function, *functionArguments):
	global name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	old_name_t, old_filesToCombine_l, old_dataColumn_l, old_removeSamplesHigherThan_l = name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	
	filesToCombine_l = [filesToCombine_l[name_t.index(name)] for name in subset]
	dataColumn_l = [dataColumn_l[name_t.index(name)] for name in subset]
	removeSamplesHigherThan_l = [removeSamplesHigherThan_l[name_t.index(name)] for name in subset]
	name_t = [name_t[name_t.index(name)] for name in subset]
	
	function(*functionArguments)
	name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l = old_name_t, old_filesToCombine_l, old_dataColumn_l, old_removeSamplesHigherThan_l


totalSignal_l = []
# fileIntersections_l = []
dt_l = []


def loadRawFiles(plot, forcedDt = None):
	global totalSignal_l, dt_l
	global name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	totalSignal_l = []
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
			dt = (t[len(t)-1]-t[0]) / (len(t)-1)
			# print(f"dt: {dt}")
			if forcedDt is not None:
				DT = forcedDt
				resample_factor = int(np.round(DT / dt))
				if resample_factor > 1:
					# Apply anti-aliasing lowpass filter before downsampling
					nyquist_freq = 1.0 / (2 * DT)
					normalized_cutoff = nyquist_freq / (1.0 / (2 * dt))
					if normalized_cutoff < 1.0:
						b, a = signal.butter(4, normalized_cutoff, btype='low')
						x = signal.filtfilt(b, a, x)
					x = x[::resample_factor]
					t = t[::resample_factor]
					dt = dt * resample_factor
			
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
			xsorted = np.sort(x)
			peakRejectionRatio = .05
			peakToPeak = xsorted[int((1-peakRejectionRatio)*len(x))] - xsorted[int(peakRejectionRatio*len(x))]
			rms = np.std(x)
			print(f"{name}: dt {dt}, peak-to-peak {peakToPeak}, RMS {rms}")
			# print(np.mean(x), np.var(x), peakToPeak, xsorted[-1] - xsorted[0])
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
		www = 0
		if name == "AOM-scan (spectrum peak)":
			www = .4e6
		ttt=0
		if name == "open loop (spectrum peak)":
			ttt = -.3
		totalSignal_l.append(x)
		# fileIntersections_l.append(fileIntersections)
		dt_l.append(dt)
		# pd.DataFrame({'t (s)': t, 'frequency (Hz)': x}).to_csv(f"{os.path.dirname(file_path)}/{name}_raw.csv", index=False)
		
		if plot:
			plt.plot(t/60/60+ttt, (x-np.mean(x)+www)*1e-6, label=name, alpha=.5)
			
	if plot:
		plt.xlabel("time, hours")
		plt.ylabel("beatnote frequency, MHz")
		plt.legend()
		plt.show()

def plotAvar():
	global totalSignal_l, dt_l
	global name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	for name, x, dt in zip(name_t, totalSignal_l, dt_l):
		# tau, avar = allan_variance.compute_avar(x, dt, input_type='mean', tau_min = dt)
		tau, avar,_,_ = allantools.oadev(x, 1/dt, 'freq', 'all')

		# def removeFirstUpwardsSlope(t,x):
		# 	dx = x[1:] - x[:-1]
		# 	firstMaxIndex = np.where(dx <= 0)[0][0]
		# 	return t[firstMaxIndex:], x[firstMaxIndex:]

		plt.loglog(tau, avar, label=name)
		# tau, avar = allan_variance.compute_avar(x, dt, input_type='mean', tau_min = dt)
		# plt.loglog(tau, avar, '.', label=name)
	plt.xlabel("Averaging time, s")
	plt.ylabel(r"Beatnote Allan deviation ($Hz / \sqrt{s}$)")
	plt.legend()
	plt.show()

def plotPSD():
	global totalSignal_l, dt_l
	global name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	for name, x, dt in zip(name_t, totalSignal_l, dt_l):
		fs = 1.0 / dt
		x = np.asarray(x)
		x_d = x - np.mean(x)
		# # Calculate the FFT of the signal
		# fft_result = np.fft.fft(x_d)
		# freqs = np.fft.fftfreq(len(fft_result), d=dt)

		# # Only keep the positive frequencies and their corresponding FFT values
		# pos_mask = freqs > 0
		# freqs = freqs[pos_mask]
		# Pxx = (np.abs(fft_result[pos_mask]) ** 2) / len(x_d)
		# f = freqs
		# plt.figure("PSD")
		# plt.loglog(freqs, Pxx, label=name, alpha=0.7)
		nperseg = min(max(2000, len(x) / 10), len(x))# min(8192*16, len(x))
		print(nperseg)
		f, Pxx = signal.welch(x_d, fs=fs, window='hann', nperseg=nperseg, detrend='constant', scaling='density')
		# Logarithmically spaced frequency bins
		# f_log = np.logspace(np.log10(f[1]), np.log10(f[-1]), num=1000)
		# Pxx_log = np.interp(f_log, f, Pxx)
		# f, Pxx = f_log, Pxx_log

		plt.figure("PSD")
		plt.loglog(f, Pxx, label=name, alpha=0.7)
	plt.xlabel("Frequency (Hz)")
	plt.ylabel("Beatnote PSD (Hz^2/Hz)")
	plt.grid(True, which="both", ls=":", alpha=0.3)
	plt.legend()
	plt.show()


def plotHistogram():
	global totalSignal_l, dt_l
	global name_t, filesToCombine_l, dataColumn_l, removeSamplesHigherThan_l
	plt.figure("histogram")
	for name, x, dt in zip(name_t, totalSignal_l, dt_l):
		x = np.asarray(x)
		x_d = x - np.mean(x)
		x_d = np.sort(x_d)
		# plt.plot(x_d/1e6, np.linspace(0,1,len(x_d)), label=name, alpha=0.7)
		# hist, bin_edges = np.histogram(x_d, bins=70, density=True)
		# bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
		bin_centers, hist = smoothPDF(x_d)
		plt.plot(bin_centers / 1e6, hist, label=name, alpha=0.7)
	plt.xlabel("Beatnote Frequency (MHz)")
	plt.ylabel("distribution")
	plt.grid(True, which="both", ls=":", alpha=0.3)
	plt.legend()
	plt.show()

######Piezo scan

# # time-dependent, open v closed
# execOnSubset(["closed loop (spectrum peak)", "open loop (spectrum peak)"], loadRawFiles, True)
# # time-dependent, normalized v non-normalized, plus histogram
# execOnSubset(["closed loop (spectrum peak)", "closed loop, peaks non-normalized (phasemeter)"], 
# 			 lambda *args: (loadRawFiles(True, 5), plotHistogram()))

#allan variance: open, closed, closed non-normalized
execOnSubset(["closed loop (spectrum peak)", "closed loop, peaks non-normalized (phasemeter)", "open loop (spectrum peak)"], 
			 lambda *args: (loadRawFiles(False, 5), plotAvar()))

# #PSD: open, closed (both phasemeter and spectrum peak), noise floor
# execOnSubset(["closed loop (spectrum peak)", "closed loop (phasemeter)", "open loop (spectrum peak)", "piezo scan system noise floor"], 
# 			 lambda *args: (loadRawFiles(False), plotPSD()))

######AOM scan

# # time-dependent, piezo v AOM, plus histogram
# execOnSubset(["closed loop (spectrum peak)", "AOM-scan (spectrum peak)"], 
# 			 lambda *args: (loadRawFiles(True), plotHistogram()))

# #PSD: open, closed (both phasemeter and spectrum peak), noise floor, AOM scan
# execOnSubset(["closed loop (spectrum peak)", "closed loop (phasemeter)", "open loop (spectrum peak)", "piezo scan system noise floor", "AOM-scan (spectrum peak)"], 
# 			 lambda *args: (loadRawFiles(False), plotPSD()))