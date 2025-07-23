
import spectrumAnalyser as sa
import matplotlib.pyplot as plt

baseAmpl, prototype = False, True
open, closed = False, True
lowPower, HighPower, preAmpInLowPower = (0,1,2)

files = [
[200e3,	prototype,	closed,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/newAmp_closed loop_setpoint0.24_iutput.7.csv"],
# [200e3,	prototype,	closed,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/newAmp_closed loop_setpoint0.24_iutput.7_secondTake.csv"],
[200e3,	prototype,	open,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/newAmp_open loop_setpoint0.24_iutput.7.csv"],
[200e3,	prototype,	closed,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/newAmp_WattLevel_closed loop_setpoint0.24_iutput.7.csv"],
[200e3,	prototype,	open,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/newAmp_WattLevel_open loop_setpoint0.24_iutput.7.csv"],
[200e3,	baseAmpl,	closed,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_closed loop_setpoint0.24_output.7.csv"],
[200e3,	baseAmpl,	open,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_open loop_setpoint0.24_iutput.7.csv"],
[200e3,	baseAmpl,	closed,	preAmpInLowPower,	"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_preAmpInLowPower_closed loop_setpoint0.24_iutput.7.csv"],
[200e3,	baseAmpl,	open,	preAmpInLowPower,	"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_preAmpInLowPower_open loop_setpoint0.24_iutput.7.csv"],
[200e3,	baseAmpl,	closed,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_WattLevel_closed loop_setpoint0.24_iutput.7.csv"],
[200e3,	baseAmpl,	open,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_200kHz/std_WattLevel_open loop_setpoint0.24_iutput.7.csv"],
[1e6,	prototype,	closed,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_1MHz/newAmp_WattLevel_closed loop_setpoint0.24_iutput.7.csv"],
[1e6,	prototype,	open,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_1MHz/newAmp_WattLevel_open loop_setpoint0.24_iutput.7.csv"],
[1e6,	baseAmpl,	closed,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_1MHz/std_closed loop_setpoint0.24_iutput.7.csv"],
[1e6,	baseAmpl,	open,	lowPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_1MHz/std_open loop_setpoint0.24_iutput.7.csv"],
[1e6,	baseAmpl,	open,	HighPower,			"d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/test_1MHz/std_WattLevel_open loop_setpoint0.24_iutput.7.csv"],
]
def getFileNames(frequency, amplifier, isLoopClosed, powerLevel, returnPropertiest = False):
	elements = [frequency, amplifier, isLoopClosed, powerLevel]
	for i in range(len(elements)):
		if not isinstance(elements[i], list):
			elements[i] = [elements[i]]
	allNames = []
	allProperties = []
	for file in files:
		if file[0] in elements[0] and file[1] in elements[1] and file[2] in elements[2] and file[3] in elements[3]:
			allNames.append(file[4])
			allProperties.append(file[:4])
	if returnPropertiest:
		return allNames, allProperties
	return allNames

def plotFiles(frequency, amplifier, isLoopClosed, powerLevel, savePath = None, showPlot = True):
	allNames, allProperties = getFileNames(frequency, amplifier, isLoopClosed, powerLevel, returnPropertiest = True)
	X, Y, label = [], [], []
	for i in range(len(allNames)):
		x, y = sa.getSpectrumAnalysis_signalHound(allNames[i], outputImpedance_Ohm = 50)
		X.append(x)
		Y.append(y)
		# label.append(f"{allProperties[i][0]//1e3}kHz, {"prototype" if allProperties[i][1] else "baseAmpl"}, {'closed' if allProperties[i][2] else 'open'}, {'low' if allProperties[i][3] == lowPower else 'high'} power")
		label.append(f"{'prototype' if allProperties[i][1]==prototype else 'reference'}, {'closed' if allProperties[i][2]==closed else 'open'} loop, {'low' if allProperties[i][3] == lowPower else 'high'} power")
	
	sa.plotNSD(X,Y, paths = label, savePath= savePath, showPlot=showPlot)

if __name__ == "__main__":
	plotFiles(200e3, [prototype, baseAmpl], [open, closed], [lowPower], "d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/23_7_25 lowPower.png")
	
	plotFiles(200e3, [prototype, baseAmpl], [open, closed], [HighPower], "d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/23_7_25 HighPower.png")
	
	#zoom at 70MHz
	plotFiles(200e3, [prototype, baseAmpl], open, [lowPower, HighPower], showPlot=False)
	plt.xlim(67e3, 74e3)
	plt.savefig("d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/23_7_25 70kHz.png", dpi=300, bbox_inches='tight')
	plt.show()

	plotFiles(1e6, [prototype, baseAmpl], [open], [lowPower, HighPower], "d:/lastline/measuresOnIntensityStabilization_21_7_25/21_7_25/23_7_25 1MHz.png")

