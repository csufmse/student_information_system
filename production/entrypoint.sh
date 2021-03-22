#!/bin/sh

GITHUB_TEST=false

# Make postgres user not need a password
sed -i -e '/postgres/s/peer/trust/' '/etc/postgresql/12/main/pg_hba.conf'

# Start postgres, create a db, and set up our db user
pg_ctlcluster 12 main start
su postgres -c "psql -c 'CREATE DATABASE $DB_NAME' postgres"

su postgres -c ../postgres_cmd.sh &&

# Set up our app and run our python tests
python3 manage.py migrate --no-input &&
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@noemail.com', '$DB_PASSWORD')" | python3 manage.py shell &&
python3 manage.py collectstatic --no-input &&
python3 manage.py test &&

# If we're in a workflow we dont run gunicorn
if $GITHUB_TEST == "True" ; then
    echo "All is well if you've made it this far";
else gunicorn config.wsgi:application --bind 0.0.0.0:8000;
fi
