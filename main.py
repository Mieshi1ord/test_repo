import flet as ft
import requests

DJANGO_API_URL = "http://127.0.0.1:8000/api"

def show_snackbar(page, message):
    snack = ft.SnackBar(content=ft.Text(message), open=True)
    page.overlay.append(snack)
    page.update()

def main(page: ft.Page):
    page.title = "Сектор практик и трудоустройства"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window.width = 400
    page.window.height = 700
    
    page.token = None
    page.user_role = None
    page.user_id = None
    
    def show_vacancies():
        page.clean()
        
        page.add(
            ft.Text("Вакансии для студентов", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, thickness=2),
        )
        
        try:
            headers = {}
            if page.token:
                headers["Authorization"] = f"Bearer {page.token}"
            
            response = requests.get(f"{DJANGO_API_URL}/vacancies/", headers=headers)
            if response.status_code == 200:
                vacancies = response.json()
                
                if not vacancies:
                    page.add(ft.Text("Нет активных вакансий", italic=True))
                    back_button = ft.TextButton("Назад", on_click=lambda e: show_main_menu())
                    page.add(back_button)
                    return
                
                for v in vacancies:
                    vacancy_id = v['id']
                    company_name = v.get('company_name', 'Не указана')
                    salary_text = f"Зарплата: от {v['salary_min']} руб." if v.get('salary_min') else ""
                    requirements_text = v['requirements'][:100] + "..." if len(v['requirements']) > 100 else v['requirements']
                    
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(v['title'], size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Компания: {company_name}"),
                                ft.Text(salary_text) if salary_text else ft.Text(""),
                                ft.Text(f"Локация: {v.get('location', 'не указана')}"),
                                ft.Text(f"Требования: {requirements_text}"),
                                ft.ElevatedButton(
                                    "Откликнуться",
                                    width=150,
                                    on_click=lambda e, vid=vacancy_id: respond_to_vacancy(vid)
                                ),
                            ], spacing=10),
                            padding=15
                        )
                    )
                    page.add(card)
                
                back_button = ft.TextButton("Назад", on_click=lambda e: show_main_menu())
                page.add(back_button)
            else:
                page.add(ft.Text(f"Ошибка загрузки: {response.status_code}", color="red"))
        except Exception as e:
            page.add(ft.Text(f"Ошибка подключения к серверу: {e}", color="red"))
    
    def respond_to_vacancy(vacancy_id):
        if not page.token:
            show_login()
            return
        
        def send_response(e):
            try:
                headers = {"Authorization": f"Bearer {page.token}"}
                response = requests.post(
                    f"{DJANGO_API_URL}/vacancies/{vacancy_id}/respond/",
                    headers=headers,
                    json={"cover_letter": "Заинтересован в вакансии"}
                )
                
                if response.status_code == 201 or response.status_code == 200:
                    show_snackbar(page, "Отклик отправлен!")
                    page.update()
                else:
                    show_snackbar(page, f"Ошибка: {response.status_code}")
            except Exception as ex:
                show_snackbar(page, f"Ошибка: {ex}")
        
        send_response(None)
    
    def show_my_responses():
        page.clean()
        
        if not page.token:
            show_login()
            return
        
        page.add(
            ft.Text("Мои отклики", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, thickness=2),
        )
        
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.get(f"{DJANGO_API_URL}/responses/", headers=headers)
            
            if response.status_code == 200:
                responses = response.json()
                
                if not responses:
                    page.add(ft.Text("У вас пока нет откликов"))
                else:
                    for r in responses:
                        status_color = "green" if r['status'] in ['invited', 'hired'] else "orange"
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(r['vacancy_title'], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Статус: {r['status']}", color=status_color),
                                    ft.Text(f"Дата: {r['created_at'][:10]}"),
                                ], spacing=5),
                                padding=10
                            )
                        )
                        page.add(card)
                
                back_button = ft.TextButton("Назад", on_click=lambda e: show_main_menu())
                page.add(back_button)
            else:
                page.add(ft.Text(f"Ошибка загрузки: {response.status_code}"))
        except Exception as e:
            page.add(ft.Text(f"Ошибка: {e}"))
    
    def delete_vacation(vacancy_id):
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.delete(f"{DJANGO_API_URL}/vacancies/{vacancy_id}/", headers=headers)
            
            if response.status_code == 204:
                show_snackbar(page, "Вакансия удалена!")
                show_company_vacancies()
            else:
                show_snackbar(page, f"Ошибка удаления: {response.status_code}")
        except Exception as ex:
            show_snackbar(page, f"Ошибка: {ex}")
    
    def show_company_vacancies():
        page.clean()
        
        page.add(
            ft.Text("Мои вакансии", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, thickness=2),
            ft.ElevatedButton("Создать вакансию", on_click=lambda e: create_vacancy(), width=200),
            ft.Divider(height=20),
        )
        
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.get(f"{DJANGO_API_URL}/vacancies/", headers=headers)
            
            if response.status_code == 200:
                vacancies = response.json()
                
                if not vacancies:
                    page.add(ft.Text("У вас пока нет созданных вакансий", italic=True))
                else:
                    for v in vacancies:
                        vacancy_id = v['id']
                        status_text = "Активна" if v['is_active'] else "Не активна"
                        status_color = "green" if v['is_active'] else "red"
                        
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(v['title'], size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Статус: {status_text}", color=status_color),
                                    ft.Text(f"Локация: {v.get('location', 'не указана')}"),
                                    ft.Row([
                                        ft.ElevatedButton("Редактировать", width=120, on_click=lambda e, vid=vacancy_id: edit_vacancy(vid)),
                                        ft.ElevatedButton("Удалить", width=120, color="red", on_click=lambda e, vid=vacancy_id: delete_vacation(vid)),
                                        ft.TextButton("Отклики", on_click=lambda e, vid=vacancy_id: show_vacancy_responses(vid)),
                                    ], spacing=10),
                                ], spacing=10),
                                padding=15
                            )
                        )
                        page.add(card)
                
                back_button = ft.TextButton("Назад", on_click=lambda e: show_main_menu())
                page.add(back_button)
            else:
                page.add(ft.Text(f"Ошибка загрузки: {response.status_code}", color="red"))
        except Exception as e:
            page.add(ft.Text(f"Ошибка: {e}"))
    
    def create_vacancy():
        page.clean()
        
        title_field = ft.TextField(label="Название вакансии", width=350)
        description_field = ft.TextField(label="Описание", multiline=True, height=100, width=350)
        requirements_field = ft.TextField(label="Требования", multiline=True, height=100, width=350)
        salary_min_field = ft.TextField(label="Зарплата от", width=350)
        location_field = ft.TextField(label="Местоположение", width=350, value="Москва")
        
        def save_vacancy(e):
            if not title_field.value:
                show_snackbar(page, "Введите название вакансии")
                return
            if not requirements_field.value:
                show_snackbar(page, "Введите требования")
                return
            
            try:
                data = {
                    "title": title_field.value,
                    "description": description_field.value or "",
                    "requirements": requirements_field.value,
                    "salary_min": int(salary_min_field.value) if salary_min_field.value else None,
                    "location": location_field.value,
                    "is_active": True
                }
                headers = {"Authorization": f"Bearer {page.token}"}
                response = requests.post(f"{DJANGO_API_URL}/vacancies/", headers=headers, json=data)
                
                if response.status_code == 201:
                    show_snackbar(page, "Вакансия создана!")
                    show_company_vacancies()
                else:
                    show_snackbar(page, f"Ошибка: {response.status_code}")
            except Exception as ex:
                show_snackbar(page, f"Ошибка: {ex}")
        
        page.add(
            ft.Text("Создание вакансии", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            title_field,
            description_field,
            requirements_field,
            salary_min_field,
            location_field,
            ft.Row([
                ft.ElevatedButton("Сохранить", on_click=save_vacancy),
                ft.TextButton("Отмена", on_click=lambda e: show_company_vacancies()),
            ])
        )
    
    def edit_vacancy(vacancy_id):
        page.clean()
        
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.get(f"{DJANGO_API_URL}/vacancies/{vacancy_id}/", headers=headers)
            
            if response.status_code == 200:
                v = response.json()
                
                title_field = ft.TextField(label="Название вакансии", width=350, value=v['title'])
                description_field = ft.TextField(label="Описание", multiline=True, height=100, width=350, value=v['description'])
                requirements_field = ft.TextField(label="Требования", multiline=True, height=100, width=350, value=v['requirements'])
                salary_min_field = ft.TextField(label="Зарплата от", width=350, value=str(v['salary_min']) if v['salary_min'] else "")
                location_field = ft.TextField(label="Местоположение", width=350, value=v['location'])
                active_checkbox = ft.Checkbox(label="Активна", value=v['is_active'])
                
                def update_vacancy(e):
                    try:
                        data = {
                            "title": title_field.value,
                            "description": description_field.value,
                            "requirements": requirements_field.value,
                            "salary_min": int(salary_min_field.value) if salary_min_field.value else None,
                            "location": location_field.value,
                            "is_active": active_checkbox.value
                        }
                        response = requests.put(f"{DJANGO_API_URL}/vacancies/{vacancy_id}/", headers=headers, json=data)
                        
                        if response.status_code == 200:
                            show_snackbar(page, "Вакансия обновлена!")
                            show_company_vacancies()
                        else:
                            show_snackbar(page, f"Ошибка: {response.status_code}")
                    except Exception as ex:
                        show_snackbar(page, f"Ошибка: {ex}")
                
                page.add(
                    ft.Text("Редактирование вакансии", size=28, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20),
                    title_field,
                    description_field,
                    requirements_field,
                    salary_min_field,
                    location_field,
                    active_checkbox,
                    ft.Row([
                        ft.ElevatedButton("Сохранить", on_click=update_vacancy),
                        ft.TextButton("Отмена", on_click=lambda e: show_company_vacancies()),
                    ])
                )
        except Exception as e:
            page.add(ft.Text(f"Ошибка: {e}"))
    
    def show_vacancy_responses(vacancy_id):
        page.clean()
        
        page.add(
            ft.Text("Отклики на вакансию", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20, thickness=2),
        )
        
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.get(f"{DJANGO_API_URL}/responses/", headers=headers)
            
            if response.status_code == 200:
                all_responses = response.json()
                vacancy_responses = [r for r in all_responses if r['vacancy'] == vacancy_id]
                
                if not vacancy_responses:
                    page.add(ft.Text("Нет откликов на эту вакансию", italic=True))
                else:
                    for r in vacancy_responses:
                        response_id = r['id']
                        status_dropdown = ft.Dropdown(
                            width=150,
                            value=r['status'],
                            options=[
                                ft.dropdown.Option("pending", "На рассмотрении"),
                                ft.dropdown.Option("viewed", "Просмотрено"),
                                ft.dropdown.Option("invited", "Приглашение"),
                                ft.dropdown.Option("rejected", "Отказ"),
                                ft.dropdown.Option("hired", "Принят"),
                            ]
                        )
                        
                        def update_status(e, rid=response_id):
                            try:
                                new_status = status_dropdown.value
                                headers = {"Authorization": f"Bearer {page.token}"}
                                response = requests.patch(
                                    f"{DJANGO_API_URL}/responses/{rid}/update_status/",
                                    headers=headers,
                                    json={"status": new_status}
                                )
                                if response.status_code == 200:
                                    show_snackbar(page, "Статус обновлен!")
                                    show_vacancy_responses(vacancy_id)
                            except Exception as ex:
                                show_snackbar(page, f"Ошибка: {ex}")
                        
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Студент: {r['student_name']}", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Сопроводительное письмо: {r.get('cover_letter', 'Нет')}"),
                                    ft.Text(f"Дата: {r['created_at'][:10]}"),
                                    ft.Row([status_dropdown, ft.ElevatedButton("Обновить статус", on_click=update_status)]),
                                ], spacing=10),
                                padding=15
                            )
                        )
                        page.add(card)
                
                back_button = ft.TextButton("Назад", on_click=lambda e: show_company_vacancies())
                page.add(back_button)
            else:
                page.add(ft.Text(f"Ошибка загрузки: {response.status_code}"))
        except Exception as e:
            page.add(ft.Text(f"Ошибка: {e}"))
    
    def show_login():
        page.clean()
        
        username_field = ft.TextField(label="Логин", width=300)
        password_field = ft.TextField(label="Пароль", password=True, width=300)
        error_text = ft.Text("", color="red")
        
        def do_login(e):
            try:
                response = requests.post(
                    f"{DJANGO_API_URL}/token/",
                    json={"username": username_field.value, "password": password_field.value}
                )
                
                if response.status_code == 200:
                    page.token = response.json()['access']
                    
                    headers = {"Authorization": f"Bearer {page.token}"}
                    profile_response = requests.get(f"{DJANGO_API_URL}/profile/", headers=headers)
                    
                    if profile_response.status_code == 200:
                        user_data = profile_response.json()
                        page.user_role = user_data.get('role', 'student')
                        page.user_id = user_data.get('id')
                    
                    show_main_menu()
                else:
                    error_text.value = "Неверный логин или пароль"
                    page.update()
            except Exception as ex:
                error_text.value = f"Ошибка подключения: {ex}"
                page.update()
        
        page.add(
            ft.Text("Вход в систему", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(height=30),
            username_field,
            password_field,
            ft.ElevatedButton("Войти", on_click=do_login, width=300),
            error_text,
            ft.TextButton("Нет аккаунта? Зарегистрироваться", on_click=lambda e: show_register())
        )
    
    def show_register():
        page.clean()
        
        username_field = ft.TextField(label="Логин", width=300)
        email_field = ft.TextField(label="Email", width=300)
        password_field = ft.TextField(label="Пароль", password=True, width=300)
        role_dropdown = ft.Dropdown(
            label="Роль",
            width=300,
            options=[
                ft.dropdown.Option("student", "Студент"),
                ft.dropdown.Option("company", "Компания"),
            ]
        )
        company_name_field = ft.TextField(label="Название компании", width=300, visible=False)
        student_group_field = ft.TextField(label="Группа", width=300, visible=False)
        error_text = ft.Text("", color="red")
        
        def on_role_change(e):
            is_company = role_dropdown.value == "company"
            company_name_field.visible = is_company
            student_group_field.visible = not is_company
            page.update()
        
        role_dropdown.on_change = on_role_change
        
        def do_register(e):
            if not username_field.value or not password_field.value:
                error_text.value = "Заполните логин и пароль"
                page.update()
                return
            
            try:
                data = {
                    "username": username_field.value,
                    "email": email_field.value,
                    "password": password_field.value,
                    "role": role_dropdown.value
                }
                
                if role_dropdown.value == "company":
                    data["company_name"] = company_name_field.value or ""
                else:
                    data["student_group"] = student_group_field.value or ""
                
                response = requests.post(f"{DJANGO_API_URL}/register/", json=data)
                
                if response.status_code == 201:
                    show_snackbar(page, "Регистрация успешна! Войдите в систему")
                    show_login()
                else:
                    error_text.value = "Ошибка регистрации. Возможно, логин уже существует"
                    page.update()
            except Exception as ex:
                error_text.value = f"Ошибка: {ex}"
                page.update()
        
        page.add(
            ft.Text("Регистрация", size=28, weight=ft.FontWeight.BOLD),
            ft.Container(height=30),
            username_field,
            email_field,
            password_field,
            role_dropdown,
            company_name_field,
            student_group_field,
            ft.ElevatedButton("Зарегистрироваться", on_click=do_register, width=300),
            error_text,
            ft.TextButton("Уже есть аккаунт? Войти", on_click=lambda e: show_login())
        )
    
    def show_main_menu():
        page.clean()
        
        page.add(
            ft.Text("Сектор практик", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
        )
        
        if page.user_role == "student":
            page.add(
                ft.ElevatedButton("Вакансии", on_click=lambda e: show_vacancies(), width=200, height=50),
                ft.ElevatedButton("Мои отклики", on_click=lambda e: show_my_responses(), width=200, height=50),
            )
        elif page.user_role == "company":
            page.add(
                ft.ElevatedButton("Мои вакансии", on_click=lambda e: show_company_vacancies(), width=200, height=50),
            )
        
        page.add(
            ft.ElevatedButton("Профиль", on_click=lambda e: show_profile(), width=200, height=50),
            ft.ElevatedButton("Выйти", on_click=lambda e: show_login(), width=200, height=50, color="red"),
        )
    
    def show_profile():
        page.clean()
        
        if not page.token:
            show_login()
            return
        
        page.add(
            ft.Text("Профиль", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
        )
        
        try:
            headers = {"Authorization": f"Bearer {page.token}"}
            response = requests.get(f"{DJANGO_API_URL}/profile/", headers=headers)
            
            if response.status_code == 200:
                user = response.json()
                page.add(
                    ft.Text(f"Логин: {user['username']}"),
                    ft.Text(f"Email: {user['email']}"),
                    ft.Text(f"Роль: {user['role']}"),
                )
                if user.get('company_name'):
                    page.add(ft.Text(f"Компания: {user['company_name']}"))
                if user.get('student_group'):
                    page.add(ft.Text(f"Группа: {user['student_group']}"))
                
                page.add(
                    ft.Container(height=20),
                    ft.TextButton("Назад", on_click=lambda e: show_main_menu())
                )
            else:
                page.add(ft.Text("Ошибка загрузки профиля", color="red"))
        except Exception as e:
            page.add(ft.Text(f"Ошибка: {e}"))
    
    show_login()

if __name__ == "__main__":
    ft.app(target=main)
