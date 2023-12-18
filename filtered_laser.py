import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, freqz
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline

def dBm_to_V_sqrtHz(y, inputImpedance_Ohm = 50, outputImpedance_Ohm = 50):
    return np.sqrt(10**(y / 10)* 0.001 * inputImpedance_Ohm) * (outputImpedance_Ohm + inputImpedance_Ohm) / inputImpedance_Ohm
        
        
def getSpectrumAnalysis_signalHound(path, isDataIndB = True, outputImpedance_Ohm = 50,attenuation =0):
    
    data = pd.read_csv(path, low_memory=False, header= None)
    array = data.to_numpy()
    binBand = array[1,0] - array[0,0]
    # print(binBand)
    # pg = 10*np.log10(len(array[:,0]))
    # print(binBand)
    # print("pg: " + str(pg) + "  | " + str(len(array[:,0])))    
    
    if isDataIndB:
        #divide by 2 (remove the voltage divider done by the SH) and multiply by the bin bandwidth, so that the output is normalized in frequency
        return array[:,0], dBm_to_V_sqrtHz(array[:,1]+ np.ones(len(array))*attenuation, outputImpedance_Ohm = outputImpedance_Ohm)  * (1/np.sqrt(binBand)) 
    

gain=5600
amp_gain = 200
prev_gain = 5600
data = pd.read_csv('merged_laser2.csv', low_memory=False, sep = ',', header = None)
array = data.to_numpy()

x, y = getSpectrumAnalysis_signalHound('rpFloor.csv',outputImpedance_Ohm=50)

# Creazione di una sinusoide nel dominio della frequenza
fs = 400e3  # Frequenza di campionamento



fft_values = array[:,1]

# Correzione della frequenza di taglio
cutoff_frequency = 5000  # Frequenza di taglio del filtro passa-alto
normalized_cutoff = cutoff_frequency / ( fs)

# Creazione del filtro passa-alto del primo ordine
b, a = butter(1, Wn=normalized_cutoff, btype='high', analog=False)

# Calcolo della risposta in frequenza del filtro passa-alto
w, h = freqz(b, a, worN=539266)

# Applicazione del filtro nel dominio della frequenza
filtered_fft = fft_values * h

# Plot del segnale originale, della risposta in frequenza del filtro e del segnale filtrato
plt.figure(figsize=(12, 20))

# plt.subplot(3, 1, 1)
# plt.plot(array[:,0], fft_values)
# plt.title('Segnale originale')
# plt.xlim([1,fs/2])
# plt.xscale('log')
# plt.yscale('log')

# plt.subplot(3, 1, 2)
# plt.plot(w, np.abs(h))
# plt.title('Risposta in frequenza del filtro passa-alto')

# plt.subplot(3, 1, 3)
plt.plot(array[:,0], np.real(filtered_fft)*(gain*amp_gain)/prev_gain)
plt.plot(x, np.real(y))
plt.title('Segnale filtrato')
plt.xlim([1,200e3])
plt.xscale('log')
plt.yscale('log')
for i in range(int(10e3),int(200e3),int(10e3)):
    plt.axvline(x=i, color ='black')

plt.tight_layout()
plt.show()

signal_int = InterpolatedUnivariateSpline(array[:,0],array[:,1], k=1)
floor_int = InterpolatedUnivariateSpline(x, y, k=1)
sum_int = InterpolatedUnivariateSpline(array[:,0],signal_int(array[:,0])**2+floor_int(array[:,0])**2)
vrms = np.sqrt((sum_int).integral(1, 200e3))
print('Vrms: ' + str(vrms))
