# Are you at home?
*Маленькие дети!<br>*
*Ни за что на свете<br>*
*Не ходите в Африку,<br>*
*В Африку гулять!*


# Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/njituew/home_mil_control.git
cd home_mil_control
```

# Настройка окружения

1. Создайте и активируйте окружение:

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

2. Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

3. В корне проекта есть шаблон для файла окружения, просто скопируйте его и переименуйте в `.env`.

(Linux/macOS):

```bash
cp .env.template .env
```

Заполните переменные окружения.

# Использование

## Администраторы

Для добавления администраторов используйте файл `admins_operations.py`. Инструкция по использованию внутри.

## Запуск

Бот готов к запуску:
```bash
python main.py
```