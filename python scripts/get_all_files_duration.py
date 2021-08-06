#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 13:31:47 2021

@author: adamguo
"""

import os
import librosa

def get_all_files_duration(input_dir,
                           condition_folders = ["noBarrierCondition",
                                                "babbleCondition",
                                                "vocoderCondition",
                                                "L2Condition",
                                                "sentenceReadingCasual",
                                                "sentenceReadingClear"]):
    """
    input_dir:
        Directory to the folder where the sound files are saved.
    condition_folders:
        A list of subfolders containing the sounds files for each condition 
        (default: ["noBarrierCondition", "babbleCondition", "vocoderCondition", 
        "L2Condition", "sentenceReadingCasual", "sentenceReadingClear"]).
    """
    # Initialize total_dur (in seconds)
    total_dur = 0.0
    
    # Iterate over all subfolders
    for subfolder in condition_folders:
        
        # Get subfolder directory
        subfolder_dir = os.path.join(input_dir, subfolder)
        
        # Get all the WAV files
        all_wav_files = [i for i in os.listdir(subfolder_dir) if i.endswith(".wav")]
        
        # Load each sound file, its the duration, and add it to total_dur
        for sound_file in all_wav_files:
            
            total_dur += librosa.get_duration(filename = os.path.join(subfolder_dir, sound_file))
            
    print("\nTotal duration of recordings:")
    print("In seconds:", total_dur)
    print("In minutes:", total_dur / 60)
    print("In hours:", total_dur / (60 * 60))

if __name__ == "__main__":
    input_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/original recordings"
    get_all_files_duration(input_dir)
    