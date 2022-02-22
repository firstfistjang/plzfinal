import ccxt
import pandas as pd
import time
import datetime
import math  
import numpy as np
import requests
def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    
def cal_target(exchange, symbol):
    # 거래소에서 symbol에 대한 ohlcv 일봉을 얻기
    coin_ohlcv = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe='1d',
        since=None,
        limit=10
    )
    #일봉 데이터를 데이터프레임 객체로 변환 
    df = pd.DataFrame(
        data=coin_ohlcv,
        columns=['datetime', 'open', 'high', 'low', 'close', 'volume']
    )
    # 전일 데이터와 금일 데이터로 목표가 계산
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', inplace=True)
    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
    df['bull'] = df['open'] > df['ma5']
    yesterday = df.iloc[-2]
    today= df.iloc[-1]
    updown = np.where(df['bull'].iloc[-1]==True,1,0)
    long_target = today['open'] + (yesterday['high']- yesterday['low']) * 0.5
    short_target = today['open'] - (yesterday['high']- yesterday['low']) * 0.5
    return (long_target, short_target, updown)

#수량계산
def cal_amount(usdt_balance,cur_price, portion):
    portion = portion
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000) / cur_price) / 1000000
    return amount

#포지션 진입
def enter_position(exchange, symbol, cur_price, long_target, short_target, updown, amount, position):
    if cur_price > long_target and updown == 1 : #long position
        position['type'] = 'long'
        position['amount'] = amount
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
    elif cur_price < short_target and updown == 0 : #short position
        position['type'] = 'short'
        position['amount'] = amount
        exchange.create_market_sell_order(symbol=symbol, amount=amount)

#포지션 정리
def exit_position(exchange, symbol, position):
    amount = position['amount']
    if position['type'] == 'long':
        exchange.create_market_sell_order(symbol=symbol, amount=amount)
        position['type'] == None
    elif position['type'] == 'short':
        exchange.create_market_buy_order(symbol=symbol, amount=amount)
        position['type'] == None