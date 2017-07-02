#!/usr/bin/env python

import ruamel.yaml
from flask_script import Manager, Shell, prompt_bool
from ludolatin import app
from app import db
from app import models
from app.models import User, Sentence, Quiz, Answer, Score, Topic, Product, Purchase, Comment

# output = dump(data, Dumper=Dumper)

manager = Manager(app)


def _make_context():
    return dict(
        app=app,
        db=db,
        models=models,
        user=User.query.first(),
        current_user=User.query.first(),
        User=User,
        Sentence=Sentence,
        Quiz=Quiz,
        Answer=Answer,
        Score=Score,
        Topic=Topic,
        Product=Product,
        Purchase=Purchase,
        Comment=Comment,
    )

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def db_meta():
    """Show database tables metadata"""
    print db
    for table in db.metadata.sorted_tables:
        print "\n", table.name, ":"
        for column in table.columns:
            print column.name, ":", column.type


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
def show_users():
    """List all users"""
    print User.query.all()


@manager.command
def load_sentences():
    """Load the content of data.yml into the English / Latin tables"""
    yaml = open('data/quiz_data.yml')
    data = ruamel.yaml.load(yaml, ruamel.yaml.RoundTripLoader)
    print data

    for topic_name, quiz in data.items():
        topic = (Topic.query.filter_by(name=topic_name).first() or Topic(name=topic_name))
        print topic
        topic.save()

        for quiz_name, sentences in quiz.items():
            quiz = Quiz(
                name=quiz_name,
                topic=topic
            )
            print quiz
            quiz.save()

            for english, translations in sentences.items():
                type = translations.pop(0)['type']

                e = Sentence(
                    type=type,
                    text=english,
                    quiz=quiz
                )

                for latin in translations:
                    l = Sentence(
                        text=latin,
                    )
                    e.translations.append(l)
                    l.translations.append(e)

                db.session.add(e)
                db.session.commit()

@manager.command
def delete_sentences():
    """Delete the content of Sentence table"""
    if prompt_bool("Are you sure you want to delete all Sentences?"):
        Sentence.query.delete()


@manager.command
def load_lessons():
    """Load the content of products.yml into the Product table"""
    yaml = open('data/lessons.yml')
    data = ruamel.yaml.load(yaml, ruamel.yaml.RoundTripLoader)
    print data

    for topic_name, text in data.items():
        topic = (Topic.query.filter_by(name=topic_name).first() or Topic(name=topic_name))
        print topic

        topic.text = unicode(text)
        topic.save()


@manager.command
def load_products():
    """Load the content of products.yml into the Product table"""
    yaml = open('data/products.yml')
    data = ruamel.yaml.load(yaml, ruamel.yaml.RoundTripLoader)
    print data

    for product_name, attributes in data.items():
        product = (Product.query.filter_by(name=product_name).first() or Product(name=product_name))
        print product

        product.description = attributes[0]
        product.price = attributes[1]
        product.pricing_formula = attributes[2]
        product.availability_function = attributes[3]

        product.save()


@manager.command
def delete_data():
    """Delete the content of the Product table"""
    if prompt_bool("Are you sure you want to delete all Products?"):
        Product.query.delete()


@manager.command
def load_data():
    """Load sentence data"""
    load_sentences()
    load_lessons()
    load_products()


@manager.command
def delete_data():
    """Delete the content of Sentence and Product tables"""
    if prompt_bool("Are you sure you want to delete all Sentences and Products?"):
        Sentence.query.delete()
        Product.query.delete()


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()
