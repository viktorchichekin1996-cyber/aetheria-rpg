# Базовый образ Node.js 18
FROM node:18-alpine

# Рабочая директория в контейнере
WORKDIR /app

# Копирование package.json
COPY package.json .

# Установка зависимостей
RUN npm install

# Копирование исходного кода
COPY . .

# Порт для React dev сервера
EXPOSE 3000

# Команда запуска dev сервера
CMD ["npm", "start"]