# Ingenuity

An open-source tool for learning Latin.

## Install
[virtualenv](https://virtualenv.pypa.io/en/stable/) provides a local install of python, pip, and any installed extensions.
If virtualenv isn't already installed, you may need a user with admin privelidges to install it:

```sh
[sudo] pip install virtualenv
```

Now clone this project:

```sh
git clone https://github.com/merelinguist/ingenuity.git
cd ingenuity
```

To create & use a virtual environment in the project directory:

```sh
virtualenv venv
source venv/bin/activate
```

Then install the project requirements in the created `venv` directory:

```sh
pip install -r requirements.txt
```

Flask requires that an enviroment variable is set to identify the file to run,
and optionally another to enable debugging output:

```sh
export FLASK_APP=ingenuity.py
export FLASK_DEBUG=1
```

You can see your configured environment variables with:

```sh
env
```

You will need to activate venv and set up the environment variables every time you open a new shell.
As a shortcut you can run the following:

```
source setup
```

Finally, initialise the database with:

```
flask db init # (if migrations & db not present)
flask db migrate
flask db upgrade
```

If the DB is not in sync for some reason, you can delete it and the migrations directory
and run the above commands to create an empty database with the current schema.

## Run

To run the app:

```sh
flask run
```

Or, to make the server available to other devices:

```sh
flask run --host=0.0.0.0
```

You will now find the server running on: http://localhost:5000, or for other devices, http://<your_local_ip>:5000

Now you can browse the API:
http://localhost:5000/api/


## Flask extensions used

Function            | Flask-Extension
------------------- | -----------------------
Model & ORM         | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/latest/)
Migration           | [Flaks-Migrate](http://flask-migrate.readthedocs.io/en/latest/)
Forms               | [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)
Login               | [Flask-Login](https://flask-login.readthedocs.org/en/latest/)
Admin               | [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/)

## Other libraries used
CSS | [Bootstrap 4 Alpha](https://v4-alpha.getbootstrap.com/)
JS  | [jQuery](https://jquery.com/)
