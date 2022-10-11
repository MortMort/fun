import os, re
 
# (EDIT): The path to the music files. If script is in folder with music files
# then dont set the path
#path = "/Users/martin/Downloads/Test"
path = os.path.dirname(__file__)
# An array of the .int files located in the path folder
files = os.listdir(path)


# 01. / A1.
# ----------------

pattern = "^(\d{2}. |\w\d\. |\w\. )(.+)( - )(.+)"     # The search pattern
replace = r'\2\3\1\4'         # The replacement
 
# Create a pattern object for pattern matching
pattern_obj = re.compile(pattern)
 
for filename in files:
    # Combine path and filename
    full_path = os.path.join(path, filename)
    # Check if an actual file is located at the full_path location
    if os.path.isfile(full_path):
        # Create a match object
        match = pattern_obj.search(filename)
        if not match :
            continue
        try:
            # Replace the match with the replacement
            new_name = match.expand(replace)
            new_name_full = os.path.join(path, new_name)
        except re.error:
            continue
        if os.path.isfile(new_name_full):
            print('%s -> %s skipped' % (filename, new_name))
        else:
            os.rename(full_path, new_name_full)
            print('%s -> %s succesfull' % (filename, new_name))


# 01 / A1
# ----------------

pattern = "^(\d{2}|\w\d|\w)( )(.+)( - )(.+)"
replace = r'\3\4\1. \5'
 
comp = re.compile(pattern)
  
for filename in files:
    #print('filename = %s' % (filename))
    full_path = os.path.join(path, filename)
    #print('fullpath = %s' % (full_path))
    if os.path.isfile(full_path):
        match = comp.search(filename)
        if not match :
            continue
        try:
            new_name = match.expand(replace)
            new_name_full = os.path.join(path, new_name)
        except re.error:
            continue
        if os.path.isfile(new_name_full):
            print('%s -> %s SKIPPED' % (filename, new_name))
        else:
            os.rename(full_path, new_name_full)
            print('%s -> %s SUCCESS' % (filename, new_name))



# Remove any possible residuals 
# ----------------

pattern = "^(- |\. |-|\.)(.+)"
replace = r'\2'
 
comp = re.compile(pattern)
  
for filename in files:
    #print('filename = %s' % (filename))
    full_path = os.path.join(path, filename)
    #print('fullpath = %s' % (full_path))
    if os.path.isfile(full_path):
        match = comp.search(filename)
        if not match :
            continue
        try:
            new_name = match.expand(replace)
            new_name_full = os.path.join(path, new_name)
        except re.error:
            continue
        if os.path.isfile(new_name_full):
            print('%s -> %s SKIPPED' % (filename, new_name))
        else:
            os.rename(full_path, new_name_full)
            print('%s -> %s SUCCESS' % (filename, new_name))


            