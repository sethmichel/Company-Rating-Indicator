# Stock-Rating-App

Gives a buy rating to user entered stocks based on recent data. Written in python, uses the Kivy framework for GUI, MYSQL for database management, the yfinance api to 
collect data, and the tweepy api to post to twitter when there's a stock at a rating of 9+.

When user enteres a ticker, the yfinance api will get that tickers recent close prices, and the % gains will be calculated for each day. The user is responsible for entering 
how far the price is from 300 exponential moving average line for that day, and if the stock has finished a particular move that day (defined in the app). Using this data, a rating
is given to the ticker for each day

The plot functionality is using the kivy garden/graph module which is very similar to matplotlib (many of the same fuctions / functionality), but it works in kivy. (kivy garden
modules are unofficial user made extentions of kivy)

Note: to make this work you have to add your own sql info in sql_handler.py, and your twitter developer keys and access tokens in twitter_handler.py.


![](https://i.imgur.com/0vMMYdt.jpg)
![](https://i.imgur.com/W9cSm4o.jpg)
![](https://i.imgur.com/ZqOGPVj.jpg)
