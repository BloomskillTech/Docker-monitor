FROM python:3.12-alpine

RUN addgroup -S monitor && adduser -S monitor -G monitor

RUN apk add docker

WORKDIR /home/monitor/backend

COPY  . .

RUN chown -R monitor:monitor /home/monitor/backend

RUN pip install -r requirements.txt

CMD ["python", "main.py"]