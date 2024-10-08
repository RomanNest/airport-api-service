FROM python:3.12.5-alpine
LABEL maintainer="rom.puh@gmail.com"

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
         --disabled-password \
         --no-create-home \
         django-user

RUN mkdir -p /vol/web/media
RUN chown -R django-user:django-user /vol/
RUN chmod -R 755 /vol/web/

USER django-user
