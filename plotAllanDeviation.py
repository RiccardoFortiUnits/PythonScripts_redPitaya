# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 13:30:59 2024

@author: lastline
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 10:18:52 2024

@author: lastline
"""

import matplotlib.pyplot as plt
import allan_variance
import lecroyInterface

(x,y)=lecroyInterface.getDataFromMultimeterLogFile("C:/Users/lastline/Documents/at-4/Acquisitions/Allan deviations/PWM_1.8V.log")

dt = x[1]-x[0]
#remove the first 20 minutes, in which the redPitaya is heating up
# y=y[int(20*60/dt):]

plt.figure()
plt.plot(x, y)
plt.xlabel("time, s")
plt.ylabel("Voltage, V")

tau, avar = allan_variance.compute_avar(y, dt)
plt.figure()
plt.loglog(tau, avar, '.')
plt.xlabel("Averaging time, s")
plt.ylabel("AVAR")

params, avar_pred = allan_variance.estimate_parameters(tau, avar)
params

plt.loglog(tau, avar, '.', label='Computed variance')
def remove_last_line(input_string):
    all_lines = input_string.split('\n')
    all_lines_except_last = all_lines[:-1]
    result_string = '\n'.join(all_lines_except_last)    
    return result_string

strParams = str(params)
plt.loglog(tau, avar_pred, label='Modeled with estimated parameters:\n'+remove_last_line(strParams))
plt.legend()
plt.xlabel("Averaging time, s")
plt.ylabel("AVAR")