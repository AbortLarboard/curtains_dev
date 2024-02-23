import flet as ft

class PageTitle(ft.Container):
    def __init__(self, title:ft.Text, icon:ft.Icon, subtitle:ft.Text):
        super().__init__()

        self.content = ft.Column()
        #self.content.spacing = 20
        #self.content.alignment = ft.MainAxisAlignment.SPACE_AROUND
        self.title = title
        self.icon = icon
        #self.icon.color = ft.colors.WHITE54

        self.title.style = ft.TextThemeStyle.TITLE_MEDIUM
        self.title.weight = ft.FontWeight.BOLD
        self.title_row = ft.Row(
            controls=[
                self.title,
                self.icon,
            ]
        )
        self.subtitle = subtitle
        self.subtitle.style = ft.TextThemeStyle.BODY_SMALL

        self.subtitle.color = ft.colors.WHITE54
        self.subtitle_row = ft.Row(controls=[self.subtitle])

        self.content.controls = [self.title_row, self.subtitle_row]

        self.margin = ft.margin.only(top=14,left=4)
        self.height = 77 - self.margin.top

