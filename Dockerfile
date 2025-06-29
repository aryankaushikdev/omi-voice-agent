FROM python:3.10-slim

# Install ffmpeg and update system
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydub openai requests python-multipart

# Expose port for Railway
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
