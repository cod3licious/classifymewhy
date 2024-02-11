FROM python:3.11.8-slim-bullseye

ENV LANG C.UTF-8
ENV PYTHONPATH $PYTHONPATH:/code
ENV PATH="/root/.local/bin:${PATH}"
ENV PIP_NO_CACHE_DIR false

WORKDIR /code

RUN pip install --default-timeout=200 --upgrade pip==23.3.2 && \
    pip install poetry==1.7.1

COPY pyproject.toml poetry.lock /code/

RUN poetry install --no-root

COPY ./src /code/src

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080", "--log-level", "info"]
