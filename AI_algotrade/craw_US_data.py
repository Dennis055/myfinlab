craw_US_data.py
import requests
import pandas
import io
import datetime

# Step 1. Get ticker list online
url = 'http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download'
dataString = requests.get(url).content
tickersRawData = pandas.read_csv(io.StringIO(dataString.decode('utf-8')))
tickers = tickersRawData['Symbol'].tolist()

# Step 2. Save the ticker list to a local file
dateToday = datetime.datetime.today().strftime('%Y%m%d')
file ='/Users/Dennis/Desktop/Myfinlab/AI_algotrade/dataUSA/'+dateToday+'.csv'
tickersRawData.to_csv(file, index=False)
print ('Tickers saved.')