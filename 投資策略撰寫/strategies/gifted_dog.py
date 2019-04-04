
import pandas as pd

def toSeasonal(df):
    season4 = df[df.index.month == 3]
    season1 = df[df.index.month == 5]
    season2 = df[df.index.month == 8]
    season3 = df[df.index.month == 11]

    season1.index = season1.index.year
    season2.index = season2.index.year
    season3.index = season3.index.year
    season4.index = season4.index.year - 1

    newseason1 = season1
    newseason2 = season2 - season1.reindex_like(season2)
    newseason3 = season3 - season2.reindex_like(season3)
    newseason4 = season4 - season3.reindex_like(season4)

    newseason1.index = pd.to_datetime(newseason1.index.astype(str) + '-05-15')
    newseason2.index = pd.to_datetime(newseason2.index.astype(str) + '-08-14')
    newseason3.index = pd.to_datetime(newseason3.index.astype(str) + '-11-14')
    newseason4.index = pd.to_datetime((newseason4.index + 1).astype(str) + '-03-31')

    return newseason1.append(newseason2).append(newseason3).append(newseason4).sort_index()

def strategy(data):
    # capital = data.get('股本合計',1)
# price = data.get('收盤價',100)
# # 先拿出計算市值需要用到的財務數據

    股本 = data.get('股本合計', 1)
    price = data.get('收盤價', 100)

    當月營收 = data.get('當月營收', 4) * 1000
    當季營收 = 當月營收.iloc[-4:].sum() # 取近4個月營收總和，當作一季的月營收（4也可以改變）
   


    # 將每季累計的財務數據，轉換成單季


    # 計算自由現金流 = 營業活動之淨現金流入 - 投資活動之淨現金流出
    投資現金流 = toSeasonal(data.get('投資活動之淨現金流入（流出）', 8))
    營業現金流 = toSeasonal(data.get('營業活動之淨現金流入（流出）', 8))
    自由現金流 = (投資現金流 + 營業現金流).iloc[-4:].sum()

    稅後淨利 = data.get('本期淨利（淨損）', 5)

    # 修正：因為有些股東權益的名稱叫作「權益總計」有些叫作「權益總額」，所以要先將這兩個dataframe合併起來喔！
    權益總計 = data.get('權益總計', 5)
    權益總額 = data.get('權益總額', 5)

    # 把它們合併起來（將「權益總計」為NaN的部分填上「權益總額」）
    權益總計.fillna(權益總額, inplace=True)

    股東權益報酬率 = 稅後淨利.iloc[-1] / 權益總計.iloc[-1]
    股東權益報酬率.describe()

    上季股東權益報酬率 = 稅後淨利.iloc[-5] / 權益總計.iloc[-5]
    上季股東權益報酬率.describe()

    營業利益 = data.get('營業利益（損失）', 5)
    營業利益成長率 = (營業利益.iloc[-1] / 營業利益.iloc[-5] - 1) * 100
    營業利益成長率.describe()

    # current
    流動資產 = data.get('流動資產合計',5)
    流動負債 = data.get('流動負債合計',5)
    current_ratio = 流動資產/流動負債
    # liability
    long_liability = data.get('非流動負債合計',5)
    long_liability

    #capital
    stocks = data.get('普通股股本',5)
    #inventory
    control_season = 2
    inventory = data.get('存貨合計',6)
    asset = data.get('資產總計',6)
    no_turnover = inventory/asset
    turnover_ratio = 1 - no_turnover
    turnover_growth_rate = (turnover_ratio.iloc[-control_season] /turnover_ratio.iloc[-control_season-4])
    turnover_growth_rate[0]

    condition1 = 當季營收 > 0
    condition2 = 自由現金流 >0
    condition3 = (營業現金流.iloc[-1]>0)
    condition4 = long_liability.iloc[-1] < long_liability.iloc[-5]
    condition5 = current_ratio.iloc[-1] >current_ratio.iloc[-5]
    condition6 = (stocks.iloc[-1] - stocks.iloc[-5])>0
    condition7 = 股東權益報酬率 > 上季股東權益報酬率
    condition8 = 營業利益成長率>0 #把毛益率改成營業利益率
    condition9 = turnover_growth_rate >0
    # condition10 = (price/10) > 3  

    # 將條件做交集（&）
    select_stock_first = condition1 & condition2 & condition3 & condition4 & condition5 

    select_stock_second = select_stock_first & condition6 &condition7&condition8 & condition9

    # 選出的股票
    select_stock = select_stock_second[select_stock_second]
    return select_stock
