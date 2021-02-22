# Student Information System

CSPC 546 Assignment: Student Information System

## Project Objective
The objective of this project is to build an online Student Information System that allows students, professors and administrative staff to manage courses, schedules and records at California State University Fullerton. This project will be conducted using an agile development methodology.

## Project Scope
The scope project is to build the online Student Information System to be accessed by Students, Professors and Administrators only via their PCs.

The major features of the system include\
FE-1: Allow access to the system for specific users via a PC.\
FE-2: Create, view, modify, request and delete classes and class schedules.\
FE-3: Manage student’s access to adding classes including availability per section and prerequisites standings.\
FE-4: Ability to view and add grades for previous courses.\
FE-5: Grant and remove system access and passwords.\
FE-6: The ability to remove students from classes.\
FE-7: The ability to request and view transcripts.\
FE-8: The ability to drop a course within a predefined date range or ad hoc.\
FE-9: Grant access to different features on the system depending on the type of user.\
FE-10: Ability to add course descriptions and group courses by major.\
FE-11: Ability to run a report that provides a student's status for degree completion.\

## Scope of Releases
The first releasable version is the minimum viable product and will include the features listed above. All additional features will be added in subsequent releases.The scope of each iteration will be defined by the selected user stories from the backlog based on their priority and the team’s capacity.

## Limitations:
LI-1: The StudentInformation System is only available for Students, Professors and Administration at California State University Fullerton.\
LI-2: The features of Student Information System are available depending on the type of user that is in the system. All features will not be available to all users.\

## Project Tasks
The Student Information System shall allow each of the following user types and their respective actions.
Students:
* log into the system via their PC
* request classes (enforce prereqs)
* display # of openings (>= 0) of all sections of a course
* select one of the open sections
* drop courses (before 2nd week)
* display current schedule and previous history (courses taken and grades)

Professors:
* log into the system via their PCs
* display entire roll for given class or schedule of given student
* display history of classes a student
* drop students from class
* enter grades for students

Administrative:
* log into the system via their PCs
* enter new students and professors into the system, and assign passwords.
* remove student and professor authorizations (student histories are retained)
* enter class schedule for a semester
* enter descriptions of new courses (including prerequisites)
* enter list of courses for degree majors
* Request student transcript (courses taken + grades earned)

System:
* updates student grade levels—(freshman - senior) dependent on units completed
* perform graduation checks (check courses completed against major)
* enforce prerequisites and not allow a student to enroll in a class for which he hasn’t taken the required previous course or courses
* produce student transcripts, lists of courses taken and grades earned on request by an administrator

See [Development Information](dev_info.md) for more information.
