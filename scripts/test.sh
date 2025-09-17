#!/bin/bash

# Скрипт для запуска тестов

echo "Запуск тестов..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен."
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не установлен."
    exit 1
fi

# Устанавливаем зависимости для тестирования
echo "Установка зависимостей для тестирования..."
pip3 install -r requirements.txt

# Запускаем тесты
echo "Выполнение тестов..."
python3 -m pytest test_api.py -v

echo "Тесты завершены!"
