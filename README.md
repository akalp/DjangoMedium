# DjangoMedium

1. Install postgres in Ubuntu
```bash
sudo apt-get update
sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib
```
2. Access to postgres user and run psql
```bash
sudo su - postgres
psql
```
3. Create db, user and privileges
```sql
CREATE DATABASE djangodb;

CREATE USER djangodbadmin WITH PASSWORD 'dAdmin95';

ALTER ROLE djangodbadmin SET client_encoding TO 'utf8';
ALTER ROLE djangodbadmin SET default_transaction_isolation TO 'read committed';
ALTER ROLE djangodbadmin SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE djangodb TO djangodbadmin;
```
Close psql and leave postgres user
```bash
\q
exit
```
4. Clone project

5. Create virtual environment
```bash
sudo pip install virtualenv
cd ~/DjangoMedium
virtualenv venv
```

6. For Using venv
```bash
source venv/bin/activate
`#use deactive for close to venv`
```

7. Install packages
```bash
pip install django psycopg2-binary pillow
```

8. Make migrations
```bash
python manage.py makemigrations blog
python manage.py migrate
```

9. Create superuser
```bash
python manage.py createsuperuser
```

10. Make migrations, again
```bash
python manage.py makemigrations blog
python manage.py migrate
```
11. Run server
```bash
python manage.py runserver
```
