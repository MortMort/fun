import re                   # Regular Expressions
import os                   # Folders and stuff
from glob import glob       # Retreving a list of folders and subfolders
import PySimpleGUI as sg    # GUI for inputting stuffff
import tkinter as tk
from tkinter import filedialog
import sys                  # Exit code when error occurs

# TO-DO: Make a pop-up which states whether any files have been changed
# and maybe which files??
# TO-DO: Remove any double spaces



# EDIT: Define patterns to look for and the replacements:
patterns = ["^(\d{2}. |\w\d\. |\w\. )(.+)( - )", 
            "^(\d{2}|\w\d|\w)( )(.+)( - )", 
            "^(- |\. )",
            "  {2,}"
            ]
replacements = [r'\2\3\1', 
                r'\3\4\1. ', 
                r'',
                r''
                ]


# Open pop-up to input folder for file renaming
# ==============================================================================
root = tk.Tk()
root.withdraw()

# Opens a pop-up. The selected directory path goes into selected_dir
selected_dir = filedialog.askdirectory()

# Check whether a folder was selected. Exit code if not
if len(selected_dir) == 0:
    print("Error! No directory selected. Stopping the script")
    sys.exit()

# Add /**/ to path such that subdirectories are found when using glob()
path = os.path.join(selected_dir, "**", "")

# Create list of folders and subfolders
all_dirs = glob(path, recursive=True)
# Loop through the list of directories
for dir in all_dirs:
    # Loop through every pattern
    for ii in range(len(patterns)):
        # Create a list of the files inside the directory
        files = os.listdir(dir)
        # Loop through every filename in the given directory
        for filename in files:
            # Combine path and filename
            full_path = os.path.join(dir, filename)
            # Check if an actual file is located at the full_path location
            if os.path.isfile(full_path):
                # Create a match object. If no match is found None is returned
                match = re.search(patterns[ii], filename)
                if not match :
                    continue
                try:
                    # Replace the match pattern with the replacement
                    new_name = re.sub(patterns[ii], replacements[ii], filename)
                    new_name_full = os.path.join(dir, new_name)
                except re.error:
                    continue
                if os.path.isfile(new_name_full):
                    print('%s -> %s SKIPPED' % (filename, new_name))
                else:
                    os.rename(full_path, new_name_full)
                    print('%s -> %s SUCCESS' % (filename, new_name))