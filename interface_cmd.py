#! python3.6
# -*- coding: utf-8 -*-

""" Bataille navale """

# Auteur : Nicolas Vincent T°S5
# 2017

import tkinter as tk

# Placement grille : choix du bateau, click droit pour le faire pivoter
# Voir notebook pour l'organisation des fenêtres
"""
class App(object):

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

    def say_hi(self):
        print("hi there, everyone!")

root = Tk()
app = App(root)

root.mainloop()
"""


class SimpleappTk(tk.Tk):
    """Test tkinter
    """
    
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        """Initialisation
        """
        
        self.grid()

        self.entryVariable = tk.StringVar()
        self.entry = tk.Entry(self,textvariable=self.entryVariable)
        self.entry.grid(column=0,row=0,sticky='EW')
        self.entry.bind("<Return>", self.onpressenter)
        self.entryVariable.set(u"Enter text here.")

        button = tk.Button(self,text=u"Click me !",
                                command=self.onbuttonblick)
        button.grid(column=1,row=0)

        self.labelVariable = tk.StringVar()
        label = tk.Label(self,textvariable=self.labelVariable,
                              anchor="w",fg="white",bg="blue")
        label.grid(column=0,row=1,columnspan=2,sticky='EW')
        self.labelVariable.set(u"Hello !")

        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())       
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)

    def onbuttonblick(self):
        self.labelVariable.set( self.entryVariable.get()+" (You clicked the button)" )
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)

    def onpressenter(self,event):
        self.labelVariable.set( self.entryVariable.get()+" (You pressed ENTER)" )
        self.entry.focus_set()
        self.entry.selection_range(0, tk.END)

if __name__ == "__main__":
    app = SimpleappTk(None)
    app.title('my application')
    app.mainloop()
