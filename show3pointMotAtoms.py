import h5py
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

directory = "G:/atom drift shots/"

files = glob.glob(os.path.join(directory, "*.h5"))
data = {
"indexes" : [],
"timings" : [],
"nOfAtoms" : [],
}
'''
for fpath in files:
    with h5py.File(fpath, "r") as h5:
        try:
            group = h5["results/MOT_in_situ"]
            data["nOfAtoms"].append(group.attrs["N_atoms"])
            data["indexes"].append(h5.attrs["run number"])
            data["timings"].append(float(h5.attrs["run time"].split("T")[1]))
        except:
            print(f"couldn't open {fpath}")

with h5py.File("d:/lastline/scanCavityMeasurements/wavemeterAndPressure/allAtomDriftShotValues.h5", "w") as h5:
    grp = h5.create_group("shots")
    for key, value in data.items():
        grp.attrs[key] = value
#'''

with h5py.File("d:/lastline/scanCavityMeasurements/wavemeterAndPressure/allAtomDriftShotValues.h5", "r") as h5:
    data = {
    "indexes" : h5["shots"].attrs["indexes"],
    "timings" : h5["shots"].attrs["timings"],
    "nOfAtoms" : h5["shots"].attrs["nOfAtoms"],
    }
atoms = []
allTimes = []
xs = np.array([252, 240, 228])

for j in range(3):
    nAtoms = np.array([data["nOfAtoms"][i] for i in range(len(data["indexes"])) if data["indexes"][i] == j])
    times = np.array([data["timings"][i] for i in range(len(data["indexes"])) if data["indexes"][i] == j], dtype=float)
    sort = np.argsort(times)
    nAtoms = nAtoms[sort]
    times = times[sort]
    allTimes.append(times)
    atoms.append(nAtoms)
    plt.plot(nAtoms, label=f"absorption imaging freq: {xs[j]}")
plt.legend()
plt.show()
atoms = np.array(atoms)
allTimes = np.array(allTimes)


def meanFit(y):
    global xs
    return xs[1] + (y[-1] - y[0]) * (xs[-1] - xs[0]) / y[1]

def gaussian_from_three_points(y):
    """
    points: list of three (x, y) pairs, with y > 0
    returns: A (height), x0 (center), sigma (width)
    """

    # log of y
    L = np.log(y)

    # Fit quadratic: L = B + C x + D x^2
    # polyfit returns [D, C, B]
    D, C, B = np.polyfit(xs, L, 2)

    # Recover Gaussian parameters
    sigma = np.sqrt(-1.0 / (2.0 * D))
    x0 = -C / (2.0 * D)
    A = np.exp(B - D * x0**2)

    return x0
    
# plt.plot(meanFit(atoms))
plt.plot(np.linspace(0,2.7,len(atoms[0])), gaussian_from_three_points(atoms), label="3-point gaussian fit")
plt.xlabel("time (h)")
plt.ylabel("Frequency drift (MHz)")
plt.legend()
plt.show()



