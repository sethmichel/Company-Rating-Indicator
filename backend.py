import datetime as dt
import sql_handler
import yfinance as yf   # get api data
import pandas as pd     # yfinance returns as panda df
from math import sin    # plot handling
from kivy_garden.graph import Graph, MeshLinePlot   # plot handling


# if yfinance is called intraday, it'll return a close price of the current price - which is wrong
# this makes sure yfinance will only be called at least 20 min after market close (most quotes are 20 min delayed)
# gets time as utc timezone (+7 hrs vs pst time)
def get_system_time():
    time = dt.datetime.utcnow().strftime("%H:%M:%S").split(":")  # # 13:25:35 as str's
    for i in range(0, 3):
        time[i] = int(time[i])
    
    return time   # [13, 25, 35 ] as ints

# calls yfinance to get all missing close_prices
# pm: date = '2020-5-8', dateend = day after date. history needs an exclusive end
def get_close_prices(ticker, date, dateend):
    # utc market times: open 13:30 - 20, closed from 20 - 13:30
    time = get_system_time()   # [13, 25, 35 ] as ints
    command = True

    # convert date to dt obj, if it's not today, then I don't care about market open times
    # I'll call this for past days, and future days, but I have other checks to prevent going beyond today and breaking
    newdate = date.split('-')
    newdate = dt.date(int(newdate[0]), int(newdate[1]), int(newdate[2]))
    today = dt.date.today()
    if (newdate == today):
        command = False

    # if it's past day then do it, if it's today then check times, it can't be past today
    # if long after market OR long before market OR (just before market open) OR at least 20 min after market close
    if (command == True or (time[0] > 20 or (time[0] < 13) or (time[0] < 13 and time[1] < 30) or (time[0] == 20 and time[1] > 20))):
        return str(yf.Ticker(ticker).history(start = date, end = dateend)["Close"][0])
    else:
        return None


# called from kivy init
# uses datetime to get the trading days of either this week or last week in form 2020-05-09
# note: this actually gets last 11 trading days, because the api needs tomorrows date to get todays date, so index 10 is just a pm for that
def get_trading_days():
    trading_days = []

    # I need the date of this week's monday, then I make the list starting last week
    x = dt.date.today()

    monday = x - dt.timedelta(7 - (7 - x.weekday()))
    add_date = monday - dt.timedelta(7)

    for i in range(0, 11):
        # moves to monday if today is sat or sun
        if (add_date.weekday() > 4):
            add_date += (dt.timedelta(1) * (7 - add_date.weekday()))   

        trading_days.append(str(add_date.year) + "-" + str(add_date.month) + "-" + str(add_date.day))
        add_date += dt.timedelta(1)

    return trading_days


# called from kivy_code init(), used to find right btns to highlight
# gets the day of week -5 it is so it fits as an index in kivy.make_row(), 0 = mon, 6 = sun
def get_todays_index():
    # if it's a sat or sun, return fri
    day = int(dt.date.today().weekday())
    if (day == 5 or day == 6):
        day = 4
    
    return day + 3   # mon = 3, fri = 7


# return ex) "8/10"
def get_todays_date():
    today = dt.date.today()
    return str(today.year) + "-" + str(today.month) + "-" + str(today.day)
    

# called from testing
# converts date for data into the name of the right sql table. (date = 2020-month-day or 2020-month
def make_table_name(date, tablenames):
    date = date.split("-")
    date = dt.date(int(date[0]), int(date[1]), 1)
    table = date.strftime('%B').lower() + str(date.year)   # ex) july2020

    return table


# called from kivy_code.update_ui()
# get tickers from this month and last month
# pm: tablenames = list of all tablenames in db
def call_get_tickers(tablenames):
    today = dt.date.today()
    ticker_list = []
    for i in range(0, 2):
        table = make_table_name(str(today.year) + "-" + str(int(today.month) - i), tablenames)

        sql_handler.check_table_exists(table, tablenames)

        add = sql_handler.get_data(table, "", "", "tickers")

        # blank sql tables trigger this
        if (add[0] != ""):
            length = len(add)
            i = 0
            j = 0
            while (j < length):
                if (add[i] in ticker_list):
                    del add[i]
                    i -= 1
                i += 1
                j += 1

            ticker_list.extend(add)

    return ticker_list


