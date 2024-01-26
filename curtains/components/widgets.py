import flet as ft

class ScaleWidget(ft.Container):
    def __init__(self, target: ft, attr_name: str, min_value = None, max_value = None,
                 stepsize: float = 0.1):
        super().__init__()
        self.attr_name = attr_name
        self.min_value = min_value
        self.max_value = max_value
        self.step_size = stepsize
        self.decrease_btn = ft.IconButton(
            icon=ft.icons.ARROW_BACK_IOS_ROUNDED,
            scale=1,
            on_click=lambda e, t=target, an=self.attr_name: self.decrease(e, t, an),
            icon_color=ft.colors.INVERSE_PRIMARY
        )
        self.increase_btn = ft.IconButton(
            icon=ft.icons.ARROW_FORWARD_IOS_ROUNDED,
            scale=1,
            on_click=lambda e, t=target, an=self.attr_name: self.increase(e, t, an),
            icon_color=ft.colors.INVERSE_PRIMARY,
            #style=ft.ButtonStyle(shape=ft.StadiumBorder())
        )
        self.number = ft.Text(value=str(getattr(target, attr_name)))
        self.content = ft.Row(
            [self.decrease_btn, self.number, self.increase_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
            spacing=0
        )

    def decrease(self, e, t, attr_name: str):
        old_val = getattr(t, attr_name)
        if self.min_value is None or old_val > self.min_value:
            setattr(t, attr_name, round(old_val - 0.1, 1))
            if self.increase_btn.disabled:
                self.increase_btn.disabled = False
                self.increase_btn.icon_color = ft.colors.INVERSE_PRIMARY
        if getattr(t, attr_name) == self.min_value:
            self.decrease_btn.disabled = True
            self.decrease_btn.icon_color = ft.colors.WHITE24
        self.number.value = str(getattr(t, attr_name))

    def increase(self, e, t, attr_name: str):
        old_val = getattr(t, attr_name)
        if self.max_value is None or old_val < self.max_value:
            setattr(t, attr_name, round(old_val + 0.1, 1))
            if self.decrease_btn.disabled:
                self.decrease_btn.disabled = False
                self.decrease_btn.icon_color = ft.colors.INVERSE_PRIMARY
        if getattr(t, attr_name) == self.max_value:
            self.increase_btn.disabled = True
            self.increase_btn.icon_color = ft.colors.WHITE24
        self.number.value = str(getattr(t, attr_name))

