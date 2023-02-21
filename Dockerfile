FROM python:3.10-slim

WORKDIR /todolist
RUN python -m venv venv
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
CMD python manage.py runserver 0.0.0.0:8000