# gets a list of sql data at app start to write to UI
# pm ex): trading_day = "2020-6-15", ticker = "cde"
def call_get_data(tablenames, trading_day, ticker):
    # time frame could go into next month
    table_to_use = make_table_name(trading_day, tablenames)

    # get the col name
    col = sql_handler.updator(int(trading_day.split("-")[2]))

    # get the cell data
    data = [trading_day]
    data.extend(sql_handler.get_data(table_to_use, col, ticker, "cell").split("*"))

    # blank cells would trigger this
    if (data[-1] == ""):
        del data[-1]

    return data   # ex) [ date, cp, % ema, bm, % gain, rating ]


# db has things separated by "*", and breakout_moves is a touple since it's many data points
def format_sql_data(table, col, data, ticker):
    # ex data)      [ cp, % ema, bm, % gain, rating ]
    # ex prev_data) [ cp, % ema, bm, % gain, rating ]
    write_data = ""
    prev_data = sql_handler.get_data(table, col, ticker, "cell")

    # format prev_data
    if (prev_data == ""):
        prev_data = "?*?*?*?*?"

    prev_data = prev_data.split("*")

    # merge data into prev_data and start re-combining prev_data into a str
    for i in range(0, len(data)):
        if (data[i] != "?"):
            prev_data[i] = str(data[i])
        write_data = write_data + prev_data[i] + "*"

    # these '' are dumb formatting for sql
    return "'" + write_data[:-1] + "'"


# collects all sql data for ticker_list into a 2d list for program to use
# each append to master_list is: [ date, cp, % ema, bm, % gain, rating ]
# pm: tablenames = all tables, ticker_list = tickers of this/last month, trading days = this/last weeks trading days
def get_all_data(tablenames, ticker_list, trading_days):
    master_list = []

    for i in range(0, len(ticker_list)):
        master_list.append([ticker_list[i]])

        get_api_data(master_list[-1], ticker_list[i], trading_days, tablenames)

    return master_list


# this is called in a loop at app start, and once when user enters new ticker
# gets sql data / api data on tickers, adds to master list
# pm: ticker = cde, trading_days = full list, i = outer loop (ticker), j = index I'm curr on since this is called in loops
# pm: data = master_list[i], it's data for 1 ticker, starts as just the ticker, then I add in [date, cp, %  ema, bm, % gain, rating ] for all 10 days
def get_api_data(data, ticker, trading_days, tablenames):
    stop_flag = ""
    filled_flag = ""
    check_date = dt.date.today() + dt.timedelta(days = 1)
    check_date = str(check_date.year) + '-' + str(check_date.month) + '-' + str(check_date.day)

    for i in range(1, 11):
        # if it's past curr weeks trading day, then yfinance breaks thus making finding % gain break
        if (trading_days[i - 1] == check_date):
            stop_flag = "past today"

        data.append(call_get_data(tablenames, trading_days[i - 1], ticker))   # dim 2

        # blank sql cells trigger this
        if (len(data[i]) == 1):
            data[i].extend(["?", "?", "?", "?", "?"])

        # get all missing cp's
        if (stop_flag != "past today" and data[i][1] == "?"):
            # returns "?" if called intraday
            data[i][1] = get_close_prices(ticker, trading_days[i - 1], trading_days[i])
            if (data[i][1] != "?"):
                filled_flag = "filled"

        # get all missing % gains
        if (stop_flag != "past today" and data[i][4] == "?" and i > 1):
            data[i][4] = calc_percent_gain(float(data[i - 1][1]), float(data[i][1]))
            filled_flag = "filled"
        
        # the first date of each ticker will be missing its % gain
        if (stop_flag != "past today" and data[1][4] == "?"):
            prior_date = get_diff_date(trading_days[0], "prior")
            cp_prior = get_close_prices(ticker, prior_date, trading_days[0])
            data[1][4] = calc_percent_gain(float(cp_prior), float(data[1][1]))

        # calculate missing ratings
        if (stop_flag != "past today" and data[i][5] == "?" and i > 5):
            data[i][5] = create_rating(data[1:i + 1])
            if (data[i][5] != "?"):
                data[i][5] = str(round(float(data[i][5]), 2))
                filled_flag = "filled"

        # if any data changed, write it to sql (possible 2 things changed so I waited to write this)
        if (filled_flag == "filled"):
            col = sql_handler.updator(int(data[i][0].split("-")[2]))
            table = make_table_name(trading_days[i - 1], tablenames)

            formatted_data = format_sql_data(table, col, data[i][1:], ticker)
            sql_handler.make_row(table, ticker, "", [])
            sql_handler.write_to_sql(table, col, formatted_data, ticker)
    
        filled_flag = ''

    return data


