import os

# Code for the configuration of the database
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'socialmedia.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'VerySecretKey'
