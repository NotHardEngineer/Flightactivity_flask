FROM python:3.10

WORKDIR /app-dev
COPY requirements.txt requirements.txt
# install google chrome
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get -y update
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb



# set display port to avoid crash
ENV DISPLAY=:99

ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

COPY . .


CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app", "--reload"]