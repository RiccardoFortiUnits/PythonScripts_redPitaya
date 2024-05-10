# -*- coding: utf-8 -*-
"""
Created on Sat May  4 11:09:34 2024

@author: lastline
"""
import numpy as np
import spectrumAnalyser as sa

print_1_minus_H = True

ng = 2e-7
ps = 8.64e-10
ng = ng ** 2
ps = ps ** 2
Pe = .0004 * 100
initialNoise = ng*Pe**2+ps*Pe
idealNoise = ps*Pe

if print_1_minus_H:
    H = np.linspace(0,0.999,1000)
else:
    H = np.linspace(0,1,1000)
X=[]
Y=[]
Names = []
for Pc in (list(Pe / np.array([10,100,1000,10000,100000])) + [0]):
    if(Pc != 0):
        Se = ng * Pe**2 * (1 - H)**2 + ps * Pe * (1 + Pe / Pc * H**2)
        Names.append(f"Pe : Pc = {Pe / Pc : .0f}")
    else:
        Se = ng * Pe**2 * (1 - H)**2 + ps * Pe
        Names.append("Pe : Pc = 0")
        
    if print_1_minus_H:
        X.append(1-H)
    else:
        X.append(H)
    Y.append(10*np.log10(2*Se / Pe**2))
    
X.append([0,1])
Y.append([10*np.log10(2*initialNoise / Pe**2)]*2)
Names.append("generator + shot noise")
X.append([0,1])
Y.append([10*np.log10(2*idealNoise / Pe**2)]*2)
Names.append("shot noise")

if print_1_minus_H:
    sa.plotNSD(X,Y,legendPosition="center right", paths=Names, axisDimensions=['1 - H(f)','dBc/Hz'], linearX=False, linearY=True)#, linearX=True)
else:
    sa.plotNSD(X,Y,legendPosition="center left", paths=Names, axisDimensions=['H(f)','dBc/Hz'], linearX=True, linearY=True)#, linearX=True)