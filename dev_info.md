# Development Information

## Coding Standards

Please follow the posted Google [StyleGuides](https://google.github.io/styleguide/)

## System Architecture
TODO

## Development Environment Instructions
TODO

### Testing Instructions
(Instructions currently only for Linux as we plan to test on an AWS EC2 instance with Ubuntu installed)
TODO: Figure out how to view the hosted ports over AWS EC2 (ports 81 for Nginx and 8000 for GUnicorn)
To get our testing of production environment running:
In the student-info-system/config/settings.py file:
* Uncomment  "SECRET_KEY = os.getenv('SECRET_KEY')"
* Uncomment  "DEBUG = os.getenv('DEBUG')"
* Comment "SECRET_KEY = "(abaz)3wml_wsqh^02#*=47psn=r1!dfx=q9g*cspm(j)5@*$a""
* Comment "DEBUG = True"

Then
* Make sure your current directory is the root folder "student_information_sytem"
* Run: docker-compose up --build
This should build and start two docker containers from the docker-compose.yml and respective Dockerfile in the root folder and the Nginx folder.
One container will run the Student Information System using Django and GUnicorn on port 8000, while the other will run Nginx on port 81.

