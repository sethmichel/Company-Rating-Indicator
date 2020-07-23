import mysql.connector


mydb = mysql.connector.connect(
        auth_plugin='',
        host = "",
        user = "",
        passwd = "",
    )

mycursor = mydb.cursor(buffered = True)


# create db only if one doens't exist
def connect_to_db():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS stockdb")
    mycursor.execute("USE stockdb")


# create a table if one doesn't exist
def create_tables(tablenames):
    for table in tablenames:
        try:
            # test if the table exists
            mycursor.execute("SELECT First FROM " + table + " WHERE Categories = 'Ticker'")

        except:
            # if not then create table
            mycursor.execute("CREATE TABLE " + table + " (Categories VARCHAR(100), First VARCHAR(100), Second VARCHAR(100), Third VARCHAR(100), Forth VARCHAR(100), Fifth VARCHAR(100), Sixth VARCHAR(100), Seventh VARCHAR(100), Eighth VARCHAR(100), Ninth VARCHAR(100), Tenth VARCHAR(100), Eleventh VARCHAR(100), Twelvth VARCHAR(100), Thirteenth VARCHAR(100), Forteenth VARCHAR(100), Fifteenth VARCHAR(100), Sixteenth VARCHAR(100), Seventeenth VARCHAR(100), Eighteenth VARCHAR(100), Nineteenth VARCHAR(100), Twentieth VARCHAR(100), TwentyFirst VARCHAR(100), TwentySecond VARCHAR(100), TwentyThird VARCHAR(100), TwentyFourth VARCHAR(100), TwentyFifth VARCHAR(100), TwentySixth VARCHAR(100), TwentySeventh VARCHAR(100), TwentyEighth VARCHAR(100), TwentyNinth VARCHAR(100), Thirtieth VARCHAR(100), ThirtyFirst VARCHAR(100))")


# returns which column I'm using since the col name can't be a varible and I can't do it any other way
def updator(col):
    switch = {1: 'First', 2: 'Second', 3: 'Third', 4: 'Forth', 5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 
        8: 'Eighth', 9: 'Ninth', 10: 'Tenth', 11: 'Eleventh', 12: 'Twelvth', 13: 'Thirteenth', 
        14: 'Forteenth', 15: 'Fifteenth', 16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', 
        19: 'Nineteenth', 20: 'Twentieth', 21: 'TwentyFirst', 22: 'TwentySecond', 23: 'TwentyThird', 
        24: 'TwentyFourth', 25: 'TwentyFifth', 26: 'TwentySixth', 27: 'TwentySeventh', 
        28: 'TwentyEighth', 29: 'TwentyNinth', 30: "Thirtieth", 31: "ThirtyFirst"}

    return switch.get(col)


# create ticker row in correct table
# pm: tablename = single table to write in
def create_row(tablename, ticker):
    # check row doesn't already exist
    if (ticker[0] not in get_data(tablename, "Categories", ticker)):
        row = "INSERT INTO " + tablename + " (Categories) VALUES (%s)"
        val = [ticker]
        mycursor.execute(row, val)

        mydb.commit()


# updates sql db
# pm: tablename = 1 table to write to, col = str day, data = data to write, plus_btn_clicked_id = "top_add_btn" or other
# data ex) [ticker, cp, % 400 ema, breakout_moves]
def write_to_sql(tablename, col, data, plus_btn_clicked_id):
    import backend

    # create the new row if needed
    if (plus_btn_clicked_id == "top_add_btn"):
        create_row(tablename, data[0])

    column = updator(col)
    
    # get sql formatted data
    write_data = backend.format_sql_data(tablename, column, data)
    sql = "UPDATE " + tablename + " SET " + column + " = " + write_data + " WHERE Categories = %s"
    ticker = [data[0]]
    mycursor.execute(sql, ticker)

    mydb.commit()


# returns either a single cell of data or the whole col
# pm: tablename = single table, col = day, row = ???
def get_data(tablename, col, ticker):
    # returns a single sql cell
    mycursor.execute("SELECT " + col + " FROM " + tablename + " WHERE Categories = '" + ticker + "'")

    data = str(mycursor.fetchall())
    if (data == "[(None,)]" or data == ['']):
        return "None"   # blank cell is none and the formatting below messes that up
    data = data[3:-3]                    # drop the "[('" and ",)]"
    data = data.replace("'", "")         # drop all '
    data = data.replace(" ", "")         # drop all spaces
    return data


# called by kivy code.update_ui
# gets list of all tickers in curr table
# pm: tablename is 1 table
def get_tickers(tablename):
    mycursor.execute("SELECT Categories FROM " + tablename)
    data = str(mycursor.fetchall())

    if (data == "[(None,)]" or data == ['']):
        return []   # blank cell is none and the formatting below messes that up
    data = data[3:-3]               # drop the "[('" and ",)]"
    data = data.replace("'", "")    # drop all '
    data = data.replace(" ", "")    # drop all spaces
    data = data.replace(",)", "")    
    data = data.replace("(", "")

    return data.split(",")






# testing
def emergency_correct_1_cell():
    connect_to_db()
    # ex data) [ [ cp, % 400 ema, breakout moves, % gain, rating ] ]
    sql = "UPDATE july2020 SET Seventeenth = %s WHERE Categories = 'cde'"
    data = ['13.20*3.5*fake*?*?']
    mycursor.execute(sql, data)

    sql = "UPDATE july2020 SET Sixteenth = %s WHERE Categories = 'cde'"
    data = ['13.59*2.6*?*?*?']
    mycursor.execute(sql, data)

    sql = "UPDATE july2020 SET Fifteenth = %s WHERE Categories = 'cde'"
    data = ['14.50*3.5*small*?*?']
    mycursor.execute(sql, data)

    sql = "UPDATE july2020 SET forteenth = %s WHERE Categories = 'cde'"
    data = ['15.70*4.5*?*?*?']
    mycursor.execute(sql, data)

    sql = "UPDATE july2020 SET Thirteenth = %s WHERE Categories = 'cde'"
    data = ['15.43*1.5*?*?*?']
    mycursor.execute(sql, data)


    mydb.commit()
    print("pause")

    #write_to_sql("July2020", "10", ['cde', '15.6', '3.2', None], "top_add_btn")
    #sql_to_UI("june2020")
    #update_db("june2020", 2, [("Ticker","aal"), ("Close_Price","22.30"), ("Percent_From_400_ema","1.2"), ("Breakout_Moves","small,big,small")], "aal")
    #update_db("june2020", 2, [("Ticker","cde"), ("Close_Price","4.15"), ("Percent_From_400_ema","3.5"),("Breakout_Moves","fake","small")], "cde")
    #update_db("june2020", 2, [("Breakout_Moves","fake","small")], "cde")

#emergency_correct_1_cell()