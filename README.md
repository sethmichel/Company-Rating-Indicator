# Stock-Rating-App
Note, Currently under construction. My future intensions are to deploy this to android (kivy is cross platform). And to possibly add a news analyzer

Gives a buy rating to user entered stocks based on recent data. Written in python, uses the Kivy framework for GUI, MYSQL for database management, and the yfinance api to 
collect data

When user enteres a ticker, the yfinance api will get that tickers recent close prices, and the % gains will be calculated for each day. The user is responsible for entering 
how far the price is from 300 exponential moving average line for that day, and if the stock has finished a particular move that day (defined in the app). Using this data, a rating
is given to the ticker for each day

The plot functionality is using the kivy garden/graph module which is very similar to matplotlib (many of the same fuctions / functionality), but it works in kivy. (kivy garden
modules are unofficial user made extentions of kivy)


