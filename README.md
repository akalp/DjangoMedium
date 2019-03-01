# DjangoMedium For BBM473 Course

1. Install postgres in Ubuntu
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-dev libpq-dev postgresql postgresql-contrib
```

2. Start the server
```bash
sudo systemctl start postgresql
```

3. Access to postgres user and run psql
```bash
sudo su - postgres
psql
```
4. Create db, user and privileges
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
5. Extract the project zip.

6. Create virtual environment
```bash
sudo pip3 install virtualenv
cd ~/DjangoMedium
virtualenv venv
```

7. For Using venv
```bash
source venv/bin/activate
`#use deactivate for close to venv`
```

8. Install packages
```bash
pip install django psycopg2-binary pillow
```

9. Make migrations
```bash
python manage.py makemigrations blog
python manage.py migrate
```

10. Create superuser
```bash
python manage.py createsuperuser
```

11. Make migrations, again
```bash
python manage.py makemigrations blog
python manage.py migrate
```

12. Connect to database with created user on terminal
```bash
sudo su postgres -l
psql -d djangodb -U djangodbadmin
```
if psql -d djangodb -U djangodbadmin is not run, please use psql djangodbadmin  -h 127.0.0.1 -d djangodb
password is dAdmin95

13. Create sequences, functions, triggers and view
```sql
CREATE SEQUENCE blog_postreport_id_seq START WITH 1;

CREATE OR REPLACE FUNCTION postreport_id_inc_trigger()
RETURNS TRIGGER AS $TRIGGER$
BEGIN
  SELECT nextval('blog_postreport_id_seq')
  INTO NEW."id";
RETURN NEW;
END;
 $TRIGGER$ LANGUAGE plpgsql;

CREATE TRIGGER postreport_id_trig BEFORE INSERT
ON blog_postreport FOR EACH ROW
EXECUTE PROCEDURE postreport_id_inc_trigger();
```
```sql
CREATE SEQUENCE blog_userreport_id_seq START WITH 1;

CREATE OR REPLACE FUNCTION userreport_id_inc_trigger()
RETURNS TRIGGER AS $TRIGGER$
BEGIN
  SELECT nextval('blog_userreport_id_seq')
  INTO NEW."id";
RETURN NEW;
END;
 $TRIGGER$ LANGUAGE plpgsql;

CREATE TRIGGER userreport_id_trig BEFORE INSERT
ON blog_userreport FOR EACH ROW
EXECUTE PROCEDURE userreport_id_inc_trigger();
```
```sql
CREATE SEQUENCE blog_reporttype_id_seq START WITH 1;

CREATE OR REPLACE FUNCTION reporttype_id_inc_trigger()
RETURNS TRIGGER AS $TRIGGER$
BEGIN
  SELECT nextval('blog_reporttype_id_seq')
  INTO NEW."id";
RETURN NEW;
END;
 $TRIGGER$ LANGUAGE plpgsql;

CREATE TRIGGER reporttype_id_trig BEFORE INSERT
ON blog_reporttype FOR EACH ROW
EXECUTE PROCEDURE reporttype_id_inc_trigger();
```
```sql
create or replace procedure insert_reporttype(val varchar(250)) as $$ 
 begin
 insert into blog_reporttype (type) values (val); 
 end; 
$$ language plpgsql;
```
```sql
create view publicationposts as 
 SELECT count(post_id) as count 
 FROM blog_publication, blog_publicationpost 
 WHERE blog_publication.id=blog_publicationpost.publication_id 
 GROUP BY blog_publication.id;
```

14. Close psql and leave djangodbadmin user
```bash
\q
exit
```

15. Run server
```bash
python manage.py runserver
```

16. Connect to admin panel
127.0.0.1:8000/admin

17. Add report types one by one.

18. Add topics one by one.
