# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the code to the working directory
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
