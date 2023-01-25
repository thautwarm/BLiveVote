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

def create_manager_window(settings: list[SettingOption], subwindows: list[tuple[Action, Action]], get_state):
    # create a window that contains a list of settings
    # we can edit the settings in this window
    root = Tk(baseName="%manager%")
    root.title("投票设置")

    root.attributes('-alpha', 1.0)
    root.configure(background='white')


    label_option = Label(root, text='选项名', font=('Helvetica', 20), background='white')
    label_option.pack()
    var_option = StringVar(root, value='桃井最中Monaka')
    entry_option = Entry(root, textvariable=var_option, font=('Helvetica', 20), background='white')
    entry_option.pack()

    label_time_start = Label(root, text='选项计票起始时间', font=('Helvetica', 20), background='white')
    label_time_start.pack()
    var_time_start = StringVar(root, value=date_to_string(datetime.now()))
    entry_time_start = Entry(root, textvariable=var_time_start, font=('Helvetica', 20), background='white')
    entry_time_start.pack()

    create_button = Button(root, text='创建选项', font=('Helvetica', 20), background='white')
    create_button.bind('<Button-1>', lambda e: add_option())
    create_button.pack()

    rm_button = Button(root, text='删除选项', font=('Helvetica', 20), background='white')
    rm_button.bind('<Button-1>', lambda e: rm_option())
    rm_button.pack()

    # create a list of options
    listbox = Listbox(root, selectmode='single', font=('Helvetica', 20), background='white')
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
        subroot, substop, substep = create_indicator_window(option_name, get_state)
        subwindows.append((substop, substep))

        def delete_subwindow():
            index = subwindows.index((substop, substep))
            subwindows.pop(index)
            listbox.delete(index)
            substop()

        subroot.protocol('WM_DELETE_WINDOW', delete_subwindow)
        listbox.insert(END, f'{option_name} {(dt)}')

    # right click and pop up a menu that support deleting

    def rm_option():
        index = listbox.curselection()
        if index:
            listbox.delete(index)
            settings.pop(index[0])
            stop, step = subwindows.pop(index[0])
            stop()

    def step():
        # check if alive and update

        try:
            if not is_alive(root):
                root.destroy()
                return
        except TclError:
            try:
                root.destroy()
            except TclError:
                pass
            return

        for stop, step in subwindows:
            step()
        root.update()

    def stop():
        for stop, step in subwindows:
            stop()
        try:
            root.destroy()
        except TclError:
            pass

    root.protocol('WM_DELETE_WINDOW', stop)

    return root, stop, step


def create_indicator_window(title: str, get_state: typing.Callable[[], dict[str,int]]):
    root = Tk(screenName=title, baseName=title)
    # set title to 'title'
    root.title(title)
    root.config(menu=Menu(root))

    root.attributes('-alpha', 0.9)
    root.attributes('-transparentcolor', 'white')

    # size is fixed to 256x128
    root.geometry('256x128')
    root.configure(background='white')
    text = ttk.Label(root, text=get_state().get(title, 0), font=('Helvetica', 100), background='white')

    st = get_state()

    def step():
        nonlocal st
        try:
            if not is_alive(root):
                root.destroy()
                return
        except TclError:
            try:
                root.destroy()
            except TclError:
                pass
            return
        new_st = get_state().get(title, 0)
        if new_st == st:
            root.update()
            return
        st = new_st
        text.configure(text=st)
        root.update()

    def stop():
        try:
            root.destroy()
        except TclError:
            pass

    text.pack()

    return root, stop, step

class UI:
    def __init__(self, settings: list[SettingOption], subwindows: list[tuple[Action, Action]], get_state):
        self.settings = settings
        self.subwindows = subwindows
        self.get_state = get_state
        self.root_tk, self.main_stop, self.main_step = create_manager_window(settings, subwindows, get_state)
        self.last_check_time = time.time()

    def stop(self):
        self.main_stop()

    def step(self):
        now = time.time()
        if now - self.last_check_time > 0.3:
            if self.is_alive():
                self.last_check_time = now
                self.main_step()
                return True
            else:
                self.stop()
                return False
        else:
            self.main_step()
            return True

    def is_alive(self):
        return is_alive(self.root_tk)

    def sync_serve(self):
        while self.step():
            pass

    async def async_serve(self):
        while self.step():
            await asyncio.sleep(0)
