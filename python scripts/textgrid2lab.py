#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:29:08 2020

@author: adamguo
"""

import os, textgrids

def textgrid2lab(input_dir, output_dir,
                 text_to_ignore,
                 target_tier = "Words",
                 uppercase = True,
                 ignore_nonspeech = True,
                 strip_punc = True):
    """ Convert (word-aligned) TextGrid annotations to LAB format.
    
    input_dir:
        Directory of folder where the TextGrids are stored.
    ouput_dir:
        Directory of folder where the output LAB files will be saved.
    text_to_ignore:
        A list of text to ignore.
    target_tier:
        Tier to be extracted and converted (default: "Words").
    uppercase:
        Convert all words to uppercase? (default: True)
    ignore_nonspeech:
        Ignore nonspeech labels (e.g., !SIL)? (default: True)
    strip_punc:
        Strip off puncuations (e.g., - and ,)? (default: True)    
    """
    
    # Get the TextGrid files in the input directory
    all_textgrids = [i for i in os.listdir(input_dir) if i.endswith(".TextGrid")]
    
    # Define punctuation
    punctuation = '!"#$%&\()*+,-./:;<=>?@[\\]^_`{|}~ '
    
    # Iterate over all TextGrid files
    for textgrid_file in all_textgrids:
        textgrid = textgrids.TextGrid(os.path.join(input_dir, textgrid_file))
        
        # Create an empty list for storing all text of this TextGrid
        all_text = []
        
        # Itervate over all intervals in target_tier
        for interval in textgrid[target_tier]:
            text = interval.text
            
            # Check whether to ignore nonspeech labels
            
            # If yes
            if ignore_nonspeech:
                
                # If text is anything other than !SIL, a nonspeech label, or blank
                if not (text == "!SIL" or text.startswith("<") or text == ""):
                    
                    # If yes, strip off the punctuation marks defined above
                    if strip_punc:
                        text = "".join([char for char in text if char not in punctuation])
                    
                    if text not in text_to_ignore:
                        # Add the result to all_text
                        all_text.append(text)
                        
                    else:
                        pass
                        
                else:
                    pass
            
            # If not ignoring nonspeech, then include everything
            else:
                
                # If yes, strip off the punctuation marks defined above
                if strip_punc:
                    text = "".join([char for char in text if char not in punctuation])
                
                if text not in text_to_ignore:
                    # Add the result to all_text
                    all_text.append(text)
                    
                else:
                    pass
        
        # Combine all text in the all_text list into one long string (separated by space)
        all_text_str = " ".join(all_text)
        
        # Finally, check if it has to be converted to uppercase
        if uppercase:
            all_text_str = all_text_str.upper()
        
        # Now write text to LAB file in the output folder
        output = open(os.path.join(output_dir,
                                   textgrid_file.replace(".TextGrid", ".lab")),
                      "w")
        output.write(all_text_str)
        output.close()
    
    print("\nDone!")

if __name__ == "__main__":
    text_to_ignore = ["'KERCHANQUE'", "'NEEDO'", "'RADON'", "'S", "'VE",
                      "1", "1SIL", "A.", "A.S", "GA"]
    input_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/channels separated/sentenceReadingClear"
    output_dir = "/Users/adamguo/Desktop/Research/Clear speech corpora/LUCID/recordings/lab files/sentenceReadingClear"   
    textgrid2lab(input_dir, output_dir, text_to_ignore)