# manage.py

import json
from flask_script import Manager, prompt_bool
from ingenuity import app
from app import db
from app.models import User, EnglishPhrase, LatinPhrase

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# output = dump(data, Dumper=Dumper)

manager = Manager(app)


@manager.command
def users():
    "List all users"
    print User.query.all()


@manager.command
def add_admin():
    "Add an admin user"
    user = User(
        email="admin@example.com",
        username="admin",
        password="password",
        is_admin="True"
    ).save()

    print "\nUser: admin"
    print "Password: password\n"

    print "Visit http://localhost/admin, login as admin, "
    print  "promote an existing user to admin, then delete this temporary admin user.\n"


@manager.command
def load_data():
    "Load the content of data.yml into the English / Latin tables"
    file = open('data.yml')
    data = load(file, Loader=Loader)
    print data
    words = data['english-latin']

    for english, latin_translations in words.items():
        e = (EnglishPhrase.query.filter_by(phrase=english).first() or
            EnglishPhrase(
                phrase=english
            )
        )

        for latin in latin_translations:
            l = (LatinPhrase.query.filter_by(phrase=latin).first() or
                LatinPhrase(
                    phrase=latin
                )
            )
            e.latin_translations.append(l)
        db.session.add(e)
        db.session.commit()
    dump_data()

@manager.command
def dump_data():
    "Output the content of the English / Latin tables as YAML"
    english = EnglishPhrase.query.all()
    print "english-latin:"
    for e in english:
        print "  " + e.phrase + ":"
        for l in e.latin_translations:
            print "    - " + l.phrase


@manager.command
def delete_data():
    "Delete the content of the English / Latin tables"
    if prompt_bool("Are you sure you want to delete all English and Latin phrases?"):
        EnglishPhrase.query.delete()
        LatinPhrase.query.delete()

        # Delete contents of the (Model-less) english_latin assocication table
        db.session.query(english_latin).delete()
        db.session.commit()
    dump_data()

@manager.command
def db_meta():
    print db
    for table in db.metadata.sorted_tables:
        print "\n", table.name, ":"
        for column in table.columns:
            print column.name, ":", column.type

if __name__ == "__main__":
    manager.run()

