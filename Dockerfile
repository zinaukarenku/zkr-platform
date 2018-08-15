FROM python:3.7

EXPOSE 8080

ENV PYTHONUNBUFFERED 1
RUN mkdir /srv/platform
WORKDIR /srv/platform

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=5s --timeout=3s CMD curl --fail http://localhost:8080/ || exit 1

CMD ["/bin/sh", "config/start.sh"]