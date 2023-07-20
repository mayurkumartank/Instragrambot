# Use the official Python image as the base image
FROM python:3.9

# Set environment variables for Python buffering and Django settings
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV=production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gettext \
        python3-dev \
        default-libmysqlclient-dev \
        gcc \
        libc-dev \
        libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY ./requirement.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirement.txt

# Copy the Django project files to the container
COPY . .

# Run Django's development server (you can replace "your_project_name" with your actual project name)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
