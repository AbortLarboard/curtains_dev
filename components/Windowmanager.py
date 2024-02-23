import flet as ft
from .ContentContainer import ContentContainer
from . import curtains

class WindowList(ft.Column):
    def __init__(self, process_col):
        super().__init__()
        self.spacing = 8
        self.padding = 0
        self.width = 620
        self.height = 500
        self.expand = False
        self.scroll = ft.ScrollMode.ALWAYS
        self.p_dict = process_col.p_dict
        self.filter_value = None


    def build_item(self, window):
        item = WindowItem(window=window)
        item.icon_container.on_click = lambda e, t=self, p=window.process.pid: filter(t, p)
        if self.filter_value and window.process != self.filter_value:
            item.visible = False
        self.controls.append(item)
        window.item = item

class WindowItem(ContentContainer):
    def __init__(self, window):
        title = ft.Text(value=window.title)
        super().__init__(title=title, icon=None, width=600, max_height=160, title_action=2)
        self.window = window
        self.process = window.process
        if self.process.icon:
            ficon = ft.Image(src_base64=window.process.icon,
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
        self.icon_container.content = ficon
        self.title_container.width = 360

        self.tofront_btn = ft.IconButton(
            icon=ft.icons.FLIP_TO_FRONT,
            icon_size=11,
            on_click=lambda e, h=self.window.hwnd:curtains.window_to_foreground(h, e=e),
            icon_color=ft.colors.WHITE54,
        )
        self.minimize_btn = ft.IconButton(
            icon=ft.icons.REMOVE,
            icon_size=11,
            on_click=lambda e, h=self.window.hwnd:curtains.window_minimize(h, e=e),
            icon_color=ft.colors.WHITE54,
        )
        self.close_btn = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_size=11,
            on_click=lambda e, h=self.window.hwnd:curtains.window_close(h, e=e),
            icon_color=ft.colors.WHITE54,
        )
        self.window_actions = ft.Container(
            content=ft.Row(
                controls=[self.minimize_btn, self.close_btn],
                spacing=0,
                #alignment=ft.MainAxisAlignment.START
                ),
            bgcolor=ft.colors.WHITE10,
            border_radius=10,
            alignment=ft.alignment.center,
        )
        #self.action_info.content.value = f'hWnd: {self.window.hwnd}'
        #self.action_info.content.italic = True
        self.action_info.content = self.window_actions
        self.action_info.width = len(self.window_actions.content.controls) * 40
        self.action_info.height = 28
        self.action_info.alignment = ft.alignment.center

        self.border = None
        self.padding = 0
        self.margin = 0
        self.height = 42
        self.title.size=13

        self.info_hwnd = ft.Row(
            controls=[
                ft.Text(value='hWnd:',color=ft.colors.WHITE54, size=11),
                ft.Text(value=self.window.hwnd, size=11, selectable=True),
            ]
        )

        self.info_position = ft.Row(
            controls=[
                ft.Text(value='left,top:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=f'({self.window.left},{self.window.top})',
                        size=11, selectable=True, width=100),
                ft.Text(value='right,bottom:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=f'({self.window.right},{self.window.bot})',size=11, selectable=True, width=100),
                ft.Text(value='size:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=f'({self.window.right - self.window.left},{self.window.bot - self.window.top})',
                        size=11, selectable=True, width=100)
            ]
        )

        self.content_col.controls = [self.info_hwnd,  self.info_position,]

    def update_window(self):
        # title
        self.window.update_title()
        self.title_container.content.value = self.window.title

        if self.body.visible:
            self.window.update_position()
            self.info_position.controls[1].value = f'({self.window.left},{self.window.top})'
            self.info_position.controls[3].value = f'({self.window.right},{self.window.bot})'
            self.info_position.controls[5].value = f'({self.window.right - self.window.left},{self.window.bot - self.window.top})'


def filter(target: ft.Column, e=None, pid=None,):
    if pid:
        e = pid
    elif type(e) == ft.control_event.ControlEvent:
        e = (e.data)
    if e != 'NONE':
        try:
            proc = target.p_dict[int(e)]
            target.filter_value = proc
            for i in target.controls:
                if i.process == proc:
                    i.visible = True
                else:
                    i.visible = False
                    i.expanded = True
                    i.toggle_content()
                    #i.clps_btn_container.content.rotate = 0
                    #i.body.visible = False
                    #i.height = i.min_height


        except Exception:
            print(Exception)

    if e == 'NONE':
        for i in target.controls:
            i.visible = True
            target.filter_value = None


class Searchfilterbar(ft.Container):
    def __init__(self, windowlist:WindowList):
        super().__init__()
        self.width=600
        self.height=38
        #self.border = ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE12))
        #self.padding = ft.padding.only(bottom=8)
        #self.bgcolor=ft.colors.WHITE10
        self.w_list = windowlist
        self.menu_dict = {}
        self.filtered_on = False
        self.p_col = None
        self.p_dict = None
        self.shown_pid = None

        self.filter_off_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.FILTER_ALT_OFF,
                icon_color=ft.colors.WHITE54,
                icon_size=18,
                on_click=lambda e, p='NONE', w=self.w_list: self.filter_icon_action(e=e, pid=p, window_col=w),
                tooltip='turn process filter off',
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            border_radius=ft.border_radius.only(topLeft=8, topRight=8),
        width = 38,
            height = 48,
        )

        self.row_0 = ft.Container(ft.Row(
                controls=[
                    ft.Container(content=self.filter_off_btn, alignment=ft.alignment.bottom_left, width=38,height=38, padding=0),
                    ], spacing=0.4),
            height=30,
            padding=0,
            margin=0,
           # bgcolor=ft.colors.AMBER
                )
        self.row_1 = ft.Container()
        self.content_col = ft.Column(
            controls=[self.row_0, self.row_1, ],
            alignment=ft.MainAxisAlignment.START,
            spacing=0,
            )

        self.content = self.content_col

    def update_filter_icons(self, e=None):
        if self.p_dict:
            for pid in self.p_dict:
                p = self.p_dict[pid]
                if pid not in self.menu_dict.copy():
                    if p.icon:
                        icon_con = p.icon
                        icon = ft.Container(ft.Image(src_base64=icon_con,
                                     width=10,
                                     height=10,
                                                     scale=0.5,
                                     fit=ft.ImageFit.SCALE_DOWN,
                                            ),
                            width=28,
                            height=48,
                            bgcolor=ft.colors.WHITE12,
                            on_click=lambda e, p=p.pid, w=self.w_list: self.filter_icon_action(e=e,pid=p, window_col=w),
                            border_radius=ft.border_radius.only(topLeft=8, topRight=8)
                        )
                    else:
                        icon = ft.Container(ft.CircleAvatar(
                            content=ft.Text(
                                value=p.display_name[0:1].title(),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                                    ),
                            scale=0.6,
                            bgcolor=ft.colors.INVERSE_PRIMARY),
                        width=28,
                        height=48,
                        bgcolor = ft.colors.WHITE12,
                        border_radius=ft.border_radius.only(topLeft=8, topRight=8),
                        on_click=lambda e, p=p.pid, w=self.w_list: self.filter_icon_action(e=e, pid=p,
                                                                                               window_col=w),

                        )
                    self.menu_dict[pid] = icon
                    self.row_0.content.controls.append(self.menu_dict[pid])
            for i in self.menu_dict.copy():
                #item = self.menu_dict[i]
                if i not in self.p_dict:
                    self.row_0.content.controls.remove(self.menu_dict[i])
                    del self.menu_dict[i]


    def filter_icon_action(self,pid, e=None ,window_col=None):
        if pid != 'NONE':
            self.shown_pid = pid
            self.height = 190
            self.row_0.content.controls[0].border = None
            self.process_infos(pid)
            for i in self.menu_dict:
                icon = self.menu_dict[i]
                if icon == self.menu_dict[pid]:
                    icon.border = ft.border.only(bottom=ft.border.BorderSide(4, ft.colors.INVERSE_PRIMARY))
                else:
                    icon.border = None
        else:
            self.shown_pid = None
            self.row_1.content = None
            self.height = 38
            for i in self.menu_dict:
                self.menu_dict[i].border = None
            self.row_0.content.controls[0].border = ft.border.only(bottom=ft.border.BorderSide(4, ft.colors.INVERSE_PRIMARY))

        filter(target=window_col,pid=pid)


    def process_infos(self, pid):
        p = self.p_dict[pid]
        if p.icon:
            icon = ft.Container(ft.Image(src_base64=p.icon,
                                     width=40,
                                     height=40,
                                     scale=1,
                                     fit=ft.ImageFit.SCALE_DOWN,
                                            ))
        else:
            icon = ft.Container(ft.CircleAvatar(
                            content=ft.Text(
                            value=p.display_name[0:1].title(),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.WHITE,
                                ),
                            radius=18,
                            bgcolor=ft.colors.INVERSE_PRIMARY),
                            border_radius=8,
                        )

        title = ft.Text(
            value=p.display_name,
            style=ft.TextThemeStyle.TITLE_SMALL,
            weight=ft.FontWeight.BOLD
        )

        path = ft.Row(
            controls=[
                ft.Text(value='path:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=p.path, size=11, selectable=True, overflow=ft.TextOverflow.FADE, width=500,
                        max_lines=1, tooltip=p.path)
            ]
        )

        cmd = ft.Row(
            controls=[
                ft.Text(value='command:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=p.cmd, size=11, selectable=True, overflow=ft.TextOverflow.FADE, width=500,
                        max_lines=1, tooltip=p.path)
            ]
        )

        pid = ft.Row(
            controls=[
                ft.Text(value='pid:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=p.pid, size=11, selectable=True),
            ]
        )

        username = ft.Row(
            controls=[
                ft.Text(value='user:', color=ft.colors.WHITE54, size=11),
                ft.Text(value=p.user, size=11, selectable=True),
            ]
        )
        self.del_titles_switch = ft.Switch(
            active_color=ft.colors.INVERSE_PRIMARY,
            value=p.delete_w_titles,
            on_change=lambda e, p=p : self.toggle_del_all_wtitles(process=p, e=e))
        self.row_1.content = ft.Container(
            ft.Column(controls=[


                ft.Row(controls=[
                    ft.Column(controls=[
                        icon
                    ]),
                    ft.Column(controls=[
                        ft.Row([title, ft.Row(controls=[
                            ft.Text(value='delete all window titles', color=ft.colors.WHITE54, size=12),
                            self.del_titles_switch]),
                            ],
                               alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                               width=548
                               ),
                        ft.Row([pid]),
                        ft.Row([path]),
                        #ft.Row([cmd]),
                        ft.Row([username])
                    ],),

                    ],
                    height=130,
                 )]),
        bgcolor=ft.colors.WHITE10,
        border_radius=ft.border_radius.only(bottomRight=8,bottomLeft=8, topRight=8),
        padding=ft.padding.only(left=4,top=12)
        )

    def toggle_del_all_wtitles(self,e, process):
        if process.delete_w_titles:
            process.delete_w_titles = False
        else:
            process.delete_w_titles = True

    def update_toggle(self):
        if self.shown_pid:
            self.del_titles_switch.value = self.p_dict[self.shown_pid].delete_w_titles







