import customtkinter

class LoadingSplash(customtkinter.CTkToplevel):
    def __init__(self, parent):
        customtkinter.CTkToplevel.__init__(self, parent)
        self.title("Splash")
        self.loadingLabel = customtkinter.CTkLabel(master=self,
                                                   text='Loading database',
                                                   text_font=("Roboto Medium", -16))
        self.loadingLabel.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)
        self.update()