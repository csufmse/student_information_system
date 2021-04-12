# Random Test Data

These scripts create plausible test data. 
All database constraints are honored, but some application constraints may not be (but not intentionally).

## Full Rebuild Process

```bash
cd student_information_system
rm db.sqlite3
rm sis/migrations/0*
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --username admin --email admin@x.com
# pass admin1, please!
python sis/test_data/ --create
# this will execute them all
```

***You must run them in ASCENDING order only, which the script does. You have been warned.***

You need not run them all, though. 

The script ```sis/test_data/__main__.py``` keeps you somewhat honest. 
It'll create in ascending order, and delete in descending order.

What are the options for arguments/parameters?
```
python sis/test_data/ -h
```

What are the options for types of data?
```
python sis/test_data/ --list
```

Delete major prerequisites?
```
python sis/test_data/ --delete --only 22
```


Delete courses (and on), then re-create?
```
python sis/test_data/ --delete --start 20
python sis/test_data/ --create --start 20
```

### Not SQLite?

For all the tables, we should have proper delete-cascade constraints in place.
So I **think** (have not tested) you can do the following to clear the db:

```SQL
DELETE FROM auth_user;
DELETE FROM sis_profile;
DELETE FROM sis_student;
DELETE FROM sis_professor;
DELETE FROM sis_admin;
DELETE FROM sis_major;
DELETE FROM sis_semester;
DELETE FROM sis_course;
DELETE FROM sis_message;
```

The models specify constraints so all the join-tables will be cleared by these.

### User accounts (Professor, Student) have passwords set by default

And they're really dumb passwords. If you want to NOT set passwords,
go into ```01_admin.py```, ```04_student.py```, and ```08_professor.py``` and
set the variable ```set_password``` to ```False``` ***before you execute the scripts***. If users are created this way,
they will not be able to log in (despite being "enabled"). **You'll have to set
your test account passwords in ```/siteadmin```**.

Obviously this is much more secure.

### Recommendation, for your convenience

Pick an ```Admin```, and go to ```/siteadmin```, ```User``` table. 
Enable *Staff* status and *Superuser* status. This makes it a user
with which you can hit both ```/schooladmin``` and ```/siteadmin```.

**That said** I haven't used the Admin site for weeks, 
and I don't want to. Any data created there may not honor the app constraints. Use the ```/schooladmin```.


Personally, I use ```hades```.


### Minor Note

the "User" table is ```auth_user```.

## Application constraints NOT honored
* there are some majors with no professors, so those classes cannot be taught.

## So what's that weird weight stuff?

(mostly in Section and SectionStudent)

We have some biases.
1. students prefer to take Major course
2. we get more As than Fs.

