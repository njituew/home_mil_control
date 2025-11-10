# Are you at home?
*Маленькие дети!<br>*
*Ни за что на свете<br>*
*Не ходите в Африку,<br>*
*В Африку гулять!*


## Установка
1. Клонируйте репозиторий:
```bash
git clone https://github.com/njituew/home_mil_control.git
cd home_mil_control
```
2. Создайте и активируйте окружение:
```bash
python -m venv venv
```
macOS/Linux:
```bash
source venv/bin/activate
```
Windows:
```bash
venv\Scripts\activate
```
3. Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```


## Настройка окружения
1. В корне проекта есть шаблон для файла окружения, просто скопируйте его и переименуйте в `.env`.

(Linux/macOS):
```bash
cp .env.template .env
```
Добавьте токен своего бота в переменную `BOT_TOKEN`.

2. В корне проекта создайте файл `admins.json`, добавьте туда telegram id админов в формате:
```json
{
    "admins": [
        {"chat_id": 100000000},
        {"chat_id": 200000000},
        ...
    ]
}
```

## Запуск
Бот готов к запуску:
```bash
python main.py
```