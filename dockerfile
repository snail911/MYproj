FROM python:3.10
RUN apt update
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
RUN pip install -r requirements.txt
CMD ["python", "recognizer/manage.py", "runserver", "0.0.0.0:8000"]