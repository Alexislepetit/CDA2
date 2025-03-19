from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:uimm@localhost/client'
app.config['SECRET_KEY'] = os.urandom(24) # to be able to use POST and Form



from app import routes