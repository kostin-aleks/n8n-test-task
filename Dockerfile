FROM naskio/n8n-python:latest

COPY requirements.txt /data/requirements.txt
COPY .env /data/.env

RUN pip3 install -r /data/requirements.txt

RUN cd /usr/local/lib/node_modules/n8n && npm install n8n-nodes-python
