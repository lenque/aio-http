FROM python:3.7
COPY . /app
RUN pip install -r /app/requirements.txt && pip install gunicorn
WORKDIR /app/aio
EXPOSE 8081
CMD gunicorn app:app --bind 0.0.0.0:8081 --worker-class aiohttp.GunicornWebWorker
# CMD python /app/aio/app.py