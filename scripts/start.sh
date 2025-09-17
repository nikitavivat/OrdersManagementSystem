#!/bin/bash

# Скрипт для запуска системы заказов

echo "Запуск системы заказов..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Запускаем контейнеры
echo "Запуск контейнеров..."
docker-compose up -d

# Ждем запуска базы данных
echo "Ожидание запуска базы данных..."
sleep 10

# Проверяем статус контейнеров
echo "Статус контейнеров:"
docker-compose ps

echo ""
echo "Система запущена!"
echo ""
echo "Доступные сервисы:"
echo "   API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   pgAdmin: http://localhost:8080"
echo ""
echo "Учетные данные для pgAdmin:"
echo "   Email: admin@orders.com"
echo "   Пароль: admin"
echo ""
echo "Для остановки системы выполните: ./scripts/stop.sh"
