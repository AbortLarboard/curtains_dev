import base64
import ctypes
import os
import pathlib
import sys
import time
from ctypes import wintypes
from functools import wraps
from io import BytesIO

import mss
import mss.windows
import psutil
import win32.lib.win32con as win32con
from win32com.client import Dispatch
import pythoncom
import win32api  # pip package pypiwin32; library is named win32; has to be imported this way
import win32gui  # pip package pypiwin32; library is named win32; has to be imported this way
import win32ui  # pip package pypiwin32; library is named win32; has to be imported this way
from PIL import Image
from pyinjector import inject

mss.windows.CAPTUREBLT = 0  # fixes cursor flickering when screenshot happens

# detect if frozen pyinstaller exe to
if getattr(sys, 'frozen', False):
    BASEDIR = sys._MEIPASS
else:
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    BASEDIR = str((pathlib.Path(BASEDIR)).parent.absolute())

enumWindows = ctypes.windll.user32.EnumWindows
enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
getWindowText = ctypes.windll.user32.GetWindowTextW
getWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW


# isWindowVisible = ctypes.windll.user32.IsWindowVisible

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def all_hwnds():
    """returns a list of window handles for all visible windows."""

    hwnd_list = []

    def foreach_window(hwnd, lParam):
        if ctypes.windll.user32.IsWindowVisible(hwnd) != 0:
            # DWM Cloaked Check
            is_cloaked = ctypes.c_int(0)
            ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(is_cloaked), ctypes.sizeof(is_cloaked))
            if is_cloaked.value == 0:
                hwnd_list.append(hwnd)

        return True

    enumWindows(enumWindowsProc(foreach_window), 0)

    return hwnd_list


def pid_of_hwnd(hwnd: int):
    """returns the name of the executable that belongs to the window"""
    lpdw_process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(lpdw_process_id))
    process_id = lpdw_process_id.value

    return process_id

def curtains_exe_path():
    pid = os.getpid()
    #print(pid)
    p_name = process_name_of_pid(pid)
    exec_path = executable_path(p_name, pid)
    return exec_path

def add_to_autostart() -> None:
    if getattr(sys, 'frozen', False):
        shell = Dispatch('WScript.Shell',pythoncom.CoInitialize())
        path = os.getenv('APPDATA')
        path = path + r'\Microsoft\Windows\Start Menu\Programs\Startup\Curtains.lnk'
        print( path)
        shortcut = shell.CreateShortCut(path)
        print(curtains_exe_path())
        shortcut.Targetpath = curtains_exe_path()
        #shortcut.WorkingDirectory = ''
        shortcut.save()
    else:
        print('need to run as .exe to add curtains to autostart')

def del_autostart() -> None:
    if check_if_autostart():
        path = os.getenv('APPDATA')
        file = path + r'\Microsoft\Windows\Start Menu\Programs\Startup\Curtains.lnk'
        os.remove(file)

def check_if_autostart() -> None:
    path = os.getenv('APPDATA')
    path = path + r'\Microsoft\Windows\Start Menu\Programs\Startup\Curtains.lnk'
    if os.path.isfile(path):
        return(True)
    else:
        return(False)


def process_name_of_pid(pid: int) -> str:
    """returns the name of executable of the process"""
    procname = psutil.Process(pid).name()
    return procname


def executable_path(name: str, pid: int) -> str:
    """returns the path of a process e.g.: explorer.exe, 1432"""
    try:
        if psutil.Process(pid).name() == name:
            return psutil.Process(pid).exe()
            # return psutil.Process.cmdline()[0]
    except Exception as e:
        print(e)
        print(f'ERROR finding process path for PID {pid} \n')


def commandline(pid: int) -> str:
    try:
        return psutil.Process(pid).cmdline()
    except Exception as e:
        print(e)
        return None


def username_of_pid(pid: int) -> str:
    """name of user which runs the process"""
    uname = psutil.Process(pid).username()

    return uname


def extract_icon(exefilename: str, hwnd: int) -> Image:
    """get the first resource icon from exefilename and returns it as bytes array"""
    # fixme: throws errors around the 5000th repetition; not cool but works for this usecase. solution(?):
    #  https://stackoverflow.com/questions/21100028/createcompatibledc-fails-after-calling-it-exactly-4-984-times
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    try:
        large, small = win32gui.ExtractIconEx(exefilename, 0)

    except Exception:
        return None

    if not large:

        return None

    else:
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(hwnd))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), large[0])
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (32, 32), bmpstr, 'raw', 'BGRA', 0, 1)
        win32gui.DestroyIcon(small[0])
        win32gui.DestroyIcon(large[0])

        return img


def image2base64(img: Image) -> str:
    """returns utf-8 decoded base64 string"""
    buffered = BytesIO()
    img = img.convert('RGBA')
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    buffered.truncate()
    return img_str.decode("utf-8")


