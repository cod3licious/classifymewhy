FROM python:3.10.8-slim-bullseye

WORKDIR /code

RUN pip install --default-timeout=200 --upgrade pip==22.3.1 && \
    pip install pipenv==2022.11.11

COPY Pipfile Pipfile.lock /code

RUN pipenv install

COPY ./src /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
