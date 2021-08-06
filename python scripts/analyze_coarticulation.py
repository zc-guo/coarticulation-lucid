#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 15:46:21 2021

@author: adamguo
"""
import os, sys, librosa, warnings
import pandas as pd
import numpy as np
from coarticulation_classes import Spectra, Coarticulation

warnings.simplefilter("error")
warnings.simplefilter("ignore", ResourceWarning)

def analyze_coarticulation(sound_folders_dir,
                           phone_pairs_data_dir,
                           output_dir,
                           sr = 44100):
    """
    Gets coarticulation measures (spectral distance and temporal transition) for 
    phone pairs.
    
    sound_folders_dir:
        Directory of the sound files (WAV) on which the analysis will be 
        performed. Each subfolder in this directory should be a condition.
    phone_pairs_data_dir:
        Directory of the phone pair data.
    output_dir:
        Directory of the output (which is the phone pairs data plus one column 
        that gives the spectral distance for each phone pair).
    sampling_rate:
        Sampling rate for loading the sound files (default: 44100, which is the 
        native sampling rate of the LUCID recordings).
    """
    # Load the phone pair data
    phone_pairs_data = pd.read_excel(phone_pairs_data_dir)
    nrow = phone_pairs_data.shape[0]
    
    # Create a new copy of the original phone data
    coart_data = phone_pairs_data.copy(deep = True)
    
    # Add new empty columns for the measures
    coart_data["Spectral_distance"] = np.nan
    coart_data["Raw_transition_duration"] = np.nan
    coart_data["Relative_transition_duration"] = np.nan
    
    # Initialize filename of previous row
    prev_filename_wav = ""
    
    # Create a dictionary specifying the full subfolder name for each condition 
    # code
    condition_folder_code_dict = {"NB": "noBarrierCondition",
                                  "BABBLE": "babbleCondition",
                                  "VOC": "vocoderCondition",
                                  "L2": "L2Condition",
                                  "READ_CO": "sentenceReadingCasual",
                                  "READ_CL": "sentenceReadingClear"}
    
    # Create the Mel-frequency filter bank
    mel_f = librosa.filters.mel(sr, n_fft = 2048, n_mels = 29, 
                                fmin = 100.0, fmax = 6000.0, htk = True, norm = 1)
    
    # Iterate over the phone pair _data
    for index, row in phone_pairs_data.iterrows():
        
        # Get file name with WAV extension and check if it is NOT the same as 
        # prev_filename_wav. If yes, load the sound file.
        filename_wav = row["Filename_wav"]
        condition_code = row["Condition"]
        
        if filename_wav != prev_filename_wav:
            
            # Get the full path to the sound file
            condition_subfolder = condition_folder_code_dict[condition_code]
            full_sound_file_path = os.path.join(sound_folders_dir,
                                                condition_subfolder,
                                                filename_wav)
                
            sound, _ = librosa.load(full_sound_file_path,
                                     sr = sr)
            
            # Then let prev_filename_wav be filename_wav
            prev_filename_wav = filename_wav
            
        # Now start the analysis. First create the Spectra objects for the 
        # phone pair.
        first_phone_ts = sound[int(row["First_phone_start_t"] * sr):
            int(row["First_phone_end_t"] * sr)]
        second_phone_ts = sound[int(row["Second_phone_start_t"] * sr):
            int(row["Second_phone_end_t"] * sr)]
        
        # Spectral distance analyais:
        ## Create Spectra objects for the first and second phones.
        first_phone_spec = Spectra(first_phone_ts, sr, mel_f, step_size = 0.010)
        second_phone_spec = Spectra(second_phone_ts, sr, mel_f, step_size = 0.010)
        
        ## Create a Coarticulation object using the two Spectra objects.
        coar = Coarticulation(first_phone_spec, second_phone_spec)
            
        ## Get the spectral distance metric for the two phones.
        spectral_distance = coar.spectral_dist()
        
        ## Add the distance data point to coart_data
        coart_data.at[index, "Spectral_distance"] = spectral_distance
        
        # Temporal transition analysis
        ## Again, create Spectra objects for the first and second phones, but 
        ## using a step size of 0.001.
        first_phone_spec = Spectra(first_phone_ts, sr, mel_f, step_size = 0.001)
        second_phone_spec = Spectra(second_phone_ts, sr, mel_f, step_size = 0.001)
        
        ## Create a Coarticulation object using the two Spectra objects.
        coar = Coarticulation(first_phone_spec, second_phone_spec)
        
        ## Get the transition duratiion metrics for the two phones.
        try:
            raw_trans_dur, relative_trans_dur = coar.temporal_trans()
        
        except RuntimeWarning:
            raw_trans_dur, relative_trans_dur = np.nan, np.nan
            
        ## Add the duration metrics to coart_data
        coart_data.at[index, "Raw_transition_duration"] = raw_trans_dur
        coart_data.at[index, "Relative_transition_duration"] = relative_trans_dur
        
        # Update progress
        sys.stdout.write("\rProgress: {0}%".format(round((float(index) / nrow) * 100)))
        sys.stdout.flush()
    
    # Finally, save the coarticulation data to the output directory
    coart_data.to_excel(
            os.path.join(output_dir, "coart_data.xlsx"),
            index = False)
    print("\nDone!")

if __name__ == "__main__":
    sound_folders_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/channels separated"
    phone_pairs_data_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/phone_pairs_data.xlsx"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings"
    analyze_coarticulation(sound_folders_dir,
                           phone_pairs_data_dir,
                           output_dir)