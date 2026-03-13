import h5py
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from regressPressureAndBlueFreq import readPressure, alignSignals
from volterraRegressor import volterraRegressor

directory = "\\\\ARQUS-CAM/Experiments/ytterbium174/2026/03/10/C_Yb174_MOT_stability/shots"
savedCsvFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/allAtomDriftShotValues_10_3_26.csv"
pressureFile = "d:/lastline/scanCavityMeasurements/wavemeterAndPressure/Ruuvi Vexlum_20260311T144916+0100.csv"
files = glob.glob(os.path.join(directory, "*.h5"))
data = {
"indexes" : [],
"timings" : [],
"freq" : [],
"nOfAtoms" : [],
}
'''
for fpath in files:
    if "_0333_" in fpath:
        with h5py.File(fpath, "r") as h5:
            try:
                group = h5["results/MOT_in_situ"]
                globGroup = h5["globals"]
                data["nOfAtoms"].append(group.attrs["N_atoms"])
                data["indexes"].append(globGroup.attrs["spectroscopy_number"])
                data["freq"].append(globGroup.attrs["abs_imaging_freq"])
                dateTtime = h5.attrs["run time"]#format: YYYYMMDD"T"hhmmss.ffffff I couldn't format it directly, so let's convert it to a more manageable format
                normalFormatTime = f"{dateTtime[:2]}.{dateTtime[2:4]}.{dateTtime[4:6]} {dateTtime[7:9]}:{dateTtime[9:11]}:{dateTtime[11:]}"
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

# plt.plot(meanFit(atoms))
t = allTimes[0]
# t -= t[0]
mu, error = lorentzian_fit(xs, atoms)
pd.DataFrame({"t (s)" : t, "frequency (Hz)" : mu * 1e6}).to_csv(savedCsvFile.replace(".csv", "_raw.csv"), index=False)
# startingTime = t[0]
# t -= startingTime

# toKeep = error < 19999.4
# toKeep[139:210] = False
# toKeep[737:] = False
# mu = mu[toKeep]
# error = error[toKeep]
# totalT = t[-1] - t[0]
# dt = totalT / len(t)
# t = np.arange(np.sum(toKeep)) * dt
# t /= 3600
# # t=t[toKeep]
# # plt.plot(np.linspace(0,12,len(atoms[0])), mu, label=f"{count}-point Lorenzian fit")
# plt.errorbar(t, mu, yerr=error, fmt=".", label=f"{count}-point Lorenzian fit")
# # plt.plot(np.linspace(0,12,len(atoms[0])), meanFit(atoms), label="weighted-average fit")
# plt.xlabel("time (h)")
# plt.ylabel("Frequency drift (MHz)")
# plt.legend()
# plt.show()

pt, p = readPressure(pressureFile)
t, (mu, p) = alignSignals((t, mu), (pt, p))
t -= t[0]
plt.plot(t, mu, label="laser frequency")
plt.ylabel("frequency (MHz)")
plt.xlabel("time (s)")
# pt -= startingTime
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(t, p, color='orange', label="room pressure")
ax2.set_ylabel('Pressure (hPa)')

vr = volterraRegressor([1])
x = p[None,:]
# x -= np.mean(x)
y = mu# - np.mean(mu)
q, mse = vr.regrade(x, y, True)
print(f"coefficients: {q}, mse: {mse}")
# plt.plot(t, y, label="blue")
ax1.plot(t, vr.estimate(x, q), c="red", label=f"estimated frequency (f={q[1]}*p)")
ax1.legend()
ax2.legend()
plt.show()