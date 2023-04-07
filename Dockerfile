FROM python:3.10.6
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn -b 0.0.0.0:80 index:server