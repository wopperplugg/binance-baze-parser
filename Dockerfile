# === STAGE 1: Build frontend ===
FROM node:24-alpine AS frontend_builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем весь frontend-код (кроме node_modules)
COPY . .

# Собираем frontend
# Предполагаем, что сборка должна вывести файлы в coins/static/
RUN npm run build

RUN echo "--- Debugging STAGE 1 file locations ---"
RUN ls -l coins/static/dist/
RUN pwd
RUN echo "----------------------------------------"

# === STAGE 2: Build backend ===
FROM python:3.12-slim AS backend

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .
# Обновляем pip и проверяем версию
RUN pip install --upgrade pip && \
    pip --version
# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=frontend_builder /app/coins/static/dist /app/coins/static/dist
# Копируем весь Django-проект (включая manage.py, binance_parser/, coins/, и т.д.)
COPY . .


# Устанавливаем переменную окружения (если нужно)
ENV DJANGO_SETTINGS_MODULE=binance_parser.settings

# Запускаем сервер (для разработки)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]