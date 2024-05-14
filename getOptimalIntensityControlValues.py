import spectrumAnalyser as sa
from spectrumAnalyser import measure
import copy
import numpy as np

#get the open-loop and closed-loop measures
initialMaxControlLaserPower = 750e-6
openLoop = measure('C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 spectral noise, laserPower .400mW (high res).csv')
closedLoop = measure('C:/Users/lastline/Documents/at-4/Acquisitions/AT4v3 controlled spectral noise, laserPower .400mW (high res).csv')

#set the limits of the experiment laser noise
maxExperimentLaser_W = 6
minExperimentLaser_W = 0.2
minAttenuation = 0.3

#get H(f) and \eta_g(f) in the worst spot for our setup (200kHz)
#todo: can it be that the worst spot is not 200kHz?
minControlFilter = 1 - np.mean(closedLoop.tiaTensionV_sqrtHz()[-100:]/openLoop.tiaTensionV_sqrtHz()[-100:])
etag_min = np.sqrt(np.mean(openLoop.laserPowerRIN_1_Hz()[-100:]))

#calculation to obtain the minimum control power. Not gonna bother writing it better...
A = ((1-minControlFilter)*etag_min*minExperimentLaser_W)**2
B = measure.rho_shotNoise**2 * minExperimentLaser_W
C = minExperimentLaser_W * minControlFilter**2
D = etag_min**2 * minExperimentLaser_W**2 + measure.rho_shotNoise**2 * minExperimentLaser_W

minControlLaser_W = B*C/(minAttenuation*D-A-B)

#obtain the laser ratio and the max control laser
laserRatio = minExperimentLaser_W / minControlLaser_W
maxControlLaser_W = maxExperimentLaser_W / laserRatio
g1 = measure.stage1Saturation / (measure.photodiodeResponsivity * maxControlLaser_W)

#get the ADC noise
ADC = measure('C:/Users/lastline/Documents/at-4/Acquisitions/ADC+modified DAC (1V) noise .csv')
averageAdcNoise = np.mean(ADC.tiaTensionV_sqrtHz()) * 1.5 #just a small boost, so that we get roughly the max

g2 = averageAdcNoise / (measure.rho_shotNoise * np.sqrt(minControlLaser_W) * measure.photodiodeResponsivity * g1)

print(f"max control laser power: {maxControlLaser_W} W")
print(f"laser power ratio:       {laserRatio}")
print(f"tia first stage gain:    {g1} V/A")
print(f"tia second stage gain:   {g2} V/V")

l = [copy.deepcopy(openLoop), copy.deepcopy(closedLoop)]
for meas in l:
    w = meas.tiaTensionV_sqrtHz()
    w *= g2 / meas.g2
    meas.g2 = g2
    meas.g1 = g1
    meas.laserPower = maxControlLaser_W * meas.laserPower / initialMaxControlLaserPower
    meas.energy_e_foldingTime_s()
powers = [0.2, 0.5,1,3,6]
for experimentLaserPower in powers:
    l[0].changeLaserPower(experimentLaserPower / laserRatio)
    l[1].changeLaserPower(experimentLaserPower / laserRatio)
    l.append(measure.experimentLaserNoiseMeasure(l[0],l[1], experimentLaserPower))
    
l[0].changeLaserPower(powers[0])
l.remove(l[1])
names = ["initial experiment noise"] + [f"controlled experiment noise, laserPower {p}W" for p in powers]

measure.plotList(l,"dB",[("frequencies", "laserPowerRIN_dBc_Hz")], axisDimensions="dBc/Hz", 
                 paths=names)

for meas in l:
    meas.reduceFrequencyRange(10e3,200e3)

names = [n.replace("experiment noise", "expected e-folding time") for n in names]
names = [n.replace("controlled ", "") for n in names]

measure.plotList(l,"exp",["energy_e_foldingTime_s"], axisDimensions=["atom resonant frequency (Hz)", "e-folding time (s)"], 
                 paths=names)
