# Start from base image with Python 3.8
FROM python:3.10

# Setup env 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#  Set working directory
WORKDIR /app
COPY Pipfile Pipfile.lock /app/

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy --ignore-pipfile

COPY . /app/