import requests
import time
import threading
import configparser
import traceback
import email
import smtplib
from stoppableThread import StoppableThread
import logging

logging.getLogger("urllib3").setLevel(logging.WARNING)

class TradePostTracker:
    def __init__(self):
        self.loading = True
        self.threads = []
        self.error = ''
        self.timer = 10
        self.itemIds = []
        self.itemData = {}
        self.server = ''
        self.port = 587
        self.sender = ''
        self.password = ''
        self.receiver = ''
        self.currentPrices = {}
        self.speaker = []
        self.alertButtons = []
    
    def addToConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            strToAdd = ''
            for item in self.itemIds:
                if item != None:
                    strToAdd += '{}|{}|{}|{}'.format(item[0], item[1], item[2], item[3]) + ', '
            config.set('Configuration','ITEMS', strToAdd.strip(', '))
            config.set('Email','server', self.server)
            config.set('Email','port', str(self.port))
            config.set('Email','sender', self.sender)
            config.set('Email','password', self.password)
            config.set('Email','receiver', self.receiver)
            with open('config.ini', 'w') as newini:
                config.write(newini)
        except Exception as e:
            self.error = traceback.format_exc()
    
    def parseConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            if config.sections() == []:
                config['Configuration'] = {'TIMER': '10', 'ITEMS': '9482|buy|100|f, 24|sell|10|t'}
                config['Email'] = {'server': 'smtp.office365.com', 'port': 587, 'sender': 'examplesender@hotmail.com', 'password': 'examplepassword', 'receiver': 'examplereceiver@emaildomain.com'}
                with open('config.ini', 'w') as configfile: config.write(configfile)
            self.timer = int(config['Configuration']['TIMER'])
            confItems = config['Configuration']['ITEMS'].replace(' ', '').split(',')
            self.server = config['Email']['server']
            self.port = int(config['Email']['port'])
            self.sender = config['Email']['sender']
            self.password = config['Email']['password']
            self.receiver = config['Email']['receiver']
            for i in confItems:
                i = i.split('|')
                if i != ['']:
                    errorFlag = False
                    for x in self.itemIds:
                        if x[0] == i[0] and x[1] == i[1]:
                            errorFlag = True
                    if errorFlag == True:
                        self.error = 'Too many duplicates in config file, see default for examples'     
                        print(self.error)
                        return
                    self.itemIds.append(i)
        except Exception as e:
            if e == 'Configuration':
                self.error = 'Error in config file, see default for examples'      
            elif e == 'Email':
                self.error = 'Error in config file, see default for examples'
            else:
                self.error = traceback.format_exc()
            
    def loadItemData(self):
        try:
            url = 'https://api.datawars2.ie/gw2/v1/items/json?filter=$fields=id,name,buy_price,sell_price'
            req = requests.get(url).json()
            for fullitem in req:
                if 'id' in fullitem and 'name' in fullitem and 'buy_price' in fullitem and 'sell_price' in fullitem:
                    self.itemData[fullitem['id']] = fullitem['name']
        except Exception as e:
            self.error = traceback.format_exc()

    def sendEmail(self, item):
        try:
            self.speaker[item[4]].set(u"\U0001F4E9")
            self.alertButtons[item[4]].configure(fg_color=("#F28C28"))
            msg = email.message_from_string('Item {} ({}) has hit the alert threshold'.format(self.itemData[int(item[0])], str(item[0])))
            msg['From'] = self.sender
            msg['To'] = self.receiver
            msg['Subject'] = "GW2 {} ({}) PA".format(self.itemData[int(item[0])], str(item[0]))
            s = smtplib.SMTP(self.server,self.port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(self.sender, self.password)
            s.sendmail(self.sender, self.receiver, msg.as_string())
            s.quit()         
        except Exception as e:
            self.error = traceback.format_exc()
    
    
    def convertPrice(self, price):
        try:
            gold = '0'
            silver = '0'
            copper = '0'
            if len(price) >= 5:
                gold = price[:-4]
            if len(price) >= 3:
                silver = price[-4:-2]
                if silver[0] == '0':
                    silver = silver[1]
            if len(price) >= 2:
                copper = price[-2:]
                if copper[0] == '0':
                    copper = copper[1]
            return ('{}g {}s {}c'.format(gold, silver, copper), (gold, silver, copper))
        except Exception as e:
            self.error = traceback.format_exc()
    
    def getCurrentPrice(self, itemId, df):
        try:
            buy = str(df['BuyPrice'])
            sell = str(df['SellPrice'])
            buyPrice = self.convertPrice(buy)
            sellPrice = self.convertPrice(sell)
            self.currentPrices[str(itemId)][0][0].set(buyPrice[1][0])
            self.currentPrices[str(itemId)][0][1].set(buyPrice[1][1])
            self.currentPrices[str(itemId)][0][2].set(buyPrice[1][2])
            self.currentPrices[str(itemId)][1][0].set(sellPrice[1][0])
            self.currentPrices[str(itemId)][1][1].set(sellPrice[1][1])
            self.currentPrices[str(itemId)][1][2].set(sellPrice[1][2])
        except Exception as e:
            self.error = traceback.format_exc()
            
    def startUpdate(self):
        self.threads.append(StoppableThread(target=self.getItemPrices))
        self.threads[0].start()
    
    def getItemPrices(self):
        while True:    
            try:
                print('running')
                if self.error != '':
                    logging.basicConfig(filename='./logs/updateThreadCrash.log', encoding='utf-8', level=logging.DEBUG)
                    logging.error(self.error)   
                    self.error = ''
                count = 0
                while count < self.timer:
                    if self.threads[0].stopped() == True:
                        print('Thread closed')
                        return                    
                    time.sleep(1)
                    count += 1
                if self.loading == False:
                    url = 'https://api.guildwars2.com/v2/commerce/prices?ids='
                    for item in self.itemIds:
                        if item != None:
                            url += str(item[0]) + ','
                    self.create_frame(requests.get(url).json())
            except Exception as e:
                self.error = traceback.format_exc()

    def create_frame(self, data):
        try:
            for item in data:
                if item == 'text':
                    print('passing')
                    continue
                df = {'id': item['id'], 'BuyPrice': item['buys']['unit_price'], 'SellPrice': item['sells']['unit_price']}
                itemId = df['id']
                for i in self.itemIds:
                    if i != None and i[0] == str(itemId):
                        targetPrice =  int(i[2])
                        if self.speaker[i[4]].get() == u"\U0001F514" and targetPrice != 0:
                            if i[1] == 'buy':
                                currentPrice = int(df['BuyPrice'])
                                if currentPrice <= targetPrice:
                                    self.sendEmail(i)
                            elif i[1] == 'sell':
                                currentPrice = int(df['SellPrice'])
                                if currentPrice >= targetPrice:
                                    self.sendEmail(i)    
                self.getCurrentPrice(itemId, df)
        except Exception as e:
            self.error = traceback.format_exc()