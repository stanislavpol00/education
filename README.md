
# Education


## 1. Local installation

### 1.1 Pre-requisite packages

```
pyenv
virtualenv
```

### 1.2 Install packages

```sh
pyenv virtualenv 3.8.7 education
pyenv activate education
```

Then install application packages

```sh
pip install -r requirements.txt
pip install -r requirements.dev.txt  # for local only
```


### 1.3 Create `education/settings/.env`

```sh
cp education/settings/.env.example education/settings/.env
```

### 1.4 Create local database name and user

```sql
DROP DATABASE IF EXISTS education;

CREATE DATABASE education;

CREATE ROLE education WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE education TO education;
ALTER USER education SUPERUSER;
```

### 1.5 Migrate database

```
python manage.py migrate
```

### 1.6 Create version

```
python manage.py createinitialrevisions
```

### 1.7 Create user

```
python manage.py createsuperuser
```

start the app and you can login directly

```
python manage.py runserver
```

