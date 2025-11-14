# Базовый образ Python
FROM python:3.9

# Установка рабочей директории
WORKDIR /app

# Копирование файла зависимостей
COPY requirements.txt requirements.txt

# Установка зависимостей
RUN pip install -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Команда для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]