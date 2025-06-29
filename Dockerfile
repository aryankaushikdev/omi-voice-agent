FROM python:3.10-slim

# Install ffmpeg and system tools
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy code and install Python dependencies
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
