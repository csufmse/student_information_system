FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Get system up to date
RUN apt-get update && apt-get -y upgrade

# Install initial Python needs (python3, pip)
RUN apt-get install -y python3 python3-pip

# Install PostgreSQL dependencies
RUN apt-get install -y libpq-dev

RUN apt-get install -y postgresql-12 postgresql-contrib

# Install python packages
COPY ./production/requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Make sure this matches the django project root folder
COPY /student-info-system /student-info-system

WORKDIR /student-info-system

COPY ./production/postgres_cmd.sh ./production/entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

