from songline import Sendline
import time
from binance import Client
import schedule
import datetime
from config import *
from my_token import *

sendline = Sendline(line_token)
binance = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)


def turn_on_alert(symbol):
    print(f'turning {symbol} alert on')
    global crypto_list
    for crypto in crypto_list:
        if crypto['symbol'] == symbol:
            crypto['alert_on'] = True
            print(f"turn {crypto['symbol']} ON")
            print(crypto_list)


def turn_off_alert(symbol):
    global crypto_list
    for crypto in crypto_list:
        if crypto['symbol'] == symbol:
            crypto['alert_on'] = False
            print(f"turn {crypto['symbol']} OFF")
            print(crypto_list)


def create_list_of_dict_from_crypto():
    result_list = []
    for crypto in CRYPTO_NEED_TO_LOAN:
        if "USDT" in crypto or "BUSD" in crypto:
            asset = crypto[0:-4]
            result_list.append({'symbol': crypto, 'alert_on': True, 'asset': asset})
    return result_list


crypto_list = create_list_of_dict_from_crypto()


while True:
    schedule.run_pending()
    time.sleep(10)
    for each_crypto in crypto_list:
        if each_crypto['alert_on']:
            try:
                details = binance.get_max_margin_loan(asset=each_crypto['asset'], isolatedSymbol=each_crypto['symbol'])
            except Exception as e:
                pass
            else:
                turn_off_alert(each_crypto['symbol'])
                current_time = datetime.datetime.today()
                time_to_alert = current_time + datetime.timedelta(minutes=SILENCE_TIME)
                staking_alert_job = schedule.every().day.at(time_to_alert.strftime("%H:%M")).do(
                    turn_on_alert, symbol=each_crypto['symbol'])    # Turn On alert in next 1 hour
                for count in range(3):
                    sendline.sendtext(f"{each_crypto['symbol']} loan is AVAILABLE NOW!!!")
                    time.sleep(3)

