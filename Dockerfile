FROM python:3

#google chrome install
ARG CHROME_VERSION=105.0.5195.125-1
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get update -qqy
RUN apt install -y /tmp/chrome.deb
RUN rm /tmp/chrome.deb

RUN mkdir -p /app
WORKDIR /app

#copying chromedriver from host
ADD chromedriver/stable/ /app/chromedriver/stable/
ADD requirements.txt /app

RUN pip install --upgrade pip \
&& pip install -r /app/requirements.txt

ADD run.py /app
RUN google-chrome --version
RUN chmod +x run.py

CMD ["python", "/app/run.py"]
