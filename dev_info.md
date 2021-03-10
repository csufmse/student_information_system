# Development Information

## Coding Standards

Please follow the posted Google [StyleGuides](https://google.github.io/styleguide/)

## System Architecture
TODO

## Development Environment Instructions
When first jumping into the project you will find the root project settings, urls, and wsgi python files within the config directory. Each app will have its own directory in the root project folder student_info_system. 

In development we will allow Django to use SQLite and runserver to see our code in action. It should already be done in the develop branch but if you notice that running "python manage.py runserver" errors out over one of the lines below, make sure you havethe correct lines commented or uncommented and try again.
In the student-info-system/config/settings.py file:
* Comment  "SECRET_KEY = os.getenv('SECRET_KEY')"
* Comment  "DEBUG = os.getenv('DEBUG')"
* Uncomment    "SECRET_KEY = "(abaz)3wml_wsqh^02#*=47psn=r1!dfx=q9g*cspm(j)5@*$a""
* Uncomment    "DEBUG = True"

### Testing Instructions
(Instructions currently only for Linux as we plan to test on an AWS EC2 instance with Ubuntu installed)
TODO: Figure out how to view the hosted ports over AWS EC2 (ports 81 for Nginx and 8000 for GUnicorn)

To get our testing of production environment running:
In the student-info-system/config/settings.py file:
* Uncomment  "SECRET_KEY = os.getenv('SECRET_KEY')"
* Uncomment  "DEBUG = os.getenv('DEBUG')"
* Comment    "SECRET_KEY = "(abaz)3wml_wsqh^02#*=47psn=r1!dfx=q9g*cspm(j)5@*$a""
* Comment    "DEBUG = True"

Then
* Make sure your current directory is the root folder "student_information_sytem"
* Create a .env file with your secret key and debug variables
* Run: docker-compose up --build
This should build and start two docker containers from the docker-compose.yml and respective Dockerfile in the root folder and the Nginx folder.
One container will run the Student Information System using Django and GUnicorn on port 8000, while the other will run Nginx on port 81. Our settings.py file will use the secret key and debug variables from our .env file. The reason we keep this file out of our git is because the secret key is used for cryptographic signing. Allowing it to be seen would cause secrutiy risks for our application. 

