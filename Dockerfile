FROM python:3.11

WORKDIR /code
RUN apt update && apt install -y libx11-dev libgl-dev
RUN pip install poetry 
COPY . /code/
RUN poetry install
CMD poetry run python main.py