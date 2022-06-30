import customtkinter
import tkinter

class FindItems(customtkinter.CTkToplevel):
    def __init__(self, parent, data):
        customtkinter.CTkToplevel.__init__(self, parent)
        self.data = data
        self.title("Item Lookup")
        self.geometry('500x500') 
        self.mainFrame = customtkinter.CTkFrame(master=self)
        self.mainFrame.grid(row=0, column=0, sticky='nswe')
        self.itemFrames = []
        self.count = 0
        for key, value in self.data.items():
            self.itemFrames.append(customtkinter.CTkLabel(master=self.mainFrame, text=value))
            self.itemFrames[self.count].grid(row=self.count, column=0)
            self.count += 1
        

            
            