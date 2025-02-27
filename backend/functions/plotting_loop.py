#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Batch plot generation for multiple HRI trial files.

@author: luka
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal

# Set up font rendering
matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True

# Loop through file numbers 1 to 3
for i in range(1, 6):
    filename = f'demo_plots/HRI_trial1_{i}.txt'
    savefile = f'demo_plots/HRI_trial1_{i}.png'
    
    # Load data
    data = np.loadtxt(filename)
    time = np.linspace(0, len(data) * 0.005, len(data))

    plt.close('all')
    plt.figure(figsize=(10, 9))

    ss = 0
    st = len(data)

    ax = plt.subplot(4, 1, 1)
    ax.plot(time[ss:st], data[ss:st, 0], 'r', label='x-axis')
    ax.plot(time[ss:st], data[ss:st, 1], 'g', label='y-axis')
    ax.plot(time[ss:st], data[ss:st, 2], 'b', label='z-axis')
    plt.ylabel('Reference Position [m]')
    plt.legend(loc="upper right")

    ax = plt.subplot(4, 1, 2)
    ax.plot(time[ss:st], data[ss:st, 3], 'r', label='x-axis')
    ax.plot(time[ss:st], data[ss:st, 4], 'g', label='y-axis')
    ax.plot(time[ss:st], data[ss:st, 5], 'b', label='z-axis')
    plt.ylabel('Measured Position [m]')
    plt.legend(loc="upper right")

    ax = plt.subplot(4, 1, 3)
    ax.plot(time[ss:st], data[ss:st, 6], 'r', label='x-axis')
    ax.plot(time[ss:st], data[ss:st, 7], 'g', label='y-axis')
    ax.plot(time[ss:st], data[ss:st, 8], 'b', label='z-axis')
    plt.ylabel('Interaction Force [N]')
    plt.ylim([-10, 10])
    plt.legend(loc="upper right")

    ax = plt.subplot(4, 1, 4)
    ax.plot(time[ss:st], data[ss:st, 9], 'r', label='x-axis')
    ax.plot(time[ss:st], data[ss:st, 13], 'g', label='y-axis')
    ax.plot(time[ss:st], data[ss:st, 17], 'b', label='z-axis')
    plt.ylabel('Stiffness [N/m]')
    plt.legend(loc="upper right")

    plt.xlabel('Time [s]')
    plt.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)

    # Save plot as PNG
    plt.savefig(savefile, format="png", bbox_inches="tight", dpi=300)
    print(f"Saved plot: {savefile}")

    # Close figure to free memory
    plt.close()
