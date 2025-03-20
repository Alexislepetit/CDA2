from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24) # to be able to use POST and Form

# Définit une clé secrète pour signer les cookies de session
app.secret_key = os.urandom(24) 



from app import routes