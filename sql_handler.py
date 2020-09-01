import mysql.connector 

mydb = mysql.connector.connect(
    auth_plugin = "",
    host = "",
    user = "",
    passwd = ""
)

mycursor = mydb.cursor(buffered = True)

# create db only if one doens't exist
def connect_to_db():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS stockdb")
    mycursor.execute("USE stockdb")


# called periodically when I need to check if a table exists
# create a table if one doesn't exist
def check_table_exists(table, tablenames):
    if (table not in tablenames):
        mycursor.execute("CREATE TABLE " + table + " (Categories VARCHAR(100), First VARCHAR(100), Second VARCHAR(100), Third VARCHAR(100), Forth VARCHAR(100), Fifth VARCHAR(100), Sixth VARCHAR(100), Seventh VARCHAR(100), Eighth VARCHAR(100), Ninth VARCHAR(100), Tenth VARCHAR(100), Eleventh VARCHAR(100), Twelvth VARCHAR(100), Thirteenth VARCHAR(100), Forteenth VARCHAR(100), Fifteenth VARCHAR(100), Sixteenth VARCHAR(100), Seventeenth VARCHAR(100), Eighteenth VARCHAR(100), Nineteenth VARCHAR(100), Twentieth VARCHAR(100), TwentyFirst VARCHAR(100), TwentySecond VARCHAR(100), TwentyThird VARCHAR(100), TwentyFourth VARCHAR(100), TwentyFifth VARCHAR(100), TwentySixth VARCHAR(100), TwentySeventh VARCHAR(100), TwentyEighth VARCHAR(100), TwentyNinth VARCHAR(100), Thirtieth VARCHAR(100), ThirtyFirst VARCHAR(100))")
        tablenames.append(table)


# create ticker row in correct table OR makes tickers user updates carry into next months table
# pm: tablename = single table to write in, ticker_list = all tickers in gui
def make_row(table, ticker, plus_btn_clicked_id, ticker_list):
    if (plus_btn_clicked_id == "top plus btn"):
        ticker_list.append(ticker)

    try:
        mycursor.execute("SELECT First FROM " + table + " WHERE Categories = '" + ticker + "'")   # this is successful every single time
        data = str(mycursor.fetchall())
        if (data != "[]"):
            return
    except:
        pass

    row = "INSERT INTO " + table + " (Categories) VALUES (%s)"
    val = [ticker]
    mycursor.execute(row, val)

    mydb.commit()


# called from kivy_code init()
# returns formated list of all tablenames in db
def get_tables():
    mycursor.execute("SHOW TABLES")
    tables = str(mycursor.fetchall())   # curr list of tuples
    
    tables = tables.strip("[']")
    tables = tables.replace("('", "")
    tables = tables.replace("',)", "")
    tables = tables.replace(" ", "")

    return tables.split(",")


# returns which column I'm using since the col name can't be a varible and I can't do it any other way
def updator(col):
    switch = {1: 'First', 2: 'Second', 3: 'Third', 4: 'Forth', 5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 
        8: 'Eighth', 9: 'Ninth', 10: 'Tenth', 11: 'Eleventh', 12: 'Twelvth', 13: 'Thirteenth', 
        14: 'Forteenth', 15: 'Fifteenth', 16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', 
        19: 'Nineteenth', 20: 'Twentieth', 21: 'TwentyFirst', 22: 'TwentySecond', 23: 'TwentyThird', 
        24: 'TwentyFourth', 25: 'TwentyFifth', 26: 'TwentySixth', 27: 'TwentySeventh', 
        28: 'TwentyEighth', 29: 'TwentyNinth', 30: "Thirtieth", 31: "ThirtyFirst"}

    return switch.get(col)


# updates 1 cell of sql db
# pm: tablename = 1 table to write to, col = "Seventeenth", data = data to write (ex: [ cp, % ema, bm, % gain, Rating ])
def write_to_sql(table, col, data, ticker):    
    sql = "UPDATE " + table + " SET " + col + " = " + data + " WHERE Categories = %s"
    ticker = [ticker]
    mycursor.execute(sql, ticker)

    mydb.commit()


# returns either a single cell of data (called here and there) or list of tickers (called from kivy_code init)
# pm: tablename = single table, col = day, flag = "cell" or "tickers"
def get_data(table, col, ticker, flag):
    # gets a single sql cell
    if (flag == "cell"):
        mycursor.execute("SELECT " + col + " FROM " + table + " WHERE Categories = '" + ticker + "'")
    else:
        mycursor.execute("SELECT Categories FROM " + table)

    data = str(mycursor.fetchall())

    # blank cell is none and the formatting below messes that up
    if (data.find("None") != -1 or data == []):
        return ''

    data = data[3:-3]                   # drop the "[('" and ",)]"
    data = data.replace("'", "")
    data = data.replace(" ", "")

    if (flag == "tickers"):
        data = data.replace(",)", "")    
        data = data.replace("(", "")
        return data.split(",")

    return data

