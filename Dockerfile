FROM python:3.10.15-slim

WORKDIR /app

COPY ./requirements.txt ./

RUN apt update && apt install -y build-essential default-libmysqlclient-dev g++ gcc git gettext libc-dev libffi-dev make memcached pkg-config python3-psycopg2 python3-dev wget

RUN pip install --upgrade pip
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY ./privateurl ./privateurl
# RUN mkdir -p ./src/logs
# RUN mkdir -p ./src/media

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
