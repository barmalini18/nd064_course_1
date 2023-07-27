FROM python:3.8
LABEL maintainer="Taras Bahnyuk"

WORKDIR /app
COPY . /app

# install app requirements
RUN pip install -r requirements.txt

# initialize the database
RUN python init_db.py

# command to run on container start
EXPOSE 3111
CMD [ "python", "app.py" ]
