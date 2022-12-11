FROM python:3.10.8-slim-bullseye

ENV LANG C.UTF-8
ENV PYTHONPATH $PYTHONPATH:/code
ENV PATH="/root/.local/bin:${PATH}"
ENV PIP_NO_CACHE_DIR false

WORKDIR /code

RUN pip install --default-timeout=200 --upgrade pip==22.3.1 && \
    pip install pipenv==2022.11.11

COPY Pipfile Pipfile.lock /code

RUN pipenv install --deploy --system --pre

COPY ./src /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "info"]