# calculates the % gain which is 1 - (yesterday's close price / todays close price)
# pm: the cp's are float close prices
def calc_percent_gain(cp_yest, cp_tod):
    return str(round((1.00 - (cp_yest / cp_tod)) * 100, 2))


# sat/sun may disable yest/today btns in UI (non-trading days)
# pm: yest_btn = yesterday btn, tod_btn = today_btn
def kivy_btn_disabler(yest_btn, tod_btn):
    day = dt.date.today().weekday()
    if (day == 0 or day == 6):
        yest_btn.disabled = True
    if (day == 6 or day == 5):
        tod_btn.disabled = True


# called from kivy
# checks format of user entered date - Note: btns are already disabled if they connect to a weekend
#  > so user could't press them - thus only check txt input
def check_user_date(txtin, trading_days, flag):
    day = dt.date.today()

    # check text input
    if (flag == "txtin"):
        if (len(txtin.text) > 5):
            return "Rejected, invalid date"
        txtin.text = txtin.text.replace("/", "-")   # does nothing if "/" isn't there
        if ("-" not in txtin.text):
            return "Rejected, invalid date format (correct ex: 4-15)"
        splitstr = txtin.text.split("-")
        if (not(splitstr[0].isnumeric() and splitstr[1].isnumeric())):
            return "Rejected, invalid date format (correct ex: 4-15)"

        date = dt.date(day.year, int(splitstr[0]), int(splitstr[1])).weekday()
        if (date == 5 or date == 6):
            return "Rejected, can't enter data for a weekend"

        return str(day.year) + "-" + txtin.text
    
    # if btns, return their dates
    else:
        day = day.weekday()   # mon = 0

        if (flag == "Yesterday"):
            return trading_days[day - 7]

        else:
            return trading_days[day - 6]


# called from kivy
# Prior to this I don't know what data fields user filled out, also formats it
# pm is a button so logic is: btn -> box -> grid -> 4 txt inputs 
def check_user_data(ui_access):
    fast = ui_access.parent.children  # the grid, data is in spots 4, 2, 0
    data = ["?", "?", "?"]   # ticker, % from 400 ema, breakout_moves

    for i in range(4, -1, -2):
        if (fast[i].text != ""):
            input = fast[i].text

            # ticker, can only have letters and /. Input will be "" is user chose to update ticker rather than make new ticker
            if (i == 4):
                if (ticker[0] == "/"):   # futures trigger this
                    ticker = ticker[1:]
                if (ticker.isalpha() == False or len(ticker) > 5):
                    return "Rejected ticker invalid. Not all alphas or too long"
 
                data[0] = input.lower()

            # check % ema
            elif (i == 2):
                if (input[-1] == "%"):
                    input = input[:-1]

                if (input.find(".") == -1):   # user could enter "small" - this is only way to catch it
                    if (input.isnumeric() == False):
                        return "Rejected, invalid number"
                    input = input + ".00"     # triggered if user wrote "5" or "10"

                holder = input.split(".")

                
                if (holder[0].isnumeric() == False or holder[1].isnumeric() == False):
                    return "Rejected, invalid number"

                if (len(holder[0]) > 5):
                    holder[0] = holder[0][:5]
                if (len(holder[1]) > 2):
                    holder[1] = holder[1][:2]

                data[1] = input

            # break out moves
            else:   
                input = input.lower()                

                if (input != "fake" and input != "small" and input != "big"):
                    return "Rejected, invalid phrase"
                elif (len(input) > 5):
                    return "Rejected, invalid phrase"
                elif (input.isalpha() == False):
                    return "Rejected, invalid phrase"

                data[2] = input

    return data


# returns data in format: [ cp, % ema, bm, % gain, Rating ]
# pm: user_data = [ticker, % ema, bm], "?" for missing data, user_date = 2020-5-6
# pm: enddate = yfinance needs day after user_date to get user_date data
def format_user_data(ticker, user_data, user_date, enddate):
    prior_date = get_diff_date(user_date, "prior")
    cp_prior = get_close_prices(ticker, prior_date, user_date)
    
    user_data = ["?", user_data[1], user_data[2], "?", "?"]
    user_data[0] = get_close_prices(ticker, user_date, enddate)
    user_data[3] = calc_percent_gain(float(cp_prior), float(user_data[0]))

    return user_data


