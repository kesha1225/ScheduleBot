FROM python:3.9

WORKDIR /schedule_bot

COPY ./poetry.lock ./
COPY ./pyproject.toml ./

RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install

COPY ./schedule_bot/ ./


CMD [ "python", "./__main__.py" ]