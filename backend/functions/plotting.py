#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 10:54:49 2017

@author: luka
"""

import scipy.io
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal
b, a = signal.butter(4, 5.0*2.0*0.006)
d, c = signal.butter(4, 0.2*2.0*0.006)

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True


data = np.loadtxt('demo_plots/HRI_trial1_4.txt')
time = np.linspace(0,len(data)*0.005,len(data))


plt.close('all')

plt.figure(figsize=(10,9))

plt.figure(1)

ss = 0
st = len(data)
#st = 10*200

ax = plt.subplot(4,1,1)
ax.plot(time[ss:st],data[ss:st,0],'r',label='x')
ax.plot(time[ss:st],data[ss:st,1],'g',label='y')
ax.plot(time[ss:st],data[ss:st,2],'b',label='z')
plt.ylabel('reference position [m]')


ax = plt.subplot(4,1,2)
ax.plot(time[ss:st],data[ss:st,3],'r',label='x')
ax.plot(time[ss:st],data[ss:st,4],'g',label='y')
ax.plot(time[ss:st],data[ss:st,5],'b',label='z')
plt.ylabel('measured position [m]')


ax = plt.subplot(4,1,3)
ax.plot(time[ss:st],data[ss:st,6],'r',label='x')
ax.plot(time[ss:st],data[ss:st,7],'g',label='y')
ax.plot(time[ss:st],data[ss:st,8],'b',label='z')
plt.ylabel('interaction force [N]')
plt.ylim([-10,10])


ax = plt.subplot(4,1,4)
ax.plot(time[ss:st],data[ss:st,9],'r',label='x')
ax.plot(time[ss:st],data[ss:st,13],'g',label='y')
ax.plot(time[ss:st],data[ss:st,17],'b',label='z')
plt.ylabel('stiffness [N/m]')


plt.xlabel('time [s]')

#plt.ylabel(r'$\tau$ [Nm]')

plt.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)

plt.show()


