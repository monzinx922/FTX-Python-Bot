from ccxt.ftx import ftx
import pandas as pd
import configparser
import datetime
import time
import requests
import sys,getopt
import math

# Note 06 MAR 2021
# Improve check order id to open, it must not open the same ID for many order.


################### Configuration file ########################
try:
    arg = getopt.getopt(sys.argv[1:], "i")
except getopt.GetoptError:
    print('please use -i and type your file location\n'
          'For example: Ritsu -i C:\\temp\\config-fundB.ini')
    sys.exit(2)
inputfile = arg[1][0]

config_loc = inputfile
print('config loc = ',config_loc)

config = configparser.ConfigParser()
config.read(config_loc)

################### Connect to Line Notify ########################

url = 'https://notify-api.line.me/api/notify'
token = config['LINE']['token']
headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
Name = config['NAME']['name']

################### Connect to Exchange ########################
api_key = config['EXCHANGE']['api_key']
api_secret = config['EXCHANGE']['api_secret']
sub_account_enable = config['EXCHANGE']['sub_account_enable']
sub_account_name = config['EXCHANGE']['sub_account_name']

if sub_account_enable == 'No':
    Ritsu = ftx({'apiKey': api_key,'secret': api_secret })
else:
    Ritsu = ftx({'headers': {'FTX-SUBACCOUNT': sub_account_name}, 'apiKey': api_key, 'secret': api_secret})

################### Grid data ########################

product = config['TRADE_GRID']['product']
Asset_token = config['TRADE_GRID']['Asset_token']
Asset_grid_range = config['TRADE_GRID']['Asset_grid_range']
Asset_grid_range = float(Asset_grid_range)

def SendCommand(Command,Amount=0.0,Price=0.0,Name='',ID=''):
    success = 0
    while (success == 0):
        try:
            if Command == 'cancel':
                Ritsu.cancel_all_orders(product)
                success = 1
            elif Command == 'balance':
                balance = Ritsu.fetch_balance()
                success = 1
                return balance
            elif Command == 'sell':
                Ritsu.create_order(product, 'limit', 'sell', Amount, Price,params={'clientOid': Name})
                success = 1
            elif Command == 'buy':
                Ritsu.create_order(product, 'limit', 'buy', Amount, Price,params={'clientOid': Name})
                success = 1
            elif Command == 'open_order':
                open_order = Ritsu.fetch_open_orders(symbol=product, limit=100)
                success = 1
                return open_order
            elif Command == 'order':
                order = Ritsu.fetch_order(id=ID,symbol=product)
                success = 1
                return order
            elif Command == 'my_trade':
                my_trade = Ritsu.fetch_my_trades(symbol=product,limit=100)
                success = 1
                return my_trade
            elif Command == 'ticker':
                ticker = Ritsu.fetch_ticker(product)
                success = 1
                return ticker
        except Exception as e:
            print(Name)
            print(e)
            msg = 'ร้าน ' + Name + 'พบปัญหา ' + str(e)
            r = requests.post(url, headers=headers, data={'message': msg})
            time.sleep(30)

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier)/multiplier

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

def main():
    print('Start Grid Trading')
    mytrade = SendCommand('my_trade',Name=Name)
    last_filled_timestamp = 0
    # check if trade record
    if mytrade != []:
        df = pd.DataFrame(mytrade)
        df = df.drop(columns='info')
        symbol = df['symbol'] == product
        df = df[symbol]
        df = df[['timestamp', 'price', 'side', 'amount']]
        df = df.sort_values(by=['timestamp'], ascending=False)
        last_filled_timestamp = df.iloc[0]['timestamp']
    print('Set last filled timestamp')

    while(1):
        print('Looping started')
        # check last filled timestamp
        mytrade = SendCommand('my_trade',Name=Name)
        current_filled_timestamp = 0
        df = pd.DataFrame(mytrade)
        if mytrade != []:
            df = df.drop(columns='info')
            symbol = df['symbol'] == product
            df = df[symbol]
            df = df[['timestamp', 'price', 'side', 'amount','order']]
            df = df.sort_values(by=['timestamp'], ascending=False)
            current_filled_timestamp = df.iloc[0]['timestamp']

        if current_filled_timestamp > last_filled_timestamp:
            # find oder id that has timestamp > last_filled_timestamp
            condition = df['timestamp'] > last_filled_timestamp
            df_condition = df[condition]
            previous_order_id = '00000000000'
            for i in range(df_condition.shape[0]):
                print('price = ', df.iloc[i]['price'], 'side = ', df.iloc[i]['side'], 'amount = ', df.iloc[i]['amount'])

                # order to open must not the same id of previous order
                if df.iloc[i]['order'] != previous_order_id:
                    # open new opposite order
                    if df.iloc[i]['side'] == 'buy':
                        print('Open sell at ', float(df.iloc[i]['price']) + Asset_grid_range)
                        SendCommand('sell', Amount=float(df.iloc[i]['amount']),
                                    Price=float(df.iloc[i]['price']) + Asset_grid_range,Name=Name)
                    else:
                        print('Open buy at ', float(df.iloc[i]['price']) - Asset_grid_range)
                        SendCommand('buy', Amount=float(df.iloc[i]['amount']),
                                    Price=float(df.iloc[i]['price']) - Asset_grid_range,Name=Name)

                        # Profit calculation
                        buy_price = (float(df.iloc[i]['price']) - Asset_grid_range)
                        buy_fee = buy_price * df.iloc[i]['amount'] * 0.019 / 100
                        cost = (buy_price * df.iloc[i]['amount']) + buy_fee

                        sell_price = (float(df.iloc[i]['price']))
                        sell_fee = sell_price * df.iloc[i]['amount'] * 0.019 / 100
                        income = (sell_price * df.iloc[i]['amount']) - sell_fee

                        profit = income - cost
                        profit_thb = round_down(profit*30, 2)

                        msg = 'ร้าน ' + Name + ' ขาย ' + Asset_token +' ได้กำไร ' + str(profit_thb) + ' บาท'
                        r = requests.post(url, headers=headers, data={'message': msg})

                previous_order_id = df.iloc[i]['order']
                time.sleep(2)
        else:
            now = datetime.datetime.now()
            print(config['NAME']['name'], ' Software version 2.0.0, Status: Running ',
                  now.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(5)

        last_filled_timestamp = current_filled_timestamp

if __name__ == "__main__":
   main()


