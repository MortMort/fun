# Import Tkinter library
import tkinter as tk

# Create an instance of tkinter frame
root = tk.Tk()

# Set the geometry of Tkinter frame
root.geometry("250x200")

# Define Function to print the input value
def display_input():
   print("Input for Python:", var1.get())
   print("Input for C++:", var2.get())

# Define empty variables
inclsubdir = tk.IntVar()

# Define a Checkbox
t1 = tk.Checkbutton(root, text="Include subdirectories?", variable=inclsubdir, onvalue=1, offvalue=0)
t1.pack()


root.mainloop()