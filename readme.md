# AFORMS Web

A-FORMS Web - это многопользовательский сервис для использования системы анализа и оптимизации авиационных конструкций AFORMS.

## Установка и развертывание

Для работы сервиса необходимо наличие установленной субд PostgresQL, решателя FEMAP Nastran.

Для установки из репозитория:

1. Клонируете репозиторий
```bash
git clone -b master https://github.com/hmcdl/aformes_web.git
```

2. Создаете виртуальное окружение для Python версии >=3.10. [дока](https://docs.python.org/3/library/venv.html "документация по venv")
```bash
<path/to/python.exe> -m venv venv
```
<path/to/python.exe> - путь к интерпретатору (по дефолту "c:\Users\Mikhail\AppData\Local\Programs\Python\Python3X\python.exe" где Х - версия Питона), venv - модуль для создания виртуального окружения, аргумент venv создает папку "venv"

Активируем (Windows):
```bash
.\venv\Scripts\activate
```
3. установка зависимостей
```bash
pip install -r requirements.txt
```

3. Установка своих секретных данных
 В той же директории создаем файл secret_data.py
В него:
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
DATABASE_NAME = "simulations_db"
DATABASE_PORT = 5432
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
DATABASE_PASSWORD = 123456
Меняем SECRET_KEY, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_PORT на акуальные. 
4. Задаем настройки в globals.py !!!Использовать прямые слэши!!!
Все эти данные задаются в соответствии с требованиями для запуска консольного приложения
sim_dir - Папка, где будут храниться проекты пользователей. !!!Вне репозитория!!!
"console_path" - путь к консольному приложению AFORMS
"solver" - путь к Фемапу
"PythonPath" - путь к интерпретатору питона, который используется в консольном приложении AFORMS. Можно задать тот же, что и при создании виртуального окружения
"optimizer_path" - путь к оптимизатору панелей
"panelcm" - путь к решателю Фомина
"materials" - путь к БД материалов
5. Создаем базу данных. Создание базы с пустыми таблицами производится из .sql файла в корне репозитория. Один из способов это сделать:
Открываем pgAdmin. Создаем сервер. В сервере создаем БД. В бд заходим в query tools, туда вставляем содержимое .sql файла и воспроизводим.

Готово, осталось только запустить. В той же директории:
```bash
uvicorn app.main:app
```
## Использование
Документация в браузере (работает только когда сервер включен): 
http://127.0.0.1:8000/docs 
Создание новых пользователей пока только через автодок (/users/Create User)
Использование приложения совместно с [aforms_web_client](https://docs.python.org/3/library/venv.html "документация по venv")