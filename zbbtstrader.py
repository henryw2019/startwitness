from zapi import ZApi
from bitshares.market import Market
from bitshares.amount import Amount
from bitshares import BitShares
from bitshares.price import Price
from bitshares.account import Account
import logging
import time
import json
import traceback

ORDER_TYPE_BUY = 1
ORDER_TYPE_SELL = 0

access_key="86fa5c58-60ab-48c3-bc44-18dcab031XXX" # your own key ZB
secret_key="a6119c62-904a-475e-8943-904b4ff85XXX" # your own key ZB
btswebsocket="wss://sg.nodes.bitshares.ws"        #bts node

account = "xxxx"            # your bitshares account
activekey=""                # your bitshares account's active key

bitshares = BitShares(btswebsocket,keys=activekey)
btsmarket = Market("BTS:CNY",blockchain_instance=bitshares)
market = "bts_qc"


zb = ZApi(access_key=access_key , secret_key=secret_key)

def trader():
    while 1:
        try:
            # trace market per 3 seconds
            logger.info("sleep 3s")
            time.sleep(3)
            zbdepth  = zb.depth(market=market,size=2)
            btsdepth = btsmarket.orderbook(5)

            logging.info(zbdepth)
            logging.info(btsdepth)

            #price
            btssell1 = btsdepth['asks'][0]['price']   #内盘卖1
            btsbuy1  = btsdepth['bids'][0]['price']   #内盘买1
            zbsell1  = zbdepth['asks'][0][0]          #zb卖1
            zbbuy1   = zbdepth['bids'][0][0]          #zb买1

            #amount
            btssellamount = btsdepth['asks'][0]['quote'].amount   #内盘卖1
            btsbuyamount  = btsdepth['bids'][0]['quote'].amount   #内盘买1
            zbsellamount  = zbdepth['asks'][0][1]          #zb卖1
            zbbuyamount   = zbdepth['bids'][0][1]          #zb买1
            
            #logic No.1  内盘买一价/外盘卖一价 => 1 
            #外盘购入X BTS，内盘卖出X BTS. （外盘rmb换成0溢价cny）
            if btsbuy1 / zbsell1 >= 1 : 
                # 比较内外盘量大小，按小者交易，确定交易量
                mytradeamount = btsbuyamount if zbsellamount > btsbuyamount else zbsellamount

                # 价格按照各自盘面1价交易
                #内盘 卖出
                myprice = Price(
                    btsbuy1, base='1.3.113', quote='1.3.0', bitshares_instance=bitshares
                )
                mybtsamount = Amount(mytradeamount, '1.3.0')
                myprice.market.sell(myprice,mybtsamount,account=account)
                #zb 买入
                zb.order(market=market,type=ORDER_TYPE_BUY,amount=mytradeamount,price=zbsell1)
            
            #logic No.2 外盘买一价格/内盘卖一价<1.015 外盘卖出X BTS，内盘买入X BTS.（内盘溢价cny换成rmb）
            if zbbuy1 / btssell1 < 1.015 :
                # 比较内外盘量大小，按小者交易，确定交易量
                mytradeamount = btsbuyamount if zbsellamount > btsbuyamount else zbsellamount
                # 价格按照各自盘面1价交易
                #zb 卖出
                zb.order(market=market,type=ORDER_TYPE_SELL,amount=mytradeamount,price=zbbuy1)
                #内盘 买入
                myprice = Price(
                    btssell1, base='1.3.113', quote='1.3.0', bitshares_instance=bitshares
                )
                mybtsamount = Amount(mytradeamount, '1.3.0')
                myprice.market.buy(myprice,mybtsamount,account=account)
        except Exception as e:
            s = traceback.format_exc()
            logger.error('Reason: %s', e)
            logger.error('traceback: %s', s)

        
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.DEBUG)
    handler = logging.FileHandler("trade.log")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s- %(lineno)d - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    while 1:
        logger.info("Begin .....")
        trader()
        logger.info(" wait for 60s  ..." )
        time.sleep(60)





