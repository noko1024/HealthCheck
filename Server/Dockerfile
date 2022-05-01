FROM python:3

COPY ./* /Server/
WORKDIR /Server

RUN pip install -r requirements.txt

CMD ["python3","./HealthCheck.py"]