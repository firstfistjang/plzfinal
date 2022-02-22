import ccxt
import pandas as pd
import time
import datetime
import larry1
import math
api_key = 
secret = 
myToken = 
#binance 객체 생성
binance = ccxt.binance(config ={
    'apiKey':api_key,
    'secret':secret,
    'enableRateLimit':True,
    'options': {
        'defaultType': 'future'
    }
})
#코인선택
symbol = "XRP/USDT"

#1회성잔고조회
balance = binance.fetch_balance()
usdt = balance['free']['USDT']

#1회성목표가조회
long_target,short_target,updown = larry1.cal_target(binance, symbol)


position = {
    "type": None,
    "amount": 0
}
op_mode = False
larry1.post_message(myToken,"#crypto", "autotrade start")

while True:
    try:
        #time
        now=datetime.datetime.now()
        #포지션 종료
        if now.hour == 8 and now.minute == 50 and (0 <= now.second < 10):
            if op_mode and position['type'] is not None:
                larry1.exit_position(binance,symbol,position)
                if position['type'] is None:
                    larry1.post_message(myToken,"#crypto", "position exit")
                op_mode = False
        #목표가 갱신 09:00:20 ~ 09:00:30
        if now.hour == 9 and now.minute == 10 and (20 <= now.second < 30):
            long_target,short_target,updown = larry1.cal_target(binance, symbol)
            #잔고조회
            balance = binance.fetch_balance()
            usdt = balance['free']['USDT']
            op_mode = True
            time.sleep(10)

        #현재가, 구매가능수량
        btc=binance.fetch_ticker(symbol)
        cur_price = btc['last']
        amount = larry1.cal_amount(usdt,cur_price, 1)

        if op_mode and position['type'] is None :
            larry1.enter_position(binance, symbol,cur_price,long_target,short_target,updown,amount,position)
            if usdt < 5 : 
                larry1.post_message(myToken,"#crypto", "position enter")
        # print(now, cur_price, long_target,short_target, updown, amount, usdt)
        time.sleep(1)
    except Exception as e:
        print(e)
        larry1.post_message(myToken,"#crypto", e)
        time.sleep(1)