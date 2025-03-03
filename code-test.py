import flet as ft

def main(page: ft.Page):
    page.title = "Game Hub"
    page.window_width = 800
    page.window_height = 600

    # Встраиваем игру змейка через iframe
    snake_game = ft.Html(
        content="""
        <iframe 
            src="https://playsnake.org/" 
            width="800" 
            height="600" 
            style="border: none;">
        </iframe>
        """
    )

    page.add(snake_game)

ft.app(target=main)