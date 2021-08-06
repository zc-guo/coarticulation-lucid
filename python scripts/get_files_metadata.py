#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 22:05:19 2020

@author: adamguo
"""

import os
import pandas as pd

def get_files_metadata(input_dir, output_dir,
                       condition_code_dict = {"noBarrierCondition": "NB",
                                              "babbleCondition": "BABBLE",
                                              "vocoderCondition": "VOC",
                                              "L2Condition": "L2",
                                              "sentenceReadingCasual": "READ_CO",
                                              "sentenceReadingClear": "READ_CL"}):
    """
    Gets the metadata of all recording files, such as the speaker ID, the 
    condition that each file belongs to, etc. Each subfolder in the input 
    directory should represent a condition. Files of the same condition 
    should be put in the same subfolder.
    
    input_dir:
        Directory of the folders where the input files are stored.
    output_dir:
        Directory where the file metadata are to be saved.
    condition_code_dict:
        A dictionary specifying the code/abbreviation for each condition
    """
    # Get a list of the directories of all the subfolders
    subfolders_dirs = [f.path for f in os.scandir(input_dir) if f.is_dir()]
    
    # Create an empty dataframe for storing the file information
    file_metadata = pd.DataFrame(columns = ["Filename","Filename_wav",
                                            "Filename_TextGrid",
                                            "Condition", "Task_type",
                                            "Style", "Scene", "Scene_ID",
                                            "Speaker_tier_AB",
                                            "Speaker", "Speaker_sex",
                                            "Partner", "Partner_sex",
                                            "Position_number"])
    
    # Iterate over all subfolders
    for subfolder in subfolders_dirs:
        
        # Get subfolder name
        subfolder_name = subfolder.split("/")[-1]
        
        # Get the condition code
        cond_code = condition_code_dict[subfolder_name]
        
        # Get all the WAV files in this subfolder
        all_wav_files = [i for i in os.listdir(subfolder) if i.endswith(".wav")]
        
        # Iterate over all the WAV files:
        for wav_file in all_wav_files:
            
            # Extract the information about the file from its file name by 
            # calling the helper function extract_file_info()
            file_info = extract_file_info(wav_file, cond_code)
            
            # Add file_info to the dataframe
            try:
                file_metadata.loc[len(file_metadata)] = file_info
                
            except ValueError:
                print("\nLength of the file info list doesn't match the columns. Make sure that all file info is in the list!")
                
    # Save to Excel
    file_metadata.to_excel(
            os.path.join(output_dir, "all_file_metadata.xlsx"),
            index = False)


def extract_file_info(file_name, cond_code):
    """
    A helper function that extracts the information about a (WAV or TextGrid) 
    file from its file name. It handles the files differently depending on 
    their condition (as the naming conventions differed for files in different 
    conditions). See "LUCID - File-Naming Convention.txt" in the LUCID corpus 
    on SpeechBox for details.
    
    file_name:
        Name of the file from which the information will be obtained.
    cond_code:
        Code of the condition to which the file belongs.
    """
    # The first three items in the info lists are: 
    # 1. file name without extension
    # 2. file name with .wav extension
    # 3. file name with .TextGrid extension
    # 4. cond_code
    file_name_no_ext = file_name.split(".")[0]
    file_info = [file_name_no_ext, file_name, file_name_no_ext + ".TextGrid",
                 cond_code]
    
    if cond_code == "NB":
        # Speaker info
        speakers = file_name_no_ext[4:-7]
        speaker_AB = file_name_no_ext[-1]
        
        # Locate the starting indice of the two speakers' IDs 
        speakers_indice = [pos for pos, char in enumerate(speakers) if char in ["M", "F"]]
        
        speaker_A = speakers[0:speakers_indice[1]]
        speaker_B = speakers[speakers_indice[1]:]
        
        # Determine who is the speaker of the recording file and who is the 
        # partner
        if speaker_AB == "A":
            speaker = speaker_A
            speaker_sex = speaker[0]
            partner = speaker_B
            partner_sex = partner[0]
            
        else:
            speaker = speaker_B
            speaker_sex = speaker[0]
            partner = speaker_A
            partner_sex = partner[0]
        
        # Scene info
        scene = file_name_no_ext[-7]
        scene_ID =  file_name_no_ext[-7:-5]
        
        # Other
        position_number = file_name_no_ext[-3]
        task_type = "Diapix"
        style = "Conversational"
        
    elif cond_code == "VOC":
        # Speaker info
        speakers = file_name_no_ext[4:-10]
        speaker_AB = file_name_no_ext[-3]
        
        # A special code for only the VOC condition: 1 when speaker A corresponds 
        # to the first channel and is the first speaker in the file name; 2 when 
        # speaker A corresponds to the second channel and is the second speaker 
        # in the file name.
        speaker_channel_code = file_name_no_ext[-1]
        
        # Locate the starting indice of the two speakers' IDs 
        speakers_indice = [pos for pos, char in enumerate(speakers) if char in ["M", "F"]]
        
        speaker_A = speakers[0:speakers_indice[1]]
        speaker_B = speakers[speakers_indice[1]:]
        
        # Determine who is the speaker of the recording file and who is the 
        # partner
        if speaker_AB == "A":
            
            if speaker_channel_code == "1":
                
                speaker_A = speakers[0:speakers_indice[1]]
                speaker_B = speakers[speakers_indice[1]:]
                
                speaker = speaker_A
                speaker_sex = speaker[0]
                partner = speaker_B
                partner_sex = partner[0]
            
            # If speaker_channel_code is "2":
            else:
                speaker_A = speakers[speakers_indice[1]:]
                speaker_B = speakers[0:speakers_indice[1]]
                
                speaker = speaker_A
                speaker_sex = speaker[0]
                partner = speaker_B
                partner_sex = partner[0]
                 
        # If speaker_AB is "B":
        else:
            
            if speaker_channel_code == "1":
                
                speaker_A = speakers[0:speakers_indice[1]]
                speaker_B = speakers[speakers_indice[1]:]
                
                speaker = speaker_B
                speaker_sex = speaker[0]
                partner = speaker_A
                partner_sex = partner[0]
            
            # If speaker_channel_code is "2":
            else:
                speaker_A = speakers[speakers_indice[1]:]
                speaker_B = speakers[0:speakers_indice[1]]
                
                speaker = speaker_B
                speaker_sex = speaker[0]
                partner = speaker_A
                partner_sex = partner[0]
        
        # Scene info
        scene = file_name_no_ext[-10]
        scene_ID =  file_name_no_ext[-10:-8]
        
        # Other
        position_number = file_name_no_ext[-5]
        task_type = "Diapix"
        style = "Clear"
    
    elif cond_code == "BABBLE":
        # Speaker info
        speakers = file_name_no_ext[4:-8]
        speaker_AB = file_name_no_ext[-1]
        
        # Locate the starting index of the speaker B (confederate listener) 
        speakerB_index = speakers.index("B")
        
        speaker_A = speakers[0:speakerB_index]
        speaker_B = speakers[speakerB_index:]
        
        # Determine who is the speaker of the recording file and who is the 
        # partner
        if speaker_AB == "A":
            speaker = speaker_A
            speaker_sex = speaker[0]
            partner = speaker_B
            partner_sex = partner[2]
            
        else:
            speaker = speaker_B
            speaker_sex = speaker[2]
            partner = speaker_A
            partner_sex = partner[0]
        
        # Scene info
        scene = file_name_no_ext[-8]
        scene_ID =  file_name_no_ext[-8:-6]
        
        # Other
        position_number = file_name_no_ext[-3]
        task_type = "Diapix"
        style = "Clear"
    
    elif cond_code == "L2":
        # Speaker info
        speakers = file_name_no_ext[4:-9]
        speaker_AB = file_name_no_ext[-1]
        
        # Locate the starting index of the speaker B (confederate listener) 
        speakerB_index = speakers.index("C")
        
        speaker_A = speakers[0:speakerB_index]
        speaker_B = speakers[speakerB_index:]
        
        # Determine who is the speaker of the recording file and who is the 
        # partner
        if speaker_AB == "A":
            speaker = speaker_A
            speaker_sex = speaker[0]
            partner = speaker_B
            partner_sex = partner[1]
            
        else:
            speaker = speaker_B
            speaker_sex = speaker[1]
            partner = speaker_A
            partner_sex = partner[0]
        
        # Scene info
        scene = file_name_no_ext[-9]
        scene_ID =  file_name_no_ext[-9:-7]
        
        # Other
        position_number = file_name_no_ext[-3]
        task_type = "Diapix"
        style = "Clear"
    
    elif cond_code == "READ_CO":
        # Speaker info
        speaker = file_name_no_ext[4:-6]
        speaker_sex = speaker[0]
        speaker_AB = "NA"
        partner = "NA"
        partner_sex = "NA"
        
        # Scene info
        scene = "NA"
        scene_ID = "NA"
        
        # Other
        position_number = "NA"
        task_type = "Sentence_reading"
        style = "Conversational"
    
    else: # READ_CL
        # Speaker info
        speaker = file_name_no_ext[4:-6]
        speaker_sex = speaker[0]
        speaker_AB = "NA"
        partner = "NA"
        partner_sex = "NA"
        
        # Scene info
        scene = "NA"
        scene_ID = "NA"
        
        # Other
        position_number = "NA"
        task_type = "Sentence_reading"
        style = "Clear"
    
    # Add all information to file_info
    file_info = file_info + [task_type, style, scene, scene_ID, speaker_AB,
                             speaker, speaker_sex, partner, partner_sex,
                             position_number]
    return file_info

if __name__ == "__main__":
    input_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/channels separated"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/metadata"
    get_files_metadata(input_dir, output_dir)