# syntax=docker/dockerfile:1
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add --no-cache \
    # Required for installing/upgrading postgres, Pillow, etc:
    gcc python3-dev \
    # Required for installing/upgrading postgres:
    postgresql-libs postgresql-dev musl-dev

# Set work directory
RUN mkdir /code
WORKDIR /code

# Install dependencies into a virtualenv
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project code
COPY . /code/