# Ingenuity

An open-source tool for learning Latin.

## Install

### Python

You'll need a working install of python and pip. OSX comes with pything, but without pip.
Either run `sudo easy_install pip` or install the latest from https://www.python.org/downloads/ (admin privelidges needed in either case).

### virtualenv

[virtualenv](https://virtualenv.pypa.io/en/stable/) provides a local install of python, pip, and any installed extensions.
If virtualenv isn't already installed, you may need a user with admin privelidges to install it:

```sh
[sudo] pip install virtualenv
```

### Ingenuity

Now fork this project on github and clone your fork to your local machine:

```sh
git clone https://github.com/<merelinguist>your_git_username/ingenuity.git
cd ingenuity
```

If you wish to keep your fork up-to-date with this repo, or check out branches from here other  than `master`,
you'll need to set this repo as your upstream:

```sh
git remote set upstream https://github.com/merelinguist/ingenuity.git
```

### Requirements

To create & use a virtual environment in the project directory:

```sh
virtualenv venv
source venv/bin/activate
```

Then install the project requirements in the created `venv` directory:

```sh
pip install -r requirements.txt
```

## Configure

Flask requires that an enviroment variable is set to identify the file to run,
and optionally another to enable debugging output:

```sh
export FLASK_APP=ingenuity.py
export FLASK_DEBUG=1

You can see your configured environment variables with:

```sh
env
```

Finally, initialise the database with:

```sh
flask db init
flask db upgrade
flask db migrate
```

## Run

To run the app:

```sh
flask run
```

Or, to make the server available to other devices:

```sh
flask run --host=0.0.0.0
```

You will now find the server running on: `http://localhost:5000`, or for other devices, `http://<your_local_ip_or_hostname>:5000`

In addition you can browse the API at:
http://localhost:5000/api/


## Flask extensions used

Function            | Flask-Extension
------------------- | -----------------------
Model & ORM         | [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/latest/)
Migration           | [Flaks-Migrate](http://flask-migrate.readthedocs.io/en/latest/)
Forms               | [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)
Login               | [Flask-Login](https://flask-login.readthedocs.org/en/latest/)
Admin               | Flask-Admin(https://flask-admin.readthedocs.io/en/latest/)

## Other libraries used
CSS | [Skeleton](http://getskeleton.com/)
JS  | [jQuery](https://jquery.com/)
