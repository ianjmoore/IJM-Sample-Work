#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 7 21:12:15 2019

@author: ijmoore
"""
"""
            ### Pole Plant - Pole Off Algorithm ###
    Locates timestamp & maximum acceleration of Pole Plant & Pole Off events 
        for overground Nordic Roller Skiing for double polling technique
        
"""
#%%  Importing relevant libraries
import pywt #Importing py wavelets
import numpy as np  #common numerical manipulation and vector math library
import h5py  #library for reading h5 files
import pylab as pl #plotting
import matplotlib.pyplot as plt #plotting
import scipy as scipy #scientific python
from scipy import signal #signal library
from scipy.signal import find_peaks  #peak finder
#%%     
def ImportH5(file, sensor_to_import=None):
    """
    Import APDM data from a H5 file.  Automatically imports time, accelerometer, 
    gyroscope and magnetometer data.

    Parameters
    ----------
    file : str
        File to import.
    sensor_to_import : {None, str}, optional
        Name of the sensor to import (number identification), or None, which imports all the sensors. Default is None.
    """
    
    if sensor_to_import is None:
        data = dict() # creating a dictionary for data storage 
    else:
        #i:what to put in dict, Creates a dictionary with an entry of None
        data = {i:None for i in ['t', 'acc', 'gyr','mag']}
    
    f = h5py.File(file, 'r')  # read H5 file
    
    # iterate through the sensors stored in the file
    for sens in f['Sensors'].keys():
        if sensor_to_import is None:
            data[sens] = {i:None for i in ['t', 'acc', 'gyr','mag']}
            
            # initialize storage for reading directly into later
            data[sens]['t'] = np.zeros(f['Sensors'][sens]['Time'].shape)
            data[sens]['acc'] = np.zeros(f['Sensors'][sens]['Accelerometer'].shape)
            data[sens]['gyr'] = np.zeros(f['Sensors'][sens]['Gyroscope'].shape)
            data[sens]['mag'] = np.zeros(f['Sensors'][sens]['Magnetometer'].shape)


            # read directly from H5 file into the body structure
            f['Sensors'][sens]['Time'].read_direct(data[sens]['t'])
            f['Sensors'][sens]['Accelerometer'].read_direct(data[sens]['acc'])
            f['Sensors'][sens]['Gyroscope'].read_direct(data[sens]['gyr'])
            f['Sensors'][sens]['Magnetometer'].read_direct(data[sens]['mag'])


            data[sens]['t'] = (data[sens]['t'] - data[sens]['t'][0])/1e6 
        else:
            if sens == sensor_to_import:
                # initialize storage for reading directly into later
                data['t'] = np.zeros(f['Sensors'][sens]['Time'].shape)
                data['acc'] = np.zeros(f['Sensors'][sens]['Accelerometer'].shape)
                data['gyr'] = np.zeros(f['Sensors'][sens]['Gyroscope'].shape)
                data['mag'] = np.zeros(f['Sensors'][sens]['Magnetometer'].shape)

                # read directly from H5 file into the body structure
                f['Sensors'][sens]['Time'].read_direct(data['t'])
                f['Sensors'][sens]['Accelerometer'].read_direct(data['acc'])
                f['Sensors'][sens]['Gyroscope'].read_direct(data['gyr'])
                f['Sensors'][sens]['Magnetometer'].read_direct(data['mag'])
                
                data['t'] = (data['t'] - data['t'][0])/1e6 
    
    return data
#%% Making a list corresponding to the names of the trials
trial_name = ["Skier 1 DP Slow Trial 1","Skier 1 DP Slow Trial 2",
              "Skier 1 DP Medium Trial 1","Skier 1 DP Medium Trial 2",
              "Skier 1 DP Fast Trial 1","Skier 1 DP Fast Trial 2",
              "Skier 2 DP Slow Trial 1","Skier 2 DP Slow Trial 2",
              "Skier 2 DP Medium Trial 1","Skier 2 DP Medium Trial 2",
              "Skier 2 DP Fast Trial 1","Skier 2 DP Fast Trial 2",
              "Skier 3 DP Slow Trial 1","Skier 3 DP Slow Trial 2",
              "Skier 3 DP Medium Trial 1","Skier 3 DP Medium Trial 2",
              "Skier 3 DP Fast Trial 1","Skier 3 DP Fast Trial 2"]
#%%             
"""                #       Windowing Algorithm       #
    1.  Computes "fbsp" continuous wavelet transformation "cwtmatr" of raw acc 
            signal (ln 129)
    2.  Finds peaks of wavelet signal using scipy.find_peaks(cwtmatr) & stores 
            in arrays w_peaks & n_w_peaks respectively (ln 132 & 133)
    3.  Plots this cwt contour plot and pos wavelet peaks (w_peaks) & neg 
            wavelet peaks (n_w_peaks) (ln 135-141)
    4.  Plots raw acc signal on same figure (ln 137)
    5.  Indexes into cwtmatr at each pos peak, generates index slice at each 
            peak (ln 145-149) 
    6.  Finds peak for that index slice of raw signal using scipy.find_peaks, 
            stores in r_peaks (ln 150)
    7.  Correlates that peak to its index in complete raw signal (acc_trial) 
            (not just slice) (ln 151)
    8.  Adds the pos peak (w_peaks) to same figure (ln 153)
    9.  Completes steps 5-8 for neg peaks (ln 156-167)
    10. Adds labels and legend (ln 169-173)

