FROM python:3.10-slim

# ARG MODE=dev
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./src /app/src
COPY ./.env /app

RUN mkdir src 
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install poetry

# Copy only the necessary files for dependency installation

# Install project dependencies
RUN cd src && poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the application code

EXPOSE 8000

# Set the command based on the build mode
CMD if [ "$MODE" = "dev" ]; then \
        python -m chainlit run app.py -d --port 8000 --host 0.0.0.0 --watch; \
    else \
        python -m chainlit run app.py --port 8000 --host 0.0.0.0; \
    fi
