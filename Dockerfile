FROM python:3.12

# Install dependencies
RUN pip install aiohttp aiogram sqlite3 fake_useragent

# Create a directory for the bot
WORKDIR /app
# Copy the bot files into the container
COPY . /app

ENTRYPOINT [ "python3", "main.py" ]