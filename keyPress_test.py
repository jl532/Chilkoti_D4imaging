#class analysisConfigurations():
#    def printSingle(self):
#        print("single array analysis selected")
#        
#    def printMult(self):
#        print("multiple array analysis selected")
#    
#    def __init__(self):
#        self.root = tk.Tk()        
#        buttonSingle = tk.Button(self.root, 
#                                 text = "Analyze Single Array",
#                                 command = self.printSingle)
#        buttonSingle.pack()
#        
#        buttonMultiple = tk.Button(self.root, 
#                                   text = "Analyze Multiple Arrays",
#                                   command = self.printMult)
#        buttonMultiple.pack()
#        
#        buttonQuit = tk.Button(self.root, 
#                               text = "Quit Program", 
#                               command = self.quitProgram)
#        buttonQuit.pack()
#        
#        self.root.mainloop()
#        
#    def quitProgram(self):
#        self.root.destroy()
#        
#test = analysisConfigurations()

#rootWindow = tk.Tk()
#buttonSingle = tk.Button(rootWindow, 
#                         text = "Analyze Single Array",
#                         command = lambda: print("single array analysis selected"))
#buttonSingle.pack()
#
#buttonMultiple = tk.Button(rootWindow, 
#                           text = "Analyze Multiple Arrays",
#                           command = lambda: print("multiple array analysis selected"))
#buttonMultiple.pack()
#
#buttonQuit = tk.Button(rootWindow, 
#                       text = "Quit Program", 
#                       command=lambda: rootWindow.destroy())
#buttonQuit.pack()
#
#rootWindow.mainloop()

import tkinter as tk
from tkinter import messagebox
root = tk.Tk()
root.overrideredirect(1)
root.withdraw()
startBool = messagebox.askyesno("D4 Automated Analysis Algorithm start page (Jason Liu Dec 2017)",
                                "Would you like to analyze your D4 Images?")