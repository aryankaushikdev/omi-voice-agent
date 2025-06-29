FROM python:3.10-slim

WORKDIR /app

# Install ffmpeg and other dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir fastapi uvicorn pydub openai requests python-multipart

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
