FROM python:latest

WORKDIR /code
COPY . .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

ENTRYPOINT ["bash", "./build.sh"]
