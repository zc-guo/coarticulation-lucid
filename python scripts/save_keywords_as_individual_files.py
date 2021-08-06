#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 15:08:02 2021

@author: adamguo
"""
import os, sys, textgrids, librosa
import pandas as pd

def save_keywords_as_individual_files(textgrid_dir,
                                      soundfile_dir,
                                      output_dir,
                                      sr = 44100,
                                      file_metadata = None,
                                      words_tier_name = "words_KW",
                                      vowels_tier_name = "vowels_KW"):
    """
    Saves tokens of the keywords as individual sound fles. Also, create dataframe 
    that provides metadata for these sound files.
    
    textgrid_dir:
        Directory of the Textgrids, which should contain tiers for the keywords and 
        for the vowels in these words. Each folder in this directory should 
        corresponds to a condition.
    sounfile_dir:
        Directory of the sound files from which the keyword tokens will be extracted. 
        Each folder in this directory should correspond to a condition.
    output_dir:
        Output directory for the sound files and metadata.
    sr:
        Sampling rate (default: 44100).
    file_metadata:
        An Excel file containing information about the input WAV/TextGrid 
        files (default: None).
    words_tier_name:
        Word-aligned annotation tier for the keywords (default: "words_KW").
    vowels_tier_namne:
        Vowel-align annotation for the vowels in the keywords (default: "words_KW").
    """
    # Load file name metadata
    if file_metadata is None:
        
        # If the metadata is not provided, try getting the data from the following folder.
        file_metadata_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/metadata/all_file_metadata.xlsx"
        print("\nNo file metadata provided. Try reading from {}...".format(file_metadata_dir))
        
        try:
            file_metadata = pd.read_excel(file_metadata_dir)
        
        except FileNotFoundError:
            print("\nNo such file or directory. Please provide the file metadata.")
    
    # Create an empty dataframe for storing the word tooken data. This dataframe 
    # should have all the columns from the metadata plus some other information 
    # about word token
    token_data = pd.DataFrame(columns = list(file_metadata.columns) + \
                              ["Keyword", "Repetition", "Token_filename_wav",
                               "Token_filename_TextGrid", "Vowel", "Word_duration"])
    
    # Get a list of all subfolders in textgrid_dir.
    subfolders_dirs = [f.path for f in os.scandir(textgrid_dir) if f.is_dir()]
    
    print("\nExtracting keyword tokens...")
    # Iterate over all subfolders:
    for subfolder in subfolders_dirs:
        
        # Get subfolder (condition) name
        subfolder_name = subfolder.split("/")[-1]
        
        # Get all the TextGrid files in this input subfolder
        all_textgrids_files = [i for i in os.listdir(subfolder) if i.endswith(".TextGrid")]
        
        # Create the corresponding subfolder in output_dir
        output_subfolder_dir = os.path.join(output_dir, subfolder_name)
        os.makedirs(output_subfolder_dir)
        
        # Under this condition subfolder, create another two folders: one for 
        # male speakers and the other for female speakers
        os.makedirs(os.path.join(output_subfolder_dir, "male"))
        os.makedirs(os.path.join(output_subfolder_dir, "female"))
        
        # Progress trackers
        pg_total = len(all_textgrids_files)
        pg_count = 0
        
        # Iterate over all the TextGrid files:
        for textgrid_file in all_textgrids_files:
            
            # Get the path to the TextGrid
            path_to_textgrid_file = os.path.join(subfolder, textgrid_file)
            
            # Get the path to the corresponding sound file in soundfile_dir
            path_to_sounfile = os.path.join(soundfile_dir, subfolder_name,
                                            textgrid_file.split(".")[0] + ".wav")
            
            
            # Get the metadata for this sound file and reset its index
            sound_md = file_metadata.loc[file_metadata["Filename_TextGrid"] == textgrid_file]
            sound_md = sound_md.reset_index(drop = True)
            
            try:
                token_data = extract_sounds_and_textgrids(
                        textgrid_path = path_to_textgrid_file,
                        soundfile_path = path_to_sounfile,
                        output_path = output_subfolder_dir,
                        sampling_rate = sr,
                        soundfile_metadata = sound_md,
                        token_data_frame = token_data,
                        words_tier = words_tier_name,
                        vowels_tier = vowels_tier_name)
                
            except KeyError:
                print("\nTier {} or {} not found.".format(words_tier_name,
                      vowels_tier_name))
                
            except IndexError:
                print("\nWarning: File {} does not contain any keywords".format(textgrid_file))
            
            # Update progress
            pg_count += 1
            sys.stdout.write("\rNow saving files to {0} in the output folder: {1}%".format(
                    subfolder_name,
                    round((float(pg_count) / pg_total) * 100)
                    ))
            sys.stdout.flush()
            
    print("\nFinished extracting keyword tokens. Now saving the metadata")
    token_data.to_excel(os.path.join(output_dir, "keyword_token_metadata.xlsx"),
                        index = False)
    
    print("\nDone!")
    

def extract_sounds_and_textgrids(textgrid_path, soundfile_path, output_path,
                                 sampling_rate, soundfile_metadata, 
                                 token_data_frame, words_tier,
                                 vowels_tier):
    """
    Extracts keyword token and save them as individual files, along with
    their TextGrids, and also creates an dataframe containing metadata for these 
    sound files.
    """
    # Open the TextGrid
    tg = textgrids.TextGrid(textgrid_path)
    
    # Get a list containing all the non-empty keyword intervals
    keyword_ints = [kw for kw in tg[words_tier] if kw.text != ""]
    
    # Get a list containing all the non-empty vowel intervals
    vowel_ints = [v for v in tg[vowels_tier] if v.text != ""]
    
    # If one or both of the two lists are empty, raise IndexError
    if len(keyword_ints) == 0 or len(vowel_ints) == 0:
        raise IndexError
    
    # Load the corresponding audio
    audio, _ = librosa.load(soundfile_path, sampling_rate)
    
    # Create a dictionary to track counts of the keywords
    kw_counts = {}
    
    # Create a list for the sound file metadata
    soundfile_metadata_list = soundfile_metadata.loc[0].tolist()
    
    # Get the speaker's gender and the gender subfolder
    gender = soundfile_metadata['Speaker_sex'][0]
    
    if gender == "F":
        gender_folder = "female"
    else:
        gender_folder = "male"
    
    # Update output path
    output_path = os.path.join(output_path, gender_folder)
    
    # Create a copy of the token dataframe to be updated
    updated_token_data_frame = token_data_frame.copy(deep = True)
    
    # Now, loop through keywords_ints
    for kw_int in keyword_ints:
        
        # Get the keyword, onset time, offset time, and duration
        keyword = kw_int.text
        onset_t = kw_int.xmin
        offset_t = kw_int.xmax
        
        # Update the count dictionary
        if keyword in kw_counts:
            kw_counts[keyword] += 1
            
        else:
            kw_counts[keyword] = 1
        
        # Now creeate the audio
        # Slice out the snippet corresponding to the keyword in the audio
        start_frame = int(onset_t * sampling_rate)
        end_frame = int(offset_t * sampling_rate)
        
        snippet = audio[start_frame:end_frame]
        
        # Save the audio (note: tk in the file name stands for token)
        filename = soundfile_path.split("/")[-1]
        filename = filename.split(".")[0]
        filename = filename + "_{}_tk{}".format(keyword, str(kw_counts[keyword]))
        audio_filename = filename + ".wav"
        librosa.output.write_wav(os.path.join(output_path, audio_filename),
                                          snippet, sampling_rate)
        
        # Calculate word duration
        word_dur = librosa.get_duration(snippet, sampling_rate)
        
        # Before creating the TextGrid, do some preparation:
        # Get a list containing all vowel intervals that belong to this keyword. 
        # Because the keywords are monosyllabic, normally there should be just 
        # one vowel in each keyword token. However, this method should scale to
        # words with any numbers of vowel.
        v_ints_for_each_kw = [v for v in vowel_ints if v.xmin >= onset_t and v.xmax <= offset_t]
        
        # Shift the xmin and xmax of each vowel interval so that they represent 
        # the timings with respect to word onet and the vowel intervals can be 
        # use for creating the TextGrids for individual sound files. The code also 
        # inserts blank interval between non-adjacent vowels, but this should 
        # happen only if the keyword is disyllabic or longer.   
        prev_xmax = 0.0
        v_ints_for_each_kw_new = []
        for i in range(len(v_ints_for_each_kw)):
            # Shift xmin and xmax
            v_ints_for_each_kw[i].xmin = v_ints_for_each_kw[i].xmin - onset_t
            v_ints_for_each_kw[i].xmax = v_ints_for_each_kw[i].xmax - onset_t
            
            # Check if an empty interval is needed before
            if v_ints_for_each_kw[i].xmin > prev_xmax:
                v_ints_for_each_kw_new.append(textgrids.Interval("",
                                                                 prev_xmax,
                                                                 v_ints_for_each_kw[i].xmin))
            
            # Add the time-shifted interval to v_ints_for_each_kw_new
            v_ints_for_each_kw_new.append(v_ints_for_each_kw[i])
            
            # Update prev_xmax
            prev_xmax = v_ints_for_each_kw[i].xmax
        
        # Add an empty interval if the vowel is not the word-final segment
        last_v_int = v_ints_for_each_kw_new[len(v_ints_for_each_kw_new) - 1]
        if last_v_int.xmax < word_dur:
            v_ints_for_each_kw_new.append(textgrids.Interval("",
                                                             last_v_int.xmax,
                                                             word_dur))

        # Create the TextGrid
        # Iitialize a TextGrid object
        tg_kw = textgrids.TextGrid()
        
        # Add the word tier
        word_interval = [textgrids.Interval(keyword, 0.0, word_dur)]
        tg_kw["word"] = textgrids.Tier(word_interval)

        # Add the vowel tier
        tg_kw["vowel"] = textgrids.Tier(v_ints_for_each_kw_new)
        
        # Save the TextGrid
        textgrid_filename = filename + ".TextGrid"
        tg_kw.write(os.path.join(output_path, textgrid_filename))
        
        # Last but not least, update token_data
        token_info_list = [keyword,
                           kw_counts[keyword],
                           audio_filename,
                           textgrid_filename]
        
        # Get vowel sequence
        v_str = ""
        
        for v_int in v_ints_for_each_kw:
            
            if v_str == "":
                v_str += v_int.text
                
            # This should occur only if there are two or more vowels in the word.
            else:
                v_str += "-{}".format(v_int.text)
         
        token_info_list.append(v_str)
        
        # Add word duration
        token_info_list.append(word_dur)
        
        # Get a copy of the list
        new_soundfile_metadata_list = soundfile_metadata_list[:]
        
        # Add the token information
        new_soundfile_metadata_list.extend(token_info_list)
       
        # Token_filename_TextGrid
        updated_token_data_frame.loc[len(updated_token_data_frame)] = new_soundfile_metadata_list
    
    # Return the updated token dataframe
    return updated_token_data_frame

if __name__ == "__main__":
    textgrid_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/files for vowel nasalization analysis/force-aligned keywords for VN"
    soundfile_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/channels separated"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/files for vowel nasalization analysis/extracted keyword tokens"
    save_keywords_as_individual_files(textgrid_dir, soundfile_dir, output_dir)