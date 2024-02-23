import threading
import flet as ft

from . import curtains
from . import database as db


class Process:
    def __init__(self, pid):
        self.pid: int = pid
        self.icon: str | None = None
        self.hidden: bool | None = None
        self.item = None
        self.col = None

        self.name: str = curtains.process_name_of_pid(pid)
        self.path: str = curtains.executable_path(self.name, self.pid)
        self.cmd: str = curtains.commandline(pid)
        self.user: str = ''
        try:
            self.user = curtains.username_of_pid(self.pid)
        except Exception as e:
            print(f'cannot get username of process. pid:{self.pid}, Exception:{e}')
        # Fixme: psutil error on some,eg:psutil.AccessDenied: (pid=1204)
        self.properties: dict = curtains.getFileProperties(self.path)
        self.display_name: str
        #print(type(self.properties['StringFileInfo']),'Look here')
        #from pprint import pprint
        #pprint(self.properties['StringFileInfo'])
        #print("======================")
        try:
            if self.properties['StringFileInfo'].get('ProductName'):
                product_name = self.properties['StringFileInfo']['ProductName']
                if product_name == 'Microsoft® Windows® Operating System':
                    if self.properties['StringFileInfo'].get('InternalName'):
                        self.display_name = self.properties['StringFileInfo']['InternalName']
                else:
                    self.display_name = product_name
            else:
                self.display_name = self.name
        except AttributeError:
            import psutil
            ps_process = psutil.Process(pid)
            self.display_name = ps_process.name()
        self.delete_w_titles = False
        self.windows: dict = dict()
        self.update_windows()
        self.higher_priv = curtains.check_priviliges(list(self.windows)[0])
        print(self.higher_priv)
        self.db_entry = db.get_row(self.path)
        if self.db_entry:
            self.icon = self.db_entry[2]
            self.hidden = bool(self.db_entry[1])

        else:
            if self.windows:
                print(self.display_name)
                win = list(self.windows.values())[0]

                img_icon = curtains.extract_icon(self.path, win.hwnd)

                if hasattr(img_icon, 'convert'):
                    self.icon = curtains.image2base64(img_icon)
            self.hidden = False
            db.add_row(self.path, self.hidden, self.icon)

    def __setattr__(self, key, value):
        super(Process, self).__setattr__(key, value)
        if key == 'hidden' and value is not None:
            db.update_hidden(self.path, value)
            self.hide_windows(value)

    def __eq__(self, val):
        if val == self.pid:
            return True

    def hide_windows(self, value):
        
        if value is True:
            h_thread = threading.Thread(target=curtains.hide_windows, args=(self.pid,))
            h_thread.start()
        elif value is False:
            uh_thread = threading.Thread(target=curtains.unhide_windows, args=(self.pid,))
            uh_thread.start()
        db.update_hidden(self.path, value)

    def update_windows(self, w_col=None):
        hwnd_set = set(curtains.all_hwnds())
        for hwnd in hwnd_set:
            if curtains.pid_of_hwnd(hwnd) == self.pid and hwnd not in self.windows: #find new windows
                win = Window(hwnd=hwnd, process=self)
                self.windows[hwnd] = (win)
                if self.hidden:
                    self.hide_windows(True)
                if w_col:
                    print('done')
                    w_col.build_item(win)
            elif curtains.pid_of_hwnd(hwnd) == self.pid and hwnd in self.windows: # already known windows
                if self.delete_w_titles:
                    self.delete_all_windowtitles()
                if self.windows[hwnd].item:
                    self.windows[hwnd].update_position()
                    self.windows[hwnd].update_title()
                    self.item.update_wcount()
                    self.windows[hwnd].item.update_window()

                elif w_col:
                    w_col.build_item(self.windows[hwnd])
        for hwnd in self.windows.copy():
            if hwnd not in hwnd_set: # detect dead windows
                if self.windows[hwnd].item in w_col.controls:
                    w_col.controls.remove(self.windows[hwnd].item)
                del self.windows[hwnd]

    def delete_all_windowtitles(self):
        for hwnd in self.windows:
            if self.windows[hwnd].title != '':
                curtains.rename_window_title(hwnd=hwnd, title='')
            #w = self.windows[hwnd]



class ProcessDict(dict):
    def __getattr__(self, pid):
        if pid in self:
            return self[pid]
        else:
            raise AttributeError("PID not found: " + pid)

    def __setattr__(self, pid, value):
        self[pid] = value

    def __delattr__(self, pid):
        if pid in self:
            del self[pid]
        else:
            raise AttributeError("PID not found: " + pid)

    def update(self):
        pid_set, hwnd_set = self.build_sets()
        self.add_new_processes(pid_set, hwnd_set)
        self.remove_dead(pid_set, hwnd_set)

    def build_sets(self):
        pid_set = set()
        hwnd_set = set(curtains.all_hwnds())
        ignore_pids = [0, 4]  # 0=system idle, 4=kernel
        # build a set of alive PIDs
        for hwnd in hwnd_set:
            found_pid = curtains.pid_of_hwnd(hwnd)
            if found_pid not in ignore_pids:
                pid_set.add(found_pid)
        return pid_set, hwnd_set

    def add_new_processes(
            self,
            pid_set,
            p_col: ft.Column = None,
            w_col: ft.Column = None,
    ):
        # add new processes
        for pid in pid_set:
            if pid not in self: # if new pid: create new Process object
                if p_col:
                    p = Process(pid)
                    p.update_windows(w_col=w_col)
                    p_col.build_item(p)
                else:
                    p = Process(pid)
                self[pid] = p

            else:
                self[pid].update_windows(w_col)# if process already exists update windows

    def remove_dead(
            self,
            pid_set,
            p_col: ft.Column = None,
            w_col: ft.Column = None,
    ):
        ignore_pids = [0, 4]
        # remove dead processes
        for process_pid in self.copy():
            if process_pid not in pid_set and process_pid not in ignore_pids:

                if p_col:
                    for hwnd in self[process_pid].windows:
                        if w_col:
                            w_col.controls.remove(self[process_pid].windows[hwnd].item)
                    self[process_pid].item.death_animation()
                    p_col.controls.remove(self[process_pid].item)

                del self[process_pid]
                continue

class Window:
    def __init__(self, hwnd: int, process: Process):
        self.hwnd = hwnd
        self.process = process
        self.title: str | None = None
        self.update_title()
        self.pid: int = process.pid
        self.left: int
        self.top: int
        self.right: int
        self.bottom: int
        self.title: str
        self.left, self.top, self.right, self.bot = curtains.window_position(self.hwnd)
        self.item = None

    def __eq__(self, val):
        if val == self.hwnd:
            return True

    def update_title(self):
        try:
            self.title = curtains.window_title(self.hwnd)
        except Exception:
            raise Exception

    def update_position(self):
        self.left, self.top, self.right, self.bot = curtains.window_position(self.hwnd)
