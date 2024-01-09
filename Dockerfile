FROM python:3.10

WORKDIR /python-docker
COPY requirements.txt requirements.txt
# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
  && apt-get -y update \
  && apt-get install -y google-chrome-stable



# set display port to avoid crash
ENV DISPLAY=:99

ENV PYTHONUNBUFFERED=1

RUN pip install -r requirements.txt

COPY . .


CMD ["gunicorn", "-b", "0.0.0.0:5000", "wsgi:app", "--reload"]