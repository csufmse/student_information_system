# Development Information

## Coding Standards

Please follow the posted Google [StyleGuides](https://google.github.io/styleguide/)

## System Architecture
Our project uses Django, with GUnicorn as our WSGI application and Nginx as our server.
There are 4 apps:
* sis = our common app where shared resources go
* student
* professor
* schooladmin

## Development Environment Instructions
When first jumping into the project you will find the root project settings, urls, and wsgi python files within the config directory. Each app will have its own directory in the root project folder student_info_system. 

In order to run the project you'll want to make sure that if you have a ".env" file it contains 
* PRODUCTION=False

In development we will allow Django to use SQLite and runserver to see our code in action.

### Testing Instructions
(Instructions currently only for Linux as we plan to test on an AWS EC2 instance with Ubuntu installed)
TODO: Figure out how to view the hosted ports over AWS EC2 (ports 81 for Nginx and 8000 for GUnicorn)

To get our testing of production environment running:
* Download the project from githib to your AWS EC2 instance
* Create a .env file with 
  * PRODUCTION=True
  * DEBUG=False
  * SECRET_KEY='secret_key'
  * And the database varaiables and their respective values
    * DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
* Then run (Note. --build is only needed if it hasn't already been built before)
  * docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

This should build and start two docker containers from the docker-compose.yml/prod.yml and respective Dockerfile in the root folder and the Nginx folder.
One container will run the Student Information System using Django and GUnicorn on port 8000, while the other will run Nginx on port 81. Our settings.py file will use the secret key and debug variables from our .env file. The reason we keep this file out of our git is because the secret key is used for cryptographic signing. Allowing it to be seen would cause security risks for our application.

