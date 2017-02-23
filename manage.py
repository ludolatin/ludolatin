# manage.py

import json
from flask_script import Manager, Shell, prompt_bool
from ingenuity import app
from app import db
from app import models
from app.models import User, Sentence, Language

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# output = dump(data, Dumper=Dumper)

manager = Manager(app)


def _make_context():
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def users():
    """List all users"""
    print User.query.all()


@manager.command
def add_admin():
    """Add an admin user"""
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
def initialise_languages():
    """ Initialise languages"""

    languages = ["English", "Latin"]

    for language in languages:
        l = (Language.query.filter_by(name=language).first() or Language(
                name=language,
            )
        )

        db.session.add(l)
        db.session.commit()


@manager.command
def load_sentences():
    """Load the content of data.yml into the English / Latin tables"""
    filename = open('data.yml')
    data = load(filename, Loader=Loader)
    print data
    words = data['english-latin']

    for english, translations in words.items():
        e = (Sentence.query.filter_by(text=english).first() or Sentence(
                text=english,
                language=Language.query.filter_by(name="English").first()
            )
        )

        for latin in translations:
            l = (Sentence.query.filter_by(text=latin).first() or Sentence(
                    text=latin,
                    language=Language.query.filter_by(name="Latin").first()
                )
            )
            e.translations.append(l)
            l.translations.append(e)

        db.session.add(e)
        db.session.commit()


@manager.command
def load_data():
    """ Initialise languages, Load sentence data"""
    initialise_languages()
    load_sentences()
    dump_data()


@manager.command
def dump_data():
    """Output the content of the English / Latin tables as YAML"""
    english_sentences = Sentence.query.join(Sentence.language).filter(Language.name == "English").all()
    print "english-latin:"
    for sentence in english_sentences:
        print "  " + sentence.text + ":"
        for latin in sentence.translations:
            print "    - " + latin.text


@manager.command
def delete_data():
    """Delete the content of the English / Latin tables"""
    if prompt_bool("Are you sure you want to delete all English and Latin phrases?"):
        Sentence.query.delete()

        # Delete contents of the (Model-less) association table
       # db.session.query(sentence_to_sentence).delete()
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
