FROM ubuntu:20.04

# Get system up to date
RUN apt-get update && apt-get -y upgrade

# Install initial Python needs (python3, pip, virtualenv)
RUN apt-get install -y python3 python3-pip && \
    python3 -m pip install virtualenv

# Install PostgreSQL dependencies
#RUN apt-get install -y libpq-dev python-dev && \
#    apt-get install postgresql postgresql-contrib

# Install python packages
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Make sure this matches the django project root folder
COPY ./student-info-system /student-info-system

WORKDIR /student-info-system

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

