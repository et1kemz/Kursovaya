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

            # Добавляем иконку "Кабинет" в NavigationBar
            page.navigation_bar.destinations.append(
                ft.NavigationBarDestination(
                    icon=ft.Icons.BOOK,
                    label='Кабинет',
                    selected_icon=ft.Icons.BOOKMARK,
                )
            )

            snack_bar_message("Успешная авторизация!")

            # Переход в кабинет
            load_tasks()
            page.navigation_bar.selected_index = 2  # Выбираем кабинет
            page.update()
            navigate(None)
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

    def add_task(e):
        task_text = task_input.value.strip()
        if task_text:
            db = sqlite3.connect('tasks.db')
            cur = db.cursor()
            cur.execute("INSERT INTO tasks (user_id, task) VALUES ((SELECT id FROM users WHERE login=?), ?)", (user_login.value, task_text))
            db.commit()
            db.close()
            
            task_input.value = ''
            load_tasks()  # Обновляем список задач
            snack_bar_message("Задача успешно добавлена!")
            page.update()

    def load_tasks():
        task_list.controls.clear()  # Очищаем список перед загрузкой новых данных
        db = sqlite3.connect('tasks.db')
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, user_id INTEGER, task TEXT)")
        
        if is_authenticated:
            cur.execute("SELECT * FROM tasks WHERE user_id=(SELECT id FROM users WHERE login=?)", (user_login.value,))
            res = cur.fetchall()
            
            for task in res:
                task_list.controls.append(ft.Row([
                    ft.Text(task[2]),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, task_id=task[0]: delete_task(task_id)),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, task_text=task[2]: edit_task(task_text, task_0))
                ]))
        
        db.commit()
        db.close()

    def delete_task(task_id):
        db = sqlite3.connect('tasks.db')
        cur = db.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        db.commit()
        db.close()
        
        load_tasks()  # Обновляем список задач
        snack_bar_message("Задача успешно удалена!")
        page.update()

    def edit_task(task_text, task_id):
        task_input.value = task_text  # Заполняем поле ввода текстом задачи
        btn_add_task.text = "Сохранить"
        
        def save_edit(e):
            new_task_text = task_input.value.strip()
            if new_task_text:
                db = sqlite3.connect('tasks.db')
                cur = db.cursor()
                cur.execute("UPDATE tasks SET task=? WHERE id=?", (new_task_text, task_id))
                db.commit()
                db.close()

                load_tasks()  # Обновляем список задач после редактирования
                btn_add_task.text = "Добавить"  # Возвращаем текст кнопки обратно

                snack_bar_message("Задача успешно обновлена!")
                task_input.value = ''  # Очищаем поле ввода
                page.update()

        btn_add_task.on_click = save_edit

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
    btn_add_task = ft.OutlinedButton(text="Добавить", width=200, on_click=add_task)

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

    panel_cabinet = ft.Row(
        [
            ft.Column(
                [
                    ft.Row([
                        ft.Text('Кабинет', size=24, weight="bold"),
                        ft.IconButton(icon=ft.icons.WB_SUNNY, tooltip="Сменить тему", on_click=toggle_theme),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text('Здесь вы можете управлять своими задачами.', size=16),
                    task_input,
                    btn_add_task,
                    task_list,
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20  # Добавляем отступы между элементами.
    )

    def navigate(e):
        index = page.navigation_bar.selected_index
        page.clean()

        if index == 0:
            page.add(panel_register)
        elif index == 1:
            page.add(panel_auth)
        elif index == 2:
            if is_authenticated:  # Проверяем статус авторизации перед отображением кабинета
                load_tasks()  # Загружаем задачи при переходе в кабинет
                page.add(panel_cabinet)
    
    theme_button = ft.OutlinedButton(text="Темная тема", width=120, on_click=toggle_theme)  # Кнопка смены темы

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER, label='Регистрация'),
            ft.NavigationBarDestination(icon=ft.Icons.VERIFIED_USER_OUTLINED, label='Авторизация'),
            # Иконка "Кабинет" будет добавлена после авторизации в функции auth_user.
        ],
        on_change=navigate
    )

    # Отображаем только панель регистрации при запуске приложения
    page.add(panel_register)

ft.app(target=main)
