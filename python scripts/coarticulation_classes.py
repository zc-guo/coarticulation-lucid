#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 00:07:30 2020

@author: adamguo

Classes for calculating spectral distance and relative transition duration for adjacent segments

Some snippets of code are taken from:
    https://github.com/megseekosh/Meas_Quechua_coartic
"""

import librosa
import numpy as np
import matplotlib.pyplot as plt

class Spectra:
    def __init__(self, time_series, sr, mel_f, window_length = 0.0256, 
                 step_size = 0.010):
        """ Gets a spectral represeentation of a (floating point) time series.
        
        time_series:
            Audio file time series (expects an array).
        sr:
            Sampling rate.
        mel_f:
            Mel-frequency filter bank.
        window_length:
            Window length (time in seconds; default: 0.0256).
        step_size:
            Step_size (times in seconds; default: 0.010).
        """
        # Initialize variables of the Spectra class
        self.time_series = time_series
        self.sampling_rate = sr
        self.window_length = window_length
        self.no_of_samples = len(time_series)
        self.step_size = step_size
        self.filter_bank = mel_f
        
        # Note: no. of samples / duration = sampling rate
        self.duration = self.no_of_samples / sr
        
            
        # Note n_fft and hop_length are basically window length and step 
        # size, respectively. But they want "numbers of samples" in each 
        # window or step. They can be obtained by multiplying sampling rate 
        # by window length or step size.
        
        
        # Get the spectra
        FFT = librosa.stft(time_series,
                               n_fft = 2048,
                               hop_length = int(sr * step_size),
                               win_length = int(sr * window_length))
            
        # Convolve the filterbank over the spectrum
        self.spectra = mel_f.dot(np.abs(FFT))  
        self.average_spectrum = np.mean(np.log(self.spectra), axis = 1)
        
            
        # Get no. of frames.
        self.no_of_frames = self.spectra.shape[1]
    
    # Getter functions    
    def get_spectra(self):
        """ Gets the spectral vectors. """
        return np.copy(self.spectra)
    
    def get_average_spectrum(self):
        """ Gets the average spectral vector. """
        return np.copy(self.average_spectrum)
    
    def get_no_of_frames(self):
        """ Gets the number of frames in the spectral representation. """
        return self.no_of_frames
    
    def get_sampling_rate(self):
        """ Gets sampling rate. """
        return self.sampling_rate
    
    def get_window_length(self):
        """ Gets the window length. """
        return self.window_length
    
    def get_no_of_samples(self):
        """ Gets the number of samples in the input time series. """
        return self.no_of_samples
    
    def get_duration(self):
        """ Gets the duration of the time series. """
        return self.duration
    
    def get_step_size(self):
        """ Gets step size (in seconds). """
        return self.step_size
    
    def get_time_series(self):
        """ Gets the time series. """
        return self.time_series
    
    def get_filter_bank(self):
        """ Gets the filter bank. """
        return self.filter_bank

class Coarticulation:
    def __init__(self, spec_first, spec_second):
        """
        Takes the Spectra objects of two adjacent phones, analyzes their coarticulatory 
        properties (i.e., computing the spectral distance and temporal transition 
        measures of coarticulation).
        
        spec_first:
            A Spectra object of the first phone.
        spec_second:
            A Spectra object of the second phone.
        """
        self.spec_first = spec_first
        self.spec_second = spec_second
        
    def spectral_dist(self):
        """ Calculates the Euclidean distance between the average spectra of the 
        two segments. """
        spec_first_average = self.spec_first.get_average_spectrum()
        spec_second_average = self.spec_second.get_average_spectrum()
        return np.linalg.norm(spec_first_average - spec_second_average)
    
    def temporal_trans(self, trans_prop = 0.8):
        """ Calculates the proportion of frames that fall into the transition 
        period. """
        # Concatenate the time series of the two phones.
        ts_first = self.spec_first.get_time_series()
        ts_second = self.spec_second.get_time_series()
        ts_combined = np.concatenate((ts_first, ts_second))
        
        # Create the Spectra object for the combined time series (assume that) 
        # the Spectra of the two phones use the same sampling rate, have the 
        # same window length, etc.). 
        sr = self.spec_first.get_sampling_rate()
        filter_bank = self.spec_first.get_filter_bank()
        window_length = self.spec_first.get_window_length()
        step_size = self.spec_first.get_step_size() 
        combined_spectra = Spectra(ts_combined, 
                                   sr,
                                   filter_bank,
                                   window_length,
                                   step_size)
        spectra = combined_spectra.get_spectra()
        
        # Get the indice of the start and end frames.
        no_frames_first = self.spec_first.get_no_of_frames()
        no_frames_second = self.spec_second.get_no_of_frames()
        start_frame = int(no_frames_first / 2)
        end_frame = no_frames_first + int(no_frames_second / 2)
        
        # Following Gerosa & Narayanan: 
        # f12(i) = d(x1, xi) − d(x2, xi) where 1 and 2 are the first and second 
        # phones, respectively, and xi is the ith frame.
        trajectory = []
        d1_list = []
        d2_list = []
        for i in np.arange(start_frame, end_frame):
            spec = np.log(spectra[:, i]) # xi
            d1 = np.linalg.norm(self.spec_first.get_average_spectrum() - spec) # d(x1, xi)
            d2 = np.linalg.norm(self.spec_second.get_average_spectrum() - spec) # d(x2, xi)
            d1_list.append(d1)
            d2_list.append(d2)
            trajectory.append(d1 - d2)  # f12(i)
        
        list1 = []
        list2 = []
        
        for value in trajectory:
            if value < 0:
                list1.append(value)
            else:
                list2.append(value)
        
        mean1 = np.mean(list1) # Mean f12 in the portion for the first phone
        mean2 = np.mean(list2) # Mean f12 in the portion for the second phone
            
        lb = mean1 * trans_prop # Lowerbound for f12 values in the transition
        ub = mean2 * trans_prop # Upperbound
        
        # Count how many frames are in the transition
        no_frames_in_trans = len([x for x in trajectory if x > lb and x < ub])
        
        # Raw (absolute) transition duration
        trans_dur = no_frames_in_trans * step_size
        
        # Duration of the two phones combined
        total_dur = combined_spectra.get_duration()
        
        # Return the raw and relative transition durations
        return trans_dur, trans_dur / total_dur