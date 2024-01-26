import math
import os
import time
from functools import wraps

from .ContentContainer import ContentContainer
from .Process import *


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


class ProcessList(ft.Column):
    def __init__(self):
        super().__init__()
        self.height = 40
        self.p_dict: ProcessDict = ProcessDict()
        self.controls = ItemList(self)
        self.all_hidden = False
        self.spacing = 8
        self.padding = 0
        self.width = 400
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        self.w_search = None
        self.window_col = None

    # @timeit
    def update(self):
        pid_set, hwnd_set = self.p_dict.build_sets()
        self.p_dict.add_new_processes(pid_set, p_col=self, w_col=self.window_col)
        self.p_dict.remove_dead(pid_set, p_col=self, w_col=self.window_col)

    def build_item(self, process):
        if self.all_hidden:
            process.hidden = True
        item = ProcessItem(width=400, max_height=40, title_action=3, process=process)
        if not self.check_user(process) or process.higher_priv:
            item.actions.controls.insert(0, ft.Icon(
                name=ft.icons.ERROR_OUTLINE_OUTLINED,
                color=ft.colors.AMBER,
                scale=0.7,
                tooltip='missing priviliges. curtains might not work on this process.'
            ))
        item.Column = self
        if self.head_controls and self.window_col:
            item.windows_btn.on_click = (lambda e, p=process, h=self.head_controls, wd=self.window_col:
                                         self.show_windows(e, p, h, wd))
        self.controls.append(item)

        process.item = item

    def check_user(self, process):
        current_user = os.getlogin()
        proc_user = process.user[-(len(current_user)):]
        if not process.user or current_user == proc_user:
            return True
        else:
            return False

    def show_windows(self, e, p, h, wd):
        h.switch_content(e, 'windows')

        if self.w_search:
            self.w_search.filter_icon_action(window_col=wd, pid=p.pid)


class ItemList(list):
    def __init__(self, processlist: ProcessList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processlist = processlist

    def append(self, item):
        super().append(item)
        # self.processlist.item_dict[item.process.pid] = item
        self.processlist.height = self.processlist.height + 44


class ProcessItem(ContentContainer):
    def __init__(self, width, max_height, title_action, process: Process):
        super().__init__(title=process.display_name, icon=None, width=width, max_height=max_height,
                         title_action=title_action)
        self.process = process
        process.item = process
        self.windows_btn = ft.IconButton(
            icon=ft.icons.DESKTOP_WINDOWS_SHARP,
            selected_icon=ft.icons.LOCK,
            selected=False,
            icon_color=ft.colors.WHITE54,
            scale=0.7,
            tooltip='show windows'
        )
        if self.process.icon:
            ficon = ft.Image(src_base64=self.process.icon,
                             width=20,
                             height=20,
                             fit=ft.ImageFit.CONTAIN, )
        else:
            ficon = ft.CircleAvatar(
                content=ft.Text(
                    value=self.process.display_name[0:1].title(),
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                radius=10,
                bgcolor=ft.colors.INVERSE_PRIMARY)
        self.window_counter = ft.Container(
            content=ft.Text(
                value=len(self.process.windows),
                style=ft.TextThemeStyle.LABEL_SMALL,
                color=ft.colors.WHITE54
            ),
            bgcolor=ft.colors.WHITE12,
            width=32,
            height=24,
            border_radius=10,
            alignment=ft.alignment.center
        )
        self.icon_container.content = ficon
        self.actions.controls.extend([self.windows_btn, self.window_counter])
        self.action_container.visible = True
        self.border = None
        # self.border_radius = 0
        self.padding = 0
        self.margin = 0
        self.height = 40
        self.title_container.width = 170
        self.title.overflow=ft.TextOverflow.FADE
        self.title_container.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        #self.title_container.bgcolor = ft.colors.AMBER
        self.animate_opacity = 1000
        self.switch.value = process.hidden
        self.switch.tooltip = 'hide windows'
        self.switch.on_change = lambda e: self.toggle_hidden(e)
        if process.hidden:
            self.toggle_hidden(True)

    def toggle_hidden(self, e):

        if type(e) == ft.control_event.ControlEvent:  # check if in construction or page loaded
            e = e.control.value

        if type(e) == bool:

            if e:
                if not self.process.hidden:
                    self.process.hidden = True
                self.title.color = ft.colors.WHITE24

            if not e:
                if self.process.hidden:
                    self.process.hidden = False
                self.title.color = ft.colors.WHITE

    def death_animation(self):
        self.disabled = True
        self.process.pid = 0
        self.title.italic = True
        self.update()
        self.opacity = 0
        self.update()
        time.sleep(1)

    def update_wcount(self):
        self.window_counter.content.value = len(self.process.windows)

    def update_window_btn(self, head, target):
        self.windows_btn.on_click = lambda e, t=target, p=self.process.pid: filter


def search_proc(e, target: ft.Column):
    def keyword_search(i):
        print(e.control.value)
        p_name = i.title_container.content.value.lower()
        if p_name.startswith(e.data.lower()):
            result = "0" + p_name
            i.bgcolor = ft.colors.WHITE24
        else:
            result = p_name
            i.bgcolor = '#1B1B1B'
        return result

    target.controls.sort(key=keyword_search)
    if e.data == '':
        for item in target.controls:
            item.bgcolor = '#1B1B1B'
    target.update()


class Searchbox(ft.Container):
    def __init__(self, target: list):
        super().__init__()
        self.target = target
        self.width = 400
        self.height = 32
        self.bgcolor = ft.colors.WHITE12
        self.margin = 0
        self.border_radius = ft.border_radius.all(8)

        self.padding = ft.padding.only(left=8, right=8)
        self.textfield = ft.Container(
            content=ft.TextField(
                height=28,
                # width=100,
                expand=True,
                hint_text="search",
                cursor_color=ft.colors.WHITE54,
                focused_bgcolor=ft.colors.WHITE12,
                border=ft.InputBorder.NONE,
                filled=False,
                multiline=False,
                text_size=12,
                cursor_radius=-2,
                # prefix_icon=ft.icons.SEARCH,
                on_change=lambda e, t=target: search_proc(e, t),
                text_align=ft.TextAlign.LEFT
            ),
            padding=ft.padding.only(bottom=-2),
            height=32,
            width=240,
            # bgcolor=ft.colors.AMBER,
            alignment=ft.alignment.bottom_left)
        self.appcounter = ft.Text(
            value=f'{len(target.controls)} APPS',
            text_align=ft.TextAlign.END,
            width=50,
            size=12,
            color=ft.colors.WHITE54,
        )
        self.sort_btn = ft.IconButton(
            icon=ft.icons.EXPAND_MORE,
            icon_color=ft.colors.WHITE54,
            on_click=lambda e, t=target: self.sort_procs(e, t),
            animate_rotation=125,
            rotate=0,
        )
        self.prefix_icon = ft.Container(content=ft.Icon(name=ft.icons.SEARCH, color=ft.colors.WHITE54), width=20)
        self.content = ft.Row(
            controls=[self.prefix_icon, self.textfield, self.sort_btn, self.appcounter],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def update_appcounter(self):
        self.appcounter.value = f'{len(self.target.controls)} APPS'
        self.appcounter.update()

    def sort_procs(self, e, target: ft.Column):
        def name(i):
            print(e.control.content.value)
            p_name = i.title_container.content.value.lower()
            return p_name

        if self.sort_btn.rotate == 0:
            order = True
            self.sort_btn.rotate = math.pi
        else:
            order = False
            self.sort_btn.rotate = 0

        target.controls.sort(key=name, reverse=order)
        target.update()
