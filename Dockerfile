FROM python:alpine3.10

RUN apk add --no-cache mariadb-dev build-base libffi-dev  # Ajout de libffi-dev

WORKDIR /app
COPY . /app
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python ./run.py

