import atexit
import time
import flet as ft
import logging
import sys

import components.curtains as curtains
from components.Settings import SettingsMenu
from components.ProcessList import ProcessList, Searchbox
from components.HeadControls import HeadControls
from components.PreviewContainer import ScreenshotContainer
from components.Windowmanager import WindowList, Searchfilterbar, filter
from components.PageTitle import PageTitle

#logging.basicConfig(level=logging.DEBUG)

# CONSTANTS
# WINDOW_WIDTH = 700
ROW_HEIGHT = 68

# COLORS
COLOR_BG = '#111111'
COLOR_SECONDARY = '#1B1B1B'
COLOR_PRIMARY = '#222222'
COLOR_TRANSPARENT = ft.colors.TRANSPARENT

# TODO: hide everything mode: if new pid = hide(pid) [easy]
# TODO: autostart on login: create Task [should be easy] https://github.com/SuperBluestar/python-windows-task-schedule/blob/main/test_schedule.py
# TODO: run as tray icon, not in taskbar: https://github.com/ndonkoHenri/Flet-as-System-Tray-Icon [should be easy]
# TODO: check if hidden = get windows to foreground, take screenshot, check if windowregion is black [easy]
# TODO: windowmanager, autorename windowtitles (rules? e.g. browser titles) #toppings

# TODO: add tooltips (flet is lacking a simple way to do this / need to wrap every control in ft.Tooltoip)
# fixme: find a way to unhide only windows that were visible before. unhiding some apps results in unclickable windows
#       that were never visible, need to tinker with C++ DLL [hard]
# TODO: reduce try/except; catch Exceptions by logging; fix with if conditions

if getattr(sys, 'frozen', False):
    logging.basicConfig(filename=(sys._MEIPASS + 'curtains.log'), encoding='utf-8', level=logging.ERROR)
else:
    logging.basicConfig(filename='curtains.log', level=logging.ERROR)



def log_error(e):
    #print(f'curtains crashed! error: {e}')
    logging.error(e)

if __name__ == "__main__":
    def main(page: ft.Page):
        print(curtains.check_if_autostart())
        curtains.add_to_autostart()
        page.on_error = lambda e: log_error(e)
        page.bgcolor = COLOR_BG
        page.window_center()
        page.window_width = (curtains.return_screensize()[0] / 3) * 1.82
        # page.scroll = ft.ScrollMode.AUTO
        page.window_frameless = False
        page.window_title_bar_hidden = False
        page.window_title_bar_buttons_hidden = False
        page.window_resizable = True
        page.title = "Curtains"

        update_interval = 1 / 65  # frequency should be higher than FPS of screensharing + time needed to hide
        processlist = ProcessList()
        searchbox = Searchbox(processlist)
        processlist_container = ft.Container(
            content=ft.Column(
                controls=[searchbox, processlist],
            ),
            margin=0
        )


        page.theme_mode = ft.ThemeMode.DARK


        screenshot_container = ScreenshotContainer()
        preview_title = PageTitle(
            title=ft.Text(value='Preview'),
            icon=ft.Icon(name=ft.icons.VISIBILITY),
            subtitle=ft.Text('Live preview of your screen. Size and interval between screenshots can be adjusted.\n'),
        )
        preview_page = ft.Column(controls=[preview_title, screenshot_container])


        dummy = ft.Container(width=200,)

        settings_title = PageTitle(
            title=ft.Text(value='Settings'),
            icon=ft.Icon(name=ft.icons.SETTINGS),
            subtitle=ft.Text('Settings menu.')
        )
        settings_menu = SettingsMenu()
        settings_page = ft.Column(controls=[settings_title, settings_menu])

        window_list = WindowList(processlist)
        window_search = Searchfilterbar(window_list)
        window_man_title = PageTitle(
            title=ft.Text(value='Windows'),
            icon=ft.Icon(name=ft.icons.DESKTOP_WINDOWS_SHARP),
            subtitle=ft.Text('List of all windows of each process. Filter by process possible.\n')
        )
        window_man = ft.Container(content=ft.Column(controls=[window_man_title, window_search, window_list], spacing=0))

        content_list = {'preview':preview_page, 'settings':settings_page, 'windows':window_man}
        #content_list = {'settings': dummy, 'preview':preview_page}

        content_col_2 = ft.Container(
            content=ft.Column([preview_page]),
            padding=ft.padding.only(12, 12, 12, 0),
            margin=0,
            width=800,
            height=curtains.return_screensize()[1],
        )
        head = HeadControls(content_col_2, page=page, processlist=processlist, contents=content_list)
        #head.preview_config_btn.on_click = lambda e, p='NONE', h=head, wd=window_list: filter(e,p,h,wd)
        content_col_1 = ft.Container(
            content=ft.Column([head, processlist_container], spacing=0),
            #scroll=ft.ScrollMode.AUTO),
            border=ft.border.only(right=ft.border.BorderSide(0.5,ft.colors.WHITE24)),
            padding=ft.padding.symmetric(0, 12),
            height=curtains.return_screensize()[1],
            width=440,
            margin=0,
        )



        content_row = ft.Row(
            controls=[content_col_1, content_col_2],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
        )
        page.padding = 0
        page.spacing = 0
        page.add(content_row)
        page.window_width = 1100

        window_search.p_col = processlist
        window_search.p_dict = window_search.p_col.p_dict
        head.window_col = window_list
        processlist.head_controls = head
        processlist.window_col = window_list
        processlist.w_search = window_search




        while True:  # main loop
            processlist.update()

            #resizing
            processlist.height = page.window_height - (head.height + searchbox.height) - 70
            window_list.height = page.window_height - (window_man_title.height + window_search.height) - 70
            #processlist.update_processes(head_target=head, window_list=window_list)
            #window_list.update_items()
            #if content_col_2.content.controls[0] == window_man:
                #window_list.build_items()
                #window_list.remove_dead()
            #     #window_search.update_dropdown()
            if content_col_2.content.controls[0] == preview_page:
                screenshot_container.update_preview()

            if content_col_2.content.controls[0] == window_man:
                window_search.update_filter_icons()
                window_search.update_toggle()


            searchbox.update_appcounter()
            #calc_window_height()
            page.update()
            time.sleep(update_interval)


    @atexit.register
    def closing_app():
        pass

    ft.app(target=main, assets_dir="assets", host="127.0.0.1")
