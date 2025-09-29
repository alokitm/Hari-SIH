# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose the port that Railway will use
EXPOSE 8501

# Command to run the application
CMD ["./start.sh"]