import mysql.connector
import datetime

thing = [1,2,23,3]
thing.insert(-1, 7)
print(thing)
print("pause")


def updator(col, table):
    switch = {1: 'First', 2: 'Second', 3: 'Third', 4: 'Forth', 5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 
        8: 'Eighth', 9: 'Ninth', 10: 'Tenth', 11: 'Eleventh', 12: 'Twelvth', 13: 'Thirteenth', 
        14: 'Forteenth', 15: 'Fifteenth', 16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', 
        19: 'Nineteenth', 20: 'Twentieth', 21: 'TwentyFirst', 22: 'TwentySecond', 23: 'TwentyThird', 
        24: 'TwentyFourth', 25: 'TwentyFifth', 26: 'TwentySixth', 27: 'TwentySeventh', 
        28: 'TwentyEighth', 29: 'TwentyNinth', 30: "Thirtieth", 31: "ThirtyFirst"}

    # "UPDATE testmay2020 SET First = %s WHERE Categories = %s"
    return "UPDATE " + table + " SET " + switch.get(col) + " = %s WHERE Categories = %s"

# called from kivy init
# uses datetime to get the weeks range excluding weekends
def tester():
    list2 = []   # will be 15 dates covering 3 weeks of weekdays

    curr_day = datetime.date.today() - datetime.timedelta(7)   # go to last week

    print(curr_day.strftime("%B"))

    for i in range(0, 15):
        # moves to monday if today is sat or sun
        if (curr_day.weekday() > 4):
            curr_day += (datetime.timedelta(1) * (7 - curr_day.weekday()))   
        
        list2.append(str(curr_day.month) + "/" + str(curr_day.day))
        curr_day += datetime.timedelta(1)


    return list2


tester()


mydb = mysql.connector.connect(
    auth_plugin='mysql_native_password',
    host = "127.0.0.1",
    user = "root",
    passwd = "PhMrlyion97!",
)

mycursor = mydb.cursor()

#mycursor.execute("CREATE DATABASE IF NOT EXISTS stockdb")
mycursor.execute("USE stockdb")

mycursor.execute("CREATE TABLE IF NOT EXISTS 5/2020 (Categories VARCHAR(20), First VARCHAR(20), Second VARCHAR(20), Third VARCHAR(20), Forth VARCHAR(20), Fifth VARCHAR(20), Sixth VARCHAR(20), Seventh VARCHAR(20), Eighth VARCHAR(20), Ninth VARCHAR(20), Tenth VARCHAR(20), Eleventh VARCHAR(20), Twelvth VARCHAR(20), Thirteenth VARCHAR(20), Forteenth VARCHAR(20), Fifteenth VARCHAR(20), Sixteenth VARCHAR(20), Seventeenth VARCHAR(20), Eighteenth VARCHAR(20), Nineteenth VARCHAR(20), Twentieth VARCHAR(20), TwentyFirst VARCHAR(20), TwentySecond VARCHAR(20), TwentyThird VARCHAR(20), TwentyFourth VARCHAR(20), TwentyFifth VARCHAR(20), TwentySixth VARCHAR(20), TwentySeventh VARCHAR(20), TwentyEighth VARCHAR(20), TwentyNinth VARCHAR(20), Thirtieth VARCHAR(20), ThirtyFirst VARCHAR(20))")  # make a table
tablename = "testmay2020"
sql = "INSERT INTO " + tablename + " (Categories) VALUES (%s)"
val = [["Ticker"], ["Rating"], ["Close_Price"], ["Percent_Gain"], ["Percent_From_400_ema"], ["Breakout_Moves"]]
for i in range(0, 6):
    mycursor.execute(sql, val[i])
mydb.commit()

#mycursor.execute('''
#                 INSERT INTO testmay2020 (Categories)
#                 VALUES ("Ticker"), ("Rating"), ("Close_Price"), ("Percent_Gain"), ("Percent_From_400_ema"), ("Breakout_Moves")                 
#                 ''')

# call a switch function to get the right column, insert the table, data, and row
col = 1
data = "77"
row = "Ticker"

sql = updator(col, "testmay2020")
val = (data, row)
mycursor.execute(sql, val)
mydb.commit()





#list2 = tester()
#print(list2)












