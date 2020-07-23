import pandas as pd
import os
import datetime
import sql_handling
import yfinance as yf


# called from kivy init
# uses datetime to get the trading days of last week and this week. excluding weekends
# so if today's fri, it's the last day of the list, then on mon the list updates to next week
def get_trading_days():
    trading_days = []

    # I need the date of this week's monday, then I make the list starting last week
    x = datetime.date.today()
    monday = x - datetime.timedelta(7 - (7 - x.weekday()))
    add_date = monday - datetime.timedelta(7)

    for i in range(0, 20):
        # moves to monday if today is sat or sun
        if (add_date.weekday() > 4):
            add_date += (datetime.timedelta(1) * (7 - add_date.weekday()))   

        trading_days.append(str(add_date.month) + "/" + str(add_date.day))
        add_date += datetime.timedelta(1)

    return trading_days


# called from kivy_code init()
# gets the day of week -5 it is so it fits as an index in kivy.make_row(), 0 = mon, 6 = sun
def get_todays_date():
    # if it's a sat or sun, return fri
    day = int(datetime.date.today().weekday())
    if (day == 5 or day == 6):
        return -1
    else:
        return day - 5


# sql needs the month and year to make a new table
# strftime("%B") converts the month num to the month name (3 -> march)
# called from kivy init(), returns list of last month, this month, and next month ex) ["12, dec2019", "Jan2020"]
def get_month_year():
    tablenames = []
    currmonth = datetime.date.today()

    first = currmonth.replace(day = 1)         # 1st of the month
    lastmonth = first - datetime.timedelta(1)  # month is now last month, year roll over included
    nextmonth = first + datetime.timedelta(32) # month is now next month, year roll over included

    tablenames.append(lastmonth.strftime("%B") + str(lastmonth.year))
    tablenames.append(currmonth.strftime("%B") + str(currmonth.year))
    tablenames.append(nextmonth.strftime("%B") + str(nextmonth.year))
    
    return tablenames


# called from testing
# when reading sql data, it could go into last or next month's tables, this determines that and returns the correct tables for the week
def get_curr_table(tablenames, date):
    picked_month = int((date[0]))
    curr_month = int(tablenames[1][0])

    if (picked_month < curr_month):
        return tablenames[0]
    elif (picked_month == curr_month):
        return tablenames[1]
    else:
        return tablenames[2]


# called from kivy_code.update_ui()
# if week goes into 2 diff months, then get tickers from 2 tables
def call_get_tickers(tablenames, trading_days):
    ticker_list = sql_handling.get_tickers(tablenames[1])

    if (trading_days[15][0] != trading_days[-1][0]):
        if (trading_days[15][0] > trading_days[-1][0]):   # if fri goes into next month
            ticker_list.extend(sql_handling.get_tickers(tablenames[2]))

        else:                                             # if mon goes into last month
            ticker_list.extend(sql_handling.get_tickers(tablenames[0]))

    return ticker_list














# called from kivy_code.call_get_data()
# gets a list of sql data at app start to write to UI
# pm ex): tablenames = list of 3 tablenames, trading_day = "6/15", ticker = "cde"
def call_get_data(tablenames, trading_day, ticker):
    # time frame could go into next month
    table_to_use = get_curr_table(tablenames, trading_day)

    # get the col name
    column = sql_handling.updator(int(trading_day.split("/")[1]))

    # get the cell data
    data = [trading_day]
    week_list = sql_handling.get_data(table_to_use, column, ticker).split("*")
    for element in week_list:
        data.append(element)

    return data





# called at start of kivy_code()
# when user wants to enter info, the today and yesterday btns should be disabled only if
# > they are non-trading days
def kivy_btn_disabler():
    disabler = [False, False]

    day = datetime.date.today().weekday()
    if (day == 0 or day == 6):
        disabler[0] = True
    if (day == 6 or day == 5):
        disabler[1] = True
    
    return disabler


# called from kivy
# checks format of user entered date - Note: btns are already disabled if they connect to a weekend
#  > so user could't press them - thus only check txt input
def check_user_date(btn1, btn2, txtin, trading_days, flag):
    # check text input  
    if (flag == "txtin"):
        if (len(txtin.text) > 5):
            return "Rejected, invalid date"
        elif ("/" not in txtin.text):
            return "Rejected, invalid date format (correct ex: 4/15)"
        splitstr = txtin.text.split("/")
        if (not(splitstr[0].isnumeric() and splitstr[1].isnumeric())):
            return "Rejected, invalid date format (correct ex: 4/15)"
        elif (txtin.text not in trading_days):
            return "Rejected, can't enter for that date"

        return txtin.text
    
    # if btns, return their dates
    else:
        day = datetime.date.today().weekday()   # mon = 0

        if (flag == "Yesterday"):
            return trading_days[day - 6]

        else:
            return trading_days[day - 5]


