# Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN mkdir -p /app/instance
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod -R 777 /app/instance

ENV FLASK_ENV=production
ENV FLASK_APP=app.py

EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]