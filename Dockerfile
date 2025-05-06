FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только файл зависимостей для кэширования слоёв
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip --no-cache-dir && \
    /venv/bin/pip install -r requirements.txt --no-cache-dir

# Копируем остальные файлы проекта
COPY . /app

# Указываем переменные окружения
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=appcore.settings

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска приложения
CMD ["python", "appcore/manage.py", "runserver", "0.0.0.0:8000"]