# called from kivy
# Prior to this I don't know what data fields user filled out, also formats it
# pm is a button so logic is: btn -> box -> grid -> 4 txt inputs
def check_user_data(ui_access):
    fast = ui_access.parent.children  # the grid, data is in spots 5, 7, 9, 11
    data = [None, None, None, None]   # ticker, cp, % from 400 ema, breakout_moves

    for i in range(6, -1, -2):
        if (fast[i].text != ""):
            input = fast[i].text

            # ticker, can only have letters and /. Input will be "" is user close to update ticker rather than make new ticker
            if (i == 6):
                if (input[0] == "/"):
                    input = ticker[1:]
                if (input.isalpha() == False or len(input) > 5):
                    return "Ticker invalid, not all alphas or too long"                
                data[0] = input.lower()

            # close price and % gain
            elif (i == 2 or i == 4):
                if (i == 2):
                    if (input[-1] == "%"):
                        input = input[:-1]
                    
                    elif (input[0] == "$"):
                        input = input[1:]

                if (input.find(".") == -1):   # user could enter "small" - this is only way to catch it
                    if (input.isnumeric() == False):
                        return "Invalid number"
                else:
                    holder = input.split(".")
                 
                    if (holder[0].isnumeric() == False or holder[1].isnumeric() == False):
                        return "Invalid number"

                    if (len(holder[0]) > 5):
                        holder[0] = holder[0][:5]
                    if (len(holder[1]) > 2):
                        holder[1] = holder[1][:2]

                    holder = holder[0] + "." + holder[1]   # testing is this a str?

                if (i == 4):
                    data[1] = input
                else:
                    data[2] = input

            # break out moves
            else:   
                input = input.lower()                

                if (input != "fake" and input != "small" and input != "big"):
                    return "invalid phrase"
                elif (len(input) > 5):
                    return "invalid phrase"
                elif (input.isalpha() == False):
                    return "invalid phrase"

                data[3] = input

    if (data == [None, None, None, None]):
        return "No data was entered"
    else:
        return data


# called from sql_handling.write_to_sql()
# this method is called in a loop, each time data is a string touple of new user entered data
# db has things separated by "*", and breakout_moves is a touple since it's many data points
def format_sql_data(tablename, new_col, data):
    # ex data) [ticker, cp, % 400 ema, breakout_moves]
    # ex prev_data) [cp, % 400 ema, breakout moves, % gain, rating]
    write_data = ""
    prev_data = sql_handling.get_data(tablename, new_col, data[0])

    # format prev_data
    if (prev_data == "None"):
        prev_data = "?*?*?*?*?"

    prev_data = prev_data.split("*")

    # replace data, data[0] is ticker so skip that
    for i in range(0, len(data[1:])):
        if (data[i + 1] != None):
            prev_data[i] = data[i + 1]

    # put the prev_data together to get ready to overwrite to sql
    for i in range(0, len(prev_data)):
        write_data = write_data + prev_data[i] + "*"

    # these '' are dumb formatting for sql
    return "'" + write_data[:-1] + "'"


# called from kivy.make_row()
# calculates the % gain which is 1 - (yesterday's close price / todays close price)
# pm: btn_list = access btn data
def find_percent_gain(btn_list, tablenames, trading_days):
    cp1 = btn_list[-1].ids["close_price"]   # the curr day in make_row()
    if (cp1 == "?"):
        return "?"

    # if cp1 is mon I need to call sql to get last fri
    if (btn_list[-2].id == "ticker_btn"):
        curr_table = get_curr_table(tablenames, btn_list[-1].ids["date"])          # get table
        fri = (trading_days[(trading_days.index(btn_list[-1].ids["date"])) - 1])   # get index / uses that to get date of last fri
        col = sql_handling.updator(int((fri.split("/"))[1]))                       # get correct col (the day)
        cp2 = sql_handling.get_data(curr_table, col, btn_list[-1].ids["ticker"])   # get data of that cell
        cp2 = cp2[1]                                                               # this is the close price of that cell
    
    else:
        cp2 = btn_list[-2].ids["close_price"]

    if (cp2 != "?"):
        return str(round(1.00 - (float(cp2) / float(cp1)), 2))
    else:
        return "?"


