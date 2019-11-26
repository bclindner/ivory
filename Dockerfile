FROM python:3.7.4

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN python -m pytest -s tests/

CMD ["python", "."]
