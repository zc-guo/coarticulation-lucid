#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 15:34:09 2020

@author: adamguo
"""
import os, sys, textgrids
import pandas as pd

sys.path.append("/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/python scripts")
from get_keywords_tiers import get_KW_phones_ints_and_times

def get_phone_pairs_data(input_dir, output_dir,
                         file_metadata = None,
                         words_tier_name = "words_KW",
                         phones_tier_name = "phones_KW"):
    """
    This functions gets the start and end points of each pair of adjacent phones 
    in each keyword (and some other information about that word)). The output 
    is an Excel dataframe that is ready to be used for coarticulation analysis.
    
    input_dir:
        Directory of the subfolders containing the TextGrid files. Note: each 
        subfolder is a condition and the TextGrids should contain word- and 
        phone-aligned tiers for the keywords.
    ouput_dir:
        Directory of the folder where the output will be saved.
    file_metadata:
        Path to an Excel file containing information about all WAV/TextGrid 
        files (default: None).
    words_tier_name:
        Word-aligned annotation tier for the keywords (default: "words_KW").
    phones_tier_name:
        Phone-aligned annotation tier for the keywords (default: "phones_KW").
    """
    # Load file name metadata
    if file_metadata is None:
        
        # If the path to the metadata is not provided, try getting the data 
        # from the # following folder.
        file_metadata_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/metadata/all_file_metadata.xlsx"
        print("\nNo file metadata provided. Try reading from " + \
              file_metadata_dir + "...")
        
        try:
            file_metadata = pd.read_excel(file_metadata_dir)
        
        except FileNotFoundError:
            print("\nNo such file or directory. Please provide the file metadata.")
    
    # Create an empty dataframe for storing the phone pairs data. This dataframe 
    # should have all the columns from the metadata plus some other information 
    # about each pair of phones.
    phone_pairs_data = pd.DataFrame(columns = list(file_metadata.columns) + \
                                    ["Keyword", "Repetition", "Phone_pair",
                                     "First_phone", "First_phone_start_t",
                                     "First_phone_end_t",
                                     "Second_phone", "Second_phone_start_t",
                                     "Second_phone_end_t"])
    
    # Get a list of all subfolders in input_dir.
    subfolders_dirs = [f.path for f in os.scandir(input_dir) if f.is_dir()]
    
    # Iterate over all subfolders:
    for subfolder in subfolders_dirs:
        
        # Get subfolder (condition) name
        # subfolder_name = subfolder.split("/")[-1]
        
        # Get all the TextGrid files in this input subfolder
        all_textgrids_files = [i for i in os.listdir(subfolder) if i.endswith(".TextGrid")]
        
        # Iterate over all the TextGrid files:
        for textgrid_file in all_textgrids_files:
            
            # Get the metadata of this TextGrid.
            textgrid_metadata = file_metadata[file_metadata["Filename_TextGrid"] == textgrid_file].values.tolist()[0]
            
            # Create TextGrid object.
            textgrid = textgrids.TextGrid(os.path.join(subfolder,
                                                       textgrid_file))
            
            # Now, call to the get_KW_phones_ints_and_times function from the 
            # get_keywords_tiers module to get the time data (and other info.) 
            # of each individual phone in the TextGrid object.
            # Note: only phone_time_data is needed.
            _, phone_time_data = get_KW_phones_ints_and_times(textgrid,
                                                              words_tier_name = words_tier_name,
                                                              phones_tier_name = phones_tier_name)
            
            # Call to the helper function to process phone_time_data into a 
            # formate appropriate for coarticulation analysis (i.e., each row 
            # represents a pair of adjacent phones in a keyword) and update the 
            # phone_pairs_data dataframe.
            phone_pairs_data = update_data(phone_pairs_data,
                                           phone_time_data,
                                           textgrid_metadata)
    
    # Write the phone pairs data to the output directory.
    phone_pairs_data.to_excel(
            os.path.join(output_dir, "phone_pairs_data.xlsx"),
            index = False)
    print("\nDone! The phone pairs data have been saved to " + output_dir)

def update_data(phone_pairs_data, phone_time_data, metadata):
    """
    Upates phone pair dataframe.
    
    phone_pairs_data:
        Dataframe to be updated.
    phone_time_data:
        Dataframe to be added.
    metadata:
        Metadata about the TextGrid/wav to which the to-be-added dataframe 
        belongs (expects a list).
    """
    
    # Iterate over rows of phone_time_data:
    for index, row in phone_time_data.iterrows():
        
        # If this in the first row (phone) in the dataframe, then let prev_phone 
        # be the current phone.
        if index == 0:
            prev_phone = row
            
        else:
            # Check if current_phone is adjacent to prev_phone. If yes, create 
            # all phone pair information and update the dataframe:
            current_phone = row
            if prev_phone["End_t"] == current_phone["Start_t"]:
                
                # Get phone pair information.
                # If the two phones are adjacent, they must be of the same word. 
                # So using either prev_phone or current_phone to get keyword and 
                # repetition should be OK.
                keyword = prev_phone["Keyword"]
                repetition = prev_phone["Repetition"]
                
                # Concatenate the phones with "_"
                phone_pair = prev_phone["Phone"] + "_" + current_phone["Phone"]
                
                # Time info. of first phone
                first_phone = prev_phone["Phone"]
                first_phone_start_t = prev_phone["Start_t"]
                first_phone_end_t = prev_phone["End_t"]
                
                # Time info. of second phone
                second_phone = current_phone["Phone"]
                second_phone_start_t = current_phone["Start_t"]
                second_phone_end_t = current_phone["End_t"]
                
                # Now create a list with all information about this phoone pair 
                # (including the metadata)
                phone_pair_info = metadata + [keyword, repetition, phone_pair,
                                              first_phone, first_phone_start_t,
                                              first_phone_end_t,
                                              second_phone, second_phone_start_t,
                                              second_phone_end_t]
                
                # Update phone_pairs_data
                try:
                    phone_pairs_data.loc[len(phone_pairs_data)] = phone_pair_info
                
                except ValueError:
                     print("\nLength of the phone pair info list doesn't match the columns. Make sure that all phone pair info is in the list!")
                
                # Finally, let current_phone be prev_phone
                prev_phone = current_phone
             
            # If no, just let current_phone be prev_phone
            else:
                prev_phone = current_phone
    
    # Return the updated phone_pairs_data
    return phone_pairs_data

if __name__ == "__main__":
    input_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/force-aligned keywords"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings"
    get_phone_pairs_data(input_dir, output_dir)