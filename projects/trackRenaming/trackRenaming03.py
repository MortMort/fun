from ast import pattern
import re                   # Regular Expressions
import os                   # Folders and stuff
from glob import glob
from turtle import title       # Retreving a list of folders and subfolders
import PySimpleGUI as sg    # GUI for inputting stuffff
import tkinter as tk        # Not used currently but it can be used
                            # to make nicer dialog boxes perhaps?
import tkfilebrowser
import sys                  # Exit code when error occurs

# TO-DO list
# - Make a pop-up which states whether any files have been changed
#   and maybe which files??
# - Check out the following link for perhaps selecting a pattern and such:
#   https://holypython.com/gui-with-python-checkboxes-and-radio-buttons-pysimplegui-part-ii/
# - Add functionality to not rename files if there already excists a file with the name

# FUNCTIONS
def select_dir():
    # Open a dialog window to select and return a folder path

    root = tk.Tk()
    root.withdraw()
    
    # Opens a pop-up. 
    selected_dir = tk.filedialog.askdirectory()

    # Check whether a folder was selected. Exit code if not
    if len(selected_dir) == 0:
        print("Error!: No directory selected in directory dialog box! Continuing though.")
    else:
        return selected_dir


def handle_subdirs(directory, incl_subdirs):
    # Returns a list of either one or several directories.

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
    # Replaces either a list of patterns with a list of replacements or a
    # single pattern with a single replacement in one or several
    # directories based on whether one chooses to include subdirectories.

    # Check if strings. If so, put into list
    if (str(type(patterns)) == "<class 'str'>"):
        patterns = [patterns]
    if (str(type(replacements)) == "<class 'str'>"):
        replacements = [replacements]

    # Handle errors
    if len(patterns) != len(replacements):
        print("Error!: Patterns != replacements! Exiting")
        sys.exit()
    
    if (str(type(directory)) != "<class 'str'>"):
        print("Error!: No directory input for pattern search! Exiting.")
        sys.exit()
    elif (len(directory) < 5):
        print("Error!: No directory input for pattern search! Exiting.")
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
                        # Replace ii'th pattern with ii'th replacement
                        new_name = re.sub(patterns[ii], replacements[ii], file_name)
                        new_name_full = os.path.join(dir, new_name)
                    except re.error:
                        continue
                    os.rename(full_file_path, new_name_full)
                    print('"%s" -> "%s"' % (file_name, new_name))   


def upper_case_first_letter(directory, incl_subdirs):
    # Uppercase the first letter in every word of all files in one or
    # several directories

    # Handle erros
    if (str(type(directory)) != "<class 'str'>"):
        print("Error!: No directory input for pattern search! Exiting.")
        sys.exit()
    elif (len(directory) < 5):
        print("Error!: No directory input for pattern search! Exiting.")
        sys.exit()

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
    # Creates a list of files from a list of one or more folders
    # NOT USED CURRENTLY

    # IF all_dirs is not in a list format then make it into a list
    if str(type(all_dirs)) == "<class 'str'>":
        dir_list = [all_dirs]
    else:
        dir_list = all_dirs

    # Predefine list of paths to every file
    full_path_file_list = []
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
                full_path_file_list.append(full_file_path)
    
    return file_list, full_path_file_list


def find_renamed_files(original_file_list, new_file_list):
    # NOT USED CURRENTLY
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


