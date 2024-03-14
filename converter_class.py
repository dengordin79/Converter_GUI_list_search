from tkinter import *
import datetime, os, sys, requests, json
from tkinter import filedialog
from tkinter import ttk
import pathlib



class Converter(Tk):
    API_KEY='3e623231f9cd13d498430eb138163340'
    SERVICE_URL=f'http://api.exchangeratesapi.io/v1/latest?access_key={API_KEY}'
    PROJECT_ROOT_PATH=os.path.dirname(__file__)
    SAVED_RATES_FOLDER=os.path.join(PROJECT_ROOT_PATH,'rates_files')
    CSV_FILE=os.path.join(PROJECT_ROOT_PATH,'exchange_record_log.csv')
    RATES_FILES_FILTER=(('rates files','*.json'),('log file','*.csv'))
    LOG_FILES_FOLDER=os.path.join(PROJECT_ROOT_PATH,'log_files')
    LOG_FILE_PATH=os.path.join(LOG_FILES_FOLDER,'conversion_history.csv')
    LOG_FILE_HEADERS=('Date_time','Ammount to convert','Currency code (from)','Currency code (to)','Result')
    CURR_SELECTOR=(('Source currency',"S"),('Turget currency',"T"))
    def __init__(self):
        super().__init__()
        self.grid_columnconfigure(0,weight=0)
        self.grid_columnconfigure(1,weight=1)
        self.grid_columnconfigure(2,weight=2)
        self.controls_frame=Frame()
        self.result_frame=Frame()
        self.info_frame=Frame()
        self.currency_frame=Frame()
        self.controls_frame.grid(column=0,row=0,rowspan=2)
        self.result_frame.grid(column=1,row=0)
        self.info_frame.grid(column=1,row=1)
        self.currency_frame.grid(column=2,row=0)
        self.currency_frame.grid_columnconfigure(0,weight=1)
        self.currency_frame.grid_columnconfigure(1,weight=0)
        self.currency_frame.grid_rowconfigure(0,weight=0)
        self.currency_frame.grid_rowconfigure(1,weight=1)
        self.rates={}
        #control frame
        Button(self.controls_frame,text='Get rates online',command=self.get_rates_online).pack()
        Button(self.controls_frame,text='Get rates from file',command=self.get_rates_offline).pack()
        Button(self.controls_frame,text='Convert',command=self.convert).pack()        
        Button(self.controls_frame,text='Display operation',command=self.get_history).pack()
        #result frame
        self.currency_switch=StringVar()
        self.currency_switch.set(self.CURR_SELECTOR[0][0])
        for curr in self.CURR_SELECTOR:
            Radiobutton(self.result_frame,
                text=curr[0],
                value=curr[1],
                variable=self.currency_switch,
                command=self.curr_selected).grid()
        #Label(self.result_frame,text='Currency to:',anchor=W).grid(column=0,row=1,sticky=(W,E))
        Label(self.result_frame,text='Amount:',anchor=W).grid(column=0,row=2,sticky=(W,E))
        Label(self.result_frame,text='Converted:',anchor=W).grid(column=0,row=3,sticky=(W,E))
       #result labels    
        self.currency_from_label=Label(self.result_frame,text='Select from list->')
        self.currency_from_label.grid(column=1,row=0)
        self.curr_to_label=Label(self.result_frame,text='Select from list->')
        self.curr_to_label.grid(column=1,row=1)
        self.amount=Entry(self.result_frame)
        self.amount.grid(column=1,row=2)
        self.result_label=Label(self.result_frame)
        self.result_label.grid(column=1,row=3)
        #info frame
        self.get_rates_label=Label(self.info_frame,text='Please, get rates!',anchor=N,fg='red')
        self.get_rates_label.grid(row=2)
        Label(self.info_frame,text='Last conversation:',anchor=N).grid(row=0)
        self.convert_history_label=Label(self.info_frame)
        self.convert_history_label.grid(row=1,sticky=(S,W,E,N))
        #currency frame
        self.all_currencies=self.read_curr_frome_file()
        self.filter_entry=Entry(self.currency_frame)
        self.filter_entry.bind('<KeyRelease>',self.filter_set)
        self.filter_entry.grid(column=0,row=0,sticky=(W,E))
        self.curr_list_variable=Variable(value=self.all_currencies)
        curr_scroll=Scrollbar(self.currency_frame)
        curr_scroll.grid(column=1,row=1,sticky=(N,S))
        self.curr_listbox=Listbox(self.currency_frame,
            listvariable=self.curr_list_variable,
            yscrollcommand=curr_scroll.set
        )
        self.curr_listbox.bind('<<ListboxSelect>>',self.print_listbox_selection)
        curr_scroll.config(command=self.curr_listbox.yview)
        self.curr_listbox.grid(column=0,row=1,sticky=(N,S,W,E))

        Button(self.currency_frame,text='Forget list',command=lambda: self.curr_listbox.grid_forget()).grid()
        Button(self.currency_frame,text='Restore list',command=lambda: self.curr_listbox.grid(column=0,row=1,sticky=(N,S,W,E))).grid()
        self.populate_list(self.all_currencies)
        
        self.mainloop()
        
    def get_rates_online(self):
        response=requests.get(self.SERVICE_URL)
        rates_dict=response.json()
        code=response.status_code
        print(f'HTTP response code: {code}')
        date=rates_dict.get('date')
        time_stamp=rates_dict.get('timestamp')
        file_name=f'rates_{date.replace("-","_")}__{time_stamp}.json'
        with open(os.path.join(self.SAVED_RATES_FOLDER,file_name),'w') as f:
            json.dump(rates_dict, f, indent=4)
            pass
        self.rates=rates_dict
        self.get_rates_label.config(text=f'Rates online {self.rates.get("date")}',fg='green')
        pass
    def get_rates_offline(self):
        rate_file=filedialog.askopenfile(
            initialdir=self.SAVED_RATES_FOLDER,
            filetypes=self.RATES_FILES_FILTER)
        self.rates=json.load(rate_file)
        self.get_rates_label.config(text=f'Rates offline {self.rates.get("date")}',fg='green')
        pass
    def convert(self):
        if len(self.rates)==0:
            print("No rates data found!!!")
            return
        currency_from=self.currency_from_label.cget("text")
        currency_to=self.curr_to_label.cget("text")
        ammount_to_convert=self.amount.get()
        ammount_to_convert=float(ammount_to_convert)
        rate_from=self.rates['rates'][currency_from]
        rate_to=self.rates['rates'][currency_to]
        res=(rate_to/rate_from)*ammount_to_convert
        self.history_string=f'{datetime.datetime.now()}\tConverting {ammount_to_convert} {currency_from} to {currency_to}, result: {res:.2f} {currency_to}'
        headers='datetime, ammount to convert, currency from, currency to, result\n'
        record_of_convert=f'{datetime.datetime.now()},{ammount_to_convert}, {currency_from},{currency_to}, {res:.2f}'
        print(self.CSV_FILE)
        with open(self.CSV_FILE,'w') as f:
            f.write(headers)
            f.write(record_of_convert)
            pass
        self.result_label.config(text=f'{res:.2f}{currency_to}')   
        conversion_data=datetime.datetime.now().strftime("%m/%d/%Y__%H:%M:%S"),str(ammount_to_convert),str(currency_from),str(currency_to),str(res)
        self._update_log_file(conversion_data)
        pass
    def _update_log_file(self,current_conversion):
        if os.path.exists(self.LOG_FILE_PATH):
            with open(self.LOG_FILE_PATH) as f: headers_from_file=f.readline()
            if headers_from_file !=",".join(self.LOG_FILE_HEADERS)+'\n':
                with open(self.LOG_FILE_PATH,'w') as f: f.write(",".join(self.LOG_FILE_HEADERS)+'\n')
                pass
            pass
        else:
            with open(self.LOG_FILE_PATH,'w') as f: f.write(",".join(self.LOG_FILE_HEADERS)+'\n')
            pass
        pass
        with open(self.LOG_FILE_PATH,'a') as f: f.write(",".join(current_conversion)+'\n')
        pass
    def get_history(self):
        self.convert_history_label.config(text=self.history_string)
        
        pass
    def get_conversion_history(self):
        TABLE_ROW_FORMAT='\u007c{:20} \u007c{:20} \u007c{:20} \u007c{:20} \u007c{:20} \u007c\n'
        result_string=''
        result_string+=106*'\u2015'+'\n'
        with open(self.LOG_FILE_PATH) as f:
            file_data=f.readlines()
            pass
        result_string+=TABLE_ROW_FORMAT.format(*(file_data[0].strip().split(',')))
        result_string+=106*'\u2015'+'\n'
        for i in range(1,len(file_data)):
            result_string+=TABLE_ROW_FORMAT.format(*(file_data[i].strip().split(',')))
        result_string+=106*'\u2015'
        print(result_string)
        self.convert_history_label.config(text=result_string)
        pass
    def print_listbox_selection(self,e):
        
        if self.currency_switch.get()=='S':
            selection_from=self.curr_listbox.selection_get().strip().split(',')
            self.currency_from_label.config(text=selection_from[2])
            print(f'Currency from = {selection_from[2]}')
        else:
            selection_to=self.curr_listbox.selection_get().strip().split(',')
            self.curr_to_label.config(text=selection_to[2])
            print(f'Currency to = {selection_to[2]}')
        pass
    def populate_list(self,codes:list):self.curr_list_variable.set(codes)
    def filter_set(self,e):
        print(f'Current filter ={self.filter_entry.get()}')
        #STEP 1 : get current filter
        curr_filter_value=self.filter_entry.get().upper()
        #STEP 2 : Create filtered list
        # filtered_list=[
        #     next_curr for next_curr in all_currencies if next_curr.count(curr_filter_value)>0
        # ]
        filtered_list=[]
        for next_curr in self.all_currencies:
            if next_curr.count(curr_filter_value)>0:
                filtered_list.append(next_curr) 
        #STEP 3 : Redraw listbox
        self.populate_list(filtered_list)
    #read all curr codes
    def read_curr_frome_file(self):
        with open(pathlib.Path(__file__).parent.joinpath('codes-all_csv.csv'),encoding='utf-8') as f:
            from_file=f.readlines()[1:]
            all_currencies=[
                line.replace('"','').strip() for line in from_file
            ]
        return all_currencies
    def curr_selected(self):
        print(self.currency_switch.get())
        pass
        
if __name__ == '__main__':
    converter=Converter() 