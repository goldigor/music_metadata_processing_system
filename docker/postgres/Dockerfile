FROM python:3.9

EXPOSE 8000

ADD . /opt/

WORKDIR /opt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "music_processing_api.main:app", "--reload", "--host", "127.0.0.1"]