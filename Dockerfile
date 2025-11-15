FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py .
COPY database.py .

# Create directory for database
RUN mkdir -p /data

# Set environment variable for database location
ENV DATABASE_PATH=/data/bot_data.db

# Run the bot
CMD ["python", "-u", "bot.py"]
