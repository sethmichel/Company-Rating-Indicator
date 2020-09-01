import tweepy
import datetime as dt


# called from backend.twitter_communicator()
# tickers = list of tuples (ticker, rating)
def initilize_api(tickers):
    callback_uri = "oob"
    key = ""
    secret_key = ""
    access_token = ""
    access_token_secret = ""
    
    auth = tweepy.OAuthHandler(key, secret_key, callback_uri)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)   # now have access to everyhting in the tweepy api
    
    check_tweet_history(api, tickers)


# check if app has tweeted today - I won't tweet again if a new stock is added that wasn't in today's
# tweet to avoid spam - just tweet once a day max
# todays_date = "8-3-2020", note: tweet_date doesn't put extra 0's in date. it's "8", not "08"
# tweet_time = "5:25" for 5am 25 min
def check_tweet_history(api, tickers):
    prev_tweet_dt = api.user_timeline(count = 1)[0].created_at   # datetime obj
    todays_dt = dt.datetime.now() # year, month, day, hr, min, sec
    
    # check it's been at least 1 day
    difference = todays_dt - prev_tweet_dt
    if (int(difference.days) >= 1):
        post_tweet(api, tickers)

    else:
        return "already posted today"


# tickers is list of tuples (ticker, rating)
def post_tweet(api, tickers):
    text = ""

    for i in range(0, len(tickers)):
        text = text + tickers[i][0] + ": " + tickers[i][1] + ", "
    text = text[0:-2]   # remove the last ", "

    if (len(text) > 279):
        text = text[0: 279]

    api.update_status("Bot: best currently tracked tickers are:\n" + text)






