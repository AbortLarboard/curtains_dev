import threading

from . import curtains
from . import database as db


class Process:
    def __init__(self, pid, hwnd_set: set = None):
        self.pid: int = pid
        self.hidden: bool | None = None
        self.windows: WindowList = WindowList()
        if hwnd_set:
            self.update_windows(hwnd_set)
        self.name: str = curtains.process_name_of_pid(pid)
        self.path: str = curtains.executable_path(self.name, self.pid)
        self.cmd: str = curtains.commandline(pid)
        self.icon: str | None = None
        self.user: str = ''   # = curtains.username_of_pid(self.pid)
        try:
            self.user = curtains.username_of_pid(self.pid)
        except Exception as e:
            print(f'cannot get username of process. pid:{self.pid}, Exception:{e}')
        # Fixme: psutil error on some,eg:psutil.AccessDenied: (pid=1204)

        self.db_entry = db.get_row(self.path)
        if self.db_entry:
            self.icon = self.db_entry[2]
            self.hidden = bool(self.db_entry[1])

        else:
            if self.windows:
                img_icon = curtains.extract_icon(self.path, self.windows[0].hwnd)
                if hasattr(img_icon, 'convert'):
                    self.icon = curtains.image2base64(img_icon)
            self.hidden = False
            db.add_row(self.path, self.hidden, self.icon)

        self.properties: dict = curtains.getFileProperties(self.path)
        self.display_name: str

        if self.properties['StringFileInfo'].get('ProductName'):
            product_name = self.properties['StringFileInfo']['ProductName']
            if product_name == 'Microsoft® Windows® Operating System':
                if self.properties['StringFileInfo'].get('InternalName'):
                    self.display_name = self.properties['StringFileInfo']['InternalName']
            else:
                self.display_name = product_name
        else:
            self.display_name = self.name

    def __setattr__(self, key, value):
        super(Process, self).__setattr__(key, value)
        if key == 'hidden' and value is not None:
            db.update_hidden(self.path, value)
            self.hide_windows(value)

    def __eq__(self, val):
        if val == self.pid:
            return True

    def hide_windows(self, value):
        match value:
            case True:
                h_thread = threading.Thread(target=curtains.hide_windows, args=(self.pid,))
                h_thread.start()
            case False:
                uh_thread = threading.Thread(target=curtains.unhide_windows, args=(self.pid,))
                uh_thread.start()
        db.update_hidden(self.path, value)

    def update_windows(self, hwnd_set):
        for hwnd in hwnd_set:
            if curtains.pid_of_hwnd(hwnd) == self.pid and hwnd not in self.windows:
                win = Window(hwnd=hwnd, process=self)
                self.windows.append(win)
            elif curtains.pid_of_hwnd(hwnd) == self.pid and hwnd in self.windows:
                index = self.windows.index(hwnd)
                self.windows[index].update_position()
                self.windows[index].update_title()
        for window in self.windows:
            if window.hwnd not in hwnd_set:
                self.windows.remove(window)

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
        pid_set = set()
        hwnd_set = set(curtains.all_hwnds())
        ignore_pids = [0, 4]  # 0=system idle, 4=kernel
        # build a set of alive PIDs
        for hwnd in hwnd_set:
            found_pid = curtains.pid_of_hwnd(hwnd)
            if found_pid not in ignore_pids:
                pid_set.add(found_pid)

                # add new processes
        for pid in pid_set:
            if pid not in self: # if new pid: create new Process object
                p = Process(pid, hwnd_set)
                p.windows = WindowDict()
                self[pid] = p
            else: # if process already exists add new windows
                for hwnd in hwnd_set:
                    if curtains.pid_of_hwnd(hwnd) == pid and hwnd not in self[pid].windows:
                        self[pid].windows[hwnd] = Window(hwnd, self[pid])

            # remove dead processes
        for process_pid in self.copy():
            if process_pid not in pid_set:
                self.pop(process_pid)
                continue
            # remove dead windows
            else:
                for window in self[process_pid].windows:
                    if window.hwnd not in hwnd_set:
                        self[process_pid].windows.pop(window.hwnd)
                    else:
                        window.update_title()
                        window.update_position()

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

    def __eq__(self, val):
        if val == self.hwnd:
            return True

    def update_title(self):
        try:
            self.title = curtains.window_title(self.hwnd)
        except Exception:
            print(Exception)

    def update_position(self):
        self.left, self.top, self.right, self.bot = curtains.window_position(self.hwnd)


class WindowList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append(self, item):
        super().append(item)
        if item.process.hidden:
            item.process.hide_windows(item.process.hidden)

class WindowDict(dict):
    def __getattr__(self, hwnd):
        if hwnd in self:
            return self[hwnd]
        else:
            raise AttributeError("hWnd not found: " + hwnd)

    def __setattr__(self, hwnd, value):
        self[hwnd] = value

    def __delattr__(self, hwnd):
        if hwnd in self:
            del self[hwnd]
        else:
            raise AttributeError("hWnd not found: " + hwnd)

