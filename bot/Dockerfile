FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.14.2-slim-bookworm

WORKDIR /app/bot

# Копируем файлы зависимостей и код
COPY pyproject.toml ./
COPY bot/ .

# Устанавливаем зависимости через pip (так как uv требует дополнительных манипуляций)
RUN pip install --no-cache-dir python-telegram-bot openai requests python-dotenv

CMD ["python", "bot.py"]
