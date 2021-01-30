FROM python:3.7-alpine
ADD exporter.py /
RUN pip3 install prometheus_client && pip3 install requests
CMD [ "python3", "-u", "./exporter.py" ]
