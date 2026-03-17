import h5py
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

directory = "\\\\ARQUS-CAM/Experiments/ytterbium174/2026/03/14/B_Yb174_MOT_stability/shots"
experimentNumber = "_0002_"
savedCsvFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/allAtomDriftShotValues_16_3_26.csv"
pressureFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/RuuviTag 171A_20260317T090345+0100.csv"
files = glob.glob(os.path.join(directory, "*.h5"))
data = {
"indexes" : [],
"timings" : [],
"freq" : [],
"nOfAtoms" : [],
}
'''
for fpath in files:
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
df.to_csv(savedCsvFile, index=False)

#'''

def time_to_seconds(time_str):
    
    """Convert time format HHMMSS.ms to seconds since 00:00"""
    time_str = str(float(time_str)).zfill(13)  # Ensure the string has the correct format
    hours = int(time_str[0:2])
    minutes = int(time_str[2:4])
    seconds = float(time_str[4:])
    if hours < 12:
        hours += 24
    return hours * 3600 + minutes * 60 + seconds

data = pd.read_csv(savedCsvFile)
mtime = os.path.getmtime(savedCsvFile)
if datetime.fromtimestamp(mtime) > datetime(2026, 3, 12):
    data["timings"] = data["timings"]
else:
    addedTime = datetime(2026, 3, 10).timestamp()
    data["timings"] = [addedTime + time_to_seconds(data["timings"][i]) for i in range(len(data["timings"]))]
    
usedIndexes,count=np.unique(data["indexes"], return_counts=True)
# usedIndexes = usedIndexes[:-1]
count = count[0]


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
#     plt.plot(nAtoms, label=f"absorption imaging freq: {xs[j]}")
# plt.legend()
# plt.show()
atoms = np.array(atoms)


def meanFit(y):
    global xs
    return np.sum(xs[:,None]*y, axis=0) / np.sum(y, axis=0)


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
            if i==535:
                pass
            popt, _ = curve_fit(lorentzian, xs, y[:,i], p0=[mu_init[i], gamma_init[i], amplitude_init[i], offset_init[i]])
            error[i] = (np.diag(_)**.5)[0]
            outs[i,:] = popt
        except:
            pass
    return outs[:,0], error
def normalize01(x):
    return (x-x.min()) / (x.max() - x.min())
    
# plt.plot(meanFit(atoms))
t = allTimes[0]
# t -= t[0]
mu, error = lorentzian_fit(xs, atoms)
pd.DataFrame({"t (s)" : t, "frequency (Hz)" : mu * 1e6}).to_csv(savedCsvFile.replace(".csv", "_raw.csv"), index=False)
# # startingTime = t[0]
# # t -= startingTime

toKeep = np.logical_and(error < .4, np.logical_and(mu < 265, mu > 235))
# toKeep[139:210] = False
# toKeep[737:] = False
mu = mu[toKeep]
error = error[toKeep]
t=t[toKeep]
# mu=mu[t-t[0]<1.92*3600]
# error=error[t-t[0]<1.92*3600]
# t=t[t-t[0]<1.92*3600]
# plt.plot(np.linspace(0,12,len(atoms[0])), mu, label=f"{count}-point Lorenzian fit")
plt.errorbar(t / 3600, mu, yerr=error, fmt=".", label=f"{count}-point Lorenzian fit")
# plt.plot(np.linspace(0,12,len(atoms[0])), meanFit(atoms), label="weighted-average fit")
plt.xlabel("time (h)")
plt.ylabel("Frequency drift (MHz)")
plt.legend()
plt.show()

from regressPressureAndBlueFreq import readPressure, alignSignals, readPTh
from volterraRegressor import volterraRegressor
pt, p, T, h = readPTh(pressureFile)
t, (mu, p, T, h) = alignSignals((t, mu), (pt, p), (pt, T), (pt, h))
t -= t[0]
plt.plot(t, mu - np.mean(mu), label="laser frequency")
# plt.plot(t, normalize01(mu - np.mean(mu)), label="laser frequency")
# plt.plot(t, normalize01(p - np.mean(p)), label="p")
# plt.plot(t, normalize01(T - np.mean(T)), label="T")
# plt.plot(t, normalize01(h - np.mean(h)), label="h")
plt.ylabel("frequency (MHz)")
plt.xlabel("time (s)")
# pt -= startingTime
ax1 = plt.gca()
# ax2 = ax1.twinx()
# ax2.plot(t, p, color='orange', label="room pressure")
# ax2.set_ylabel('Pressure (hPa)')

vr = volterraRegressor([1,1,1])
x = np.column_stack((p, T, h)).T
x -= np.mean(x, axis=1)[:,None]
y = mu - np.mean(mu)
q, mse = vr.regrade(x, y, True)
print(f"coefficients: {q}, mse: {mse}")
# plt.plot(t, y, label="blue")
ax1.plot(t, vr.estimate(x, q), c="red", label=f"estimated frequency (p+T+h)")
ax1.plot(t, vr.estimate(x, q*np.array([1,1,0,0])), c="orange", label=f"pressure dependence (f={q[1]}*p)")
ax1.plot(t, vr.estimate(x, q*np.array([1,0,1,0])), c="grey", label=f"temperature dependence (f={q[2]}*T)")
ax1.plot(t, vr.estimate(x, q*np.array([1,0,0,1])), c="cyan", label=f"humidity dependence (f={q[3]}*h)")


# ax1.plot(t, y - vr.estimate(x, q*np.array([1,1,0,0])), c="black", label=f"error")

ax1.legend()
# ax2.legend()
plt.show()