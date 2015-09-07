FROM ubuntu:14.04

# Upgrade OS and install dependencies
RUN apt-get update; \
    apt-get install -y \
            git \
            libpq-dev \
            python-dev \
            python-pip

# Without this requirements.txt breaks pip
RUN pip install -U pip
RUN pip install -U gunicorn

RUN mkdir /code
WORKDIR /code

# Install python app requirements
ADD requirements.txt /code/requirements.txt

# Make sure unrevisioned installs are added after cache buster
RUN pip install -Ur requirements.txt

# Copy the code (cache buster)
ADD . /code

EXPOSE 8000

CMD ["gunicorn", "--access-logfile=-", "--error-logfile=-", \
     "--bind=0.0.0.0:8000", "--workers=6", "--timeout=120", \
     "--reload app:create_app()"]
