import math
import time

import flet as ft


class ContentContainer(ft.Container):

    def __init__(self, title= None, max_height: int = 52, width: int = 208,
                 title_action: int = 1,
                 icon=None):
        super().__init__()
        self.color_secondary = ft.colors.WHITE54
        self.min_height = 40
        self.height = self.min_height
        self.max_height = max_height
        self.width = width
        self.padding = 8
        self.content_padding = 16
        self.animate = 128
        self.border = ft.border.all(1, ft.colors.WHITE10)
        self.border_radius = ft.border_radius.all(8)
        self.bgcolor = '#1B1B1B'

        self.icon_container = ft.Container(alignment=ft.alignment.center_left)
        if icon:
            self.icon_container.content = icon

        self.title_container = ft.Container(alignment=ft.alignment.center_left)
        if title:
            if type(title) == str:
                title = ft.Text(value=title)

            self.title_container.content = title
            self.title = self.title_container.content

        self.actions = ft.Row(spacing=0)
        self.action_container = ft.Container(
            content=self.actions,
            alignment=ft.alignment.center_right,
        )
        self.clps_btn_container = ft.Container(alignment=ft.alignment.center)

        self.title_row = ft.Row(
            controls=[
                self.icon_container,
                self.title_container,
                ft.Container(content=None, expand=True),
                self.action_container,
                self.clps_btn_container,
            ], width=self.width
        )

        self.switch = ft.Switch(
            value=True,
            active_color=ft.colors.INVERSE_PRIMARY,
        )

        self.arrow = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_IOS,
            on_click=lambda e: self.toggle_content(e),
            icon_color=self.color_secondary,
            icon_size=11,
            rotate=0
        )

        self.action_info = ft.Container(content=ft.Text(
            value='Example',
            color=self.color_secondary,
        ))

        self.content_col = ft.Column(controls=[])
        self.body = ft.Container(
            content=self.content_col,
            padding=ft.padding.symmetric(0, self.content_padding),
            # bgcolor=ft.colors.WHITE10
        )
        if title_action ==0:
            self.height = self.max_height
        elif title_action == 1:
            self.clps_btn_container.content = self.arrow
            self.body.visible = False

        elif title_action == 2:
            self.clps_btn_container.content = self.arrow
            self.actions.controls.insert(-1, ft.Container(content=self.action_info))
            self.body.visible = False

        elif title_action == 3:
            self.clps_btn_container.content = self.switch
            self.body.visible = False


        self.content = ft.Column(controls=[
            ft.Container(
                content=self.title_row,
                height=self.min_height,
                padding=ft.padding.only(left=self.content_padding / 2, right=self.content_padding / 2),
                alignment=ft.alignment.center
            ),
            self.body
        ])

        if title is None:
            self.title_row.controls.remove(self.title_container)
            self.height = max_height

        self.expanded = False

    def toggle_content(self, e=None):
        if self.expanded == False:
            # self.height == self.min_height:
            self.clps_btn_container.content.rotate = (math.pi / 2)
            self.height = self.max_height
            self.body.visible = True
            self.content.controls[0].border = ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.WHITE12))
            time.sleep(self.animate / 1000)
            self.expanded = True

        else:
            self.clps_btn_container.content.rotate = 0
            self.content.controls[0].border = None
            self.body.visible = False
            self.height = self.min_height
            self.expanded = False
