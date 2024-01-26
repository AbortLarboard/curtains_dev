import flet as ft
import math

class HeadControls(ft.Container):
    def __init__(self, content_col, page, processlist, contents):
        super().__init__()
        green = '#00FE47'
        yellow = ft.colors.AMBER
        blue = ft.colors.INVERSE_PRIMARY
        red = ft.colors.RED_900
        self.window_col = None
        self.content_area = content_col
        self.contents = contents
        self.page = page
        self.processlist = processlist
        self.p_dict = processlist.p_dict
        self.alignment = ft.alignment.bottom_center
        self.height = 140
        self.width = 380
        self.padding = 0
        self.margin = 8
        self.status_icon_allhidden = ft.Stack(
            controls=[
                ft.Icon(name=ft.icons.SHIELD_OUTLINED,scale=5, color=blue, opacity=0.1),
                ft.Icon(name=ft.icons.SHIELD_OUTLINED, scale=4, color=blue, opacity=0.3),
                ft.Icon(name=ft.icons.SHIELD_OUTLINED, scale=3, color= blue, opacity=1),
                ft.Icon(name=ft.icons.VISIBILITY_OFF, scale=1.5, color=blue, opacity=1)
            ],
            height=60,
        )
        self.status_icon_visible = ft.Stack(
            controls=[
                ft.Icon(name=ft.icons.VISIBILITY, scale=1.5, color=yellow, opacity=1),

                ft.Icon(name=ft.icons.SHIELD_OUTLINED,scale=5, color=yellow, opacity=0.1),
                ft.Icon(name=ft.icons.SHIELD_OUTLINED, scale=4, color=yellow, opacity=0.3),
                ft.Icon(name=ft.icons.SHIELD_OUTLINED, scale=3, color=yellow, opacity=1),
            ],
            height=60,
        )

        #self.status_yellow = ft.Text(value='Privacy: partial')
        #self.status_yellow = ft.Text(value='Privacy: partial')
        self.status_icon = self.status_icon_allhidden
        self.status_text = ft.Text(value='Curtains')
        self.status_description = ft.Text(
            value='privacy for your windows',
            color=blue,
            size=12,
            style=ft.TextStyle.italic
            #opacity=0.5
        )
        self.status_container = ft.Container(
            content=ft.Column(
                controls=[
                    self.status_icon,
                    self.status_text,
                    self.status_description,
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            width=140,
            #bgcolor='yellow',
            alignment=ft.alignment.center,
            padding= ft.padding.only(bottom=4)
                )

        self.expand_content_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ARROW_FORWARD_IOS,
                icon_color=ft.colors.WHITE54,
                icon_size=18,
                #style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
                rotate=0,
                animate_rotation=100,
                on_click=lambda e: self.toggle_content(e),

            ),
            bgcolor=ft.colors.WHITE12,
            border_radius=8
        )
        self.windows_content_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.DESKTOP_WINDOWS_SHARP,
                icon_color=ft.colors.WHITE54,
                icon_size=18,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            on_click=lambda e: self.switch_content(e),
            border_radius=8,
            data='windows',
            tooltip='Windows'
        )

        self.settings_content_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.SETTINGS_SHARP,
                icon_color=ft.colors.WHITE54,
                icon_size=18,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            on_click=lambda e: self.switch_content(e),
            border_radius=8,
            alignment=ft.alignment.center,
            data='settings',
            tooltip='Settings'
        )

        self.preview_config_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.VISIBILITY_SHARP,
                icon_color=ft.colors.WHITE54,
                icon_size=18,
                #style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.INVERSE_PRIMARY,
            on_click=lambda e: self.switch_content(e),
            border_radius=8,
            padding=0,
            margin=0,
            data='preview',
            disabled=True,
            tooltip='Preview'
        )
        # self.unhide_all_btn = ft.Container(
        #     content=ft.IconButton(
        #         icon=ft.icons.VISIBILITY,
        #         icon_color=ft.colors.WHITE54,
        #         style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder())
        #     ),
        #     bgcolor=ft.colors.WHITE12,
        #     border_radius=8
        # )
        self.all_hidden_switch = ft.Switch(
                    value=False,
                    active_color=ft.colors.INVERSE_PRIMARY,
                    on_change=lambda e: self.toggle_all_hidden(e),
                )

        self.btn_row0 = ft.Row(
            controls=[
                ft.Text(value='hide everything', color=ft.colors.WHITE54, size=12),
                ft.Container(
                    content=self.all_hidden_switch,
                    padding= ft.padding.only(right=6)
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        self.btn_row1 = ft.Row(
            controls=[
                self.windows_content_btn,
                self.preview_config_btn,
                self.settings_content_btn,
                ft.Container(width=1, height=38, bgcolor=ft.colors.WHITE12),
                self.expand_content_btn,
            ],
            alignment=ft.MainAxisAlignment.END,

        )
        self.controls_container = ft.Container(
            ft.Column(
                controls=[
                    ft.Container(self.btn_row1),
                    ft.Container(
                        content=self.btn_row0,
                        #bgcolor=red,
                        #alignment=ft.alignment.bottom_center,
                        height=24,
                        padding=0,
                        margin=0,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=232,
                spacing=0,
            ),
            alignment=ft.alignment.bottom_center,
            #bgcolor=green,
            padding=0,
            margin=0,
        )
        self.content = ft.Row(
            controls=[
                self.status_container,
                ft.VerticalDivider(width=0.5, color=ft.colors.WHITE12),
                self.controls_container,
            ]
        )
    def toggle_content(self, e):
        if self.expand_content_btn.content.rotate == math.pi:
            self.expand_content_btn.content.rotate = 0
            self.content_area.visible = True
            self.page.window_width = 1070

        else:
            self.expand_content_btn.content.rotate = math.pi
            self.content_area.visible = False
            self.page.window_width = 440

    def toggle_all_hidden(self, e):
        for p in self.p_dict:
            self.p_dict[p].delete_w_titles = e.control.value
            self.p_dict[p].item.switch.value = e.control.value
            self.p_dict[p].item.toggle_hidden(e.control.value)
        self.processlist.all_hidden = e.control.value

    def switch_content(self, e):
        key = e.control.data
        print(type(self.contents))
        print(self.contents[key])
        self.content_area.content.controls = [self.contents[key]]
        for btn in self.btn_row1.controls:
            if btn.data == key:
                btn.bgcolor =ft.colors.INVERSE_PRIMARY
                btn.disabled = True
            else:
                btn.bgcolor = ft.colors.WHITE12
                btn.disabled = False