"""     
plt.close("all")
wname = str("fbsp")#frequency-b spline wavelet 
scale = int(61)  #dilates or compresses the wavelet signal 
width = np.arange(1, 63)#setting desired width using arange: returns evenly spaced values w/in given range
# Using a for loop to step through & plot cwt of all 18 trials
for i in range(1,19):
    trial_file = "/Users/ijmoore/Desktop/UVMSenior/UVMSpring19/"\
    +"McGinnis_Internship/Skiing_Study/CWT_for_loop/"\
    +str(i)+".h5"
    trial = ImportH5(trial_file, sensor_to_import='3498')#importing trial (dict)
    #assigning variable names to Time, Acceleration & Gyro arrays for Skier DP Speed & Trial
    t_trial   = trial['t']#assigning 't' key to array, t_trial
    acc_trial = trial['acc']#assigning 'acc' key to array, acc_trial (acceleration)
#    gyr_trial = trial['gyr']
    plt.figure() #prepping the figure 
    acc_trial = acc_trial[:, 0]#assigning acc_trial to x direc only, vertically aligned with the pole 
    #x column (0th indicie) of acc_trial assigning this column to cwtmatr & performing cwt on x dir of acc_trial
    cwtmatr, _ = pywt.cwt(acc_trial, width, wname)#takes additional argument of scales (orange fbsp signal)
    N = len(t_trial)
    T = int(1/np.mean(np.diff(t_trial)) - (1/(1.5*np.mean(np.diff(t_trial)))))#Period function (in prototype phase)
    w_peaks, w_props = scipy.signal.find_peaks(cwtmatr[scale, :], distance=70, prominence=65)#w_peaks := x index of (pos) wavelet peaks of cwtmatr
    n_w_peaks, n_w_props = scipy.signal.find_peaks(-cwtmatr[scale, :], distance=80, prominence=75)#n_w_peaks := x index of (neg) wavelet peaks of cwtmatr
        ## Plotting CWT contour plot and peaks
    plt.contourf(cwtmatr, cmap='binary')#contourf is filled contours (grey background plot)
    axx = pl.gca().twinx()#Create a twin axes sharing the x-axis
    axx.plot(acc_trial, label="acc: x-axis")#plot the original signal 
    axx.plot(cwtmatr[scale, :], label="cwt, scale =%i" % scale)#plots the wavelet signal
    len_t_trial = np.arange(len(t_trial))# spacing the y points for the corresponding sample (x i.e. t) values
    axx.plot(len_t_trial[w_peaks], cwtmatr[scale, w_peaks], 'y*', label="CWT Pole Plant")#plotting positive wavelet peaks (maxima) 
    axx.plot(len_t_trial[n_w_peaks], cwtmatr[scale, n_w_peaks], 'r*', label="CWT Pole Off")#plotting negative wavelet peaks (minima) 
    
        ## Pole Plant Index Slice function ##
    #for loop to index and slice at every pos peak slice
    for j in range(0,len(w_peaks)):#determines number of steps in for loop based on number of peaks in w_peaks
        slice_ind = (w_peaks[j])#assigns the index of current iteration to slice_ind
        slice_begin = slice_ind-10 #setting -x lim  for slice 
        slice_end = slice_ind+25 #setting +x lim for slice 
        acc_slice = acc_trial[slice_begin:slice_end]
        r_peaks, r_props = scipy.signal.find_peaks(acc_slice, distance=80, prominence=5)#peaks stores index of pos peak from cwtmatr 
        acc_trial_r_peaks_ind = slice_begin + r_peaks#locates index of peak in acc_trial
        len_t_trial = np.arange(len(t_trial))#spacing the y points for the corresponding sample (x i.e. t_trial) vals
        axx.plot(len_t_trial[acc_trial_r_peaks_ind], acc_trial[acc_trial_r_peaks_ind], 'go')#, label="Raw Pole Plant") #plotting positive wavelet peaks (maxima) 
        t_name = trial_name[i-1]#assigning corresponding trial_name to  var t_name 
        
            ## Pole Off Index slice function ##
    #for loop to index and slice at every neg peak slice
    for k in range(0,len(n_w_peaks)):#determines number of steps in for loop based on number of peaks in n_w_peaks
        n_slice_ind = (n_w_peaks[k])#assigns the index of current iteration to n_slice_ind
        n_slice_begin = n_slice_ind-25 #setting -x lim  for slice 
        n_slice_end = n_slice_ind+15 #setting +x lim for slice
        n_acc_slice = acc_trial[n_slice_begin:n_slice_end]
        r_n_peaks, r_n_props = scipy.signal.find_peaks(-n_acc_slice, distance=40, prominence=40)#stores the index of neg peak from cwtmatr 
        acc_trial_r_n_peaks_ind = n_slice_begin + r_n_peaks#locates index of peak in acc_trial
        len_t_trial = np.arange(len(t_trial))#spacing the y points for the corresponding sample (x i.e. t_trial) vals
        axx.plot(len_t_trial[acc_trial_r_n_peaks_ind], acc_trial[acc_trial_r_n_peaks_ind], 'bo')#, label="Raw Pole Off")#plotting negative wavelet peaks (minima) 
        t_name = trial_name[i-1]#assigning corresponding trial_name to  var t_name 
        
    plt.title(f"Pole Plant and Pole off of {t_name} using \n CWT {wname} and find_peaks", fontsize=17)
    plt.gca().set_xlabel("Samples)", fontsize=15)
    plt.gca().set_ylabel(r"Acceleration $(\frac{m}{s^2})$", fontsize=15)
    plt.plot([], [], 'go', label="Raw Pole Plant")
    plt.plot([], [], 'bo', label="Raw Pole Off")
    axx.legend(loc=1)
    plt.show()