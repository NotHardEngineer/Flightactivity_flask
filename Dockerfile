FROM python:3.10

WORKDIR /python-docker
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
CMD ["flask", "db", "migrate"]
CMD ["flask", "db", "upgrade"]
CMD ["flask", "run", "--host=0.0.0.0"]