import tkinter
import customtkinter
from tradePostTracker import TradePostTracker
from PIL import Image, ImageTk
from loadingSplash import LoadingSplash

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class Gui(customtkinter.CTk):
    def __init__(self, trader):
        super().__init__()
        self.width = 1285
        self.height = 720        
        self.withdraw()
        self.title("GW2 trading tracker")
        self.geometry(f"{self.width}x{self.height}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)        
        splash = LoadingSplash(self)
        self.trader = trader
        self.watchNumber = tkinter.StringVar()
        self.trader.parseConfig()
        self.trader.loadItemData()
        self.settingsOpen = False
        self.itemFrames = []
        self.updatePrices = []
        self.count = 0
        self.goldImage = ImageTk.PhotoImage(Image.open("Images\Gold.png").resize((15,15)))
        self.silverImage = ImageTk.PhotoImage(Image.open("Images\Silver.png").resize((15,15)))
        self.copperImage = ImageTk.PhotoImage(Image.open("Images\Bronze.png").resize((15,15)))
        self.notiTrue = u"\U0001F514"
        self.notiFalse = u"\U0001F515"        
        #self.grid_columnconfigure(1, weight=1)
        #self.grid_rowconfigure(0, weight=1)
        self.frameLeft = customtkinter.CTkFrame(master=self)
        self.frameLeft.grid(row=0, column=0, columnspan=7, sticky="nswe")
        self.frameRight = customtkinter.CTkFrame(master=self)
        self.frameRight.grid(row=0, column=8, sticky="nswe", padx=0, pady=0)    
        # Right info/add/settings panel
        self.addFrame = customtkinter.CTkFrame(master=self.frameRight)
        self.addFrame.grid(row=1, column=0, sticky='nswe', pady=5, padx=5)
        self.vcmd = (self.register(self.checkItemId))
        self.entry = customtkinter.CTkEntry(
            self.addFrame, 
            width=180, 
            placeholder_text='Item ID',
            validate='all', validatecommand=(self.vcmd, '%P'))
        self.entry.grid(row=0, column=0, sticky='nswe', pady=0, padx=0)
        self.add = customtkinter.CTkButton(master=self.addFrame,
                                           width=20,
                                                text="+",
                                                fg_color=("gray75", "gray30"),
                                                command=self.addItem)
        self.add.grid(row=0, column=1, sticky='nswe', pady=0, padx=0)                 
        self.itemsInDb = customtkinter.CTkLabel(master=self.frameRight,
                                                   text='Items in database: ' + str(len(self.trader.itemData)),
                                                   fg_color=("white", "gray38"),
                                                   width=200,
                                                   justify=tkinter.CENTER)
        self.itemsInDb.grid(row=2, column=0, sticky="nswe", pady=5, padx=0)
        self.itemsWatched = customtkinter.CTkLabel(master=self.frameRight, 
                                                textvariable=self.watchNumber, 
                                                fg_color=("white", "gray38"), 
                                                width=200,
                                                justify=tkinter.CENTER)
        self.itemsWatched.grid(row=3, column=0, sticky="nswe", pady=5, padx=0)          
        self.settings = customtkinter.CTkButton(master=self.frameRight,
                                                fg_color=("gray75", "gray30"),
                                                text='Settings',
                                                width=200,
                                                command=lambda: self.showSettings())
        self.settings.grid(row=4, sticky='nswe', pady=5)  
        self.settingsFrame = customtkinter.CTkFrame(master=self.frameRight)
        self.serverVar = tkinter.StringVar(self.settingsFrame, self.trader.server)
        self.portVar = tkinter.StringVar(self.settingsFrame, self.trader.port)
        self.fromEmailVar = tkinter.StringVar(self.settingsFrame, self.trader.sender)
        self.passwordVar = tkinter.StringVar(self.settingsFrame, self.trader.password)       
        self.toEmailVar = tkinter.StringVar(self.settingsFrame, self.trader.receiver)        
        self.listSavedItems()
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
                                             textvariable=self.serverVar)
        self.server.grid(row=5, pady=5, padx=5)
        self.port = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Port',
                                             validate='all', validatecommand=(self.vcmd, '%P'),
                                             textvariable=self.portVar)
        self.port.grid(row=6, pady=5, padx=5)
        self.fromEmail = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Send from',
                                             textvariable=self.fromEmailVar)
        self.fromEmail.grid(row=7, pady=5, padx=5)
        self.password = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Password',
                                             show="*",
                                             textvariable=self.passwordVar)
        self.password.grid(row=8, pady=5, padx=5)
        self.toEmail = customtkinter.CTkEntry(master=self.settingsFrame,
                                             placeholder_text='Send to',
                                             textvariable=self.toEmailVar)
        self.toEmail.grid(row=9, pady=5, padx=5)
        self.saveEmail = customtkinter.CTkButton(master=self.settingsFrame,
                                                 text='Save',
                                                 fg_color=("#315399"),
                                                 command=self.parseEmail)
        self.saveEmail.grid(row=10, pady=5, padx=5)             
        
    def checkItemId(self, P):
        try:
            self.entry.configure(fg_color=('gray30'))
        except:
            pass
        valid = ['', 'Item ID']
        if str.isdigit(P) or P in valid:
            return True
        else:
            return False 
    
    def digitcheck(self, P):
        valid = ['', 'Gld', 'Slv', 'Cpr']
        if str.isdigit(P) or P in valid:
            return True
        else:
            return False           
    
    def parseEmail(self):
        self.saveEmail.configure(fg_color=("gray75", "gray30"),
                                 state=tkinter.DISABLED)
        self.settings.configure(fg_color=("gray75", "gray30"))
        self.trader.server = self.serverVar.get()
        self.trader.port = int(self.portVar.get())
        self.trader.sender = self.fromEmailVar.get()
        self.trader.password = self.passwordVar.get()
        self.trader.receiver = self.toEmailVar.get()
        self.trader.addToConfig()
        self.settingsOpen = False
        self.settingsFrame.grid_remove()       
        
        
    def changeMute(self, item, priceGold=None, priceSilver=None, priceCopper=None):
        if item[2] == '0' or item[2] == 0:
            priceGold.configure(fg_color='red')
            priceSilver.configure(fg_color='red')
            priceCopper.configure(fg_color='red')  
            self.trader.speaker[item[0]].set(self.notiFalse)
            self.trader.alertButtons[item[0]].configure(fg_color=("#A7171A"))            
            return
        if self.trader.speaker[item[0]].get() == self.notiTrue:
            self.trader.speaker[item[0]].set(self.notiFalse)
            self.trader.alertButtons[item[0]].configure(fg_color=("#A7171A"))
        else: 
            self.trader.speaker[item[0]].set(self.notiTrue)
            self.trader.alertButtons[item[0]].configure(fg_color=("#71C562"))    
        
    def listSavedItems(self):
        self.watchNumber.set('Items being tracked: {}'.format(str(len(self.trader.itemIds))))           
        for index, item in enumerate(self.trader.itemIds):
            self.listSingleItem(item)
            self.count += 1          

    def updatePrice(self, index, item, price, priceGold, priceSilver, priceCopper):
        priceGold.configure(fg_color='gray22')
        priceSilver.configure(fg_color='gray22')
        priceCopper.configure(fg_color='gray22')
        gold = 0
        silver = 0
        copper = 0
        if str.isdigit(price[0].get()):
            gold = int(price[0].get())
        if str.isdigit(price[1].get()):
            silver = int(price[1].get())
        if str.isdigit(price[2].get()):
            copper = int(price[2].get())
        price = gold * 10000 + silver * 100 + copper
        if price == 0:
            self.trader.speaker[item[0]].set(u"\U0001F515")
            self.trader.alertButtons[item[0]].configure(fg_color=("#A7171A"))              
        self.trader.itemIds[index][2] = price
        self.trader.addToConfig()
        self.updatePrices[index].grid_remove()

    def addItem(self):
        try:
            try:
                itemId = int(self.entry.get())
            except:
                self.entry.configure(fg_color=('red'))
            if itemId not in self.trader.itemData:
                self.entry.configure(fg_color=('red'))
                print('Item not found')
            else:
                already_in = False
                for i in self.trader.itemIds:
                    if i != None and int(i[0]) == itemId:
                        already_in = True
                        self.entry.configure(fg_color=('red'))
                        print('already in')
                        break
                if already_in == False:
                    item = [str(itemId), 'buy', '0', 'f']
                    try:
                        self.trader.itemIds[self.count] = item
                    except:
                        self.trader.itemIds.append(item)
                    self.listSingleItem(item)
                    self.trader.addToConfig()
                    self.setWatchNumber()  
                    self.count += 1
        except Exception as e:
            print('error in adding item: ', e)

    def deleteItem(self, index, item): 
        self.trader.itemIds[index] = None
        self.trader.addToConfig()
        frame = self.itemFrames[index]
        if frame != None:
            frame.destroy()
            self.itemFrames[index] = None
        self.setWatchNumber()
        self.count -= 1


    def on_closing(self):
        self.trader.threads[0].stop()
        self.destroy()

    def setWatchNumber(self):
        n = 0
        for i in self.trader.itemIds:
            if i != None:
                n += 1
        self.watchNumber.set('Items being tracked: {}'.format(str(n)))    









    def listSingleItem(self, item):
        self.trader.currentPrices[item[0]] = [[tkinter.StringVar(value='...'), tkinter.StringVar(value='...'), tkinter.StringVar(value='...')], 
                                              [tkinter.StringVar(value='...'), tkinter.StringVar(value='...'), tkinter.StringVar(value='...')]]
        #if item[3] == 't':
        #    self.trader.speaker[item[0]] = tkinter.StringVar(value=self.notiTrue)
        self.trader.speaker[item[0]] = tkinter.StringVar(value=self.notiFalse)
        price = self.trader.convertPrice(item[2])[1]
        gold_var = tkinter.StringVar()
        gold_var.set(str(price[0]))

        silver_var = tkinter.StringVar()
        silver_var.set(str(price[1]))

        copper_var = tkinter.StringVar()
        copper_var.set(str(price[2]))

        try:
            self.itemFrames[self.count] = customtkinter.CTkFrame(master=self.frameLeft, corner_radius=0, fg_color='gray20')
        except:
            self.itemFrames.append(customtkinter.CTkFrame(master=self.frameLeft, corner_radius=0, fg_color='gray20'))

        self.itemFrames[self.count].grid(row=self.count, column=0, sticky="nswe")
        
        self.itemFrames[self.count].columnconfigure(0, minsize=40) # id
        self.itemFrames[self.count].columnconfigure(1, minsize=350) # name
        self.itemFrames[self.count].columnconfigure(2, minsize=44) # buysell
        self.itemFrames[self.count].columnconfigure(3, minsize=120) # target
        self.itemFrames[self.count].columnconfigure(4, minsize=40) # save
        self.itemFrames[self.count].columnconfigure(5, minsize=180) # current   
        self.itemFrames[self.count].columnconfigure(6, minsize=40) # noti
        self.itemFrames[self.count].columnconfigure(7, minsize=40) # delete                   
        
        # ITEM ID AND NAME
        itemIdLabel = customtkinter.CTkLabel(master=self.itemFrames[self.count],
                                              text=item[0])
        itemIdLabel.grid(row=0, column=0, pady=2, padx=2, sticky='w')        
        
        itemLabel = customtkinter.CTkLabel(master=self.itemFrames[self.count],
                                              text=self.trader.itemData[int(item[0])])
        itemLabel.grid(row=0, column=1, pady=2, padx=2, sticky='w')
        
        # BUY SELL BUTTONS
        buySellButtons = customtkinter.CTkFrame(master=self.itemFrames[self.count])
        buySellButtons.grid(row=0, column=2, pady=2, padx=2, sticky='w')
        buyButton = customtkinter.CTkButton(master=buySellButtons,
                                         width=20,
                                         command=lambda i=self.count, it=item, b='buy': checkbox_event(i, it, b),
                                         text='Buying')
        buyButton.grid(row=0, column=0, pady=2, padx=2) 
        
        sellButton = customtkinter.CTkButton(master=buySellButtons,
                                          width=20,
                                          command=lambda i=self.count, it=item, b='sell': checkbox_event(i, it, b),
                                          text='Selling')
        sellButton.grid(row=0, column=1, pady=2, padx=2) 
        
        # Target price
        
        pricevcmd = (self.register(self.digitcheck))
        priceFrame = customtkinter.CTkFrame(master=self.itemFrames[self.count])
        priceFrame.grid(row=0, column=3)
        
        priceGold = customtkinter.CTkEntry(master=priceFrame,
                                           text_color='#e0b930',
                                           validate='all', validatecommand=(pricevcmd, '%P'),
                                           textvariable=gold_var,
                                           width=40)
        priceGold.grid(row=0, column=0)
        priceSilver = customtkinter.CTkEntry(master=priceFrame,
                                           placeholder_text='Slv',
                                           text_color='#adaeae',
                                           validate='all', validatecommand=(pricevcmd, '%P'),
                                           textvariable=silver_var,
                                           width=40)
        priceSilver.grid(row=0, column=1)
        priceCopper = customtkinter.CTkEntry(master=priceFrame,
                                           placeholder_text='Cpr',
                                           text_color='#d59f61',
                                           validate='all', validatecommand=(pricevcmd, '%P'),
                                           textvariable=copper_var,
                                           width=40)
        priceCopper.grid(row=0, column=2)            
        
        
        
        # Update target price to config
        self.updatePrices.append(None)
        self.updatePrices[self.count] = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                                                text=u"\u2713",
                                                                width=5,
                                                                fg_color=("gray75", "gray30"),
                                                                command=lambda i=self.count, it=item, 
                                                                p=(gold_var, silver_var, copper_var),
                                                                pg=priceGold, ps=priceSilver, pc=priceCopper: self.updatePrice(i, it, p, pg, ps, pc))

        def callback(index, v, *args):
            invalid = ['Gld', 'Slv', 'Cpr', '']
            if v.get() not in invalid:
                self.updatePrices[index].grid(row=0, column=4, pady=2, padx=2)  
        copper_var.trace_add('write', lambda *args, i=self.count, v=copper_var: callback(i, v, *args))
        silver_var.trace_add('write', lambda *args, i=self.count, v=silver_var: callback(i, v, *args))
        gold_var.trace_add('write', lambda *args, i=self.count, v=gold_var: callback(i, v, *args))    
        
        # Notifactions
        self.trader.alertButtons[item[0]] = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                                textvariable=self.trader.speaker[item[0]],
                                                text_font=('',-20),
                                                width=5,
                                                fg_color=("#A7171A"),
                                                command=lambda i=item, pg=priceGold, ps=priceSilver, pc=priceCopper: self.changeMute(i, pg, ps, pc))
        self.trader.alertButtons[item[0]].grid(row=0, column=6, pady=2, padx=2)             
        
        # Delete item
        deleteItemButton = customtkinter.CTkButton(master=self.itemFrames[self.count],
                                            text=u"\u274C",
                                            text_color='red',
                                            width=5,
                                            fg_color=("gray75", "gray30"),
                                            command=lambda i=self.count, it=item: self.deleteItem(i, it))
        deleteItemButton.grid(row=0, column=7, sticky='s', pady=10, padx=(10, 10))
        
        def checkbox_event(index, item, setting):          
            print(self.trader.currentPrices[item[0]][1][0].get())
            self.trader.itemIds[index][1] = setting
            self.trader.addToConfig()
            currentPriceFrame = customtkinter.CTkFrame(master=self.itemFrames[index])
            currentPriceFrame.grid(row=0, column=5, pady=2, padx=2, sticky='w')           
            if setting == 'sell':
                gold = customtkinter.CTkLabel(master=currentPriceFrame,
                                              width=1,
                                              text_color='#e0b930',
                                              textvariable=self.trader.currentPrices[item[0]][1][0])
                gold.grid(row=0, column=0, pady=0, padx=0, sticky='ew')
                gold['compound'] = tkinter.RIGHT
                gold['image'] = self.goldImage                
                silver = customtkinter.CTkLabel(master=currentPriceFrame,
                                                width=1,
                                                text_color='#adaeae',
                                                textvariable=self.trader.currentPrices[item[0]][1][1])
                silver.grid(row=0, column=1, pady=0, padx=0, sticky='ew')
                silver['compound'] = tkinter.RIGHT
                silver['image'] = self.silverImage                
                copper = customtkinter.CTkLabel(master=currentPriceFrame,
                                                width=1,
                                                text_color='#d59f61',
                                                textvariable=self.trader.currentPrices[item[0]][1][2])
                copper.grid(row=0, column=2, pady=0, padx=0, sticky='ew')
                copper['compound'] = tkinter.RIGHT
                copper['image'] = self.copperImage
                sellButton.configure(state=tkinter.DISABLED,
                                                  fg_color="#315399")
                buyButton.configure(state=tkinter.NORMAL,
                                 fg_color=("gray75", "gray30"))
            elif setting == 'buy':
                gold = customtkinter.CTkLabel(master=currentPriceFrame,
                                              width=1,
                                              text_color='#e0b930',
                                              textvariable=self.trader.currentPrices[item[0]][0][0])
                gold.grid(row=0, column=0, pady=0, padx=0, sticky='ew')
                gold['compound'] = tkinter.RIGHT
                gold['image'] = self.goldImage                
                silver = customtkinter.CTkLabel(master=currentPriceFrame,
                                                width=1,
                                                text_color='#adaeae',
                                                textvariable=self.trader.currentPrices[item[0]][0][1])
                silver.grid(row=0, column=1, pady=0, padx=0, sticky='ew')
                silver['compound'] = tkinter.RIGHT
                silver['image'] = self.silverImage                
                copper = customtkinter.CTkLabel(master=currentPriceFrame,
                                                width=1,
                                                text_color='#d59f61',
                                                textvariable=self.trader.currentPrices[item[0]][0][2])
                copper.grid(row=0, column=2, pady=0, padx=0,  sticky='ew')
                copper['compound'] = tkinter.RIGHT
                copper['image'] = self.copperImage
                sellButton.configure(state=tkinter.NORMAL,
                                 fg_color=("gray75", "gray30"))   
                buyButton.configure(state=tkinter.DISABLED,
                                                 fg_color="#315399")
        checkbox_event(self.count, item, item[1])        
        
if __name__ == "__main__":
    tradeObject = TradePostTracker()
    tradeObject.startUpdate()
    app = Gui(tradeObject)
    app.mainloop()