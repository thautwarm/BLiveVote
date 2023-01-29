from __future__ import annotations
import asyncio
import time
import typing
from tkinter import *
from tkinter import ttk
from datetime import datetime

class SettingOption(typing.TypedDict):
    option: str
    start: float

class Action(typing.Protocol):
    def __call__(self):
        ...

def string_to_date(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%d %H:%M')

def date_to_string(d: datetime) -> str:
    return d.strftime('%Y-%m-%d %H:%M')

def is_alive(root: Tk) -> bool:
    try:
        return root.winfo_exists()
    except:
        return False

def check_alive(root: Tk):
    try:
        if not is_alive(root):
            root.destroy()
            return False
    except TclError:
        try:
            root.destroy()
        except TclError:
            pass
        return False
    return True

def create_manager_window(settings: list[SettingOption], get_state):
    # create a window that contains a list of settings
    # we can edit the settings in this window
    root = Tk(baseName="%manager%")
    root.title("投票设置")

    root.attributes('-alpha', 1.0)
    root.configure(background='white')


    label_option = Label(root, text='选项名', font=('Source Han Sans CN', 20), background='white')
    label_option.pack()
    var_option = StringVar(root, value='桃井最中Monaka')
    entry_option = Entry(root, textvariable=var_option, font=('Source Han Sans CN', 20), background='white')
    entry_option.pack()

    label_time_start = Label(root, text='选项计票起始时间', font=('Source Han Sans CN', 20), background='white')
    label_time_start.pack()
    var_time_start = StringVar(root, value=date_to_string(datetime.now()))
    entry_time_start = Entry(root, textvariable=var_time_start, font=('Source Han Sans CN', 20), background='white')
    entry_time_start.pack()

    create_button = Button(root, text='创建选项', font=('Source Han Sans CN', 20), background='white')
    create_button.bind('<Button-1>', lambda e: add_option())
    create_button.pack()

    rm_button = Button(root, text='删除选项', font=('Source Han Sans CN', 20), background='white')
    rm_button.bind('<Button-1>', lambda e: rm_option())
    rm_button.pack()

    # create a list of options
    listbox = Listbox(root, selectmode='single', font=('Source Han Sans CN', 20), background='white')
    listbox.pack(fill='both', expand=True)

    # create a button to add a new option
    def add_option():
        try:
            # Year/month/day/hour/minute
            dt = string_to_date(var_time_start.get())
        except:
            dt = datetime.now()

        v = datetime.timestamp(dt)
        option_name = var_option.get()

        settings.append({'option': option_name, 'start': v})
        listbox.insert(END, f'{option_name} {(dt)}')

    # right click and pop up a menu that support deleting

    def rm_option():
        index = listbox.curselection()
        if index:
            listbox.delete(index)
            settings.pop(index[0])

    def step():
        if check_alive(root):
            root.update()

    def stop():
        if check_alive(root):
            root.destroy()

    root.protocol('WM_DELETE_WINDOW', stop)

    return root, stop, step


def create_indicator_window(get_state: typing.Callable[[], tuple[str,int]]):
    root = Tk(screenName='投票框', baseName='%indicator%')
    # set title to 'title'
    root.title('投票')
    root.config(menu=Menu(root))

    root.configure(background='green')

    # set font size to 40
    root.option_add('*Font', ('Source Han Sans CN', 40))

    # set window size to 600x200
    root.geometry('600x200')

    st = label, value = get_state()

    show_label = ttk.Label(root, text=label, background='green', justify='center')
    show_value = ttk.Label(root, text=value, background='green', justify='center')

    st = get_state()

    def step():
        nonlocal st
        if not check_alive(root):
            return
        new_st = label, value = get_state()
        if new_st == st:
            root.update()
            return
        st = new_st
        show_label.configure(text=label)
        show_value.configure(text=value)
        root.update()

    def stop():
        if check_alive(root):
            root.destroy()

    show_label.pack()
    show_value.pack()

    root.protocol('WM_DELETE_WINDOW', stop)
    return root, stop, step

class UI:
    def __init__(self, settings: list[SettingOption], get_state):
        self.settings = settings
        self.get_state = get_state
        self.root_tk, self.main_stop, self.main_step = create_manager_window(settings, get_state)
        def get_state_last():
            if settings:
                opt =  settings[-1]
                st = get_state()
                label = opt["option"]
                return label, st.get(label, 0)
            return "未知项目", 0
        self.indicator_tk, self.indicator_stop, self.indicator_step = create_indicator_window(get_state_last)
        self.last_check_time = time.time()

    def stop(self):
        self.main_stop()
        self.indicator_stop()

    def step(self):
        now = time.time()
        if now - self.last_check_time > 0.3:
            if self.is_alive():
                self.last_check_time = now
                self.main_step()
                self.indicator_step()
                return True
            else:
                self.stop()
                return False
        else:
            self.main_step()
            self.indicator_step()
            return True

    def is_alive(self):
        return is_alive(self.root_tk)

    def sync_serve(self):
        while self.step():
            pass

    async def async_serve(self):
        while self.step():
            await asyncio.sleep(0)
