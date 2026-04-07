# Use an official lightweight Python image
FROM python:3.10-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# Set up our working directory
WORKDIR /app

# Copy our requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our app code
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Run the application using Gunicorn (a production server for Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "app:app"]