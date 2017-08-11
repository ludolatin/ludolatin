[![Stories in Ready](https://badge.waffle.io/ludolatin/ludolatin.png?label=ready&title=Ready)](https://waffle.io/ludolatin/ludolatin?utm_source=badge)
# LudoLatin

An open-source tool for learning Latin.

See what's next on my [kanban](https://trello.com/b/NWzloF3z/ludolatin).

Test it out on [ludolatin.com](https://www.ludolatin.com/)


## Install
[virtualenv](https://virtualenv.pypa.io/en/stable/) provides a local install of python, pip, and any installed extensions.
If virtualenv isn't already installed, you may need a user with admin privelidges to install it:

```
[sudo] pip install virtualenv
```

Now clone this project:

```
git clone https://github.com/merelinguist/ludolatin.git
cd ludolatin
```

To create and use a virtual environment in the project directory:

```
virtualenv venv
source venv/bin/activate
```

Then install the project requirements in the created `venv` directory:

```
pip install -r requirements.txt
```

Flask requires that an environment variable is set to identify the file to run,
and optionally another to enable debugging output:

```
export FLASK_APP=ludolatin.py
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

In production you also need to create the following environment variables: 
```
FLASK_ENV=production
DATABASE_USERNAME='<someone>',
DATABASE_PASSWORD='<something>'

```


## Database

You'll need a MySQL database. (Other databases will work with some minor code changes 
(specifically the GROUP BY date SQL queries), but sqlite is not so good with migrations.)

### Database configuration
If you are using mysql 5.7.5 or above, you will need to add a line to your `my.cnf` config file to remove
`ONLY_FULL_GROUP_BY`:

```
sql_mode = "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"
```

If you don't know where that file is, run: 
```
mysqld --verbose --help | grep -A 1 "Default options"
```

then check each location in turn.

The error that you'll see without this is:
```
sqlalchemy.exc.ProgrammingError
ProgrammingError: (mysql.connector.errors.ProgrammingError) 1055 (42000): Expression #1 of ORDER BY clause is not in GROUP BY clause and contains nonaggregated column 'ingenuity_dev.score.created_at' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by [SQL: u'SELECT sum(score.score) AS sum_1 \nFROM score \nWHERE %(param_1)s = score.user_id GROUP BY date_format(score.created_at, %(date_format_1)s) ORDER BY score.created_at DESC \n LIMIT %(param_2)s'] [parameters: {u'date_format_1': '%Y-%m-%d', u'param_1': 18, u'param_2': 7}]
```

To run mysql without starting it at boot, run:
```
mysql.server start
```

Full details on [SitePoint](https://www.sitepoint.com/quick-tip-how-to-permanently-change-sql-mode-in-mysql/).

### Database creation

Now that the database is installed and configured, create a database:

```
mysql -u root -e "CREATE DATABASE ludolatin_dev"
```

Finally, create the migrations and initialise the database with:

```
flask db init
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

You will now find the server running on: `http://localhost:5000`, or for other devices, http://<your_local_ip>:5000

You can also browse the API at: `http://localhost:5000/api/` (Note, most of the API is unused.)

To add an admin user, load data, etc. use:

```
python manage.py <command>
```

For a full list of commands type:

```
python manage.py
```

## Flask extensions used

Function            | Flask-Extension
------------------- | -----------------------
Model & ORM         | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/)
Database migration  | [Flaks-Migrate](http://flask-migrate.readthedocs.io/)
Forms               | [Flask-WTF](https://flask-wtf.readthedocs.io/)
Form validation     | [WTForms](https://wtforms.readthedocs.io/)
Authentication      | [Flask-Login](https://flask-login.readthedocs.org/)
Authorisation       | [Flask-Principal](https://flask-principal.readthedocs.io/)
Admin               | [Flask-Admin](https://flask-admin.readthedocs.io/)
Markdown            | [Flask-Misaka](https://flask-misaka.readthedocs.io/)
Articles            | [Flask-Blogging](https://flask-blogging.readthedocs.io/)
SSL redirection     | [Flask-SSLify](https://github.com/kennethreitz/flask-sslify)
CLI                 | [Flask-Script](https://flask-script.readthedocs.io/)

## Other libraries used

Function | Library
-------- | -------
CSS      | [Bootstrap 4 Alpha](https://v4-alpha.getbootstrap.com/)
JS       | [jQuery](https://jquery.com/)
