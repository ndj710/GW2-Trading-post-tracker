import requests
import sqlalchemy
import time
import pandas as pd
pd.options.mode.chained_assignment = None
from datetime import datetime
import threading
import configparser
import traceback
import email
import smtplib
from stoppableThread import StoppableThread


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
        self.priceEngine = sqlalchemy.create_engine('sqlite:///../priceData.db')
        self.currentPrices = {}
        self.speaker = {}
        self.alertButtons = {}
    
    def addToConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read('../config.ini')
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
            with open('../config.ini', 'w') as newini:
                config.write(newini)
        except Exception as e:
            self.error = 'Error in TPTaddToConfig'
            print(self.error + ' ', e)
    
    def parseConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read('../config.ini')
            if config.sections() == []:
                config['Configuration'] = {'TIMER': '10', 'ITEMS': '9482|buy|100|f, 24|sell|10|t'}
                config['Email'] = {'server': 'smtp.office365.com', 'port': 587, 'sender': 'examplesender@hotmail.com', 'password': 'examplepassword', 'receiver': 'examplereceiver@emaildomain.com'}
                with open('../config.ini', 'w') as configfile: config.write(configfile)
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
                    self.itemIds.append(i)
        except Exception as e:
            if e == 'Configuration':
                self.error = 'Error in config file, see default for examples'      
            elif e == 'Email':
                self.error = 'Error in config file, see default for examples'
            else:
                self.error = 'Error in TPTparseConfig'
            print(self.error + ' ', e)
            
    def loadItemData(self):
        try:
            url = 'https://api.datawars2.ie/gw2/v1/items/json?filter=$fields=id,name,buy_price,sell_price'
            req = requests.get(url).json()
            for fullitem in req:
                if 'id' in fullitem and 'name' in fullitem and 'buy_price' in fullitem and 'sell_price' in fullitem:
                    self.itemData[fullitem['id']] = fullitem['name']
        except Exception as e:
            self.error = 'Error in TPTloadItemData'
            print(self.error + ' ', e)
            print(traceback.format_exc())

    def sendEmail(self, item):
        try:
            self.speaker[item[0]].set(u"\U0001F515")
            self.alertButtons[item[0]].configure(fg_color=("#A7171A"))               
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
            self.error = 'Error in TPTsendEmail'
            print(self.error + ' ', e)
    
    
    def convertPrice(self, price):
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
    
    def getCurrentPrice(self, itemId, table_df):
        try:
            buy = str(table_df['BuyPrice'][len(table_df)-1])
            sell = str(table_df['SellPrice'][len(table_df)-1])
            buyPrice = self.convertPrice(buy)
            sellPrice = self.convertPrice(sell)
            self.currentPrices[str(itemId)][0][0].set(buyPrice[1][0])
            self.currentPrices[str(itemId)][0][1].set(buyPrice[1][1])
            self.currentPrices[str(itemId)][0][2].set(buyPrice[1][2])
            self.currentPrices[str(itemId)][1][0].set(sellPrice[1][0])
            self.currentPrices[str(itemId)][1][1].set(sellPrice[1][1])
            self.currentPrices[str(itemId)][1][2].set(sellPrice[1][2])
        except Exception as e:
            self.error = 'Error in TPTgetCurrentPrice'
            print(self.error + ' ', e)
            
    def startUpdate(self):
        self.threads.append(StoppableThread(target=self.getItemPrices))
        self.threads[0].start()
    
    def getItemPrices(self):
        while True:
            if self.threads[0].stopped() == True:
                print('Thread closed')
                break        
            try:
                print('running')
                time.sleep(self.timer)
                if self.loading == False:
                    url = 'https://api.guildwars2.com/v2/commerce/prices?ids='
                    for item in self.itemIds:
                        if item != None:
                            url += str(item[0]) + ','
                    self.create_frame(requests.get(url).json())
            except Exception as e:
                self.error = 'Error in TPTgetItemPrice'
                print(self.error + ' ', e)

    def create_frame(self, data):
        try:
            for item in data:
                if item == 'text':
                    print('passing')
                    continue
                df = pd.DataFrame([item])
                date = datetime.now()
                df['Time'] = date.strftime("%d-%m-%Y, %H:%M:%S")
                df['BuyPrice'] = df['buys'][0]['unit_price']
                df['BuyAmount'] = df['buys'][0]['quantity']
                df['SellPrice'] = df['sells'][0]['unit_price']
                df['SellAmount'] = df['sells'][0]['quantity']
                df = df.loc[:, ['id', 'whitelisted', 'BuyPrice', 'BuyAmount', 'SellPrice', 'SellAmount', 'Time']]
                itemId = df['id'][0]
                
                for i in self.itemIds:
                    if i != None and i[0] == str(itemId):
                        targetPrice =  int(i[2])
                        if self.speaker[str(itemId)].get() != u"\U0001F515" and targetPrice != 0:
                            try:
                                table_df = pd.read_sql_table(str(itemId), self.priceEngine)
                                if i[1] == 'buy':
                                    currentPrice = int(df['BuyPrice'][0])
                                    if currentPrice <= targetPrice:
                                        self.sendEmail(i)
                                elif i[1] == 'sell':
                                    currentPrice = int(df['SellPrice'][0])
                                    if currentPrice >= targetPrice:
                                        self.sendEmail(i)
                            except Exception as e:
                                self.error = 'Error in TPTcreateframe inner loop'
                                print(self.error + ' ', e)
                                pass
                        break            
                
                df.to_sql(str(itemId), self.priceEngine, if_exists='append', index=False)
                self.getCurrentPrice(itemId, df)
        except Exception as e:
            print('error: ', e)
            pass