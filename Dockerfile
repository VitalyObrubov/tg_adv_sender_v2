# Docker-команда FROM указывает базовый образ контейнера
# базовый образ - это Linux с предустановленным python-3.9
FROM python:3.10-slim
# Скопируем файл с зависимостями в контейнер
COPY requirements.txt .
# Установим зависимости внутри контейнера
RUN pip3 install -r requirements.txt
# Скопируем остальные файлы в контейнер
COPY . .
# запускаем скрипт
CMD ["python", "./bot_manager.py"]
