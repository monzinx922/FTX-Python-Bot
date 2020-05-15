from okex_api_spot import *
import time
import datetime
import requests

################### Connect to Line Notify ########################
url = 'https://notify-api.line.me/api/notify'
token = 'Your Token Here'
headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}

###################################################################
################### Connect to Server #############################
api_key = 'Your API key'
secret_key = 'Your Secret key'
passphrase_key = 'Your passpharse key'
fund_pass = 'Your fund pass'
try:
    okex = Okex(api_key, secret_key, passphrase_key, fund_pass)
except:
    now = datetime.datetime.now()
    print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
    print('Process will be retry in 10 sec')
    time.sleep(10)
    okex = Okex(api_key, secret_key, passphrase_key, fund_pass)

################################################################


################### Account Status #############################
#print('Current account status')
#spot_account_xrp = okex.spot_account('xrp')
#print('Currency = ', spot_account_xrp['currency'])
#print('Balance = ', spot_account_xrp['balance'], ' XRP')
#print('Available = ', spot_account_xrp['available'], ' XRP')
#print('On hole = ', spot_account_xrp['holds'], ' XRP')

#spot_account_usdt = okex.spot_account('usdt')
#print('Currency = ', spot_account_usdt['currency'])
#print('Balance = ', spot_account_usdt['balance'], ' USDT')
#print('Available = ', spot_account_usdt['available'], ' USDT')
#print('On hole = ', spot_account_usdt['holds'], ' USDT')
#################################################################


################### Define Variables#############################
UnitAttackRange = 0.0032

JobType1 = 'Swordman'
JobType2 = 'Archer'
JobType3 = 'Cannon'

Log_Path = "C:\\temp\\OKEx100Soldiers.log"
#################################################################


