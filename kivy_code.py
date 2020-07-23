# If viewing on github, add sql connection info like username and password
# to the sql_handling.py file

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
import random

import backend
import sql_handling

# all graphics/widgets: grids, btns, labels for all data
class Main_Page(BoxLayout):
    def __init__(self, **kwargs):
        super(Main_Page, self).__init__(**kwargs)      # this is only for if kivy code goes in the py file

        # backend things
        sql_handling.connect_to_db()                     # sql: create db
        self.tablenames = backend.get_month_year()       # sql: table needs the month and year
        sql_handling.create_tables(self.tablenames)      # sql: create table
        self.trading_days = backend.get_trading_days()   # ui: get dates to display
        self.todays_date = backend.get_todays_date()     # python: today's date to be used here and there
        self.disabler = backend.kivy_btn_disabler()      # ui: used later, user can't add info to non-trading days (used in individual_ticker_add_btn)

        # ---------------------------------------------------------------------------------

        # UI things
        self.orientation = 'vertical'     # rows not cols
        
        # there are 2 gridlayouts, the first doens't move, the 2nd scrolls
        # make gridlayout which is basically the whole boxlayout
        self.upper_search_layout = GridLayout(rows = 1, cols = 3, size_hint_y = 0.05)
        self.search_bar = TextInput(multiline = False, hint_text = "Enter a ticker...", size_hint_x = 0.6)
        self.search_btn = Button(text = "Search", size_hint_x = 0.2)
        self.add_data = Button(text = "+", size_hint_x = 0.1, id = "top_add_btn")
        self.add_data.fbind("on_release", self.individual_ticker_add_btn)
        self.search_bar.bind(on_text_validate = self.on_search_enter)
        self.search_btn.bind(on_release = self.on_search_enter)

        # add serach box / btn to parents
        self.upper_search_layout.add_widget(self.search_bar)
        self.upper_search_layout.add_widget(self.search_btn)
        self.upper_search_layout.add_widget(self.add_data)

        self.add_widget(self.upper_search_layout)

        # make the 2nd, scrollable gridlayout
        self.scroll = ScrollView(do_scroll_x = False, do_scroll_y = True)       # a scroll view will contain the stock gridlayout
        self.stock_grid = GridLayout(cols = 9, size_hint_y = None)              # holds my stocks
        self.stock_grid.bind(minimum_height = self.stock_grid.setter("height")) # makes the gridlayout scrollabel via the scrollview

        # some things used throughout
        self.btn_list = []                                                                # holds all btns but the headers
        self.ticker_list = backend.call_get_tickers(self.tablenames, self.trading_days)   # holds all tickers used (so I don't have to call sql over and over)
        self.header_names = ["Rating", "Ticker"]
        self.header_names.extend(self.trading_days[15:])   # adds more dates to self.header_names

        self.make_header_row(self.header_names)
        
        # add the last things to their parents (gridlayout to scroll view, to main boxlayout)
        self.scroll.add_widget(self.stock_grid)
        self.add_widget(self.scroll)

        # method reads sql and calls make_row
        self.update_ui("start of app")
        self.highlight_today()

        #print("somewhere for a break statement") testing


    # create error popup
    # By default, any click outside the popup will close it
    def create_popup(self, error_mes):
        popup = Popup(title = "Invalid Data Entered", title_align = "center",
                      content = Label(text = error_mes), size_hint = (0.5, 0.5))
        popup.open()


    # EVENT: user entered a ticker to search
    # I need to test if it's valid, if it's in the saved_df, or call backend to find it
    def on_search_enter(self, instance):
        pass


    # EVENT: called from individual_ticker_add_btn
    # if user types anything, de-select pressed btn's
    def modalview_txtin_selector(self, btn1, btn2, enter_btn, instance, txt):
        default_color = [1, 1, 1, 1]

        if (btn1.background_color != default_color) : btn1.background_color = default_color
        elif (btn2.background_color != default_color) : btn2.background_color = default_color

        if (enter_btn.disabled == True and txt != "") : enter_btn.disabled = False  # txt can't be "" because it's called on modalview creation so it would enable the enter_btn
        elif (txt == "" and instance.text == "" and enter_btn.disabled == False) : enter_btn.disabled = True


    # EVENT: called from kivy.individual_ticker_add_btn()
    # CODE: mark btn as selected, de-selected other btn, un-disable enter_btn, delete txtin text
    # > since can't have 2 dates selected
    def modalview_btn_selector(self, other_btn, txtin, enter_btn, instance):
        color = [0, 255, 255, 0.4]
        default_color = [1, 1, 1, 1]

        instance.background_color = color
        if (other_btn.background_color == color) : other_btn.background_color = default_color
        if (txtin.text != "") : txtin.text = ""
        if (enter_btn.disabled == True) : enter_btn.disabled = False


    # EVENT: user clicks "enter" btn in modelview of individual_ticker_add_btn()
    # send the new data to sql
    # check date and data are valid
    # pm: plus_btn_clicked_id = update_ticker_btn or other, instance = model view enter btn
    def send_data_sql(self, btn1, btn2, txtin, plus_btn_clicked_id, instance):        
        # tell what method user entered date with
        if (btn1.background_color == [0, 255, 255, 0.4]): flag = "Yesterday"
        elif (btn2.background_color == [0, 255, 255, 0.4]): flag = "Today"
        else: flag = "txtin"

        # check users date validity
        user_date = backend.check_user_date(btn1, btn2, txtin, self.trading_days, flag)
        if (len(user_date) > 5):   # error checking
            self.create_popup(user_date)
            return

        # check users data validity
        user_data = backend.check_user_data(btn1)   # btn1 just because its parent is grid
        if (isinstance(user_data, str)):
            self.create_popup(user_data)
            return

        # decide which table to use
        curr_table = backend.get_curr_table(self.tablenames, user_date)

        # for updating cells instead of adding new ticker, instance has ticker name saved, and I move it here bec my code looks there later
        if (plus_btn_clicked_id == "update_ticker_btn"):
            btn1.parent.children[6].text = instance.id   # testing, not sure if this is needed
            user_data[0] = instance.id
        else:
            self.ticker_list.append(user_data[0])

        # write to db
        sql_handling.write_to_sql(curr_table, int(user_date.split("/")[1]), user_data, plus_btn_clicked_id)

        # only do this if the chosen date is this week
        self.update_ui(plus_btn_clicked_id)


    # EVENT: user clicked + btn next to a ticker
    # enter_btn is only possible if user has selected a date
    # modelview is a boxlayout of 3 rows - date selectors, gridlayout w/textinputs, enter btn
    # pm: flag 
    def individual_ticker_add_btn(self, instance):
        view = ModalView(size_hint = (0.6, 0.7))
        box = BoxLayout(orientation = "vertical")
        grid = GridLayout(rows = 6, cols = 2)

        # date selectors, I make these as vars because I need them later (easier to read)
        txtin = TextInput(hint_text = "ex) 4/15")
        btn1 = Button(text = "Yesterday", disabled = self.disabler[0])
        btn2 = Button(text = "Today", disabled = self.disabler[1])

        grid.add_widget(Label(text = "Enter Date (last week or this week)"))
        grid.add_widget(txtin)
        grid.add_widget(btn1)
        grid.add_widget(btn2)

        enter_btn = Button(text = "Enter", disabled = True)

        # entering data
        grid.add_widget(Label(text = "Ticker"))
        if (instance.id == "top_add_btn"):
            grid.add_widget(TextInput(hint_text = "ex) cde"))
        else:
            grid.add_widget(TextInput(disabled = True))
            enter_btn.id = instance.ids["ticker"]   # if user wants to update a ticker's info, this is how I tell what ticker that is since they don't type it in

        grid.add_widget(Label(text = "Close Price"))
        grid.add_widget(TextInput(hint_text = "ex) 15.67 or 1.00"))
        grid.add_widget(Label(text = "% From The 400 ema"))
        grid.add_widget(TextInput(hint_text = "ex) 3.4%"))
        grid.add_widget(Label(text = "Break Out Moves"))
        grid.add_widget(TextInput(hint_text = "enter fake, small, or big"))

        enter_btn.fbind("on_release", self.send_data_sql, btn1, btn2, txtin, instance.id)
        txtin.fbind("text", self.modalview_txtin_selector, btn1, btn2, enter_btn)
        btn1.fbind("on_release", self.modalview_btn_selector, btn2, txtin, enter_btn)
        btn2.fbind("on_release",self.modalview_btn_selector, btn1, txtin, enter_btn)

        box.add_widget(grid)
        box.add_widget(enter_btn)
        view.add_widget(box)

        view.open()


    # -----------------------------------------------------------------------------------------


    # called by make_row(), make_header_row()
    # makes & returns btns
    # pm: words = text to write, turn_on = disabled or not
    # note: background_disabled_normal: disables the background color when the button is disabled - which is always
    def make_btn(self, words, turn_on, color, background_dis_norm):
        return Button(text = words, size_hint_y = None, height = Window.size[1] / 10,
                      background_disabled_normal = background_dis_norm, background_color = color, disabled = turn_on)
        

    # when user enters a new ticker to track, this adds 1 more row populated by the ticker and 5 '?' note boxees
    # pm: btn_list = list of all btns in gridlayout, write_text = my 4d list, max_len = the most numb of tickers in the biggest day (needed for for loops), plus_btn_clicked_id = if top add btn or update btn were pushed
    # ex data) [date, cp, % 400 ema, breakout moves, % gain, rating]
    # ex data) [6/15, ?, 15.6, 'fake,fake', 4.3, 7.5]
    def make_row(self, ticker, data, plus_btn_clicked_id):
        holder = ["Plot", "+"]
        row_start_index = len(self.btn_list)

        # first make the rating btn
        self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
        self.btn_list[-1].id = "rating_btn"
        self.btn_list[-1].ids["ticker"] = ticker
        
        # now make the leading ticker btn
        self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
        self.btn_list[-1].id = "ticker_btn"
        self.btn_list[-1].ids["ticker"] = ticker
        self.btn_list[-1].ids["close_price"] = "?"

        for i in range(0, 5):
            # make btns for the whole week
            self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
            self.btn_list[-1].ids["ticker"] = ticker
            self.btn_list[-1].ids["date"] = data[i][0]
            self.btn_list[-1].ids["percent_400_ema"] = data[i][2]
            self.btn_list[-1].ids["breakout_moves"] = data[i][3]

            # handle close price
            self.btn_list[-1].ids["close_price"] = data[i][1]
            if (data[i][1] != "?"):
                self.btn_list[-1].text = "$"
            self.btn_list[-1].text += data[i][1]

            # handle % gain
            if (data[i][4] == "?"):
                self.btn_list[-1].ids["percent_gain"] = backend.find_percent_gain(self.btn_list, self.tablenames, self.trading_days)
            else:
                self.btn_list[-1].ids["percent_gain"] = data[i][4]

            # handle rating
            # only enough data for a rating if user pushed update ticker btn
            if (data[i][5] == "?" and plus_btn_clicked_id == "update_ticker_btn"):
                self.btn_list[-1].ids["rating"] = backend.create_rating(self.btn_list[-1], self.tablenames, data[:i + 1], self.trading_days[10:15], ticker)
            else:
                self.btn_list[-1].ids["rating"] = data[i][5]

            # handle curr_btn text
            self.btn_list[-1].text = self.btn_list[-1].ids["rating"] + "\n" + self.btn_list[-1].ids["close_price"] + "\n" + self.btn_list[-1].ids["breakout_moves"]

        # handle rating_btn and ticker_btn
        self.btn_list[row_start_index + 1].ids["close_price"] = data[self.todays_date][1]
        self.btn_list[row_start_index + 1].text = ticker + "\n" + self.btn_list[self.todays_date].text
        self.btn_list[row_start_index].ids["rating"] = data[self.todays_date][5]
        self.btn_list[row_start_index].text = data[self.todays_date][5]

        # insert the plot and add data btns "plot" then "+"
        for j in range(0, 2):
            self.btn_list.append(self.make_btn(holder[j], False, [1,1,1,1], "background_disabled_normal"))
            self.btn_list[-1].ids["ticker"] = ticker

        self.btn_list[-1].id = "update_ticker_btn"
        self.btn_list[-1].fbind("on_release", self.individual_ticker_add_btn)

        # finally, add everything to the gridlayout
        for j in range(len(self.btn_list) - 9, len(self.btn_list)):
            self.stock_grid.add_widget(self.btn_list[j])


    # called from init()
    # makes col heading buttons - since they're headers they're only done once
    def make_header_row(self, header_names):
        for name in header_names:
            self.stock_grid.add_widget(self.make_btn(name, True, [1,0,0,1], ""))

        # last 3 of header row need to be invisable
        for i in range(0, 2):
            self.stock_grid.add_widget(self.make_btn("", True, [0,0,0,0], ""))

        self.highlight_today()


    # called by kivy.make_header_row
    # highlights todays trading day yellow-ish
    def highlight_today(self):
        # header_names is 9 btns long, ignore last 2
        self.header_names[self.todays_date - 2].background_color


    # called at app start and when user enters new info
    # update UI would have to call kivy_code - making circular imports, so I did this
    # creates 2d list "data" which is the whole weeks info on each ticker, calls make_row for each ticker
    def update_ui(self, plus_btn_clicked_id):
        data = []   # will be a 2D list of each ticker weeks data
        flag = "empty"

        if (self.ticker_list != []):   # skips everything if the table is empty
            self.delete_data()
            for i in range(0, len(self.ticker_list)):
                for j in range(0, 5):
                    data.append(backend.call_get_data(self.tablenames, self.trading_days[j + 15], self.ticker_list[i]))

                    # only call make_row later if there's something in the list
                    if (not (len(data[j]) == 2 and data[j][1] == "None")):
                        flag = "filled"

                # call make_row for that 1 tickers week
                if (flag == "filled"):
                    # change blank sql cells from ['date', ['none']] to ['date', ['?'...'?']]
                    for j in range(0, 5):
                        if (len(data[j]) == 2):
                            del data[j][1]
                            data[j].extend(["?", "?", "?", "?", "?"]) 

                    self.make_row(self.ticker_list[i], data, plus_btn_clicked_id)

                flag = "empty"
                data = []
        
        self.testing()
  
  
    # called during update_ui() before make_row()
    # needed for redrawing ui after user user changes data
    def delete_data(self):
        for i in range(0, len(self.btn_list)):
            del self.btn_list[0]
            del self.children[0].children[0].children[0]   # self -> scrollview -> gridlayout -> btns


    # testing
    def testing(self):
        print("rating:     " + self.btn_list[0].text)
        print("ticker_btn: " + self.btn_list[1].text)
        for i in range(0, 7):
            

        
class myApp(App):
    def build(self):
        return Main_Page()


if __name__ == "__main__":
    myApp().run()





