def select_options(*default_directory):
    # Used to select options and to select a folder
    # Used such that options can be included when running the script
    # Defualt directory is input such that 
	
    root = tk.Tk()
    root.title("Options")
    
    def cancel_renaming():
        # Exits the script
        print("Renaming cancelled: Exiting script")
        sys.exit()


    def open_folder():
        # Opens a dialog window for selection of a folder

        global selected_dir
        selected_dir = tk.filedialog.askdirectory()
            

    def exit_tk():
        # When pressing "Continue". 
        global selected_dir
        # Handle not choosing a folder
        if 'selected_dir' not in globals() or len(selected_dir) == 0:
            if default_directory == 0:
                print("Warning!: No directory selected in directory dialog box! Folder set to default.")
                selected_dir = default_directory
            else:
                print("Warning!: No directory selected in directory dialog box and no default folder supplied. Returning empty string")
                selected_dir = ""
        #root.destroy()
        root.quit()


    # get screen width and height
    screen_width = root.winfo_screenwidth() # width of the screen
    screen_height = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk win window
    box_width = 250 # width for the Tk window
    box_height = 200 # height for the Tk window
    x_corr = (screen_width * 0.5) - (box_width/2)
    y_corr = (screen_height * 0.25) - (box_height/2)

    # set the dimensions of the screen and where it is placed
    root.geometry('%dx%d+%d+%d' % (box_width, box_height, x_corr, y_corr))

    # Define empty variables for checkboxes
    checkbox_val = tk.IntVar()
    checkbox_val_2 = tk.IntVar()
    checkbox_val_3 = tk.IntVar()

    # Set up checkboxes
    t1 = tk.Checkbutton(root, text="Include subdirectories?", 
    variable=checkbox_val, onvalue=1, offvalue=0)
    t1.pack()
    t2 = tk.Checkbutton(root, text="01 -> A1?", 
    variable=checkbox_val_2, onvalue=1, offvalue=0)
    t2.pack()
    t3 = tk.Checkbutton(root, text="Underscores to spaces?", 
    variable=checkbox_val_3, onvalue=1, offvalue=0)
    t3.pack()

    # Set up buttons
    tk.Button(root, text="Select folder", command=open_folder).pack()
    tk.Button(root, text="Start renaming", command=exit_tk).pack()
    tk.Button(root, text="Cancel renaming", command=cancel_renaming).pack()

    root.mainloop()


    return selected_dir, checkbox_val.get(), checkbox_val_2.get(), checkbox_val_3.get()
    

    





# ==============================================================================
# SCRIPT

# Adding this line to more easily differnetiate file erros and script output
# from the annoying Alpha value message..
print("------------------------------------------------------------------")


# Patterns for moving ex 01 and A1 to after " - "
patterns = [
            "([a-zA-Z])-([a-zA-Z])",                # Firstly "-" -> " - "
            "^(\d{2}. |\w\d\. |\w\. )(.+)( - )",    # 01. -> - 01.
            "^(\d{2}|\w\d|\w)( )(.+)( - )",         # 01 -> - 01.
            "^(- +|\. +| +)"                        # Remove "- " and ". " and " " from start
            ]
replacements = [
                r'\1 - \2',
                r'\2\3\1', 
                r'\3\4\1. ',
                r''
                ]

# Patterns for replacing ex 01 with A1.
patterns2 = [
            r"((\b01 )|(\b01\. ))",
            r"((\b02 )|(\b02\. ))",
            r"((\b03 )|(\b03\. ))",
            r"((\b04 )|(\b04\. ))",
            r"( \w\d)( )"               # Put . after
            ]
replacements2 = [
                r'A1. ',
                r'A2. ',
                r'B1. ',
                r'B2. ',
                r'\1.\2'
                ]

# Patterns for cleaning up names in general.
patterns3 = [
            " {2,}"        # Replace two or more spaces with one space
            ]
replacements3 = [
            r' '
            ]

# Note when using Path Finder use "Copy path as UNIX" for the correct
# path format. Spaces (" ") should not be backslashed

default_dir = "/Volumes/28862793/Music/DJ/New Discoveries/29. October/Silat Beksi - Special Edition [BBR005]"
#elected_dir = select_dir()

# Opens a dialog to select whether to include subdirectories
selected_dir, incl_subdirs, dig_to_vinyl, rvm_underscores = select_options()

# Turn underscores into spaces
if rvm_underscores:
    pattern_replace(selected_dir, r"(?<!\.)\_", " ", incl_subdirs)

# 01. name -> name - 01.
pattern_replace(selected_dir, patterns, replacements, incl_subdirs)

# 01 -> A1, 03 -> B1
if dig_to_vinyl:
    pattern_replace(selected_dir, patterns2, replacements2, incl_subdirs)

# Clean up files
#pattern_replace(selected_dir, patterns3, replacements3, incl_subdirs)

# Uppercase first letter in words?
upper_case_first_letter(selected_dir, incl_subdirs)

# Put the damn Cover back to cover!
#pattern_replace(selected_dir, "Cover\.jpg", "cover.jpg", incl_subdirs)





# find_renamed_files(["file1", "file2"], ["file1", "fileFoo"])