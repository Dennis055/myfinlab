import requests
import json
import re
import time
import pandas as pd


class CmoneyVirtualStock():
    
    def __init__(self, email, password, wait_time=1):
        
        """
        輸入帳號(email)密碼(password)來登入，並設定每個request的延遲時間是wait_time
        
        """
        
        self.ses = requests.Session()
        res = self.ses.get('https://www.cmoney.tw/member/login/')
        self.wait_time = wait_time

        # get view state
        viewstate = re.search( 'VIEWSTATE"\s+value=.*=', res.text )
        viewstate = viewstate.group()

        # get eventvalidation
        eventvalidation = re.search( 'EVENTVALIDATION"\s+value=.*\w', res.text )
        eventvalidation = eventvalidation.group( )
        
        time.sleep(self.wait_time)
        
        res = self.ses.post('https://www.cmoney.tw/member/login/', {
                '__VIEWSTATE': viewstate[18:],
            '__EVENTVALIDATION': eventvalidation[24:],
            'ctl00$ContentPlaceHolder1$mail': email,
            'ctl00$ContentPlaceHolder1$pw': password,
            'ctl00$ContentPlaceHolder1$loginBtn': '登入',
            'ctl00$ContentPlaceHolder1$check': 'on',
        })
        
        time.sleep(self.wait_time)
        
        res = self.ses.get('https://www.cmoney.tw/vt/main-page.aspx')

        aids = re.findall('aid=[\d]*', res.text )
        aids = [a.split('=')[1] for a in aids]
        aids = [a for a in aids if a.isdigit()]
        self.aids = aids
        
        self.aid = aids[0]
        print('accounts', aids)
        print('current account', self.aid)
        
    def get_price(self, sid):
        
        """
          輸入sid='1101'，會拿到以下的資料：
           {'StockInfo': {'Commkey': '1101',
          'Name': '台泥',
          'MarketType': 2,
          'RefPrice': 42.9,
          'CeilPrice': 47.15,
          'FloorPrice': 38.65,
          'SalePrice': 43.1,
          'TotalQty': 8665,
          'DecimalPoint': 1,
          'LowPr': 42.6,
          'BuyPr1': 43.05,
          'SellPr1': 43.1,
          'BuyPr2': 43.0,
          'SellPr2': 43.15,
          'BuyPr3': 42.95,
          'SellPr3': 43.2,
          'BuyPr4': 42.9,
          'SellPr4': 43.25,
          'BuyPr5': 42.85,
          'SellPr5': 43.3,
          'BuyQty1': 73.0,
          'SellQty1': 43.0,
          'BuyQty2': 459.0,
          'SellQty2': 42.0,
          'BuyQty3': 111.0,
          'SellQty3': 178.0,
          'BuyQty4': 169.0,
          'SellQty4': 120.0,
          'BuyQty5': 46.0,
          'SellQty5': 230.0,
          'DealTime': '2018-08-22T11:40:53',
          'OrderTime': '2018-08-22T11:40:53'},
         'SalePrice': '43.1',
         'IsWarrant': False}
        """
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/HandlerGetStockPrice.ashx', params={
            'q': sid,
            'accountType': 1,
            'isSDAndSell': 'false',
            })
        return json.loads(res.text)
        
    def buy(self, sid, quantity, price=None):
        
        """
        購買兩張台泥股票:
        例如sid='1101', quantity=2
        假如沒有輸入price就是以當前價格買入
        假如輸入了price就是限價買入
        """
        
        if price is None:
            price = self.get_price(sid)['StockInfo']['CeilPrice']
            time.sleep(self.wait_time)
            
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/userset.ashx', params={
            'act': 'NewEntrust',
            'aid': self.aid,
            'stock': sid,
            'price': price,
            'ordqty': quantity,
            'tradekind': 'c',
            'type': 'b',
            'hasWarrant': 'false',
        })
        
    def sell(self, sid, quantity, price=None):

        """
        賣出兩張台泥股票:
        例如sid='1101', quantity=2
        假如沒有輸入price就是以當前價格買入
        假如輸入了price就是限價買入
        """
        
        if price is None:
            price = self.get_price(sid)['StockInfo']['FloorPrice']
            time.sleep(self.wait_time)
            
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/userset.ashx', params={
            'act': 'NewEntrust',
            'aid': self.aid,
            'stock': sid,
            'price': price,
            'ordqty': 1,
            'tradekind': 'c',
            'type': 's',
            'hasWarrant': 'false',
        })
    
    def account_status(self):
        
        """
        查看目前account的狀態：
        [{'Id': '1101',
          'Name': '台泥',
          'TkT': '現股',
          'NowPr': '43.05',
          'DeAvgPr': '43.20',
          'IQty': '1',
          'IncomeLoss': '-402',
          'Ratio': '-0.93',
          'Cost': '43,200.00',
          'ShowCost': '43,200.00',
          'TodayQty': '0',
          'BoardLostSize': '1000',
          'IsWarrant': '0'}]
        """
        
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
            'act': 'InventoryDetail',
            'aid': self.aid,
        })
        
        return json.loads(res.text)
    
    def clear_account(self):
        
        """將所有的股票做即刻賣出的動作"""
        
        acc = self.account_status()
        time.sleep(self.wait_time)
        for s in acc:
            print('sell ', s['Id'], s['IQty'])
            self.sell(s['Id'], s['IQty'])
            time.sleep(self.wait_time)
            
    def buy_list(self, s):
        
        """
        將清單中的股票即刻買入的動作，其中s為一個dictionary或series，
        例如
        以字典表示：
        
        s = {
            '1101': 2,
            '2330': 1,
        }
        
        或是以pandas series表示：
        
        1101    2
        2330    1
        dtype: int64
        
        兩種都可以，假如數字為負號，則會進行賣出的動作
        """
        
        for sid, q in s.items():
            print('buy ', sid, q)
            if q > 0:
                self.buy(sid.split()[0], q)
            else:
                self.sell(sid.split()[0], abs(q))
            time.sleep(self.wait_time)
            
    def get_orders(self):
        
        """拿到當下的委託"""
        
        res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
            'act': 'EntrustQuery',
            'aid': self.aid,
        })
        
        return json.loads(res.text)
        
    def cancel_all_orders(self):
        
        """清空當下的委託"""
        
        orders = self.get_orders()
        time.sleep(self.wait_time)
        for o in orders:
            print(o['Id'])
            if o['CanDel'] == '1':
                res = self.ses.get('https://www.cmoney.tw/vt/ashx/accountdata.ashx', params={
                    'act': 'DeleteEntrust',
                    'aid': self.aid,
                    'GroupId': 0,
                    'OrdNo': o['CNo'],
                })

                time.sleep(self.wait_time)
                
    def adjust_holdings(self, newlist):
        
        """
        將持股更新成newlist，newlist的結構可以參考buy_list的input，是一樣的。
        """
        
        newlist = pd.Series(newlist)
        status = self.account_status()
        oldlist = pd.Series({s['Id']:s['IQty'] for s in status}).astype(int)
        newlist = newlist.reindex(oldlist.index | newlist.index).fillna(0)
        oldlist = oldlist.reindex(oldlist.index | newlist.index).fillna(0)

        self.buy_list(newlist - oldlist)