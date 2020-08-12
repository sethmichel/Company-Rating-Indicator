# If viewing on github, add sql connection info like username and password 
# to the sql_handler.py file

# sql line 34


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup

import backend
import sql_handler


# all graphics/widgets: grids, btns, labels for all data
class Main_Page(BoxLayout):
    def __init__(self, **kwargs):
        super(Main_Page, self).__init__(**kwargs)      # this is only for if kivy code goes in the py file

        # backend things
        sql_handler.connect_to_db()                                    # create db
        self.tablenames = sql_handler.get_tables()                     # list of all sql tables
        self.trading_days = backend.get_trading_days()                 # list of last/this week's trading days, excludes weekends
        self.btn_list = []                                             # holds all btns but the headers
        self.ticker_list = backend.call_get_tickers(self.tablenames)   # holds all tickers used (so I don't have to call sql over and over)
        self.master_list = backend.get_all_data(self.tablenames, self.ticker_list, self.trading_days)
        self.todays_index = backend.get_todays_index()                 # day of the week
        self.plot_tickers = []                                         # tickers to show on the plot
        self.plot_colors = [[1,0,0,1], [1,1,0,1], [1,0,1,1], [0.5,.75,.9,1], [0,1,0.3,1]]   # red, yellow, purple, light blue, green | line colors for plot
        self.plot_ratings = []                                         # holds ratings for the plot (2d list)
        self.plot_dates = backend.plot_make_dates()                    # x-axis of plot, 10 most recent trading dates

        # ---------------------------------------------------------------------------------

        # UI things
        self.orientation = 'vertical'     # rows not cols
                
        # this can't a method since I want access to stock_grid later and don't want to try navigating through 2 layers of children for it
        scroll = ScrollView(do_scroll_x = False, do_scroll_y = True)              # a scroll view will contain the stock gridlayout
        self.stock_grid = GridLayout(cols = 9, size_hint_y = None)                # holds my stocks
        self.stock_grid.bind(minimum_height = self.stock_grid.setter("height"))   # makes the gridlayout scrollabel via the scrollview
        scroll.add_widget(self.stock_grid)

        self.add_widget(self.create_top_grid())    # 1st of 2 gridlayouts (the upper one)
        self.add_widget(scroll)                    # 2nd of 2 grids (scrollable stock holder)

        # some things used throughout / app start methods
        self.make_header_row(["Rating", "Ticker"])   # make the ehader row
        #self.highlight_today()
        self.update_ui("start of app")


    # called by init()
    # returns the top area of my ui which is a grid layout containing
    # search bar, search btn, add ticker btn, and info btn
    def create_top_grid(self):
        grid = GridLayout(rows = 1, cols = 4, size_hint_y = 0.05)

        search_bar = TextInput(multiline = False, hint_text = "Enter a ticker...", size_hint_x = 0.5)
        search_btn = Button(text = "Search", size_hint_x = 0.2)
        add_data = Button(text = "+", size_hint_x = 0.1, id = "top add btn")
        info_btn = Button(text = "i", size_hint_x = 0.1, id = "info btn")

        add_data.fbind("on_release", self.modalview_menu)
        search_bar.bind(on_text_validate = self.on_search_enter)
        search_btn.bind(on_release = self.on_search_enter)
        info_btn.bind(on_release = self.infobtn_popup)

        # add serach box / btn to parents
        grid.add_widget(search_bar)
        grid.add_widget(search_btn)
        grid.add_widget(add_data)
        grid.add_widget(info_btn)

        return grid


    # user clicked the info btn
    # pm: instance = the info btn from the upper gridlayout
    def infobtn_popup(self, instance):
        popup = Popup(title = "Info", title_align = "center", size_hint = (0.6, 0.6))
        info_text = Label(text = "Only enter data for tickers within the last 10 trading days\nFor each ticker:\n\n1. Enter the distance the close price is from the 300 ema line\n2. Using a 5 day price chart, enter if the stock finished a wave motion. That is, it crossed the 200 ema a while back and it recrossed it on the chosen day. Regardless of above or below the line, enter this as a positive number. You give it a rating based on how big a wave it was\n    ---'fake' means it was a pansey wave and there wasn't a notable overall change\n    ---'small' means it was a small change (this takes longer than a fake)\n    ---'big' means a large price change (which also takes a while)", text_size = (popup.width * 4.5, None))
        popup.content = info_text

        popup.open()


    # create error popup
    # By default, any click outside the popup will close it
    def create_popup(self, error_mes):
        popup = Popup(title = "Invalid Data Entered", title_align = "center",
                      content = Label(text = error_mes), size_hint = (0.5, 0.5))
        popup.open()


    # EVENT: user entered a ticker to search
    # if ticker doenst' exist: do a popup saying so
    # else, move the tickers row to the first in the table / also that to master_list
    # highlight it for 1 second
    def on_search_enter(self, instance):
        ticker = instance.parent.children[2].text
        if (ticker not in self.ticker_list):
            self.create_popup("Rejected: not a current ticker")
            return
 
        # move ticker data from its pos to the front of masterlist - do same for ticker_list
        tick_pos = self.ticker_list.index(ticker)
        self.ticker_list.insert(0, ticker)
        self.master_list.insert(0, self.master_list[tick_pos])
        
        del self.ticker_list[tick_pos + 1]
        del self.master_list[tick_pos + 1]

        self.update_ui("on search enter")


    # EVENT: called from modalview_menu
    # if user types anything, de-select pressed btn's
    def modalview_txtin_selector(self, yest_btn, tod_btn, enter_btn, instance, txt):
        deselected_color = [1, 1, 1, 1]

        if (yest_btn.background_color != deselected_color):
            yest_btn.background_color = deselected_color

        elif (tod_btn.background_color != deselected_color):
             tod_btn.background_color = deselected_color

        # txt can't be "" because it's called on modalview creation so it would enable the enter_btn
        if (enter_btn.disabled == True and txt != ""):
             enter_btn.disabled = False
        
        elif (txt == "" and instance.text == "" and enter_btn.disabled == False):
             enter_btn.disabled = True


    # EVENT: called from kivy.modalview_menu()
    # mark btn as selected, de-selected other btn, un-disable enter_btn, delete txtin text
    # > since can't have 2 dates selected
    def modalview_btn_selector(self, other_btn, txtin, enter_btn, instance):
        selected_color = [0, 255, 255, 0.4]
        deselected_color = [1, 1, 1, 1]

        instance.background_color = selected_color
        if (other_btn.background_color == selected_color):
            other_btn.background_color = deselected_color

        if (txtin.text != ""):
            txtin.text = ""
            
        if (enter_btn.disabled == True):
            enter_btn.disabled = False


    # EVENT: user clicked + btn next to a ticker
    # enter_btn is only possible if user has selected a date
    # modelview is a boxlayout of 3 rows - date selectors, gridlayout w/textinputs, enter btn
    # pm: instance = which ever + btn was clicked
    def modalview_menu(self, instance):
        view = ModalView(size_hint = (0.6, 0.7))
        box = BoxLayout(orientation = "vertical")
        grid = GridLayout(rows = 5, cols = 2)

        # date selectors, I make these as vars because I need them later (easier to read)
        txtin = TextInput(hint_text = "ex) 4-15")
        yest_btn = Button(text = "Yesterday")
        tod_btn = Button(text = "Today")
        backend.kivy_btn_disabler(yest_btn, tod_btn)   # testing, do the btns keep the changes?

        enter_btn = Button(text = "Enter", disabled = True)

        grid.add_widget(Label(text = "Enter Date"))
        grid.add_widget(txtin)
        grid.add_widget(yest_btn)
        grid.add_widget(tod_btn)

        # entering data
        grid.add_widget(Label(text = "Ticker"))
        if (instance.id == "top add btn"):
            grid.add_widget(TextInput(hint_text = "ex) cde"))
        else:
            grid.add_widget(TextInput(disabled = True))
            enter_btn.id = instance.ids["ticker"]   # if user wants to update a ticker's info, this is how I tell what ticker that is since they don't type it in

        grid.add_widget(Label(text = "% From The 400 ema"))
        grid.add_widget(TextInput(hint_text = "ex) 3.4%", multiline = False))
        grid.add_widget(Label(text = "Break Out Moves"))
        grid.add_widget(TextInput(hint_text = "enter fake, small, or big", multiline = False))

        enter_btn.fbind("on_release", self.send_data_sql, yest_btn, tod_btn, txtin, instance.id)
        txtin.fbind("text", self.modalview_txtin_selector, yest_btn, tod_btn, enter_btn)
        yest_btn.fbind("on_release", self.modalview_btn_selector, tod_btn, txtin, enter_btn)
        tod_btn.fbind("on_release",self.modalview_btn_selector, yest_btn, txtin, enter_btn)

        box.add_widget(grid)
        box.add_widget(enter_btn)
        view.add_widget(box)

        view.open()
    
    
    # send the new data to sql
    # check date and data are valid
    # pm: plus_btn_clicked_id = update ticker btn or other, instance = model view enter btn
    def send_data_sql(self, yest_btn, tod_btn, txtin, plus_btn_clicked_id, instance):        
        # tell what method user entered date with
        if (yest_btn.background_color == [0, 255, 255, 0.4]): flag = "Yesterday"
        elif (tod_btn.background_color == [0, 255, 255, 0.4]): flag = "Today"
        else: flag = "txtin"

        # check users date validity
        user_date = backend.check_user_date(txtin, self.trading_days, flag)
        if (user_date.find("Rejected") != -1):   # error checking
            self.create_popup(user_date)
            return

        # check users data validity (curr format = [ ticker, % ema, bm ])
        user_data = backend.check_user_data(yest_btn)   # yest_btn just because its parent is grid (random UI access)
        if (isinstance(user_data, str)):
            self.create_popup(user_data)
            return

        curr_table = backend.make_table_name(user_date, self.tablenames)

        # ticker is saved in user_data if new ticker, otherwise it's in instance.id, this code makes it simpler so I'm only using 1
        if (len(user_data[0]) > 1):
            instance.id = user_data[0]

        # for updating cells instead of adding new ticker, instance has ticker name saved, and I move it here bec my code looks there later
        sql_handler.make_row(curr_table, instance.id, plus_btn_clicked_id, self.ticker_list)

        # update master_list
        if (user_date in self.trading_days):
            self.master_list = backend.compare_masterlist(self.master_list, self.trading_days, self.ticker_list, self.tablenames, user_data, user_date, plus_btn_clicked_id, curr_table, instance.id)

            # update UI
            self.update_ui(plus_btn_clicked_id)



    # -----------------------------------------------------------------------------------------


    # called by make_row(), make_header_row()
    # makes & returns btns
    # pm: words = text to write, turn_on = disabled or not
    # note: background_disabled_normal: disables the background color when the button is disabled - which is always
    # note: background_down = "", normally when user clicks btn, even if disabled, it'll flash a default color, this disables that so it doesn't flash anything
    # note: background_disabled_down = ""
    def make_btn(self, words, turn_on, color, back_dis_norm):
        return Button(text = words, size_hint_y = None, height = Window.size[1] / 10,
                      background_down = "", background_disabled_normal = back_dis_norm, 
                      background_disabled_down = "", background_color = color, 
                      disabled = turn_on)


    # when user enters a new ticker to track, this adds 1 more row populated by the ticker and 5 '?' note boxees
    # pm: plus_btn_clicked_id = if top add btn or update btn were pushed, rating_index = for rating, what index (ticker) of master_list to use
    # ex data) [date, cp, % 400 ema, breakout moves, % gain, rating], [data for next day], [...]
    def make_row(self, ticker, data, plus_btn_clicked_id, rating_index):
        holder = ["Plot", "+"]
        row_start_index = len(self.btn_list)
        todays_date = backend.get_todays_date()   # ex) "8/10"
        marker = "?"

        # first make the rating btn
        self.btn_list.append(self.make_btn("", False, [1,0,0,1], "", ))
        self.btn_list[-1].id = "rating_btn"
        self.btn_list[-1].ids["ticker"] = ticker

        # now make the leading ticker btn
        self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
        self.btn_list[-1].id = "ticker_btn"
        self.btn_list[-1].ids["ticker"] = ticker

        # make btns for the whole week (0 is just the ticker, the data is 1-6)
        for i in range(0, 5):
            if (marker == "-"):
                for j in range(0, len(data[i])):
                    data[i][j] = data[i][j].replace("?", marker)
            
            self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
            
            self.btn_list[-1].ids["ticker"] = ticker
            self.btn_list[-1].ids["date"] = data[i][0] 
            self.btn_list[-1].ids["close_price"] = data[i][1]
            self.btn_list[-1].ids["percent_400_ema"] = data[i][2]
            self.btn_list[-1].ids["breakout_moves"] = data[i][3]
            self.btn_list[-1].ids["percent_gain"] = data[i][4]
            self.btn_list[-1].ids["rating"] = data[i][5]

            # handle curr_btn text
            self.btn_list[-1].text = self.btn_list[-1].ids["rating"] + "\n"
            if (data[i][1] != marker):
                self.btn_list[-1].text += "$"
            self.btn_list[-1].text += (self.btn_list[-1].ids["close_price"] + "\n" + self.btn_list[-1].ids["breakout_moves"])

            # highlight all of todays btns
            if (self.btn_list[-1].ids["date"] == todays_date):
                self.btn_list[-1].background_normal = ""             # disables background image (grey) so the background color isn't tinted grey
                self.btn_list[-1].background_color = [1,1,0.3,0.9]   # yellow
                marker = "-"

        # handle rating_btn and lead ticker_btn
        self.btn_list[row_start_index + 1].ids["close_price"] = data[self.todays_index - 3][1]
        self.btn_list[row_start_index + 1].text = ticker + "\n$" + data[self.todays_index - 3][1]

        self.btn_list[row_start_index].ids["rating"] = data[self.todays_index - 3][5]
        self.btn_list[row_start_index].text = data[self.todays_index - 3][5]

        # insert the plot and add data btns "plot" then "+"
        for j in range(0, 2):
            self.btn_list.append(self.make_btn(holder[j], False, [1,1,1,1], "background_disabled_normal"))
            self.btn_list[-1].ids["ticker"] = ticker

        self.btn_list[-1].id = "update ticker btn"
        self.btn_list[-1].fbind("on_release", self.modalview_menu)
        self.btn_list[-2].id = "plot btn"
        self.btn_list[-2].bind(on_release = self.plot_reset_data)

        # finally, add everything to the gridlayout
        for j in range(len(self.btn_list) - 9, len(self.btn_list)):
            self.stock_grid.add_widget(self.btn_list[j])


    # makes col heading buttons - since they're headers they're only done once
    # goes rating, ticker, then dates which are formated diff, then invisible btns - thus 3 loops
    def make_header_row(self, header_names):
        for name in header_names:
            self.stock_grid.add_widget(self.make_btn(name, True, [1,0,0,1], ""))

        for name in self.trading_days[5:-1]:
            self.stock_grid.add_widget(self.make_btn(name[5:], True, [1,0,0,1], ""))

        # last 3 of header row need to be invisable
        for i in range(0, 2):
            self.stock_grid.add_widget(self.make_btn("", True, [0,0,0,0], ""))


    # called by kivy.make_header_row
    # highlights todays trading day yellow-ish
    def highlight_today(self):
        if (self.todays_index == None):
            return

        self.stock_grid.children[-(self.todays_index)].background_color = [1, 1, 0.5, 0.8]   # yellow
            

    # called at app start and when user enters new info
    # update UI would have to call kivy_code - making circular imports, so I did this
    # calls kivy_code.makerow for each ticker, using master_list as data
    def update_ui(self, plus_btn_clicked_id):
        if (self.ticker_list != []):           # skips everything if the table is empty
            self.delete_data()

            for i in range(0, len(self.ticker_list)):   # make 1 row at a time
                self.make_row(self.master_list[i][0], self.master_list[i][6:], plus_btn_clicked_id, i)


    # called during update_ui() before make_row()
    # needed for redrawing ui after user user changes data
    def delete_data(self):
        for i in range(0, len(self.btn_list)):
            del self.btn_list[0]
            del self.children[0].children[0].children[0]   # self -> scrollview -> gridlayout -> btns


    # plot handling
    # --------------------------------------------------------------------------------


   # EVENT: user clicked plot btn, because I reset the modal view when user adds/del plot
    # > tickers, this is the best way to maintain /reset data. Otherwise I recollect data
    # > each time modal view is reset
    # w/o this: after each plot, these vars are populated with all the data that was on the plot
    # > so next time I'd make a plot, it'd be populated with a bunch of data user doesn't want
    def plot_reset_data(self, instance):
        self.plot_ratings = [backend.plot_get_ratings(self.master_list, self.ticker_list.index(instance.ids["ticker"]))]
        self.plot_tickers = [instance.ids["ticker"]]

        self.plot_create(instance)


    # pm: ticker = ticker clicked, instance is the btn at first, ignore it
    # modalview -> boxlayout 
    # [0]: boxlayout [0]: scrollview -> gridlayout made of labels and btns
    #                [1]: (legend) gridlayout made of labels
    # [1]: boxlayout [0]: plot
    #                [1]: list of labels showing the dates as x-ticks
    def plot_create(self, instance):
        mainview = ModalView(size_hint = (0.75, 0.75))
        box = BoxLayout(orientation = "horizontal", padding = [0,15,15,10])   # left, top, right, bot

        # make a the left side
        leftbox = BoxLayout(orientation = "vertical", size_hint_x = 0.3)

        scroll = ScrollView(do_scroll_x = False, do_scroll_y = True)        # a scroll view will contain the ticker gridlayout
        ticker_grid = GridLayout(rows = len(self.ticker_list), cols = 2, size_hint_y = None)   # holds tickers
        ticker_grid.bind(minimum_height = ticker_grid.setter("height"))                        # makes the gridlayout scrollabel via the scrollview

        # populate the scrollview / gridlayout
        for i in range(0, len(self.ticker_list)):
            ticker_grid.add_widget(Label(text = self.ticker_list[i], size_hint_x = 0.6))
            ticker_grid.add_widget(Button(text = "+", size_hint_x = 0.4))

            # if ticker is shown on plot
            if ((self.ticker_list[i] in self.plot_tickers) and len(self.plot_tickers) > 0):
                ticker_grid.children[0].text = 'X'
                ticker_grid.children[0].background_color = [1,0,0,1]

            # bind event methods to btns
            if (ticker_grid.children[0].text == "+"):
                ticker_grid.children[0].fbind("on_release", self.plot_add_ticker, ticker_grid.children[1].text, mainview)
            else:
                ticker_grid.children[0].fbind("on_release", self.plot_cancel_ticker, ticker_grid.children[1].text, mainview)

        rightbox = BoxLayout(orientation = "vertical")
        rightbotgrid = GridLayout(rows = 1, cols = 13, size_hint_y = 0.05)

        rightbotgrid.add_widget(Label(size_hint_x = 1/13))   # make invisible labels for formatting
        for i in range(1, 10):   # make actual labels
            rightbotgrid.add_widget(Label(text = self.plot_dates[i], size_hint_x = 1/13))

        # combine everything
        scroll.add_widget(ticker_grid)                
        leftbox.add_widget(scroll)
        leftbox.add_widget(self.plot_make_legend())        # the graph doesn't have legend functionality, so make one
        rightbox.add_widget(backend.make_plot(self.plot_ratings, self.plot_dates, self.plot_tickers, self.plot_colors))
        rightbox.add_widget(rightbotgrid)
        rightbox.add_widget(Label(text = "Dates", size_hint_y = 0.05))
        box.add_widget(leftbox)
        box.add_widget(rightbox)
        mainview.add_widget(box)

        mainview.open()
        

    def plot_make_legend(self):
        # containg_box is just the label saying "legend" then the actual legend
        containing_box = BoxLayout(orientation = "vertical", size_hint_y = 0.5, padding = 10)
        containing_box.add_widget(Label(text = "Legend", size_hint = (1, 0.1)))

        # this is the actual legend
        legend_grid = GridLayout(rows = 6, cols = 2)
        legend_grid.add_widget(Label(text = "Ticker"))   # col title
        legend_grid.add_widget(Label(text = "Color"))    # col title
        
        # populated legend_grid
        for i in range(0, len(self.plot_tickers)):
            legend_grid.add_widget(Label(text = self.plot_tickers[i]))
            legend_grid.add_widget(Button(background_color = self.plot_colors[i], disabled = True, background_disabled_normal = ""))

        for i in range(len(legend_grid.children) - 1, 11):
            legend_grid.add_widget(Label())

        containing_box.add_widget(legend_grid)

        return containing_box


    # EVENT: user clicked btn to cancel a ticker from the modalview - so erase it
    # pm: ticker = 'cde', instance = X btn clicked
    def plot_cancel_ticker(self, ticker, mainview, instance):
        spot = self.plot_tickers.index(ticker)
        instance.text = "+"
        instance.background_color = [1, 1, 1, 1]
        
        del self.plot_tickers[spot]
        del self.plot_ratings[spot]

        mainview.dismiss()      # cancel modalview
        self.plot_create(None)   # restart modalview


    # pm: ticker = 'cde', instance = + btn clicked
    def plot_add_ticker(self, ticker, mainview, instance):
        if (len(self.plot_tickers) == 5):
            return

        instance.text = "X"
        instance.background_color = [1,0,0,1]
        
        self.plot_tickers.append(ticker)
        self.plot_ratings.append(backend.plot_get_ratings(self.master_list, self.ticker_list.index(ticker)))

        mainview.dismiss()       # cancel modalview
        self.plot_create(None)   # restart modalview






class myApp(App):
    def build(self):
        return Main_Page()

if __name__ == "__main__":
    myApp().run()





















