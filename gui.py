import tkinter
import tkinter.messagebox
import customtkinter
from TradePostTracker import TradePostTracker
import math
import time
import threading

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class Splash(customtkinter.CTkToplevel):
    def __init__(self, parent):
        customtkinter.CTkToplevel.__init__(self, parent)
        self.title("Splash")
        self.loadingLabel = customtkinter.CTkLabel(master=self,
                                                   text='Loading database',
                                                   text_font=("Roboto Medium", -16))
        self.loadingLabel.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)
        self.update()
        

class App(customtkinter.CTk):

    WIDTH = 1200
    HEIGHT = 520

    def __init__(self, trader):
        super().__init__()
        self.withdraw()
        splash = Splash(self)
        self.trader = trader
        self.watchNumber = tkinter.StringVar()
        self.trader.parseConfig()
        self.trader.loadItemData()
        self.settingsOpen = False
        self.itemFrames = []
        self.updatePrices = []
        self.watchNumber.set('Items being tracked: {}'.format(str(len(self.trader.itemIds))))
        self.title("GW2 trading tracker")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.count = 0
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame_left = customtkinter.CTkFrame(master=self)
        self.frame_left.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)
        
        
        
        
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20) 

        
        
        
        
        
        
        
        
        
        self.infoHead = customtkinter.CTkLabel(master=self.frame_left, text="Information", 
                                               text_font=("Roboto Medium", -16))
        self.infoHead.grid(row=1, column=0, pady=10, padx=10)  
        self.itemsInDb = customtkinter.CTkLabel(master=self.frame_left, 
                                                textvariable=self.watchNumber, 
                                                fg_color=("white", "gray38"), 
                                                justify=tkinter.CENTER)
        self.itemsInDb.grid(row=3, column=0, sticky="nw", pady=10, padx=10)  
        self.itemsInDb = customtkinter.CTkLabel(master=self.frame_left,
                                                   text='Items in database: ' + str(len(self.trader.itemData)),
                                                   fg_color=("white", "gray38"),
                                                   justify=tkinter.CENTER)
        self.itemsInDb.grid(row=2, column=0, sticky="nw", pady=10, padx=10)
        self.settings = customtkinter.CTkButton(master=self.frame_left,
                                                fg_color=("gray75", "gray30"),
                                                text='Settings',
                                                command=lambda: self.showSettings())
        self.settings.grid(row=4, sticky='s')  
        self.settingsFrame = customtkinter.CTkFrame(master=self.frame_left)
        self.server_var = tkinter.StringVar(self.settingsFrame, self.trader.server)
        self.port_var = tkinter.StringVar(self.settingsFrame, self.trader.port)
        self.from_email_var = tkinter.StringVar(self.settingsFrame, self.trader.sender)
        self.password_var = tkinter.StringVar(self.settingsFrame, self.trader.password)       
        self.to_email_var = tkinter.StringVar(self.settingsFrame, self.trader.receiver)        
        self.addFrame = customtkinter.CTkFrame(master=self.frame_left)
        self.addFrame.grid(row=1, column=0, sticky='w', pady=0, padx=20)
        self.entry = customtkinter.CTkEntry(
            self.addFrame, 
            width=100, 
            placeholder_text='Item ID'
            )
        self.entry.grid(row=0, column=0, sticky='w', pady=0, padx=0)
        self.add = customtkinter.CTkButton(master=self.addFrame,
                                           width=20,
                                                text="+",
                                                fg_color=("gray75", "gray30"),
                                                command=self.addItem)
        self.add.grid(row=0, column=1, sticky='w', pady=0, padx=0)         
        self.listItems()
        splash.destroy()
        self.trader.loading = False
        
    def showSettings(self):
        if self.settingsOpen == True:
            self.settingsOpen = False
            self.settings.configure(fg_color=("gray75", "gray30"))
            self.settingsFrame.grid_remove()
            return
        else:
            self.settingsOpen = True
            self.settings.configure(fg_color=("#315399"))
        self.settingsFrame.grid(row=5)
        self.server = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='SMTP Server',
                                             textvariable=self.server_var)
        self.server.grid(row=5, pady=5, padx=5)
        self.port = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Port',
                                             textvariable=self.port_var)
        self.port.grid(row=6, pady=5, padx=5)
        self.from_email = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Send from',
                                             textvariable=self.from_email_var)
        self.from_email.grid(row=7, pady=5, padx=5)
        self.password = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Password',
                                             show="*",
                                             textvariable=self.password_var)
        self.password.grid(row=8, pady=5, padx=5)
        self.to_email = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Send to',
                                             textvariable=self.to_email_var)
        self.to_email.grid(row=9, pady=5, padx=5)
        self.saveEmail = customtkinter.CTkButton(master=self.settingsFrame,
                                                 text='Save',
                                                 fg_color=("#315399"),
                                                 command=self.parseEmail)
        self.saveEmail.grid(row=10, pady=5, padx=5)           
                                             
    def parseEmail(self):
        self.saveEmail.configure(fg_color=("gray75", "gray30"),
                                 state=tkinter.DISABLED)
        self.settings.configure(fg_color=("gray75", "gray30"))
        self.trader.server = self.server_var.get()
        self.trader.port = int(self.port_var.get())
        self.trader.sender = self.from_email_var.get()
        self.trader.password = self.password_var.get()
        self.trader.receiver = self.to_email_var.get()
        self.trader.addToConfig()
        self.settingsOpen = False
        self.settingsFrame.grid_remove()        
    
    def listItems(self):
        self.watchNumber.set('Items being tracked: {}'.format(str(len(self.trader.itemIds))))           
        for index, item in enumerate(self.trader.itemIds):
            self.listItemFrame(item)
            self.count += 1
    def getPrice(self, price):
        price = int(price)
        gold = math.floor(price / 10000)
        price = (price / 10000 - gold) * 100
        silver = math.floor(price)
        price = price - silver
        copper = math.floor(price * 100)
        return (gold, silver, copper)    

                                                    
    def listItemFrame(self, item):
        self.trader.currentPrices[item[0]] = [tkinter.StringVar(), tkinter.StringVar()]
        if item[3] == 't':
            self.trader.speaker[item[0]] = tkinter.StringVar(value=self.trader.notiTrue)
        else:
            self.trader.speaker[item[0]] = tkinter.StringVar(value=self.trader.notiFalse)
        price = self.getPrice(item[2])
        gold_var = tkinter.StringVar()
        gold_var.set(str(price[0]))

        silver_var = tkinter.StringVar()
        silver_var.set(str(price[1]))

        copper_var = tkinter.StringVar()
        copper_var.set(str(price[2]))

        try:
            self.itemFrames[self.count] = customtkinter.CTkFrame(master=self.frame_right)
        except:
            self.itemFrames.append(customtkinter.CTkFrame(master=self.frame_right, corner_radius=0))

        self.updatePrices.append(None)
        self.updatePrices[self.count] = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                                                text='ü',
                                                                width=5,
                                                                text_font=('Wingdings'),
                                                                fg_color=("gray75", "gray30"),
                                                                command=lambda i=self.count, it=item, p=(gold_var, silver_var, copper_var): self.updatePrice(i, it, p))

        def callback(index, *args):
            self.updatePrices[index].grid(row=0, column=6, pady=2, padx=2)  
        copper_var.trace_add('write', lambda *args, i=self.count: callback(i, *args))
        silver_var.trace_add('write', lambda *args, i=self.count: callback(i, *args))
        gold_var.trace_add('write', lambda *args, i=self.count: callback(i, *args))
        self.itemFrames[self.count].grid(row=self.count, column=0, columnspan=13, sticky="nswe")
        self.itemFrames[self.count].columnconfigure(0, minsize=100)
        self.itemFrames[self.count].columnconfigure(1, minsize=400)
        self.itemFrames[self.count].columnconfigure((3,4), minsize=40)
        self.itemFrames[self.count].columnconfigure(5, minsize=100)
        self.itemFrames[self.count].columnconfigure(6, minsize=40)
        
        self.trader.alertButtons[item[0]] = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                                textvariable=self.trader.speaker[item[0]],
                                                text_font=('',-20),
                                                width=5,
                                                fg_color=("#A7171A"),
                                                command=lambda i=item: self.trader.changeMute(i))
        self.trader.alertButtons[item[0]].grid(row=0, column=12, pady=2, padx=2)        
        itemIdLabel = customtkinter.CTkLabel(master=self.itemFrames[self.count],
                                              text=item[0],
                                              width=100,
                                              text_font=("Roboto Medium", -16))
        itemIdLabel.grid(row=0, column=0, pady=2, padx=2, sticky='w')        
        
        itemLabel = customtkinter.CTkLabel(master=self.itemFrames[self.count],
                                              text=self.trader.itemData[int(item[0])],
                                              width=100,
                                              text_font=("Roboto Medium", -16))
        itemLabel.grid(row=0, column=1, sticky='w', pady=2, padx=2)
        buyButton = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                         width=20,
                                         command=lambda i=self.count, it=item, b='buy': checkbox_event(i, it, b),
                                         text='Buying')
        buyButton.grid(row=0, column=3, pady=2, padx=2) 
        
        sellButton = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                          width=20,
                                          command=lambda i=self.count, it=item, b='sell': checkbox_event(i, it, b),
                                          text='Selling')
        sellButton.grid(row=0, column=4, pady=2, padx=2) 
        
        priceFrame = customtkinter.CTkFrame(master=self.itemFrames[self.count])
        priceFrame.grid(row=0, column=5)
        
        priceGold = customtkinter.CTkEntry(master=priceFrame,
                                           placeholder_text='G',
                                           textvariable=gold_var,
                                           width=40)
        priceGold.grid(row=0, column=0)
        priceSilver = customtkinter.CTkEntry(master=priceFrame,
                                           placeholder_text='S',
                                           textvariable=silver_var,
                                           width=40)
        priceSilver.grid(row=0, column=1)
        priceCopper = customtkinter.CTkEntry(master=priceFrame,
                                           placeholder_text='C',
                                           textvariable=copper_var,
                                           width=40)
        priceCopper.grid(row=0, column=2)            
        
        itemButton = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                            text=u"\u274C",
                                            text_color='red',
                                            width=5,
                                            fg_color=("gray75", "gray30"),
                                            command=lambda i=self.count, it=item: self.deleteItem(i, it))
        itemButton.grid(row=0, column=13, sticky='s', pady=10, padx=(40, 20))
        
        def checkbox_event(index, item, setting):          
            self.trader.itemIds[index][1] = setting
            self.trader.addToConfig()
            if setting == 'sell':
                currentPrice = customtkinter.CTkLabel(master=self.itemFrames[index],
                                                      textvariable=self.trader.currentPrices[item[0]][1],
                                                      text_font=("Roboto Medium", -16))
                currentPrice.grid(row=0, column=11, pady=2, padx=2)                    
                sellButton.configure(state=tkinter.DISABLED,
                                                  fg_color="#315399")
                buyButton.configure(state=tkinter.NORMAL,
                                 fg_color=("gray75", "gray30"))
            elif setting == 'buy':
                currentPrice = customtkinter.CTkLabel(master=self.itemFrames[index],
                                                      textvariable=self.trader.currentPrices[item[0]][0],
                                                      text_font=("Roboto Medium", -16))
                currentPrice.grid(row=0, column=11, pady=2, padx=2) 
                sellButton.configure(state=tkinter.NORMAL,
                                 fg_color=("gray75", "gray30"))   
                buyButton.configure(state=tkinter.DISABLED,
                                                 fg_color="#315399")
        checkbox_event(self.count, item, item[1])        
        
        
        
    def updatePrice(self, index, item, price):
        self.updatePrices[index].grid_remove()
        gold = int(price[0].get())
        silver = int(price[1].get())
        copper = int(price[2].get())
        price = gold * 10000 + silver * 100 + copper
        self.trader.itemIds[index][2] = price
        self.trader.addToConfig()    
        
    def deleteItem(self, index, item): 
        self.trader.itemIds[index] = None
        self.trader.addToConfig()
        frame = self.itemFrames[index]
        if frame != None:
            frame.destroy()
            self.itemFrames[index] = None
        self.setWatchNumber()
        self.count -= 1
        
    def addItem(self):
        itemId = int(self.entry.get())
        if itemId not in self.trader.itemData:
            print('Item not found')
        else:
            item = [str(itemId), 'buy', '0', 'f']
            try:
                self.trader.itemIds[self.count] = item
            except:
                self.trader.itemIds.append(item)
            print('inside add', self.trader.itemIds)
            self.listItemFrame(item)
            self.trader.addToConfig()
            self.setWatchNumber()  
            self.count += 1
            
    def on_closing(self):
        self.destroy()

    def setWatchNumber(self):
        n = 0
        for i in self.trader.itemIds:
            if i != None:
                n += 1
        self.watchNumber.set('Items being tracked: {}'.format(str(n)))    
if __name__ == "__main__":
    tradeObject = TradePostTracker()
    tradeObject.startUpdate()
    app = App(tradeObject)
    app.mainloop()