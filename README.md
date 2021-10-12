## ClickOH Test

### Requirements

It is necessary to have PostgreSQL installed and then to enter to
the PostgreSQL interactive terminal program, execute:

```sh
$ psql postgres
```

Then execute the following commands:

```postgres
=# CREATE USER user_clickoh WITH PASSWORD 'clickoh';
=# ALTER ROLE user_clickoh CREATEDB;
=# CREATE DATABASE clickoh_db;
=# GRANT ALL PRIVILEGES ON DATABASE clickoh_db TO user_clickoh;
```

### Clone repository

```sh
$ git clone https://github.com/eemanuel/clickoh_test.git
```

### Create virtualenv

Above the cloned directory

```sh
$ virtualenv venv
$ source venv/bin/activate
```

### Install requirements

At the same level than manage.py

```sh
$ pip install -r requirements.txt
```

### To run development server inside virtualenv

Make migrations and migrate:

```sh
$ python manage.py makemigrations
$ python manage.py migrate
```

```sh
$ python manage.py runserver
```

### Check in browser the url

```sh
http://localhost:8000/
```

## Endpoints

**Product:**

[POST] [GET] [PUT] [PATCH] [DELETE] /product/

**Order:**

[POST] [GET] [PATCH] [DELETE] /order/orders/

**OrderDetail:**

[POST] [PUT] [PATCH] [DELETE] /order/order-details/
