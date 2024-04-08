FROM python:3.12.2-slim

WORKDIR /app

COPY ./requirements.txt ./main.py ./config.json 

RUN pip install -r ./requirements.txt

CMD ["python", "main.py"]