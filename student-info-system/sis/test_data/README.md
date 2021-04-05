# Random Test Data

These scripts create plausible test data. 
All database constraints are honored, but some application constraints may not be.

## Full Rebuild Process

```bash
cd student_information_system
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# admin with pass admin1, please!
python sis/test_data/01_major.py
# ... and so on, by number
```

***You must run them in ASCENDING order only. You have been warned.***

You need not run them all though. 

### Not SQLite?

For all the tables, we should have proper delete-cascade constraints in place.
So I **think** (have not tested) you can do the following to clear the db:

```SQL
DELETE FROM auth_user;
DELETE FROM sis_student;
DELETE FROM sis_professor;
DELETE FROM sis_admin;
DELETE FROM sis_major;
DELETE FROM sis_semester;
DELETE FROM sis_course;
```

The models specify constraints so all the join-tables will be cleared by these.

### User accounts (Admin, Professor, Student) have passwords set by default

And they're really dumb passwords. If you want to NOT set passwords,
go into ```01_admin.py```, ```04_student.py```, and ```08_professor.py``` and
set the variable ```set_password``` to ```False``` ***before you execute the scripts***. If users are created this way,
they will not be able to log in (despite being "enabled"). **You'll have to set
your test account passwords in ```/siteadmin```**.

Obviously this is much more secure.

### Recommendation, for your convenience

Pick an ```Admin```, and go to ```/siteadmin```, ```User``` table. 
Enable *Staff* status and *Superuser* status. This makes it a user
with which you can hit both ```/schooladming``` and ```/siteadmin```.

Personally, I use Hades.

## Partial, or adding data

You can run the following only once:
* major
* admin
* semester 
You can tweak things, and perhaps rerun to get more data:
* student (this also creates semester students)
* professor
* course

You can tweak and run to get more (easily):
* major prerequisites
* course prerequisites
* section
* section students

The "only once" scripts have hard-coded data. The other ones either 
take from a list (Student, Prof, Course), or generate random data (no hard-coded lists).

## Clearing some data out

Assuming you're messing around in your dev area and are in a hurry, 
you can delete some of the data by hand without rebuilding everything.

**Do a clean run of data and test before you check anything in!**

Say you want to reset the sections:
```bash
sqlite3 db.sqlite3
delete from sis_section;
# you must then delete the other data (since sqlite3 does not cascade
delete from sis_sectionstudent;
```
Then you can run the ```section``` and ```sectionstudent``` scripts.

### Minor Note

the "User" table is ```auth_user```.

## Application constraints NOT honored
* ```Section``` may be added to "old" ```Semester``` even with statuses 
like ```Open```.
  * Properly, old semester section should all be closed, etc.
* Section status ```Grading``` and ```Graded``` are not at all correct.
  * they do not reflect all SectionStudents, etc.
    
* there are some majors with no professors, so those classes cannot be taught.

## So what's that weird list stuff?

(mostly in Section and SectionStudent)

```python
statuses = (SectionStudent.REGISTERED,) * 20 + \
        (SectionStudent.AWAITING_GRADE) * 3 + \
        (SectionStudent.GRADED,) * 50 + \
        (SectionStudent.DROP_REQUESTED,) * 3 + \
        (SectionStudent.DROPPED,) * 1

# no grade inflation here :-/
grades = (0,) * 2 + (1,) * 2 + (2,) * 4 + (3,) * 4 + (4,) * 5

```
This is used to simulate a rondel with different probabilities. Feel free to
adjust the multipliers to get the composition you want. 

The latter example biases towards As and Bs.

