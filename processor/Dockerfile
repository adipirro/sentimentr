FROM python:3-alpine

COPY . /repo_processor
WORKDIR /repo_processor

RUN pip install -r requirements.txt

CMD ["python","server.py"]
