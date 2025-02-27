#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Batch plot generation for a single HRI trial file (HRI_trial1_3.txt),
saving as a vectorized PDF with correct minus signs.

@author: luka
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['axes.unicode_minus'] = False

# File to process
filename = 'demo_plots/HRI_trial1_3.txt'
#savefile = 'demo_plots/HRI_trial1_3.pdf'  # Save as PDF now
savefile = 'demo_plots/HRI_trial1_3.svg'  # Save as SVG now

# Load data
data = np.loadtxt(filename)
time = np.linspace(0, len(data) * 0.005, len(data))

# Time range selection
time_start = 15  
time_end = 100    
mask = (time >= time_start) & (time <= time_end)

plt.close('all')
plt.figure(figsize=(10, 9))  # Keep same figure size

# layout
ticksize = 14  # Font size for ticks

# Subplot 1: Reference Position
ax = plt.subplot(4, 1, 1)
ax.plot(time[mask], data[mask, 0], 'r', label='x-axis')
ax.plot(time[mask], data[mask, 1], 'g', label='y-axis')
ax.plot(time[mask], data[mask, 2], 'b', label='z-axis')
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)
plt.xlim([time_start, time_end])
plt.ylabel('Ref. Position [m]', fontsize=ticksize)
# plt.legend(loc="center right")  # Legend in middle right

# Subplot 2: Measured Position
ax = plt.subplot(4, 1, 2)
ax.plot(time[mask], data[mask, 3], 'r', label='x-axis')
ax.plot(time[mask], data[mask, 4], 'g', label='y-axis')
ax.plot(time[mask], data[mask, 5], 'b', label='z-axis')
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)
plt.xlim([time_start, time_end])
plt.ylabel('Meas. Position [m]',fontsize=ticksize)
plt.legend(loc="center", fontsize=ticksize, bbox_to_anchor=(0.5, 0.45))

# Subplot 3: Interaction Force
ax = plt.subplot(4, 1, 3)
ax.plot(time[mask], data[mask, 6], 'r', label='x-axis')
ax.plot(time[mask], data[mask, 7], 'g', label='y-axis')
ax.plot(time[mask], data[mask, 8], 'b', label='z-axis')
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)
plt.ylabel('Interaction Force [N]', fontsize=ticksize)
plt.ylim([-10, 10])
plt.xlim([time_start, time_end])
# plt.legend(loc="lower right")  # Legend at bottom right
# plt.legend.fontsize = 30  # Reduce legend font size

# Subplot 4: Stiffness
ax = plt.subplot(4, 1, 4)
ax.plot(time[mask], data[mask, 9], 'r', label='x-axis')
ax.plot(time[mask], data[mask, 13], 'g', label='y-axis')
ax.plot(time[mask], data[mask, 17], 'b', label='z-axis')
plt.xticks(fontsize=ticksize)
plt.yticks(fontsize=ticksize)
plt.xlim([time_start, time_end])
plt.ylabel('Stiffness [N/m]', fontsize=ticksize)
# plt.legend(loc="upper right")  # Legend remains at top right

plt.xlabel('Time [s]', fontsize=ticksize)
plt.tight_layout()

# Save plot as PDF (vectorized format)
plt.savefig(savefile, format="svg", bbox_inches="tight")
print(f"Saved plot: {savefile}")

# Close figure to free memory
plt.close()
