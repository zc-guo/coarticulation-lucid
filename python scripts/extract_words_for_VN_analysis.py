#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 13:50:34 2021

@author: adamguo
"""

import os, sys, textgrids, shutil

sys.path.append("/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/python scripts")
import get_keywords_tiers

def extract_words_for_VN_analysis(input_dir,
                                  output_dir,
                                  keywords,
                                  words_tier_name = "words_KW",
                                  phones_tier_name = "phones_KW",
                                  vowels_tier_name = "vowels_KW"):
    """
    Gets the sound files for coarticulatory vowel nasalization analysis. This 
    script extracts all tokens of the specified keywords and saves each of them as 
    an individual WAV file.
    
    input_dir:
        Directory of the subfolders containing the TextGrid files. Note: each 
        subfolder is a condition and the TextGrids should contain word- and 
        phone-aligned tiers for the keywords.
    output_dir:
        Directory of the output folder. This folder will contain the metadata and 
        subfolders for the conditions. 
    keywords:
        A list of keywords to be extracted and analyzed.
    words_tier_name:
        Word-aligned annotation tier for the keywords (default: "words_KW").
    phones_tier_name:
        Phone-aligned annotation tier for the keywords (default: "phones_KW").
    """    
    # Convert all keywords in the keyword list to uppercase.
    keywords = [kw.upper() for kw in keywords]
    
    # Vowel labels
    vowels = ["AO1", "AY1", "IY1", "AE1", "IH1", "UH1", "AA1", "EH1", "UW1"]
    
    # Now, call to the get_keywords_tiers function from get_keywords_tiers.py to 
    # get the word- and phone-aligned intervals of the keywords, add them as 
    # new tiers to the original TextGrids, and save the TextGrids as new files to 
    # the output output_dir/tmp.
    tmp_dir = os.path.join(output_dir, "tmp")
    os.makedirs(tmp_dir)
    
    get_keywords_tiers.get_keywords_tiers(input_dir = input_dir,
                                          output_dir = tmp_dir,
                                          keywords = keywords,
                                          words_tier_name_KW = words_tier_name,
                                          phones_tier_name_KW = phones_tier_name,
                                          print_fin_msg = False)
    
    print("\nFinished getting TextGrids with separate tiers for the keywords...")
    
    # Create the force-aligned keywords for VN subfolder under output_dir
    subfolder1_dir = os.path.join(output_dir, "force-aligned keywords for VN")
    os.makedirs(subfolder1_dir)
    
    # Now, get a list of the directories of all the subfolders in output_dir/tmp.
    subfolders_dirs = [f.path for f in os.scandir(tmp_dir) if f.is_dir()]
    
    # Iterate over all subfolders:
    for subfolder in subfolders_dirs:
        
        # Get subfolder (condition) name
        subfolder_name = subfolder.split("/")[-1]
        
        # Create subfolder directory
        sub_subfolder1_dir = os.path.join(subfolder1_dir, subfolder_name)
        os.makedirs(sub_subfolder1_dir)
        
        # Get all the TextGrid files in this subfolder
        all_textgrids_files = [i for i in os.listdir(subfolder) if i.endswith(".TextGrid")]
        
        # Iterate over all the TextGrid files:
        for textgrid_file in all_textgrids_files:
                        
            # Create TextGrid object
            textgrid = textgrids.TextGrid(os.path.join(subfolder,
                                                       textgrid_file))
            
            # Re-use the get_KW_words_ints function from get_keywords_tiers.py. 
            # Note that it can also be used for getting a tier with just vowels. 
            # Simply supply the vowel label list for the keyword argument and 
            # phones_tier_names for the words_tier_name argument.
            keyword_vowels_intervals = get_keywords_tiers.get_KW_words_ints(
                    textgrid = textgrid,
                    keywords = vowels,
                    words_tier_name = phones_tier_name)
            
            # Add it as a new tier to the TextGrid object
            keyword_vowels_intervals_tier = textgrids.Tier(keyword_vowels_intervals)
            textgrid[vowels_tier_name] = keyword_vowels_intervals_tier
            
            # Save the TextGrid to output/force-aligned keywords for VN/subfolder
            textgrid.write(os.path.join(sub_subfolder1_dir,
                                        textgrid_file))
    
    print("\nFinished adding the vowel tier...")
    
    # Remove tmp
    shutil.rmtree(tmp_dir)
    
    print("\nDone!")
    
            
if __name__ == "__main__":
    input_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/force-aligned"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/files for vowel nasalization analysis"
    keywords = ["PIN", "BIN", "PEAS", "BEE", "PILL", "BILL", "SIGN", "SHINE"]
    extract_words_for_VN_analysis(input_dir, output_dir, keywords)
    