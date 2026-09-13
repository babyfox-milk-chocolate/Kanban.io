# Kanban.io

> Kanban-приложение для управления проектами и задачами

![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.15-A30000?logo=django&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white)


<img width="2559" height="1113" alt="Снимок экрана 2026-09-11 215246" src="https://github.com/user-attachments/assets/7b88e6b0-d840-484e-a6a0-b0daf49d1f44" />

---

## Что внутри 

- **JWT-аутентификация** — регистрация, вход, обновление токена. Авто-refresh при истечении access-токена
- **Проекты и задачи** — организация задач по проектам, изоляция данных: каждый пользователь видит только свои 
- **Kanban-доска** — разделение на Open/In Progress/Done с **drag & drop** и сохранением порядка карточек
- **Живой поиск** по задачам в реальном времени
- **Личный кабинет** — простая статистика, редактирование профиля, смена пароля, **загрузка аватара**

---

## Стек технологий

**Backend:** Django · Django REST Framework · Simple JWT · PostgreSQL · Pillow

**Frontend:** Vue 3 (Composition API) · Vite · Pinia · Vue Router · Axios · Tailwind CSS · vuedraggable

**Инфраструктура:** Docker · Docker Compose - PostgreSQL

---

<img width="2157" height="1307" alt="image" src="https://github.com/user-attachments/assets/1ff86225-5e95-408a-b7f3-54b4963197b8" />

## Структура

```
kanban.io/
├── docker-compose.yml
├── backend/                
│   ├── taskmanager/             
│   ├── users/              
│   └── boards/             
└── frontend/               
    └── src/
        ├── api/            # axios + интерцепторы
        ├── stores/         # Pinia: auth, theme
        ├── router/         # роуты  
        ├── views/          # Login, Register, Board, Profile
        └── components/     
```

## Тестирование
 
API покрыт тестами на `pytest-django`. Основной фокус — **изоляция данных**: проверка, что пользователь не может получить доступ к чужим проектам и задачам (чтение, изменение, удаление), а также что задачу нельзя создать в чужой доске.
 
Что покрыто:
 
- **Аутентификация** — регистрация, хеширование пароля, логин, обновление токена, отказ без токена
- **Изоляция досок** — пользователь видит и меняет только свои проекты (чужие → `404`)
- **Изоляция задач** — запрет на создание задачи в чужой доске (→ `403`)
- **CRUD и валидация** — создание, фильтрация по доске, смена статуса, проставление владельца из токена

Запуск тестов:
 
```bash
docker compose exec backend pytest -v
```

##  Запуск

### 1. Клонируем репозиторий 

```bash
git clone https://github.com/babyfox-milk-chocolate/Kanban.io.git
cd kanban.io
```

### 2. Настраиваем переменные окружения

```env
POSTGRES_DB=kanbanio
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=secret
DEBUG=True
```

### 3. Поднимаем backend + БД

```bash
docker compose up --build
```

Миграции + суперпользователь:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### 4. Фронт

```bash
cd frontend
npm install
npm run dev
```

## Ручки 

| Метод | Эндпоинт | Что делает |
|-------|----------|----------|
| `POST` | `/api/auth/register/` | Регистрация |
| `POST` | `/api/auth/login/` | Вход (возвращает пару access и refresh) |
| `POST` | `/api/auth/refresh/` | Обновление access-токена |
| `GET/PATCH` | `/api/auth/profile/` | Профиль + статистика |
| `POST` | `/api/auth/change-password/` | Смена пароля |
| `POST` | `/api/auth/avatar/` | Загрузка аватара |
| `GET/POST` | `/api/boards/` | Список / создание проектов |
| `GET/POST` | `/api/tasks/` | Список / создание задач |
| `POST` | `/api/tasks/reorder/` | Сохранение порядка задач |