# called from kivy.make_row()
# use custom formula to give each day a buy rating - only if there's enough prior / present info
# pm: tablenames = last/curr/next month, this_weeks_data = data from this week up to the curr day since this is called for each btn
# pm: last_week_trade_days = dates of mon-fri last week
def create_rating(curr_btn, tablenames, this_weeks_data, last_week_trade_days, ticker):
    # ex data) [ [ date, cp, % 400 ema, breakout moves, % gain, rating ] ]
    # ex data) [ [ 6/15, ?, 15.6, 'fake,fake', 4.3, 7.5 ] ]
    # this_weeks_data is the same as data
    data = []
    for i in range(0, 5):
        data.append(call_get_data(tablenames, last_week_trade_days[i], ticker))
        if (len(data[-1]) == 2):
            data[-1] = [data[-1][0], "?", "?", "?", "?", "?"]
    
    data.extend(this_weeks_data)

    breakout_handler = [0, []]      # accepts return which is tuple of score and breakout_list
    percent_gain_handler = [0, 0]   # accepts return which is tuple of score and counter
    percent_ema_handler = [0, 0]    # accepts return which is tuple of score and counter
    rating_handler = [0, 0]         # accepts return which is tuple of score and counter

    # for past data then this weeks data, for each category, and for each day of the week
    # cat is 2 - 6 bec 0 and 1 are date and cp neither of which is used in this block
    for cat in range(2, 6):
        for day in range(0, len(data)):
            test_data = data[-day - 1][cat]

            if (test_data != "?"):
                if (len(breakout_handler[1]) < 3 and cat == 3):
                    breakout_handler = rating_breakout_moves(test_data, breakout_handler)

                if (percent_gain_handler[1] < 5 and cat == 4):
                    percent_gain_handler = rating_percent_gain(float(test_data), percent_gain_handler)

                if (percent_ema_handler[1] < 5 and cat == 2):
                    percent_ema_handler = rating_percent_ema(float(test_data), percent_ema_handler)

                if (rating_handler[1] < 5 and cat == 5):
                    rating_handler = rating_rating(float(test_data), rating_handler)

    # only return rating if there's enough data
    if (breakout_handler[1] < 1 or percent_gain_handler[1] < 5 or percent_ema_handler[1] < 5 or rating_handler < 5):
        return "?"
    else:
        return str((breakout_handler[0] + percent_gain_handler[0] + percent_ema_handler[0] + rating_handler[0]) / 4.0)


# called from create_rating()
# updates score with prev % ema's - part of calculating rating
# pm: test_data = that days float % ema
def rating_percent_ema(test_data, handler):
    handler[1] += 1

    if (test_data < 0):
        test_data = test_data * -1

    # each "if" is giving score based on what % the test_data is (0 - 10%)
    if (test_data < 1):
        handler[0] += 5

    elif (test_data > 1 and test_data < 2):
        handler[0] += 6
    elif (test_data > 2 and test_data < 3):
        handler[0] += 3
    elif (test_data > 3 and test_data < 4):
        handler[0] += 1
    
    return handler 


# called from create_rating()
# updates score with breakout_moves - part of calculating rating
def rating_breakout_moves(test_data, handler):
    if (test_data == "fake"):
        handler[1].append("fake")
        handler[0] += 1

    elif (test_data == "small"):
        handler[1].append("small")
        handler[0] += 2

    elif (test_data == "big"):
        handler[1].append("big")
        handler[0] += 3

    # 3 fakes in a row = 2 pts
    if (len(handler[1]) > 2 and handler[1][-1] == "fake" and handler[1][-2] == "fake" and handler[1][-3] == "fake"):
        handler[0] += 2
    # 2 fakes in row = 1 pt
    elif (len(handler[1]) > 1 and handler[1][-1] == "fake" and handler[1][-2] == "fake"):
        handler[0] += 1
    # small then fake = 1 pt
    if (len(handler[1]) > 1 and handler[1][-1] == "small" and handler[1][-2] == "fake"):
        handler[0] += 1

    return handler


# called from create_rating()
# updates score with prev percent_gain's - part of calculating rating
# pm: test_data = that days float % gain
def rating_percent_gain(test_data, handler):
    handler[1] += 1

    if (test_data < 0):
        test_data = test_data * -1

    # each "if" is giving score based on what % the test_data is (0 - 10%)
    if (test_data < 1): 
        handler[0]

    elif (test_data > 1 and test_data < 2): 
        handler[0] += 1, 
    elif (test_data > 2 and test_data < 3): 
        handler[0] += 1
    elif (test_data > 3 and test_data < 4): 
        handler[0] += 3 
    elif (test_data > 4 and test_data < 5): 
        handler[0] += 3
    elif (test_data > 5 and test_data < 6): 
        handler[0] += 4
    elif (test_data > 6 and test_data < 7): 
        handler[0] += 5
    elif (test_data > 7 and test_data < 8): 
        handler[0] += 6
    elif (test_data > 8 and test_data < 9): 
        handler[0] += 8
    elif (test_data > 9 and test_data < 10): 
        handler[0] += 9

    else: handler[0] += 10

    return handler


# called from create_rating()
# updates score with prev ratings - part of calculating rating
# pm: test_data = that days str rating
def rating_rating(test_data, handler):
    handler[1] += 1

    # if test_data < 1 then don't add anything to score

    if (test_data > 1 and test_data < 4): 
        handler[0] += 2

    if (test_data > 4 and test_data < 6): 
        handler[0] += 3

    if (test_data > 6 and test_data < 7): 
        handler[0] += 4

    if (test_data > 7 and test_data < 8): 
        handler[0] += 5
    
    if (test_data > 8 and test_data < 9): 
        handler[0] += 6

    else:
        handler[0] += 8

    return handler







def testing():
    dates = ['6/2', '6/11', '6/12', '6/17', '6/18']
    data = [('Ticker', 'ugaz'), ('Close_Price', '15.6'), ('Percent_From_400_ema', '3.4')]
    btn_list = None
    user_date = '6/17'
    plus_btn_clicked_id = 'top_add_btn'
    

    sql_handling.connect_to_db()
    #call_get_data("june2020", dates)
    #kivy_code.make_row(btn_list, mast_list, trading_day)


#testing()




#print("pause")

































