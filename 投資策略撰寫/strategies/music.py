def strategy(data):
    
    # 計算 alpha beta (截點跟焦點)
    days = 800
    c = data.get('收盤價', days)
    
    # 請參考 https://zh.wikipedia.org/w/index.php?title=%E7%B7%9A%E6%80%A7%E5%9B%9E%E6%AD%B8
    # 中的單變量回歸

    y = c.iloc[-days:]
    x = pd.Series(list(range(days)), index=y.index)
    midy = y.mean(axis=0)
    midx = days/2

    beta = (y - midy).mul(x - midx, axis=0).sum()/((x-midx)**2).sum()
    alpha = midy - midx * beta


    # 計算中線跟標準差
    X = pd.DataFrame({k: x for k in beta.index})
    mid_line = ((X * beta + alpha))
    std = (y - mid_line).std()
    
    conditions = [
        (c.iloc[-1] < mid_line.iloc[-1] - 2*std),
        c.iloc[-1] > c.iloc[-20:].mean()
    ]
    
    selected_stock = sum(conditions) == len(conditions)
    
    return selected_stock[selected_stock]