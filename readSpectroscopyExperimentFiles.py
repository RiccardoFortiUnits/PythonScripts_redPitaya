import h5py
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from tqdm import tqdm

flashDrivePath = "d:/"
computerStoragePath = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/"

class hiddenList(list):
	def __set__(self, instance, value):
		self.append(value)
	def __get__(self, instance, owner):
		if instance is not None:
			return self[instance.i]
		return self
class v:
	name = hiddenList()
	directory = hiddenList()
	experimentNumber = hiddenList()
	savedCsvFileName = hiddenList()
	removingFunction = hiddenList()
	pressureFile = hiddenList()
	i = 0
	@staticmethod
	def len():
		return len(v.name)
	def iteration(self):
		for i in range(self.len()):
			self.i = i
			yield i
	
vv = v()
# '''
vv.name = "14/3/26 compensation 3.7"
vv.directory = "//ARQUS-CAM/Experiments/ytterbium174/2026/03/14/B_Yb174_MOT_stability/shots"
vv.experimentNumber = "_0002_"
vv.savedCsvFileName = "allAtomDriftShotValues_14_3_26.csv"
vv.removingFunction = lambda t, f, e: np.logical_and(e < .4, np.logical_or((t-t[0])/3600 < 1.2947, (t-t[0])/3600 > 1.6694))
vv.pressureFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/RuuviTag 171A_20260316T092055+0100.csv"
#'''

# '''
vv.name = "16/3/26 no compensation"
vv.directory = "//ARQUS-CAM/Experiments/ytterbium174/2026/03/16/C_Yb174_MOT_stability/shots"
vv.experimentNumber = "_0104_"
vv.savedCsvFileName = "allAtomDriftShotValues_16_3_26.csv"
vv.removingFunction = lambda t, f, e: np.ones_like(t, dtype=bool)
vv.pressureFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/RuuviTag 171A_20260317T090345+0100.csv"
#'''


def extractDataFromExperimentFiles(directory, savedCsvFile_flashDrive):
	global flashDrivePath
	print(f""""extracting all the data out of folder {directory}. If you see that many files are not 
		able to be opened, it's probably an error in the measurement, and you can assume that all 
		the following files will have the same error. Just type Ctrl+C on the terminal to terminate 
		the file reading. The already read files will be correctly saved""")	
	data = {
	"indexes" : [],
	"timings" : [],
	"freq" : [],
	"nOfAtoms" : [],
	}
	files = glob.glob(os.path.join(directory, "*.h5"))
	for fpath in tqdm(files):
		if experimentNumber in fpath:
			with h5py.File(fpath, "r") as h5:
				try:
					group = h5["results/MOT_in_situ"]
					globGroup = h5["globals"]
					data["nOfAtoms"].append(group.attrs["N_atoms"])
					data["indexes"].append(globGroup.attrs["spectroscopy_number"])
					data["freq"].append(globGroup.attrs["abs_imaging_freq"])
					dateTtime = h5.attrs["run time"]#format: YYYYMMDD"T"hhmmss.ffffff I couldn't format it directly, so let's convert it to a more manageable format
					normalFormatTime = f"{dateTtime[:4]}.{dateTtime[4:6]}.{dateTtime[6:8]} {dateTtime[9:11]}:{dateTtime[11:13]}:{dateTtime[13:]}"
					time = datetime.strptime(normalFormatTime, "%Y.%m.%d %H:%M:%S.%f").timestamp()
					data["timings"].append(float(time))
				except:
					print(f"couldn't open {fpath}")
	df = pd.DataFrame(data)
	df.to_csv(f"{flashDrivePath}/{savedCsvFile_flashDrive}", index=False)
	return df
def time_to_seconds(time_str):    
	"""Convert time format HHMMSS.ms to seconds since 00:00"""
	time_str = str(float(time_str)).zfill(13)  # Ensure the string has the correct format
	hours = int(time_str[0:2])
	minutes = int(time_str[2:4])
	seconds = float(time_str[4:])
	if hours < 12:
		hours += 24
	return hours * 3600 + minutes * 60 + seconds
def lorentzian_fit(xs, y):
	"""
	Fit a lorentzian with offset to the data.
	Parameters: mu (center), gamma (width), amplitude, offset
	Returns: (mu, gamma, amplitude, offset)
	"""
	from scipy.optimize import curve_fit        
	def lorentzian(x, mu, gamma, amplitude, offset):
		return amplitude * gamma**2 / ((x - mu)**2 + gamma**2) + offset        
	# Initial guesses
	mu_init = xs[np.argmax(y, axis=0)]
	gamma_init = np.repeat((xs.max() - xs.min()) / 4, y.shape[1])
	amplitude_init = np.max(y, axis=0) - np.min(y, axis=0)
	offset_init = np.min(y, axis=0)
	outs = np.zeros((y.shape[1], 4))
	error = np.zeros(y.shape[1])
	for i in range(len(gamma_init)):
		try:
			popt, _ = curve_fit(lorentzian, xs, y[:,i], p0=[mu_init[i], gamma_init[i], amplitude_init[i], offset_init[i]])
			error[i] = (np.diag(_)**.5)[0]
			outs[i,:] = popt
		except:
			pass
	return outs[:,0], error
