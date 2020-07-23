   
# ex data) [date, Rating, cp, percent gain, % from 400 ema, breakout_moves]
# ex data) [6/15, blank, 15.6, 5.6, 4.3, 'fake,fake']
 def make_row(self, ticker, data):
        for i in range(0, 5):
            # make btns for the whole week
            self.btn_list.append(self.make_btn("", False, [1,0,0,1], ""))
            self.btn_list[-1].ids["ticker"] = ticker
            self.btn_list[-1].ids["date"] = data[i][0]

            # blank sql cells return none for ['date', ['none']]
            if (len(data[i]) == 1):
                data[i][1] = "blank"
                for j range(2, 5):
                    data[i].append("blank")

                self.btn_list[-1].ids["percent_gain"] = data[i][3] + "%"
                self.btn_list[-1].ids["percent_400_ema"] = data[i][4] + "%"
            
                # handle all rating matters with the row
                if (data[i][1] == "blank"):
                    self.btn_list[-1].ids["rating"] = "missing"
                else:
                    self.btn_list[-1].ids["rating"] = data[i][1]
                    self.btn_list[-1].text = data[i][1]
                    self.btn_list[row_start_index].ids["rating"] = data[i][1]

                # handle all close price matters with the row
                if (data[i][2] == "blank"):
                    self.btn_list[-1].ids["close_price"] = "missing"
                else:
                    self.btn_list[-1].ids["close_price"] = "$" + data[i][2]
                    self.btn_list[-1].text += data[i][2]
                    self.btn_list[row_start_index + 1].ids["close_price"] = "$" + data[i][2]

                # handle all breakout moves matters with the row
                if (data[i][5] == "blank"):
                    self.btn_list[-1].ids["breakout_moves"] = "missing"
                else:
                    self.btn_list[-1].ids["breakout_moves"] = data[i][5]

                # breakout moves may be too long - cut it / add to ui
                    if (len(data[i][4]) > 12):
                        self.btn_list[-1].text += data[i][4][:12] + "..."
                    else:
                        self.btn_list[-1].text += data[i][4]


        

# test passing in btn is a deep copy
def add_if_there(data, btn, key):
    try:
        # add things
        btn.ids[key] = data[i][1] + "%"
    except:
        # move on
        pass




        # insert the plot and add data btns "plot" then "+"
        for j in range(0, 2):
            self.btn_list.append(self.make_btn(holder[j], False, [1,1,1,1], "background_disabled_normal"))
            self.btn_list[-1].ids["ticker"] = ticker

        self.btn_list[-1].id = "update_ticker_btn"
        self.btn_list[-1].fbind("on_release", self.individual_ticker_add_btn)

        # finally, add everything to the gridlayout
        for i in range(0, len(self.btn_list)):
            self.stock_grid.add_widget(self.btn_list[i])
 
 
 
                #add_if_there(data, self.btn_list[-1], "percent_gain", i, 3)





