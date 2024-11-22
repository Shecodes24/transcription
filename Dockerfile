 
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 so the app is accessible
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Start the Flask application using gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
