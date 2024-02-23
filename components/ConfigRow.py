import flet as ft


class ConfigRow(ft.Row):

    def __init__(self, text: str, target: ft.Control, col1_width: int, col2_width: int):
        super().__init__()
        self.height = 38

        self.text = ft.Container(
            content=ft.Text(value=text),
            width=col1_width,
            alignment=ft.alignment.center_left,
            height= self.height,
        )

        self.target = ft.Container(
            margin= ft.margin.symmetric(0,0),
            content=target,
            width=col2_width,
            height= self.height,
            alignment=ft.alignment.center,
        )
        self.controls = [self.text, self.target]


class ConfigColumn(ft.Column):
    def __init__(self, config_dict:dict, col1_width: int, col2_width: int):
        super().__init__()
        self.width = col1_width + col2_width
        self.spacing = 0
        for i in config_dict:
            row = ConfigRow(i, config_dict[i], col1_width, col2_width)
            self.controls.append(row)