# sometimes I need the prior date, sometimes I need the next date
def get_diff_date(user_date, command):
    new_date = user_date.split("-") 
    new_date = dt.date(int(new_date[0]), int(new_date[1]), int(new_date[2]))
    day = new_date.weekday()

    if (command == "prior"):
        if (day == 0):
            new_date -= dt.timedelta(days = 3)   # user_date is almost always mon, so go to last fri
        else:
            new_date -= dt.timedelta(days = 1)   # adding new ticker triggers this
    else:
        if (day < 4):
            new_date += dt.timedelta(days = 1)
        elif (day == 5):
            new_date += dt.timedelta(days = 2)
        else:
            new_date += dt.timedelta(days = 3)  

    return str(new_date.year) + '-' + str(new_date.month) + '-' + str(new_date.day)


# called when user updates tickers data
# if user_date is in master_list, then update master_list. Else, reformat
# user_data so it works with sql then insert at start of master_list
# ex) user_data: [ ticker, % ema, bm ], sql needs to be: [ cp, % ema, bm, % gain, Rating ]
# pm: user_date: 2020-5-6
def compare_masterlist(master_list, trading_days, ticker_list, tablenames, user_data, user_date, plus_btn_clicked_id, table, ticker):    
    next_date = get_diff_date(user_date, "next")   # guarenteed to need cp, so get next days date for yfinance

    if (plus_btn_clicked_id == "update ticker btn"):
        date_pos = trading_days.index(user_date) + 1

        if (user_date in trading_days):
            # add new data to master_list, then write that to sql
            tick_pos = ticker_list.index(ticker)   # tickerlist and masterlist are in same order, masterlist has ticker wrapped in list so I do this

            for i in range(2, 4):
                if (master_list[tick_pos][date_pos][i] != user_data[i - 1] and user_data[i - 1] != "?"):
                    master_list[tick_pos][date_pos][i] = user_data[i - 1]

            # possibly the days rating changed
            master_list[tick_pos][date_pos][-1] = create_rating(master_list[tick_pos][1:date_pos])

            col = sql_handler.updator(int(user_date.split("-")[2]))
            write_data = format_sql_data(table, col, master_list[tick_pos][date_pos][1:], ticker)   # combine data with sql data
            sql_handler.write_to_sql(table, col, write_data, ticker)          # write data to sql

        else:
            # format user_data, write to sql. doesn't go in master_list
            user_data = format_user_data(ticker, user_data, user_date, next_date)

            col = sql_handler.updator(int(user_date.split("-")[2]))
            write_data = format_sql_data(table, col, user_data[1:], ticker)   # combine data with sql data
            sql_handler.write_to_sql(table, col, write_data, ticker)          # write data to sql

    # add new ticker
    else:
        master_list.append([ticker])

        get_api_data(master_list[-1], ticker, trading_days, tablenames)

        date_pos = trading_days.index(user_date) + 1
        master_list[-1][date_pos][2] = user_data[1]   # add % ema from user data
        master_list[-1][date_pos][3] = user_data[2]   # add bm from user data

        col = sql_handler.updator(int(user_date.split("-")[2]))
        write_data = format_sql_data(table, col, ['?', user_data[1], user_data[2], "?", "?"], ticker)   # combine data with sql data
        sql_handler.write_to_sql(table, col, write_data, ticker)          # write data to sql

    return master_list
        

# use custom formula to give each day a buy rating - only if there's enough prior / present info
# pm: data = [ date, cp, % ema, bm, % gain, rating ]
def create_rating(data):
    breakout_handler = [0, []]      # accepts return which is tuple of score and breakout_list
    percent_gain_handler = [0, 0]   # accepts return which is tuple of score and counter
    percent_ema_handler = [0, 0]    # accepts return which is tuple of score and counter
    day = dt.date.today().weekday()

    for i in range(len(data) - 1, 0, -1):
        if (data[i][2] != "?" and percent_ema_handler[1] < 5):
            percent_ema_handler = rating_percent_ema(float(data[i][2]), percent_ema_handler)

        if (data[i][3] != "?" and len(breakout_handler[1]) < 3):
            breakout_handler = rating_breakout_moves(data[i][3], breakout_handler)

        if (data[i][4] != "?" and percent_gain_handler[1] < 5):
            percent_gain_handler = rating_percent_gain(float(data[i][4]), percent_gain_handler)

    # only return rating if there's enough data
    if (len(breakout_handler[1]) < 1 or percent_gain_handler[1] < 5 or percent_ema_handler[1] < 5):
        return "?"
    else:
        return str((breakout_handler[0] + percent_gain_handler[0] + percent_ema_handler[0]) / 3.35)


