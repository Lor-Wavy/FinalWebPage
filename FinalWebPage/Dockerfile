# Use the official lightweight Python image as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Cloud Run expects the application to listen on the port specified by the PORT environment variable.
# Gunicorn will handle this automatically, but we expose the port for clarity.
EXPOSE 8080

# Run the production Gunicorn server when the container launches.
# We instruct Gunicorn to run the 'app' Flask application object inside 'app.py'.
# The production server must bind to 0.0.0.0 (all interfaces).
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app