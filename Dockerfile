FROM python:3.7

RUN apt-get update && apt-get install -y \
  tidy

EXPOSE 8080

ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/platform
WORKDIR /srv/platform

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/sh", "config/start.sh"]