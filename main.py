import flet as ft
from flet import Page, SnackBar, Text
import sqlite3

def main(page: ft.Page):
    page.title = "Task Management App"
    page.theme_mode = 'dark'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 400
    page.window.height = 500

    is_authenticated = False

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

            page.window.width = 600
            page.window.height = 600

            # Обновляем NavigationBar после авторизации
            page.navigation_bar.destinations = [
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOK,
                    label='Кабинет',
                    selected_icon=ft.Icons.BOOKMARK,
                )
            ]
            page.navigation_bar.selected_index = 0  # Выбираем кабинет
            page.update()

            snack_bar_message("Успешная авторизация!")

            # Переход в кабинет
            load_tasks()
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
        global user_login_value
        user_login_value = e.control.value
        if all([user_login.value, user_pass.value]):
            btn_reg.disabled = False
            btn_auth.disabled = False
        else:
            btn_reg.disabled = True
            btn_auth.disabled = True

        page.update()

    def snack_bar_message(message):
        snack_bar = ft.SnackBar(ft.Text(message))
        page.open(snack_bar)

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

    user_login = ft.TextField(label="Логин", width=200, on_change=validate)
    user_pass = ft.TextField(label="Пароль", password=True, width=200, on_change=validate)
    
    btn_reg = ft.OutlinedButton(text="Зарегистрировать", width=200, on_click=register, disabled=True)
    btn_auth = ft.OutlinedButton(text="Авторизовать", width=200, on_click=auth_user, disabled=True)

    # Поля для работы с задачами
    task_input = ft.TextField(label="Введите задачу", width=200)
    btn_add_task = ft.OutlinedButton(text="Добавить", width=200, on_click=lambda e: add_task())

    # Список задач
    task_list = ft.ListView(spacing=10)

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

    

    def add_task(e):
        """Добавляет задачу в список."""
        if task_input.value:
            task_list.controls.append(ft.Text(task_input.value))
            task_input.value = ""
            page.update()  # Обновляем страницу, чтобы отобразить новую задачу

    btn_add_task.on_click = add_task  # Привязываем обработчик к кнопке

    def add_task(e):
        """Добавляет задачу в список."""
        if task_input.value:
            task_list.controls.append(ft.Text(task_input.value))
            task_input.value = ""
            page.update()  # Обновляем страницу, чтобы отобразить новую задачу

    btn_add_task.on_click = add_task  # Привязываем обработчик к кнопке

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
    
    page.add(panel_cabinet)

    def navigate(e):
        """Обрабатывает переключение между панелями."""
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

    def show_register():
        """Отображает панель регистрации."""
        page.clean()
        page.add(panel_register)

    def show_auth():
        """Отображает панель авторизации."""
        page.clean()
        page.add(panel_auth)

    def show_cabinet():
        """Отображает панель кабинета."""
        page.clean()
        load_tasks()  # Загружаем задачи при переходе в кабинет
        page.add(panel_cabinet)
        
        # Добавляем вкладки на навигационную панель
        if len(page.navigation_bar.destinations) == 1:  # Проверка, чтобы не добавлять повторно
            page.navigation_bar.destinations.extend([
                ft.NavigationBarDestination(icon=ft.Icons.GAMES, label='Игры'),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label='Настройки'),
                ft.NavigationBarDestination(icon=ft.Icons.NEWSPAPER, label='Новости'),
                ft.NavigationBarDestination(icon=ft.Icons.STAR, label='Достижения'),
                ft.NavigationBarDestination(icon=ft.Icons.PEOPLE, label='Сообщество'),
            ])
            page.update()

    def add_task():
        """Добавляет задачу в список."""
        task_text = task_input.value.strip()
        
        if task_text:
            # Добавление задачи в список и базу данных (если нужно)
            task_list.controls.append(ft.Text(task_text))
            task_input.value = ''  # Очищаем поле ввода задачи
            snack_bar_message("Задача добавлена!")
        
        page.update()

    def load_tasks():
        """Загружает задачи (пример с заглушкой)."""
        # Здесь можно добавить логику загрузки задач из базы данных.
        task_list.controls.clear()  # Очищаем текущий список задач (если есть).

    def show_games():
        """Отображает список игр."""
        games_panel = ft.Column(
            [
                ft.Text("Доступные игры:", size=24),
                # Здесь можно добавить кнопки для запуска игр
                ft.ElevatedButton(text="Игра 1", on_click=lambda e: launch_game("Игра 1")),
                ft.ElevatedButton(text="Игра 2", on_click=lambda e: launch_game("Игра 2")),
                # Добавьте другие игры по аналогии
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.add(games_panel)

    def show_settings():
        """Отображает настройки."""
        settings_panel = ft.Column(
            controls=[
                ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Здесь вы можете настроить ваш лаунчер.", size=16),
                ft.Divider(height=2, color=ft.colors.GREY_400),  # Тонкий разделитель

                ft.Row(
                    [
                        ft.Text("Тема:", size=18),
                        ft.ElevatedButton(
                            text="Сменить тему",
                            icon=ft.icons.WB_SUNNY,
                            on_click=toggle_theme,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,  # Равномерное распределение
                ),
                ft.Divider(height=2, color=ft.colors.GREY_400),  # Тонкий разделитель

                ft.ElevatedButton(
                    text="Применить",
                    on_click=lambda e: snack_bar_message("Настройки применены!"),
                    width=150,  # Фиксированная ширина кнопки
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Центрирование по горизонтали
            spacing=15,  # Расстояние между элементами
            width=400,  # Фиксированная ширина панели настроек
        )
        page.add(settings_panel)
        page.update()  # Добавлено обновление страницы

    show_settings()
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
        page.add(news_panel)

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
        page.add(achievements_panel)

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
        page.add(community_panel)

    def launch_game(game_name):
        """Запускает игру (заглушка)."""
        snack_bar_message(f"Запуск {game_name}...")

    theme_button = ft.OutlinedButton(text="Темная тема", width=120, on_click=toggle_theme)  # Кнопка смены темы

    # Изначально панель навигации с регистрацией и авторизацией
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER, label='Регистрация'),
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER_OUTLINED, label='Авторизация'),
        ],
        on_change=navigate
    )

    # Отображаем только панель регистрации при запуске приложения
    show_register()

ft.app(target=main)
