import re
import os
from glob import glob
from pathlib import Path

# A file will be renamed if any part of the file name matches the pattern.
# The replacements are the WHOLE file name and not just the matching 
# parts of the file name.

# EDIT: The path to the music files. If script is in folder with music files
path = "/Users/martin/Downloads/Test 2/**/"
# EDIT: Define patterns to look for and the replacements. 
patterns = ["^(\d{2}. |\w\d\. |\w\. )(.+)( - )(.+)", 
            "^(\d{2}|\w\d|\w)( )(.+)( - )(.+)", 
            "^(- |\. |-|\.)(.+)"]
replacements = [r'\2\3\1\4', 
                r'\3\4\1. \5', 
                r'\3\4\1. \5']

all_dirs = glob(path, recursive=True)

for dir in all_dirs:

    for ii in range(len(patterns)):
        files = os.listdir(dir)

        pattern = patterns[ii]     # The search pattern
        replace = replacements[ii] # The replacement
        
        # Create a pattern object for pattern matching
        pattern_obj = re.compile(pattern)
        
        for filename in files:
            # Combine path and filename
            full_path = os.path.join(dir, filename)
            # Check if an actual file is located at the full_path location
            if os.path.isfile(full_path):
                # Create a match object
                match = pattern_obj.search(filename)
                if not match :
                    continue
                try:
                    # Replace the match with the replacement
                    new_name = match.expand(replace)
                    new_name_full = os.path.join(dir, new_name)
                except re.error:
                    continue
                if os.path.isfile(new_name_full):
                    print('%s -> %s SKIPPED' % (filename, new_name))
                else:
                    os.rename(full_path, new_name_full)
                    print('%s -> %s SUCCESS' % (filename, new_name))