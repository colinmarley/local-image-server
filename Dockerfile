FROM python:3-slim-buster

RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py upload_images.py /code/

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8082"]
