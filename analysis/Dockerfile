FROM python:2-alpine

COPY . /sentiment-server
WORKDIR /sentiment-server

RUN mv nltk_data /root/nltk_data && \
    pip install -r requirements.txt && \
    python -m textblob.download_corpora

EXPOSE 5000

CMD ["python","server.py"]
