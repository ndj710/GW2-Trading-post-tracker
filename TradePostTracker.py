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
import math
import tkinter

class TradePostTracker:
    def __init__(self):
        self.loading = True
        self.notiTrue = u"\U0001F514"
        self.notiFalse = u"\U0001F515"
        self.error = ''
        self.timer = 10
        self.itemIds = []
        self.itemData = {}
        self.server = ''
        self.port = 587
        self.sender = ''
        self.password = ''
        self.receiver = ''
        self.engine = sqlalchemy.create_engine('sqlite:///itemData.db')
        self.currentPrices = {}
        self.speaker = {}
        self.alertButtons = {}
    
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
            self.error = 'Error in TPTaddToConfig'
            print(self.error + ' ', e)
    
    def parseConfig(self):
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            if config.sections() == []:
                config['Configuration'] = {'TIMER': '10', 'ITEMS': '9482|buy|100|f, 24|sell|10|t'}
                config['Email'] = {'server': 'smtp.office365.com', 'port': '587', 'sender': '', 'password': '', 'receiver': ''}
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
            def load(itemReq):
                url = 'https://api.guildwars2.com/v2/items?ids='
                nameId = {'id': [], 'name': []}
                for index, item in enumerate(itemReq):
                    if index % 100 != 0:
                        url += str(item) + ','
                    else:
                        url += str(item)
                        req = requests.get(url).json()
                        if "text" not in req:
                            for fullitem in req:
                                nameId['id'].append(fullitem['id'])
                                nameId["name"].append(fullitem['name'])
                            df = pd.DataFrame.from_dict(nameId)
                            df.to_sql('Items', self.engine, if_exists='append', index=False)
                            url = 'https://api.guildwars2.com/v2/items?ids='
                            nameId = {'id': [], 'name': []}
                req = requests.get(url).json()
                if "text" not in req:
                    for fullitem in req:
                        nameId['id'].append(fullitem['id'])
                        nameId["name"].append(fullitem['name'])
                    url = 'https://api.guildwars2.com/v2/items?ids='        
                    df = pd.DataFrame.from_dict(nameId)
                    df.to_sql('Items', self.engine, if_exists='append', index=False)
            connection = self.engine.connect()
            metadata = sqlalchemy.MetaData()
            tab = sqlalchemy.Table('Items', metadata, autoload=True, autoload_with=self.engine)
            query = sqlalchemy.select([tab])
            result = connection.execute(query)
            result = result.fetchall()
            for i in result:
                self.itemData[i[0]] = i[1]
            itemReq = requests.get('https://api.guildwars2.com/v2/commerce/prices').json()
            notAdded = []
            for i in itemReq:
                try:
                    self.itemData[i]
                except:
                    notAdded.append(i)
            load(notAdded)
        except Exception as e:
            if str(e) == 'Items':
                itemReq = requests.get('https://api.guildwars2.com/v2/commerce/prices').json()
                load(itemReq)
                connection = self.engine.connect()
                metadata = sqlalchemy.MetaData()
                tab = sqlalchemy.Table('Items', metadata, autoload=True, autoload_with=self.engine)
                query = sqlalchemy.select([tab])
                result = connection.execute(query)
                result = result.fetchall()
                for i in result:
                    self.itemData[i[0]] = i[1]
            else:
                self.error = 'Error in TPTloadItemData'
                print(self.error + ' ', e)
                print(traceback.format_exc())
        
    def sendEmail(self, item):
        try:
            print('sending email')
            msg = email.message_from_string('Item {} has hit the alert threshold'.format(str(item)))
            msg['From'] = self.sender
            msg['To'] = self.receiver
            msg['Subject'] = "Price Alert for: " + str(item)
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
        gold = math.floor(price / 10000)
        price = (price / 10000 - gold) * 100
        silver = math.floor(price)
        price = price - silver
        copper = math.floor(price * 100)
        return '{}g {}s {}c'.format(gold, silver, copper)    
    
    def getCurrentPrice(self, itemId, table_df):
        try:
            buy = int(table_df['BuyPrice'][len(table_df)-1])
            sell = int(table_df['SellPrice'][len(table_df)-1])
            buyPrice = self.convertPrice(buy)
            sellPrice = self.convertPrice(sell)
            print(itemId, buyPrice, sellPrice)
            self.currentPrices[str(itemId)][0].set(buyPrice)
            self.currentPrices[str(itemId)][1].set(sellPrice)
            print('did the update')
        except Exception as e:
            self.error = 'Error in TPTgetCurrentPrice'
            print(self.error + ' ', e)
            
    def changeMute(self, item):
        if self.speaker[item[0]].get() == self.notiTrue:
            self.speaker[item[0]].set(self.notiFalse)
            self.alertButtons[item[0]].configure(fg_color=("#A7171A"))
        else: 
            self.speaker[item[0]].set(self.notiTrue)
            self.alertButtons[item[0]].configure(fg_color=("#71C562"))
            
    def startUpdate(self):
        update_thread = threading.Thread(target=self.getItemPrices)
        update_thread.start()
    
    def getItemPrices(self):
        while True:
            try:
                time.sleep(self.timer)
                if self.loading == False:
                    print('updating')
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
                        if self.speaker[str(itemId)].get() != self.notiFalse and targetPrice != 0:
                            try:
                                table_df = pd.read_sql_table(str(itemId), self.engine)
                                if i[1] == 'buy':
                                    currentPrice = int(df['BuyPrice'][0])
                                    if currentPrice <= targetPrice:
                                        self.changeMute(i)
                                        self.sendEmail(i)
                                elif i[1] == 'sell':
                                    currentPrice = int(df['SellPrice'][0])
                                    print(i[0], currentPrice, targetPrice)
                                    print(i[0], self.convertPrice(currentPrice), self.convertPrice(targetPrice))
                                    if currentPrice >= targetPrice:
                                        self.changeMute(i)
                                        self.sendEmail(i)
                            except Exception as e:
                                self.error = 'Error in TPTcreateframe inner loop'
                                print(self.error + ' ', e)
                                pass
                        break            
                
                df.to_sql(str(itemId), self.engine, if_exists='append', index=False)
                self.getCurrentPrice(itemId, df)
        except Exception as e:
            self.error = 'Error in TPTcreateframe'
            print(self.error + ' ', e)
            print(traceback.format_exc())