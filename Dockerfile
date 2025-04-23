FROM python:3.12.10-slim-bullseye
WORKDIR /usr/local/tposts
ENV PYTHONPATH=src

COPY . .

RUN python -m venv ../poetry
RUN ../poetry/bin/pip install -U pip setuptools
RUN ../poetry/bin/pip install poetry==1.8
RUN ln -s ../poetry/bin/poetry ../bin/poetry

ARG ENV
RUN chmod +x /usr/local/tposts/entrypoint.$ENV.sh
RUN echo "Running"

