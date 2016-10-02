from flask import Flask
import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'B0Zr98j/3yX R~XHH!jmN]LWX/,?RM'

db_url = 'mysql://root:password@localhost/instagram_clone'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True					# to suppress warning at startup


engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
alchemy_session = Session()

db = SQLAlchemy(app)

# for creating tables into database
from models import *

# create database tables if not created
db.create_all()
db.session.commit()
print "Tables created"

CORS(app)

def register_blueprints(app):
	from .views import views
	app.register_blueprint(views)

register_blueprints(app)
