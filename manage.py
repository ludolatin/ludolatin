# manage.py

import ruamel.yaml
from flask_script import Manager, Shell, prompt_bool
from ingenuity import app
from app import db
from app import models
from app.models import User, Sentence, Language, Quiz, Answer, Score, Topic, Product, Purchase

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
        Language=Language,
        Quiz=Quiz,
        Answer=Answer,
        Score=Score,
        Topic=Topic,
        Product=Product,
        Purchase=Purchase
    )

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


def initialise_languages():
    """Initialise languages"""

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
    yaml = open('data/quiz_data.yml')
    data = ruamel.yaml.load(yaml, ruamel.yaml.RoundTripLoader)
    print data

    for topic_name, quiz in data.items():
        topic = (Topic.query.filter_by(name=topic_name).first() or Topic(name=topic_name))
        print topic
        topic.save()

        for quiz_name, sentences in quiz.items():
            language = Language.query.filter_by(name="English").first()
            quiz = Quiz(
                name=quiz_name,
                topic=topic
            )
            print quiz
            quiz.save()

            for english, translations in sentences.items():
                e = Sentence(
                    text=english,
                    language=language,
                    quiz=quiz
                )

                for latin in translations:
                    l = Sentence(
                        text=latin,
                        language=Language.query.filter_by(name="Latin").first()
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
    topics = Topic.query.all()
    quizzes = Quiz.query.all()

    print topics
    print quizzes

    for quiz in quizzes:
        english_sentences = Sentence.query.join(Sentence.language, Sentence.quiz).\
            filter(Language.name == "English", Quiz.name == quiz.name).all()
        print quiz.name + ":"
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

if __name__ == "__main__":
    manager.run()
