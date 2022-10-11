import re                   # Regular Expressions
import os                   # Folders and stuff
from glob import glob       # Retreving a list of folders and subfolders

import PySimpleGUI as sg    # GUI for inputting stuffff

# Test string for git push

# GUI for inputting path to folder
# TO-DO: Include possibility of inputting folder by selecting it in a window!
# TO-DO: Make code stop running if no path is input!
# ==============================================================================
# Add some color to the windowp
sg.theme('SandyBeach')     
  
# Very basic window. Return values using automatic-numbered keys
layout = [
    [sg.Text('Please enter path. e.g. "/Users/martin/Documents')],
    [sg.Text('Path', size =(15, 1)), sg.InputText()],
    [sg.Submit(), sg.Cancel()]
]
  
window = sg.Window('Simple data entry window', layout)
event, values = window.read()
window.close()
  
# The input data looks like a simple list  when automatic numbered
print(event, values[0]) 

# The path input via the GUI
input_path = values[0]

path =  os.path.join(input_path, "**", "")
print("joined path:", path) 


# ==============================================================================

# EDIT: Define patterns to look for and the replacements:
patterns = ["^(\d{2}. |\w\d\. |\w\. )(.+)( - )", 
            "^(\d{2}|\w\d|\w)( )(.+)( - )", 
            "^(- |\. )"
            ]
replacements = [r'\2\3\1', 
                r'\3\4\1. ', 
                r''
                ]

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