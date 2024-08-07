# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get -y install gcc postgresql \
    && apt-get clean

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy project
COPY . /app/

# Debug information
RUN echo "PYTHONPATH is set to $PYTHONPATH" \
    && echo "Contents of /app:" \
    && ls /app \
    && echo "Contents of /app/app:" \
    && ls /app/app \
    && echo "Contents of /app/tests:" \
    && ls /app/tests

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