def saveRawFrequency(savedCsvFile, indexesToKeep = lambda t, f, error : np.ones_like(t,dtype=bool)):
	data = pd.read_csv(savedCsvFile)
	mtime = os.path.getmtime(savedCsvFile)
	if datetime.fromtimestamp(mtime) > datetime(2026, 3, 12):
		data["timings"] = data["timings"]
	else:
		addedTime = datetime(2026, 3, 10).timestamp()
		data["timings"] = [addedTime + time_to_seconds(data["timings"][i]) for i in range(len(data["timings"]))]
		
	atoms = []
	allTimes = []
	xs =np.array(np.unique([f for f in data["freq"]]))

	for j in range(len(xs)):
		nAtoms = np.array([data["nOfAtoms"][i] for i in range(len(data["indexes"])) if data["freq"][i] == xs[j]])
		times = np.array([data["timings"][i] for i in range(len(data["indexes"])) if data["freq"][i] == xs[j]], dtype=float)
		sort = np.argsort(times)
		nAtoms = nAtoms[sort]
		times = times[sort]
		allTimes.append(times)
		atoms.append(nAtoms)
	lengths = np.array([len(a) for a in atoms])
	m = lengths.min()
	if lengths.max() != m:
		for i in range(len(xs)):
			atoms[i] = atoms[i][:m]
			allTimes[i] = allTimes[i][:m]
	atoms = np.array(atoms)
	t = np.mean(np.array(allTimes),axis=0)
	mu, error = lorentzian_fit(xs, atoms)
	toKeep = indexesToKeep(t,mu,error)# np.logical_and(error < .4, np.logical_and(mu < 265, mu > 235))
	f = mu[toKeep]
	error = error[toKeep]
	t=t[toKeep]
	pd.DataFrame({"t (s)" : t, "frequency (Hz)" : f * 1e6}).to_csv(savedCsvFile.replace(".csv", "_raw.csv"), index=False)
	return t, f, error
def plotFrequencyuWithError(t, f, error):

	plt.errorbar((t - t[0]) / 3600, f, yerr=error, fmt=".", label=f"laser frequency drift")
	plt.xlabel("time (h)")
	plt.ylabel("Frequency drift (MHz)")
	plt.legend()
	plt.show()
def plotFrequency_v_pTh(t, f, pressureFile, onlyPressure = False):
	from regressPressureAndBlueFreq import readPressure, alignSignals, readPTh
	from volterraRegressor import volterraRegressor
	pt, p, T, h = readPTh(pressureFile)
	t, (f, p, T, h) = alignSignals((t, f), (pt, p), (pt, T), (pt, h))
	t -= t[0]
	plt.plot(t, f - np.mean(f), label="laser frequency")
	plt.ylabel("frequency (MHz)")
	plt.xlabel("time (s)")
	ax1 = plt.gca()
	ax2 = ax1.twinx()
	ax2.plot(t, p, color='orange', label="room pressure")
	ax2.set_ylabel('Pressure (hPa)')

	vr = volterraRegressor(np.ones(1 if onlyPressure else 3, dtype=int))
	x = np.row_stack((p)) if onlyPressure else np.row_stack((p,T,h))
	x -= np.mean(x, axis=1)[:,None]
	y = f - np.mean(f)
	q, mse = vr.regrade(x, y, True)
	print(f"coefficients: {q}, mse: {mse}")
	if onlyPressure:
		ax1.plot(t, vr.estimate(x, q), c="red", label=f"pressure dependence (f={q[1]}*p)")
		ax1.plot(t, y - vr.estimate(x, q), c="black", label=f"pressure estimation error")
	else:
		ax1.plot(t, vr.estimate(x, q), c="red", label=f"estimated frequency (p+T+h)")
		ax1.plot(t, vr.estimate(x, q*np.array([1,1,0,0])), c="purple", label=f"pressure dependence (f={q[1]}*p)")
		ax1.plot(t, vr.estimate(x, q*np.array([1,0,1,0])), c="grey", label=f"temperature dependence (f={q[1]}*p)")
		ax1.plot(t, vr.estimate(x, q*np.array([1,0,0,1])), c="cyan", label=f"humidity dependence (f={q[1]}*p)")
		ax1.plot(t, y - vr.estimate(x, q*np.array([1,1,0,0])), c="black", label=f"pressure estimation error")
	ax1.legend()
	ax2.legend()
	plt.show()

for i in vv.iteration():
	t, f, error = saveRawFrequency(f"{computerStoragePath}{vv.savedCsvFileName}",vv.removingFunction)
	# plotFrequencyuWithError(t,f,error)
	plotFrequency_v_pTh(t, f, vv.pressureFile)
