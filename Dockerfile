FROM python:3.11-slim

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "./main.py"]
