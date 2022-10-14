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


# FUNCTIONS
def select_dir():
    root = tk.Tk()
    root.withdraw()

    # Opens a pop-up. 
    selected_dir = filedialog.askdirectory()

    # Check whether a folder was selected. Exit code if not
    if len(selected_dir) == 0:
        print("No directory selected!")
    else:
        return selected_dir


def handle_subdirs(directory, incl_subdirs):
    # A simple function for
    if incl_subdirs == True:
        # Add /**/ to path such that subdirectories are found when using glob()
        path = os.path.join(directory, "**", "")
        return glob(path, recursive=True)
    elif incl_subdirs == False:
        path = os.path.join(directory, "")
        return [path]
    else:
        print("Error!: incl_subdirs not set to either of the two options: True, False. Exiting")
        sys.exit()



def pattern_replace(directory, patterns, replacements, incl_subdirs):

    # Handle errors
    if len(patterns) != len(replacements):
        print("Error!: Patterns != replacements! Exiting")
        sys.exit()
    
    all_dirs = handle_subdirs(directory, incl_subdirs)

    print("List of renamed files:")


    for ii in range(len(patterns)):
        # Loop through the list of directories
        for dir in all_dirs:
            # Create a list of the files inside the directory
            files = os.listdir(dir)
                
            # Loop through every file_name in the given directory
            for file_name in files:
                # Combine path and file_name
                full_file_path = os.path.join(dir, file_name)
                # Check if an actual file is located at the full_file_path location
                if os.path.isfile(full_file_path):
                    # Create a match object. If no match is found None is returned
                    match = re.search(patterns[ii], file_name)
                    if not match :
                        continue
                    try:
                        new_name = re.sub(patterns[ii], replacements[ii], file_name)
                        new_name_full = os.path.join(dir, new_name)
                    except re.error:
                        continue
                    os.rename(full_file_path, new_name_full)
                    print('%s -> %s' % (file_name, new_name))        




def upper_case_first_letter(directory, incl_subdirs):

    # Creates a list of subdirectories. If incl_subdirs if false
    # the list just includes one directory
    all_dirs = handle_subdirs(directory, incl_subdirs)

    # The following pattern will pick out any lowercase characters at beginning
    # of words
    pattern = r"(?<!\.)\b[a-z]"

    print("List of uppercase'd files:")

    for dir in all_dirs:
        # Create a list of the files inside the directory
        files = os.listdir(dir)
        # Loop through every file_name in the given directory
        for file_name in files:
            # Combine path and file_name
            full_file_path = os.path.join(dir, file_name)
            # Check if an actual file is located at the full_file_path location
            if os.path.isfile(full_file_path):
                # Create a match object. If no match is found None is returned
                match = re.search(pattern, file_name)
                if not match :
                    continue
                try:
                    # Find all (lowercase) letters matching the pattern
                    lower_case = re.findall(pattern, file_name)
                    new_name_temp = file_name # Predefine temporary name from file_name
                    # In the following loop lowercase character is flipped to
                    # upper case and replaced with the re.sub() function iteratively
                    for char in lower_case:
                        char_pattern = r"(?<!\.)\b" + char  # NOTE: This pattern should match
                                                            # the pattern in the top of the script
                        new_name_temp = re.sub(char_pattern, char.upper(), new_name_temp)
                    new_name = new_name_temp    
                    new_name_full = os.path.join(dir, new_name)
                except re.error:
                    continue
                os.rename(full_file_path, new_name_full)
                print('%s -> %s' % (file_name, new_name))


def create_filelist(all_dirs):
    # NOT USED CURRENTLY

    # IF all_dirs is not in a list format then make it into a list
    if str(type(all_dirs)) == "<class 'str'>":
        dir_list = [all_dirs]
    else:
        dir_list = all_dirs

    # Predefine list of paths to every file
    full_file_path_list = []
    file_list = []
    for dir in dir_list:
        # Create a list of the files inside the directory
        files = os.listdir(dir)

        # Loop through every file_name in the given directory
        for file_name in files:
            file_list.append(file_name)
            # Combine path and file_name
            full_file_path = os.path.join(dir, file_name)
            # Check if an actual file is located at the full_file_path location
            if os.path.isfile(full_file_path):
                full_file_path_list.append(full_file_path)
    
    return file_list, full_file_path_list

def find_renamed_files(original_file_list, new_file_list):

    if len(original_file_list) != len(new_file_list):
        print("Error!: The two file lists are not the same length! Exiting")
        sys.exit()
    
    # Set up list
    renamed_list = []
    original_list = []


    # Set up iterator
    new_file_iter = iter(new_file_list)
    # Go through list of files
    for original_file in original_file_list:
        new_file = next(new_file_iter)
        if original_file != new_file:
            renamed_list.append(new_file)
            original_list.append(original_file)
            print('%s -> %s' % (original_file, new_file))


# ==============================================================================
# SCRIPT

# EDIT: Define patterns to look for and the replacements:

# Patterns for moving ex 01 and A1 to after " - "
patterns = [
            "^(\d{2}. |\w\d\. |\w\. )(.+)( - )",    # 01. -> - 01.
            "^(\d{2}|\w\d|\w)( )(.+)( - )",         # 01 -> - 01.
            "^(- +|\. +| +)",                       # Remove "- " and ". " and " " from start
            " {2,}"                                 # Replace two or more spaces with one space
            ]
replacements = [
                r'\2\3\1', 
                r'\3\4\1. ',
                r'',
                r' '
                ]

# Patterns for replacing ex 01 with A1.
patterns2 = [
            r"((01 )|(01\. ))",
            r"((02 )|(02\. ))",
            r"((03 )|(03\. ))",
            r"((04 )|(04\. ))",
            r"( \w\d)( )"
            ]
replacements2 = [
                r'A1. ',
                r'A2. ',
                r'B1. ',
                r'B2. ',
                r'\1.\2'
                ]

# Adding this line to more easily differnetiate file erros and script output
# form the annoying Alpha value message..
print("------------------------------------------------------------------")

# Opens a pop-up. The selected directory path goes into selected_dir
selected_dir = select_dir()

pattern_replace(selected_dir, patterns, replacements, incl_subdirs = 0)
upper_case_first_letter(selected_dir, incl_subdirs=False)

# PROBLEM: the function does not run through pattern recursively!
#for ii in range(len(patterns2)):
pattern_replace(selected_dir, patterns2, replacements2, incl_subdirs=0)


find_renamed_files(["file1", "file2"], ["file1", "fileFoo"])