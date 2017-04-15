# Ingenuity

An open-source tool for learning Latin.

See what's next on my [kanban.](https://trello.com/b/NWzloF3z/ingenuity)

## Install
[virtualenv](https://virtualenv.pypa.io/en/stable/) provides a local install of python, pip, and any installed extensions.
If virtualenv isn't already installed, you may need a user with admin privelidges to install it:

```
[sudo] pip install virtualenv
```

Now clone this project:

```
git clone https://github.com/merelinguist/ingenuity.git
cd ingenuity
```

To create & use a virtual environment in the project directory:

```
virtualenv venv
source venv/bin/activate
```

Then install the project requirements in the created `venv` directory:

```
pip install -r requirements.txt
```

Flask requires that an enviroment variable is set to identify the file to run,
and optionally another to enable debugging output:

```
export FLASK_APP=ingenuity.py
export FLASK_DEBUG=1
```

You can see your configured environment variables with:

```
env
```

You will need to activate venv and set up the environment variables every time you open a new shell.
As a shortcut you can run the following:

```
source setup
```

Finally, initialise the database with:

```
flask db upgrade
```

If the DB is not in sync for some reason, you can delete it and the migrations directory
and run the following commands to create an empty database with the current schema:

```
flask db init # (if migrations & db not present)
flask db migrate
flask db upgrade
```

## Run

To run the app:

```
flask run
```

Or, to make the server available to other devices:

```
flask run --host=0.0.0.0
```

You will now find the server running on: http://localhost:5000, or for other devices, http://<your_local_ip>:5000

You can also browse the API at: http://localhost:5000/api/ (Note, most of the API is unused.)

To add an admin user, load data etc, use:

```
python manage.py <command>
```

For a list of commands type:

```
python manage.py
```

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
