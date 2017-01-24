FROM python:3-alpine

COPY . /analysis-server
WORKDIR /analysis-server

RUN mv nltk_data /root/nltk_data && \
    pip install -r requirements.txt && \
    python -m textblob.download_corpora

EXPOSE 5000

CMD ["python","server.py"]
