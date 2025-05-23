# main.py
import flet as ft
import sqlite3
import subprocess
import sys

def main(page: ft.Page):
    page.title = "Task Management App"
    page.theme_mode = 'dark'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 400
    page.window_height = 500

    is_authenticated = False

    # Функция для смены темы
    def toggle_theme(e):
        if page.theme_mode == 'dark':
            page.theme_mode = 'light'
            theme_button.text = "Темная тема"
            snack_bar_message("Сменена на светлую тему!")
        else:
            page.theme_mode = 'dark'
            theme_button.text = "Светлая тема"
            snack_bar_message("Сменена на темную тему!")
        page.update()

    # Кнопка для смены темы
    theme_button = ft.ElevatedButton(text="Светлая тема", on_click=toggle_theme)

    # Инициализация NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER, label='Регистрация'),
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER_OUTLINED, label='Авторизация'),
        ],
        on_change=lambda e: navigate(e)
    )

    # Добавление NavigationBar на страницу
    page.add(page.navigation_bar)

    def auth_user(e):
        nonlocal is_authenticated
        db = sqlite3.connect('tasks.db')
        cur = db.cursor()
        cur.execute(f"SELECT * FROM users WHERE login = '{user_login.value}' AND pass = '{user_pass.value}'")
        if cur.fetchone() is not None:
            is_authenticated = True
            user_login.value = ''
            user_pass.value = ''
            btn_auth.text = 'Авторизовано'

            page.window_width = 600
            page.window_height = 600

            # Обновляем NavigationBar после авторизации
            page.navigation_bar.destinations = [
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOK,
                    label='Кабинет',
                    selected_icon=ft.Icons.BOOKMARK,
                ),
                ft.NavigationBarDestination(icon=ft.Icons.GAMES, label='Игры'),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label='Настройки'),
                ft.NavigationBarDestination(icon=ft.Icons.NEWSPAPER, label='Новости'),
                ft.NavigationBarDestination(icon=ft.Icons.STAR, label='Достижения'),
                ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label='Сообщество'),
            ]
            page.navigation_bar.selected_index = 0  # Выбираем кабинет
            page.update()

            snack_bar_message("Успешная авторизация!")

            # Переход в кабинет
            show_cabinet()  # Отображаем кабинет

        else:
            snack_bar_message("Неверно введенные данные!")

        db.commit()
        db.close()
        page.update()

    def register(e):
        db = sqlite3.connect('tasks.db')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            login TEXT,
            pass TEXT        
        )""")
        cur.execute(f"INSERT INTO users VALUES(NULL, '{user_login.value}', '{user_pass.value}')")
        
        db.commit()
        db.close()

        user_login.value = ''
        user_pass.value = ''
        btn_reg.text = 'Зарегистрирован'
        snack_bar_message("Пользователь успешно зарегистрирован!")
        page.update()

    def validate(e):
        if all([user_login.value, user_pass.value]):
            btn_reg.disabled = False
            btn_auth.disabled = False
        else:
            btn_reg.disabled = True
            btn_auth.disabled = True

        page.update()

    def snack_bar_message(message):
        snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar = snack_bar
        snack_bar.open = True
        page.update()

    user_login = ft.TextField(label="Логин", width=200, on_change=validate)
    user_pass = ft.TextField(label="Пароль", password=True, width=200, on_change=validate)
    
    btn_reg = ft.OutlinedButton(text="Зарегистрировать", width=200, on_click=register, disabled=True)
    btn_auth = ft.OutlinedButton(text="Авторизовать", width=200, on_click=auth_user, disabled=True)

    panel_register = ft.Row(
        [
            ft.Column(
                [
                    ft.Text('Регистрация'),
                    user_login,
                    user_pass,
                    btn_reg,
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    panel_auth = ft.Row(
        [
            ft.Column(
                [
                    ft.Text('Авторизация'),
                    user_login,
                    user_pass,
                    btn_auth,
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    panel_cabinet = ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Text("Кабинет Игрока", size=24, weight="bold"),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Text("Ваша статистика:", size=16),
            ft.Text(f"Никнейм: {user_login.value}", size=14),
            ft.Text(f"Очки: {1}", size=14),
            ft.ElevatedButton("Профиль", on_click=lambda _: print("Переход в профиль")),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )
    
    def show_register():
        """Отображает панель регистрации."""
        page.clean()
        page.add(panel_register)
        page.update()

    def show_auth():
        """Отображает панель авторизации."""
        page.clean()
        page.add(panel_auth)
        page.update()

    def show_cabinet():
        """Отображает панель кабинета."""
        page.clean()
        page.add(panel_cabinet)
        page.update()

    # Словарь с данными игр
    games_data = {
        "Doodle Jump": {
            "icon": "https://play-lh.googleusercontent.com/Wk-7Rw4jW6v7zGtEjxuH8TdY9zQx8UJ2sOZkqYwQ8yJY9y9y9y9y9y9y9y9y9y9y9y9",
            "description": "Классическая игра с прыжками по платформам!",
            "rating": 4.7,
            "genre": "Аркада, Платформер",
            "release_date": "2009",
            "screenshots": [
                "https://play-lh.googleusercontent.com/Wk-7Rw4jW6v7zGtEjxuH8TdY9zQx8UJ2sOZkqYwQ8yJY9y9y9y9y9y9y9y9y9y9y9",
                "https://play-lh.googleusercontent.com/Wk-7Rw4jW6v7zGtEjxuH8TdY9zQx8UJ2sOZkqYwQ8yJY9y9y9y9y9y9y9y9y9y9y9",
                "https://play-lh.googleusercontent.com/Wk-7Rw4jW6v7zGtEjxuH8TdY9zQx8UJ2sOZkqYwQ8yJY9y9y9y9y9y9y9y9y9y9y9",
            ],
        },
        "Snake": {
            "icon": "https://cdn-icons-png.flaticon.com/512/427/427533.png",
            "description": "Классическая казуальная змейка!",
            "rating": 4.8,
            "genre": "Казуальная, Аркада",
            "release_date": "1976",
            "screenshots": [
                "https://play-lh.googleusercontent.com/xInkwhn9D7uVRWCNGOg5ImkhOCJDFISQ0ggmW_x_5U0-Ui2CPkx8uaiKKMxYBYtRsBc=w526-h296-rw",
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR31u23GxmdazjFvCRdtYz2rtsPjvGYGQmui_sjb0R668UtBqXsSR6-o9kW7KWYa__8iRo&usqp=CAU",
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTMCtw55_OJcwo5Vnmjh-b9jzygg87qRKOPShvpwCICNAI2pS5I_3LL0b6S7HjHNqlkkGQ&usqp=CAU",
            ],
        },
    }

    def show_game_details(game_name):
        """Показывает подробности об игре."""
        game_data = games_data.get(game_name, {})
        if not game_data:
            snack_bar_message("Данные об игре не найдены!")
            return

        # Создаем контейнер для деталей игры
        details_panel = ft.Column(
            [
                ft.Text(game_name, size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Описание игры:", size=18),
                ft.Text(game_data["description"], size=14),
                ft.Text(f"Рейтинг: ⭐⭐⭐⭐ ({game_data['rating']}/5)", size=14),
                ft.Text(f"Жанр: {game_data['genre']}", size=14),
                ft.Text(f"Дата выхода: {game_data['release_date']}", size=14),
                ft.Text("Скриншоты:", size=18),
                ft.Row(
                    [
                        ft.Image(src=url, width=400, height=300)
                        for url in game_data["screenshots"]
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.ElevatedButton(
                    text="Назад",
                    on_click=lambda e: show_games(),  # Возвращаемся к списку игр
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Очищаем страницу и добавляем детали игры
        page.clean()
        page.add(details_panel)
        page.update()

    def show_games():
        """Отображает вкладку с играми."""
        def launch_game(game_name):
            """Запускает игру."""
            if game_name == "Snake":
                # Запускаем игру "Змейка" в отдельном процессе
                subprocess.Popen([sys.executable, "snake_game.py"])
            elif game_name == "Doodle Jump":
                # Запускаем игру "Doodle Jump" в отдельном процессе
                subprocess.Popen([sys.executable, "doodle_jump.py"])
            else:
                snack_bar_message(f"Запуск {game_name}...")
            
    
        def create_game_card(game_name, game_data):
            """Создает карточку для игры."""
            return ft.Card(
                elevation=5,
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(src=game_data["icon"], width=150, height=150, fit=ft.ImageFit.COVER),
                            ft.Text(game_name, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(game_data["description"], size=14, color=ft.Colors.GREY_400),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=16),
                                    ft.Text(str(game_data["rating"]), size=14, color=ft.Colors.GREY_400),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        text="Играть",
                                        icon=ft.Icons.PLAY_ARROW,
                                        on_click=lambda e: launch_game(game_name),
                                    ),
                                    ft.ElevatedButton(
                                        text="Подробнее",
                                        on_click=lambda e: show_game_details(game_name),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=200,
                    padding=10,
                    border_radius=ft.border_radius.all(10),
                )
            )

        # Создаем карточки для игр
        game_cards = [
            create_game_card(game_name, game_data)
            for game_name, game_data in games_data.items()
        ]

        # Создаем контейнер для карточек игр
        games_panel = ft.Column(
            [
                ft.Text("Доступные игры:", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    game_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Добавляем игры на страницу
        page.clean()
        page.add(games_panel)
        page.update()

    def show_settings():
        """Отображает настройки."""
        settings_panel = ft.Column(
            [
                ft.Text("Настройки", size=24),
                theme_button,  # Используем глобальную кнопку
                ft.ElevatedButton(text="Применить", on_click=lambda e: snack_bar_message("Настройки применены!")),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.clean()
        page.add(settings_panel)
        page.update()

    def show_news():
        """Отображает новости."""
        news_panel = ft.Column(
            [
                ft.Text("Новости", size=24),
                ft.Text("Последние обновления и события."),
                ft.Text("Новость 1: Вышла новая версия!"),
                ft.Text("Новость 2: Акция на игры!")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.clean()
        page.add(news_panel)
        page.update()

    def show_achievements():
        """Отображает достижения."""
        achievements_panel = ft.Column(
            [
                ft.Text("Достижения", size=24),
                ft.Text("Ваши игровые достижения."),
                ft.Text("Достижение 1: Пройдена первая игра!"),
                ft.Text("Достижение 2: Открыты все уровни!")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.clean()
        page.add(achievements_panel)
        page.update()

    def show_community():
        """Отображает сообщество."""
        community_panel = ft.Column(
            [
                ft.Text("Сообщество", size=24),
                ft.Text("Общайтесь с другими игроками."),
                ft.ElevatedButton(text="Форум", on_click=lambda e: snack_bar_message("Открываем форум...")),
                ft.ElevatedButton(text="Чат", on_click=lambda e: snack_bar_message("Открываем чат..."))
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.clean()
        page.add(community_panel)
        page.update()

    def navigate(e):
        """Обрабатывает переключение между панелями."""
        if page.navigation_bar is not None:
            page.clean()
            if is_authenticated:
                if page.navigation_bar.selected_index == 0:
                    show_cabinet()
                elif page.navigation_bar.selected_index == 1:
                    show_games()
                elif page.navigation_bar.selected_index == 2:
                    show_settings()
                elif page.navigation_bar.selected_index == 3:
                    show_news()
                elif page.navigation_bar.selected_index == 4:
                    show_achievements()
                elif page.navigation_bar.selected_index == 5:
                    show_community()
            else:
                if page.navigation_bar.selected_index == 0:
                    show_register()
                elif page.navigation_bar.selected_index == 1:
                    show_auth()

    # Отображаем только панель регистрации при запуске приложения
    show_register()

ft.app(target=main)