# updates score with prev % ema's - part of calculating rating
# pm: test_data = that days float % ema
def rating_percent_ema(test_data, handler):
    handler[1] += 1

    if (test_data < 0.0):
        test_data = test_data * -1

    # each "if" is giving score based on what % the test_data is (0 - 10%)
    if (test_data <= 1.0):
        handler[0] += 2.08

    elif (test_data > 1.0 and test_data <= 2.0):
        handler[0] += 2.5
    elif (test_data > 2.0 and test_data <= 3.0):
        handler[0] += 1.25
    elif (test_data > 3.0 and test_data <= 4.0):
        handler[0] += 0.41
    
    return handler 


# updates score with breakout_moves - part of calculating rating
def rating_breakout_moves(test_data, handler):
    if (test_data == "fake"):
        handler[1].append("fake")
        handler[0] += 0.83

    elif (test_data == "small"):
        handler[1].append("small")
        handler[0] += 1.66

    elif (test_data == "big"):
        handler[1].append("big")
        handler[0] += 2.50

    # 3 fakes in a row = 2 pts
    if (len(handler[1]) > 2 and handler[1][-1] == "fake" and handler[1][-2] == "fake" and handler[1][-3] == "fake"):
        handler[0] += 1.00
    # 2 fakes in row = 1 pt
    elif (len(handler[1]) > 1 and handler[1][-1] == "fake" and handler[1][-2] == "fake"):
        handler[0] += 0.50
    # small then fake = 1 pt
    if (len(handler[1]) > 1 and handler[1][-1] == "small" and handler[1][-2] == "fake"):
        handler[0] += 0.50

    return handler


# updates score with prev percent_gain's - part of calculating rating
# pm: test_data = that days float % gain
def rating_percent_gain(test_data, handler):
    handler[1] += 1

    if (test_data < 0):
        test_data = test_data * -1

    # each "if" is giving score based on what % the test_data is (0 - 10%)
    if (test_data <= 1): 
        handler[0]

    elif (test_data > 1.0 and test_data <= 2.0): 
        handler[0] += 0.25
    elif (test_data > 2.0 and test_data <= 3.0): 
        handler[0] += 0.25
    elif (test_data > 3.0 and test_data <= 4.0): 
        handler[0] += 0.75
    elif (test_data > 4.0 and test_data <= 5.0): 
        handler[0] += 0.75
    elif (test_data > 5.0 and test_data <= 6.0): 
        handler[0] += 1.0
    elif (test_data > 6.0 and test_data <= 7.0): 
        handler[0] += 1.25
    elif (test_data > 7.0 and test_data <= 8.0): 
        handler[0] += 1.5
    elif (test_data > 8.0 and test_data <= 9.0):
        handler[0] += 2
    elif (test_data > 9.0 and test_data <= 10.0): 
        handler[0] += 2.25

    else: handler[0] += 2.5

    return handler


def make_plot(ratings_list, plot_dates, plot_tickers, plot_colors):
    # Prepare the data
    x = [1,2,3,4,5,6,7,8,9,10]

    # make the graph
    graph = Graph(ylabel='Ratings', x_ticks_major = 1, y_ticks_minor = 1, y_ticks_major = 1, 
                  y_grid_label=True, x_grid_label=False, padding=5, x_grid=True, y_grid=True, 
                  xmin=0, xmax=10, ymin=0, ymax=10)

    if (len(plot_tickers) > 0):
        i = 0
        while (i < len(plot_tickers)):
            plot = MeshLinePlot(color = plot_colors[i])
            plot.points = [(i, j) for i, j in zip(x, ratings_list[i])]

            graph.add_plot(plot)
            i += 1

    return graph


# return tickers ratings for plot, those are stored as str's in master__list
def plot_get_ratings(master_list, ticker_index):
    new_list = []

    for i in range(0, 10):
        new_list.append(master_list[ticker_index][i + 1][5])

        if (new_list[-1] == "?" or new_list[-1] == "-"):
            new_list[-1] = 0.0

        new_list[-1] = float(new_list[-1])

    return new_list


# will be the x-axis of plot. 10 most recent trading days
def plot_make_dates():
    date_list = []

    date = dt.date.today()        # todays date
    week_index = date.weekday()

    if (week_index == 5):
        date -= dt.timedelta(days = 1)

    # go backward from today (or fri if it's a weekend)
    for i in range(0, 10):
        # change weekends to fri
        if (date.weekday() == 6):
            date -= dt.timedelta(days = 2)

        date_list.insert(0, str(date.month) + "/" + str(date.day))

        date -= dt.timedelta(days = 1)

    return date_list
        

