################### Class Soldier ###############################
##---- Properties ----#
#   - Name
#   - Job
#   - Zone
#   - Position
#----- Method ---------#
#   - PrisonerCal
#   - LastOrderID
#   - IsUnitJoined
#   - IsUnitInTheWar
#   - UnitSellProcess
#   - UnitBuyProcess
#   - UnitAction
#----------------------#
class Soldier:
    #Set up properties
    def __init__(self, Name, Job, Zone, Position):
        self.Name = Name
        self.Job = Job
        if self.Job == 'Swordman':
            self.AttackRange = UnitAttackRange * 1
        elif self.Job == 'Archer':
            self.AttackRange = UnitAttackRange * 2
        elif self.Job == 'Cannon':
            self.AttackRange = UnitAttackRange * 4
        else:
            print('Attack range is not set')
            self.AttackRange = UnitAttackRange
        self.Zone = Zone
        self.Position = Position
        self.LastAction = 'None'
        self.InWar = 0

    #Check Prisoner for add when create new buy order
    def PrisonerCal(self):
        SellPrice = round(self.Position + self.AttackRange, 4)
        SellFee = SellPrice * 0.001
        SellRealize = SellPrice - SellFee
        PrisonerAmount = round(SellRealize / self.Position, 3)
        return PrisonerAmount

    #Find Last Filled Order ID
    def LastOrderID(self):
        try:
            OrderList = okex.get_order_list('filled', 'XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            OrderList = okex.get_order_list('all', 'XRP/USDT')
        UnitOrders = []
        UnitLastOrderID = ''
        UnitMaxTime = datetime.datetime(2000, 1, 1)

        # Find last order of soldier
        for UnitOrder in OrderList:
            UnitTime = datetime.datetime.strptime(UnitOrder['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if UnitTime > UnitMaxTime:
                UnitMaxTime = UnitTime
                UnitLastOrderID = UnitOrder['order_id']

        return UnitLastOrderID

    #Check if unit has filled order
    def IsUnitJoined(self):
        #print(self.Name, ' check joined status')
        try:
            OrderList = okex.get_order_list('all', 'XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            OrderList = okex.get_order_list('all', 'XRP/USDT')
        UnitJoined = False
        for order in OrderList:
            if order['client_oid'] == self.Name and order['status'] == 'filled':
                UnitJoined = True
                #print(self.Name, ' is joined')
        return UnitJoined

    #Check if unit in open order, InWar will be 1 if unit has open order
    def IsUnitInTheWar(self):
        self.InWar = 0
        #print(self.Name, ' check war status')
        try:
            OpenOrders = okex.get_all_open_orders()
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            OpenOrders = okex.get_all_open_orders()
        for OpenOrder in OpenOrders:
            #print('Order Name = ', OpenOrder['client_oid'], 'Soldier Name = ', self.Name)
            if OpenOrder['client_oid'] == self.Name:
                self.InWar = 1
                #print(self.Name, ' check found status is in the war')

    #Place Sell order follow strategy
    def UnitSellProcess(self,price):
        Round_price = round(price,4)
        #print(self.Name, ' In Sell Process')
        try:
            UnitSell = okex.place_limit_sell_order('XRP/USDT', Round_price, '1', self.Name)
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            UnitSell = okex.place_limit_sell_order('XRP/USDT', Round_price, '1', self.Name)
        if UnitSell['error_code'] == '0':
            now = datetime.datetime.now()
            msg = self.Name+ ' action Sell at '+ str(Round_price)+ ' In Zone : ', str(self.Zone) + ' Order Id: '+ UnitSell['order_id'] +' Time: '+ now.strftime("%Y-%m-%d %H:%M:%S")
            print(msg)
            f = open(Log_Path,"a")
            f.write(msg)
            f.close()
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)
        else:
            msg = self.Name + ' Error while sending Sell order'
            print(msg)
            f = open(Log_Path, "a")
            f.write(msg)
            f.close()
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)

    # Place Buy order follow strategy
    def UnitBuyProcess(self,price):
        Round_price = round(price, 4)
        Unit = self.PrisonerCal()
        try:
            UnitBuy = okex.place_limit_buy_order('XRP/USDT', Round_price, str(Unit), self.Name)
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            UnitBuy = okex.place_limit_buy_order('XRP/USDT', Round_price, str(Unit), self.Name)
        if UnitBuy['error_code'] == '0':
            now = datetime.datetime.now()
            msg = self.Name + ' action Buy at ' + str(Round_price) +' In Zone : ',str(self.Zone)+ ' Order Id: '+ UnitBuy['order_id'] +' Time: '+ now.strftime("%Y-%m-%d %H:%M:%S")
            print(msg)
            f = open(Log_Path, "a")
            f.write(msg)
            f.close()
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)
        else:
            msg = self.Name + ' Error while sending Buy order'
            print(msg)
            f = open(Log_Path, "a")
            f.write(msg)
            f.close()
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)

    def UnitAction(self):
        #print(self.Name, ' start action')
        try:
            current_price = okex.get_ticker('XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            current_price = okex.get_ticker('XRP/USDT')
        last_price = float(current_price['last'])
        self.IsUnitInTheWar()

        if self.InWar == 0:
            #print(self.Name, ' Not in the war , going to the war')
            if self.IsUnitJoined() == True:
                UnitLastOrderID = self.LastOrderID()
                try:
                    UnitLastOrder = okex.get_order_details(UnitLastOrderID, 'XRP/USDT')
                except:
                    now = datetime.datetime.now()
                    print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
                    print('Process will be retry in 10 sec')
                    time.sleep(10)
                    UnitLastOrder = okex.get_order_details(UnitLastOrderID, 'XRP/USDT')
                if UnitLastOrder['side'] == 'buy':
                    self.LastAction = 'Sell'
                    if last_price > self.Position + self.AttackRange:
                        self.UnitSellProcess(last_price+0.0005)
                        #print('last price > position + attack range')
                        #print(self.Name, 'Position = ', self.Position, ' Attack Range = ', self.AttackRange)
                    else:
                        self.UnitSellProcess(self.Position + self.AttackRange)
                        #print('last price < postion + attack range')
                        #print(self.Name, 'Position = ', self.Position, ' Attack Range = ', self.AttackRange)
                else:
                    self.LastAction = 'Buy'
                    if last_price < self.Position:
                        self.UnitBuyProcess(last_price-0.0005)
                    else:
                        self.UnitBuyProcess(self.Position)
            else:
                #print(self.Name, ' is not join before')
                if self.LastAction == 'Buy':
                    #print(self.Name, ' last action is Buy')
                    if last_price > self.Position + self.AttackRange:
                        #print(self.Name, ' last_price > self.Position + self.AttackRange')
                        #print(self.Name, 'Position = ', self.Position, ' Attack Range = ', self.AttackRange)
                        self.UnitSellProcess(last_price+0.0005)
                    else:
                        #print(self.Name, ' last_price < self.Position + self.AttackRange')
                        #print(self.Name, 'Position = ', self.Position, ' Attack Range = ', self.AttackRange)
                        self.UnitSellProcess(self.Position + self.AttackRange)
                else:
                    #print(self.Name, ' last action is Sell')
                    if last_price < self.Position:
                        self.UnitBuyProcess(last_price-0.0005)
                    else:
                        self.UnitBuyProcess(self.Position)
        else:
            self.InWar = 1
            #print(self.Name, 'is in the war')
#################################################################


################### Class Zone ###############################
##---- Properties ----#
#   - Number
#   - High
#   - Low
#----- Method ---------#
#
#----------------------#
class Zone:
    def __init__(self, Number, High, Low):
        self.Number = Number
        self.High = High
        self.Low = Low
#################################################################


################### Class Market ###############################
##---- Properties ----#
#   - LastFilledOrderID
#   - LastMaxTime
#   - NewLastFilledOrderID
#   - NewMaxTime
#----- Method ---------#
#   - IsNewFilled
#----------------------#
class Market:
    def __init__(self):
        self.LastFilledOrderID = ''
        self.LastMaxTime = datetime.datetime(2000,1,1)
        # Find last order of filled
        try:
            OrderList = okex.get_order_list('filled', 'XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            OrderList = okex.get_order_list('filled', 'XRP/USDT')
        for order in OrderList:
            UnitTime = datetime.datetime.strptime(order['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if UnitTime > self.LastMaxTime:
                self.LastMaxTime = UnitTime
                self.LastFilledOrderID= order['order_id']
    def IsNewFilled(self):
        try:
            OrderList = okex.get_order_list('filled', 'XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            OrderList = okex.get_order_list('filled', 'XRP/USDT')
        self.NewLastFilledOrderID = ''
        self.NewMaxTime = datetime.datetime(2000, 1, 1)
        for order in OrderList:
            UnitTime = datetime.datetime.strptime(order['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if UnitTime > self.NewMaxTime:
                self.NewMaxTime = UnitTime
                self.NewLastFilledOrderID = order['order_id']
        NewLastFilledOrder = okex.get_order_details(self.NewLastFilledOrderID, 'XRP/USDT')
        if self.NewMaxTime > self.LastMaxTime:
            self.LastMaxTime = self.NewMaxTime
            now = datetime.datetime.now()
            msg = NewLastFilledOrder['client_oid'] + 'is Filled ' + 'Side: ' + NewLastFilledOrder['side'] + ' ' +NewLastFilledOrder['product_id']+' Price: ' + NewLastFilledOrder['price'] + ' Size: ' + NewLastFilledOrder['size'] + ' Time: '+ now.strftime("%Y-%m-%d %H:%M:%S")
            print(msg)
            f = open(Log_Path, "a")
            f.write(msg)
            f.close()
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)
#################################################################


################# Build Zone ####################################
Zones = []
Lowest = 0.0057
ZoneRange = 0.0157
for i in range(64):
    High = round(Lowest+ZoneRange,4)
    NewZone = Zone(i+1,High,Lowest)
    Zones.append(NewZone)
    Lowest = High
###############################################################
######################## Zone 15 ###############################
Zone15_70Percent = round(Zones[14].Low + ZoneRange*70/100,4)
Zone15_60Percent = round(Zones[14].Low + ZoneRange*60/100,4)
Zone15_50Percent = round(Zones[14].Low + ZoneRange*50/100,4)
Zone15_40Percent = round(Zones[14].Low + ZoneRange*40/100,4)
Zone15_30Percent = round(Zones[14].Low + ZoneRange*30/100,4)
Zone15_20Percent = round(Zones[14].Low + ZoneRange*20/100,4)

#----------------------------------------------------------------
# Send Swordman to Zone 15, Position 60 % of Zone
#----------------------------------------------------------------
Liam = Soldier('Liam', JobType1,15,Zone15_60Percent)

#----------------------------------------------------------------
# Send Archer to Zone 15, Position 40 % of Zone
#----------------------------------------------------------------
Noah = Soldier('Noah', JobType2,15,Zone15_30Percent)

####################################################################

######################## Zone 14 #################################
Zone14_70Percent = round(Zones[13].Low + ZoneRange*70/100,4)
Zone14_60Percent = round(Zones[13].Low + ZoneRange*60/100,4)
Zone14_50Percent = round(Zones[13].Low + ZoneRange*50/100,4)
Zone14_40Percent = round(Zones[13].Low + ZoneRange*40/100,4)
Zone14_30Percent = round(Zones[13].Low + ZoneRange*30/100,4)
Zone14_20Percent = round(Zones[13].Low + ZoneRange*20/100,4)

#----------------------------------------------------------------
# Send Swordman to Position 0.216
#----------------------------------------------------------------
William = Soldier('William', JobType1,14,0.216)

#----------------------------------------------------------------
# Send Archer to Position 0.218
#----------------------------------------------------------------
James = Soldier('James', JobType2,14,0.218)

#----------------------------------------------------------------
# Send Archer to Position 0.218
#----------------------------------------------------------------
Logan = Soldier('Logan', JobType2,14,0.2115)

####################################################################

######################## Zone 13 #################################
Zone13_70Percent = round(Zones[12].Low + ZoneRange*70/100,4)
Zone13_60Percent = round(Zones[12].Low + ZoneRange*60/100,4)
Zone13_50Percent = round(Zones[12].Low + ZoneRange*50/100,4)
Zone13_40Percent = round(Zones[12].Low + ZoneRange*40/100,4)
Zone13_30Percent = round(Zones[12].Low + ZoneRange*30/100,4)
Zone13_20Percent = round(Zones[12].Low + ZoneRange*20/100,4)

#----------------------------------------------------------------
# Send Swordman to Position 0.2026
#----------------------------------------------------------------
Benjamin = Soldier('Benjamin', JobType1,13,0.2026)

#----------------------------------------------------------------
# Send Archer to Position 0.1985
#----------------------------------------------------------------
Mason = Soldier('Mason', JobType2,13,0.1985)

#----------------------------------------------------------------
# Send Archer to Position 0.1930
#----------------------------------------------------------------
Elijah = Soldier('Elijah', JobType3,13,0.1930)

####################################################################

######################## Zone 12 #################################
Zone12_70Percent = round(Zones[11].Low + ZoneRange*70/100,4)
Zone12_60Percent = round(Zones[11].Low + ZoneRange*60/100,4)
Zone12_50Percent = round(Zones[11].Low + ZoneRange*50/100,4)
Zone12_40Percent = round(Zones[11].Low + ZoneRange*40/100,4)
Zone12_30Percent = round(Zones[11].Low + ZoneRange*30/100,4)
Zone12_20Percent = round(Zones[11].Low + ZoneRange*20/100,4)

#----------------------------------------------------------------
# Send Swordman to Position 0.189
#----------------------------------------------------------------
Oliver = Soldier('Oliver', JobType1,12,0.189)

#----------------------------------------------------------------
# Send Archer to Position 0.185
#----------------------------------------------------------------
Jacob = Soldier('Jacob', JobType2,12,0.185)

#----------------------------------------------------------------
# Send Archer to Position 0.181
#----------------------------------------------------------------
Lucas = Soldier('Lucas', JobType3,12,0.181)

####################################################################

######################## Zone 11 #################################
Zone11_70Percent = round(Zones[10].Low + ZoneRange*70/100,4)
Zone11_60Percent = round(Zones[10].Low + ZoneRange*60/100,4)
Zone11_50Percent = round(Zones[10].Low + ZoneRange*50/100,4)
Zone11_40Percent = round(Zones[10].Low + ZoneRange*40/100,4)
Zone11_30Percent = round(Zones[10].Low + ZoneRange*30/100,4)
Zone11_20Percent = round(Zones[10].Low + ZoneRange*20/100,4)

#----------------------------------------------------------------
# Send Swordman to Position 0.1743
#----------------------------------------------------------------
Michael = Soldier('Michael', JobType1,11,0.1743)

#----------------------------------------------------------------
# Send Archer to Position 0.1706
#----------------------------------------------------------------
Alexander = Soldier('Alexander', JobType2,11,0.1706)

#----------------------------------------------------------------
# Send Archer to Position 0.1666
#----------------------------------------------------------------
Ethan = Soldier('Ethan', JobType3,11,0.1666)

####################################################################

#Setup Soldiers
Liam.LastAction = 'Buy'
Noah.LastAction = 'Buy'
William.LastAction = 'Buy'
James.LastAction = 'Buy'
Logan.LastAction = 'Buy'
Benjamin.LastAction = 'Buy'
Mason.LastAction = 'Buy'
Elijah.LastAction = 'Buy'
Oliver.LastAction = 'Sell'
Jacob.LastAction = 'Sell'
Lucas.LastAction = 'Sell'
Michael.LastAction = 'Sell'
Alexander.LastAction = 'Sell'
Ethan.LastAction = 'Sell'

#Setup Market
CurrentMarket = Market()


############## START #############
print('OKEx100Soldier version 1.0.0')
print('64 Zones ', 'Lowest = ',Zones[0].Low, ' Hightest = ',Zones[63].High)
print('Deployed 14 Soldiers')

while(1):
    now = datetime.datetime.now()
    Liam.UnitAction()
    Noah.UnitAction()
    William.UnitAction()
    James.UnitAction()
    Logan.UnitAction()
    Benjamin.UnitAction()
    Mason.UnitAction()
    Elijah.UnitAction()
    Oliver.UnitAction()
    Jacob.UnitAction()
    Lucas.UnitAction()
    Michael.UnitAction()
    Alexander.UnitAction()
    Ethan.UnitAction()
    CurrentMarket.IsNewFilled()

    if now.minute % 59 == 0:
        try:
            current_price = okex.get_ticker('XRP/USDT')
        except:
            now = datetime.datetime.now()
            print('Connection error with OKEx at ' + now.strftime("%Y-%m-%d %H:%M:%S"))
            print('Process will be retry in 10 sec')
            time.sleep(10)
            current_price = okex.get_ticker('XRP/USDT')
        last_price = float(current_price['last'])
        #print(now.strftime("%Y-%m-%d %H:%M:%S"),' Server is running + On testing, Last Price: ',last_price)