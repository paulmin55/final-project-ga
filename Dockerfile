FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "python" ]
CMD ["-m", "flask", "run", "--host", "0.0.0.0"]
EXPOSE 5000