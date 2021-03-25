import os
import sys

import django

sys.path.append(".")   # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")   # noqa
django.setup()   # noqa

from datetime import date, timedelta

from sis.models import Semester

s = Semester(year=2015,
             date_registration_opens=date(2015, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2015, 9, 15) + timedelta(days=0),
             date_last_drop=date(2015, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2015, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2015,
             date_registration_opens=date(2015, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2015, 9, 15) + timedelta(days=90),
             date_last_drop=date(2015, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2015, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2015,
             date_registration_opens=date(2015, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2015, 9, 15) + timedelta(days=180),
             date_last_drop=date(2015, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2015, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2015,
             date_registration_opens=date(2015, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2015, 9, 15) + timedelta(days=270),
             date_last_drop=date(2015, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2015, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2016,
             date_registration_opens=date(2016, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2016, 9, 15) + timedelta(days=0),
             date_last_drop=date(2016, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2016, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2016,
             date_registration_opens=date(2016, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2016, 9, 15) + timedelta(days=90),
             date_last_drop=date(2016, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2016, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2016,
             date_registration_opens=date(2016, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2016, 9, 15) + timedelta(days=180),
             date_last_drop=date(2016, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2016, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2016,
             date_registration_opens=date(2016, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2016, 9, 15) + timedelta(days=270),
             date_last_drop=date(2016, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2016, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2017,
             date_registration_opens=date(2017, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2017, 9, 15) + timedelta(days=0),
             date_last_drop=date(2017, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2017, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2017,
             date_registration_opens=date(2017, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2017, 9, 15) + timedelta(days=90),
             date_last_drop=date(2017, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2017, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2017,
             date_registration_opens=date(2017, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2017, 9, 15) + timedelta(days=180),
             date_last_drop=date(2017, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2017, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2017,
             date_registration_opens=date(2017, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2017, 9, 15) + timedelta(days=270),
             date_last_drop=date(2017, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2017, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2018,
             date_registration_opens=date(2018, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2018, 9, 15) + timedelta(days=0),
             date_last_drop=date(2018, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2018, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2018,
             date_registration_opens=date(2018, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2018, 9, 15) + timedelta(days=90),
             date_last_drop=date(2018, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2018, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2018,
             date_registration_opens=date(2018, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2018, 9, 15) + timedelta(days=180),
             date_last_drop=date(2018, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2018, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2018,
             date_registration_opens=date(2018, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2018, 9, 15) + timedelta(days=270),
             date_last_drop=date(2018, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2018, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2019,
             date_registration_opens=date(2019, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2019, 9, 15) + timedelta(days=0),
             date_last_drop=date(2019, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2019, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2019,
             date_registration_opens=date(2019, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2019, 9, 15) + timedelta(days=90),
             date_last_drop=date(2019, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2019, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2019,
             date_registration_opens=date(2019, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2019, 9, 15) + timedelta(days=180),
             date_last_drop=date(2019, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2019, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2019,
             date_registration_opens=date(2019, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2019, 9, 15) + timedelta(days=270),
             date_last_drop=date(2019, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2019, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2020,
             date_registration_opens=date(2020, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2020, 9, 15) + timedelta(days=0),
             date_last_drop=date(2020, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2020, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2020,
             date_registration_opens=date(2020, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2020, 9, 15) + timedelta(days=90),
             date_last_drop=date(2020, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2020, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2020,
             date_registration_opens=date(2020, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2020, 9, 15) + timedelta(days=180),
             date_last_drop=date(2020, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2020, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
s = Semester(year=2020,
             date_registration_opens=date(2020, 9, 15) + timedelta(days=270) -
             timedelta(days=-60),
             date_started=date(2020, 9, 15) + timedelta(days=270),
             date_last_drop=date(2020, 9, 15) + timedelta(days=270) + timedelta(days=14),
             date_ended=date(2020, 9, 15) + timedelta(days=270) + timedelta(weeks=11),
             semester='SU')
s.save()
s = Semester(year=2021,
             date_registration_opens=date(2021, 9, 15) + timedelta(days=0) - timedelta(days=-60),
             date_started=date(2021, 9, 15) + timedelta(days=0),
             date_last_drop=date(2021, 9, 15) + timedelta(days=0) + timedelta(days=14),
             date_ended=date(2021, 9, 15) + timedelta(days=0) + timedelta(weeks=11),
             semester='FA')
s.save()
s = Semester(year=2021,
             date_registration_opens=date(2021, 9, 15) + timedelta(days=90) - timedelta(days=-60),
             date_started=date(2021, 9, 15) + timedelta(days=90),
             date_last_drop=date(2021, 9, 15) + timedelta(days=90) + timedelta(days=14),
             date_ended=date(2021, 9, 15) + timedelta(days=90) + timedelta(weeks=11),
             semester='WI')
s.save()
s = Semester(year=2021,
             date_registration_opens=date(2021, 9, 15) + timedelta(days=180) -
             timedelta(days=-60),
             date_started=date(2021, 9, 15) + timedelta(days=180),
             date_last_drop=date(2021, 9, 15) + timedelta(days=180) + timedelta(days=14),
             date_ended=date(2021, 9, 15) + timedelta(days=180) + timedelta(weeks=11),
             semester='SP')
s.save()
