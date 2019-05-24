#!/usr/bin/env python3
import time, datetime
import logging
import json
import os
import sys
from bitshares.witness import Witness
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.price import Price
from bitshares import BitShares
from bitshares.blockchain import Blockchain
from bitshares.memo import Memo
import traceback

btswebsocket		= "wss://ws.gdex.top"               #seednode to connect to!
ctswebsocket		= "wss://www.citshares.org/ws"      #seednode to connect to!

btsaccount = "citshares-gateway"  #account of bts receive CNY
memokey = "5Kxxx"                 #memo key of bts account 

ctsaccount = "bitshares-gateway"  #CTS account to send CNY 
keys = "5Hxxx"                    #keys of cts

maxamount = 100                   #recharge limit

logfilename = "cts_gateway.log"   #record log

# Setup node instance
btsnet = BitShares(btswebsocket,keys=memokey)
ctsnet = BitShares(ctswebsocket,keys=keys)
btsblockchain = Blockchain(blockchain_instance=btsnet,mode='irreversible')
ctsblockchain = Blockchain(blockchain_instance=ctsnet,mode='irreversible')

def gateway():
    for op in btsblockchain.ops():
      if op['op'][0] == 'transfer':
        if op['op'][1]['to'] == Account(btsaccount,blockchain_instance=btsnet).get('id') :
          #this op is transfer to me
          recvamount = Amount(op['op'][1]['amount'],blockchain_instance=btsnet)
          if recvamount.symbol != "CNY":
            logger.warn('Receive not CNY: %s', recvamount)
            continue
          else:
            sendamount = maxamount if recvamount > maxamount else recvamount.amount
            m = Memo(blockchain_instance=btsnet)
            toctsaccount = m.decrypt(op['op'][1]['memo'])
            fromaccount = Account(account_name=op['op'][1]['from'],blockchain_instance=btsnet).get('name')
            if toctsaccount != "" :
              try:
                ctsnet.transfer(to=toctsaccount,amount=sendamount,asset='CNY',memo=fromaccount,account=ctsaccount)
              except Exception as e:
                logger.error('Reason: %s', e)
                logger.error('FAIL: from %s send %s CNY to %s', fromaccount,sendamount,toctsaccount)
            else:
              logger.warn('FAIL: from %s send %s CNY to NULL %s', fromaccount,sendamount,toctsaccount)


# Main Loop
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.DEBUG)
    handler = logging.FileHandler(logfilename)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Begin......")
    while True:
      try:
        gateway()
      except Exception as e:
        s = traceback.format_exc()
        logger.error('Reason: %s', e)
        logger.error('traceback: %s', s)

      logger.info("sleep 3s")
      time.sleep(3)
