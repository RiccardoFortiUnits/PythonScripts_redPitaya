import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as cnst
from volterraRegressor import volterraRegressor
import pandas as pd
from datetime import datetime
c = cnst.c


def read_lta(filepath, returnTimeExtremes = False):
    """
    Robust reader for FreeSurfer .lta files.
    Extracts the first 4x4 numeric transformation matrix found.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    if returnTimeExtremes:
        startTime = lines[5].split('\t')[1].removesuffix("\n")
        EndTime = lines[6].split('\t')[1].removesuffix("\n")
        startTime = datetime.strptime(startTime, "%d.%m.%Y, %H:%M:%S.%f").timestamp()
        EndTime = datetime.strptime(EndTime, "%d.%m.%Y, %H:%M:%S.%f").timestamp()

    lines = lines[56:]
    col1, col2 = [], []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                col1.append(float(parts[0]))
                col2.append(float(parts[1]))
            except ValueError:
                continue  # skip non-numeric lines

    if returnTimeExtremes:
        return np.array(col1), np.array(col2), startTime, EndTime
    return np.array(col1), np.array(col2)

''' 28/2/26, acquisition without pressure compensator, to see the correlation between pressure drifts and frequency
lta_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/27.02.2026, 09.52_night_bluelock.lta"
pressure_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/Ruuvi VEXLUM_20260227T102451+0100.csv"
timeRange = (8.5e3, 3.6e4)
#'''

''' 2/3/26 ovenight acquisition with conversion coefficient calculated in the previous acquisition (about -4MHz/hPa). The drift is still quite visible...
lta_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/03.03.2026, 09.42,  539.390307 THz.lta"
pressure_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/Ruuvi Vexlum_20260303T095456+0100.csv"
timeRange = (0, 2.6e4)
#'''

''' 3/3/26 small acquisition with doubled coefficient (to respect to the previous one). Maybe we're just compensating on the wrong direction, so we're actually worsening the drift
lta_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/03.03.2026, 12.52,  539.390306 THz.lta"
pressure_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/Ruuvi Vexlum_20260303T125414+0100.csv"
timeRange = (0, 2.6e4)
#'''

# ''' 3/3/26 longer acquisition with the compensation coefficient reversed
lta_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/03.03.2026, 18.08,  539.390304 THz - MOT blue drift.lta"
pressure_path = "D:/lastline/scanCavityMeasurements/wavemeterAndPressure/Ruuvi Vexlum_20260303T181012+0100.csv"
timeRange = (0, 1e4)
#'''

#get timings and frequencies from the wavemeter acquisitions
times, freqs, fst, fet = read_lta(lta_path, True)
times -= times[0]
freqs = np.asarray(freqs)
N = 300
blueFreqRanges = [397.91118, 399.911195]
indexes_green = np.arange(len(freqs))[freqs>450]
indexes_blue = np.arange(len(freqs))[(freqs<blueFreqRanges[1]) & (freqs>blueFreqRanges[0])]

times_green = times[indexes_green]*1e-3
freqs_green = c/freqs[indexes_green] * 1e9# in 
indexes_green = np.logical_and(times_green > timeRange[0],
                                                times_green < timeRange[1])
times_green = times_green[indexes_green]
freqs_green = freqs_green[indexes_green] # in 

times_blue = times[indexes_blue]*1e-3 # in s
freqs_blue = c/freqs[indexes_blue] * 1e9
indexes_blue = np.logical_and(times_blue > timeRange[0],
                                                times_blue < timeRange[1])
times_blue = times_blue[indexes_blue]
freqs_blue = freqs_blue[indexes_blue]

#frequencies filtered, since they are constantly jumping
green_avg = freqs_green.mean()
moving_avg_green = np.convolve(freqs_green, np.ones(N)/N, mode='valid')
times_green = times_green[:len(moving_avg_green)]
blue_avg = freqs_blue.mean()
moving_avg_blue = np.convolve(freqs_blue, np.ones(N)/N, mode='valid')
times_blue = times_blue[:len(moving_avg_blue)]

#read data from the pressure signal
df = pd.read_csv(pressure_path)

times_pressure = np.zeros(len(df["Date"]))
for i in range(len(times_pressure)):
    dt = datetime.strptime(df["Date"][i], "%Y-%m-%d %H:%M:%S")
    times_pressure[i] = dt.timestamp()

if "Pressure (hPa)" in df.columns:
    pressure = df["Pressure (hPa)"].to_numpy()
else:
    pressure = df["Air pressure (hPa)"].to_numpy()
startingpressureTimeIndex = np.searchsorted(times_pressure, fst)
times_pressure -= times_pressure[startingpressureTimeIndex]

indexes_pressure = np.logical_and(times_pressure > timeRange[0],
                                                times_pressure < timeRange[1])
times_pressure = times_pressure[indexes_pressure]
pressure = pressure[indexes_pressure]

moving_avg_green -= green_avg
moving_avg_blue -= blue_avg
pressure -= np.mean(pressure)

moving_avg_green /= 1e6
moving_avg_blue /= 1e6

#'''
#show the raw data
plt.plot(times_blue / 3600, moving_avg_blue, c='blue', label='blue')
plt.plot(times_green / 3600, moving_avg_green, c='green', label='green')
plt.plot(times_pressure / 3600, pressure, c='orange', label='pressure')
plt.xlabel("time (h)")
plt.ylabel("frequency variation (MHz), or pressure (hPa)")
plt.legend()
plt.show()
#'''

t = times_pressure
green = np.interp(t, times_green, moving_avg_green)
blue = np.interp(t, times_blue, moving_avg_blue)

t /= 3600

#fit the blue curve with the green and pressure curves. It can be a non-linear fit too
vr = volterraRegressor([1,1])
x = np.column_stack((pressure, green)).T
q, mse = vr.regrade(x, blue, True)
print(f"coefficients: {q}, mse: {mse}")
plt.plot(t, blue, label="blue")
plt.plot(t, vr.estimate(x, q), label="estimated (green + pressure)", c="red")
plt.plot(t, vr.estimate(np.column_stack((np.ones_like(pressure) * np.mean(pressure), green)).T, q), label="estimated (green only)", c="green")
plt.plot(t, vr.estimate(np.column_stack((pressure, np.ones_like(pressure) * np.mean(green))).T, q), label="estimated (pressure only)", c="orange")

plt.xlabel("time (h)")
plt.ylabel("frequency variation (MHz)")
plt.legend()
plt.show()