@timeit
def hide_windows(pid: int) -> None:
    """inject dll into process to hide it"""
    # inject into process
    # 1.Try 64-bit dll
    try:
        inject(pid, (BASEDIR + r"/assets/Hide.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 64\n')
        # print(e)
        pass

    # 2.Try 32-bit dll
    try:
        inject(pid, (BASEDIR + r"/assets/Hide_32bit.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 32\n already hidden\n')
        # print(e)
        pass


@timeit
def unhide_windows(pid: int) -> None:
    """inject dll into process to unhide it"""
    # inject into process
    # 1.Try 64-bit dll
    try:
        inject(pid, (BASEDIR + r"\assets\Unhide.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 64\n already visible\n')
        # print(e)
        pass
    # 2.Try 32-bit dll
    try:
        inject(pid, (BASEDIR + r"\assets\Unhide_32bit.dll"))

    except Exception as e:
        # print(f'{e}\n{pid} 32\n')
        # print(e)
        pass


def minimize_window(hwnd: int):
    """minimizes the window"""
    ctypes.windll.user32.CloseWindow(hwnd)


def window_position(hwnd: int):
    """return: left, top, right, bottom pixel position of a window"""
    rect = wintypes.RECT()
    ff = ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
    # print(rect.left, rect.top, rect.right, rect.bottom)
    return rect.left, rect.top, rect.right, rect.bottom


def window_to_foreground(hwnd: int, e=None):
    """bring window to front"""
    #fixme: more complicated than thought, does not work everytime
    #win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    ctypes.windll.user32.ShowWindow(hwnd, 2)
    ctypes.windll.user32.CloseWindow(hwnd)
    ctypes.windll.user32.BringWindowToTop(hwnd)
    ctypes.windll.user32.SwitchToThisWindow(hwnd, True)



def window_minimize(hwnd: int, e=None):
    ctypes.windll.user32.CloseWindow(hwnd)

def window_close(hwnd: int, e=None):
    #ctypes.windll.user32.DestroyWindow(hwnd)
    ctypes.windll.user32.PostMessageA(hwnd, 0x10, 0, 0)



def window_title(hwnd: int) -> str:
    """returns title of window"""
    text_len_in_characters = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    string_buffer = ctypes.create_unicode_buffer(
        text_len_in_characters + 1)  # +1 for the \0 at the end of the null-terminated string.
    ctypes.windll.user32.GetWindowTextW(hwnd, string_buffer, text_len_in_characters + 1)

    # fixme: ambiguous if an error or title is empty.
    result = string_buffer.value
    # if result == "":
    #     result = '<NO TITLE>'
    return result


def rename_window_title(hwnd: int, title: str = "") -> None:
    """new title for given window"""
    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowtextw
    try:
        ctypes.windll.user32.SetWindowTextW(hwnd, title)

    except Exception as e:
        print(e)
        pass

def check_priviliges(hwnd: int):
    orig_title = window_title(hwnd)
    print(f'orig: {orig_title}')
    dummy_title = ''
    if orig_title == '':
        dummy_title = '#123'
    print(f'dum: {dummy_title}')
    rename_window_title(hwnd, dummy_title)
    print(f'new: {window_title(hwnd)}')
    if window_title(hwnd) == orig_title:
        return True
    if window_title(hwnd) == dummy_title:
        rename_window_title(hwnd, orig_title)
        return False




def return_screensize() -> (int,int):
    """returns the screensize/resolution for all displays"""
    # https://learn.microsoft.com/de-de/windows/win32/api/winuser/nf-winuser-getsystemmetrics?redirectedfrom=MSDN
    ctypes.windll.user32.SetProcessDPIAware()
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    return width, height


# @timeit
def take_screenshot(fraction):
    """returns a screenshot of the whole screen; resized to quarter original size"""
    try:
        with mss.mss() as sct:  # much faster than ImageGrab.grab()); could be even faster if bbox + threading
            # The monitor or screen part to capture
            monitor = sct.monitors[-1]  # or a region
            # Grab the data
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            width, height = img.size
            img.resize((width // fraction, height // fraction))
            return [img, (width, height)]

    except Exception as e:
        print(e)


def is_black(img: Image):
    """returns True if all pixels are black, else False"""
    # take screenshot
    # img = ImageGrab.grab()
    return not img.getbbox()


def getFileProperties(fname):
    # source: https://stackoverflow.com/a/7993095
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
                 'CompanyName', 'LegalCopyright', 'ProductVersion',
                 'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                 'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                                                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                                                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            # print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        pass

    return props

# def isvisible(hwnd): # this does not work. needs to be called via dll injection to make it work
#     # print(ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011))
#     # return ctypes.windll.user32.IsWindowVisible(hWnd)
#     #     ### not working as supposed
#     return bool(ctypes.windll.user32.GetWindowDisplayAffinity(hwnd))


# def getlayered(hwnd): did not need it but could be useful
#     # see https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getlayeredwindowattributes
#     return ctypes.windll.user32.GetLayeredWindowAttributes(hwnd)
