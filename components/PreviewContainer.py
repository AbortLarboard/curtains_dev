import flet as ft
import time
import logging
from . import curtains
from .ContentContainer import ContentContainer
from .widgets import ScaleWidget

class ScreenshotContainer(ContentContainer):
# TODO not sure if useful: safe screenshot
    def __init__(self):
        icon = ft.Icon(name=ft.icons.VISIBILITY_SHARP, color=ft.colors.WHITE54)
        super().__init__(width=800, max_height=500, title_action=0)
        self.border = None
        self.padding = ft.padding.only(left=4)
        self.bgcolor = None
        self.content_col.spacing = 0
        self.title_row.visible = False
        self.alignment = ft.alignment.top_center
        #self.content.padding = ft.padding.only(top=0,left=8,)
        #self.body.padding = ft.padding.only(top=0, left=8, )
        self.width = 600
        self.height = 440
        self.s_width = None
        self.s_height = None
        self.fraction = 4
        self.update_delay = 0.5  # seconds between screenshots
        self.all_hidden = ft.Icon(name=ft.icons.QUESTION_MARK_OUTLINED, color=ft.colors.WHITE54)

        self.row_interval = ft.Row(
            [
                ft.Container(ft.Text(value='interval'), width=100, padding=ft.padding.only(left=8)),
                ft.Container(
                    ScaleWidget(self, 'update_delay', min_value=0.1),
                    width=200,
                    alignment=ft.alignment.center),
            ],

        )
        self.row_all_hidden = ft.Row(
            [
                ft.Container(ft.Text(value='all hidden'), width=100, padding=ft.padding.only(left=8)),
                ft.Container(
                    self.all_hidden,
                    width=200,
                    alignment=ft.alignment.center),
            ],
            #alignment=ft.MainAxisAlignment.START
        )
        img, (self.s_width,self.s_height) = curtains.take_screenshot(self.fraction)
        self.wh_original = (self.s_width, self.s_height)
        self.screenshot = ft.Image(
            src_base64=curtains.image2base64(img),
            #fit=ft.ImageFit.FIT_WIDTH,
        )
        self.size_plus_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ADD,
                icon_color=ft.colors.WHITE54,
                icon_size=8,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            width=24,
            height=24,
            border_radius=ft.border_radius.only(bottomRight=8, topRight=8),
            padding=0,
            margin=0,
            alignment=ft.alignment.center,
            on_click=lambda e: self.decr_fraction(e),

        )
        self.size_minus_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.REMOVE,
                icon_color=ft.colors.WHITE54,
                icon_size=8,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            width=24,
            height=24,
            border_radius=ft.border_radius.only(topLeft=8, bottomLeft=8),
            padding=0,
            margin=0,
            alignment=ft.alignment.center,
            on_click=lambda e: self.incr_fraction(e),
        )

        self.updt_plus_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ADD,
                icon_color=ft.colors.WHITE54,
                icon_size=8,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            width=24,
            height=24,
            border_radius=ft.border_radius.only(bottomRight=8, topRight=8),
            padding=0,
            margin=0,
            alignment=ft.alignment.center,
            on_click=lambda e: self.incr_updti(e),

        )
        self.updt_minus_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.REMOVE,
                icon_color=ft.colors.WHITE54,
                icon_size=8,
                style=ft.ButtonStyle(shape=ft.CountinuosRectangleBorder()),
            ),
            bgcolor=ft.colors.WHITE12,
            width=24,
            height=24,
            border_radius=ft.border_radius.only(topLeft=8, bottomLeft=8),
            padding=0,
            margin=0,
            alignment=ft.alignment.center,
            on_click=lambda e: self.decr_updti(e),
        )

        self.scale_ctrls = ft.Row([
            self.size_minus_btn,
            ft.Container(
                content=ft.Text(value=(round(1/self.fraction,1)), color=ft.colors.WHITE54, style=ft.TextThemeStyle.BODY_SMALL),
                bgcolor=ft.colors.WHITE12,
                height=24,
                width=28,
                alignment=ft.alignment.center
            ),
            self.size_plus_btn,
        ], spacing=2)
        self.update_ctrls = ft.Row([
            self.updt_minus_btn,
            ft.Container(
                content=ft.Text(value=self.update_delay, color=ft.colors.WHITE54, style=ft.TextThemeStyle.BODY_SMALL),
                bgcolor=ft.colors.WHITE12,
                height=24,
                width=28,
                alignment=ft.alignment.center

            ),
            self.updt_plus_btn,
                                    ],
            spacing=2)
        self.toggle_screenshots = ft.Switch(active_color=ft.colors.INVERSE_PRIMARY)
        self.toggle_row = ft.Row(controls=[ft.Text('capture', color=ft.colors.WHITE54, style=ft.TextThemeStyle.BODY_SMALL), self.toggle_screenshots], spacing=2)
        self.control_row = ft.Row([
            self.toggle_row,
            ft.Text('scale', color=ft.colors.WHITE54, style=ft.TextThemeStyle.BODY_SMALL),
            self.scale_ctrls,
            ft.Container(width=12),
            ft.Text('rate', color=ft.colors.WHITE54, tooltip='delay between screenshots in seconds'),
            ft.Container(content=self.update_ctrls,),
        ])

        # self.unhide_all_btn = ft.Container(
        self.screenshot_time = time.time()
        self.content = ft.Column([
            self.title_row,
            self.control_row,
            ft.Container(
                self.screenshot,
                padding=0,
                width=self.s_width,
                height=self.s_height,
                alignment= ft.alignment.top_left

            ),
        ],
        alignment=ft.MainAxisAlignment.START)

    def update_preview(self):
        if self.toggle_screenshots.value and (time.time() - self.screenshot_time) >= self.update_delay:
            screenshot, (self.s_width, self.s_height) = curtains.take_screenshot(self.fraction)
            if screenshot:
                self.screenshot.src_base64 = curtains.image2base64(screenshot)
                self.screenshot_time = time.time()
                if curtains.is_black(screenshot):
                    self.all_hidden.name = ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED
                    self.all_hidden.color = ft.colors.GREEN
                else:
                    self.all_hidden.name = ft.icons.ERROR_OUTLINE_ROUNDED
                    self.all_hidden.color = ft.colors.RED
            else:
                logging.exception(f'Error happened while taking a screenshot')
        # if self.toggle_screenshots is False:
        #     self.screenshot.opacity = 0.1
        #     self.all_hidden.name = ft.icons.QUESTION_MARK_OUTLINED
        #     self.all_hidden.color = ft.colors.WHITE54

    def decr_fraction(self, e):
        if self.fraction > 2:
            self.fraction -= 1
            self.scale_ctrls.controls[1].content.value = round(1/self.fraction,1)
            self.content.controls[-1].width = self.wh_original[0]/self.fraction
            self.width = self.wh_original[0]/self.fraction
            self.height = (self.wh_original[1]/self.fraction) + 100
            #self.content.controls[-1].height = self.height / self.fraction
            self.content.update()

    def incr_fraction(self, e):
        if self.fraction < 4:
            self.fraction += 1
            self.scale_ctrls.controls[1].content.value = round(1/self.fraction,1)
            self.width = self.wh_original[0]/self.fraction
            self.height = (self.wh_original[1]/self.fraction) + 100
            self.content.controls[-1].width = self.wh_original[0]/self.fraction
            self.content.update()

    def incr_updti(self, e):
        self.update_delay += 0.1
        self.update_ctrls.controls[1].content.value = round(self.update_delay, 1)
        self.update_ctrls.controls[1].update()

    def decr_updti(self, e):
        if self.update_delay > 0.2:
            self.update_delay -= 0.1
            self.update_ctrls.controls[1].content.value = round(self.update_delay, 1)
            self.update_ctrls.controls[1].update()

    def check_all_hidden(self, img):
        if curtains.is_black(img):
            print('all hidden')
