# manage.py

import json
from flask_script import Manager, prompt_bool
from ingenuity import app
from app import db
from app.models import User, EnglishPhrase, LatinPhrase, english_latin

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

    for english, translations in words.items():
        e = (EnglishPhrase.query.filter_by(text=english).first() or
            EnglishPhrase(
                text=english
            )
        )

        for latin in translations:
            l = (LatinPhrase.query.filter_by(text=latin).first() or
                LatinPhrase(
                    text=latin
                )
            )
            e.translations.append(l)
        db.session.add(e)
        db.session.commit()
    dump_data()

@manager.command
def dump_data():
    "Output the content of the English / Latin tables as YAML"
    english_phrases = EnglishPhrase.query.all()
    print "english-latin:"
    for phrase in english_phrases:
        print "  " + phrase.text + ":"
        for latin in phrase.translations:
            print "    - " + latin.text


@manager.command
def delete_data():
    "Delete the content of the English / Latin tables"
    if prompt_bool("Are you sure you want to delete all English and Latin phrases?"):
        EnglishPhrase.query.delete()
        LatinPhrase.query.delete()

        # Delete contents of the (Model-less) english_latin association table
       # db.session.query(english_latin).delete()
       # db.session.commit()
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
