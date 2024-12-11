from app import app, db
from app.models import User, Post
from datetime import datetime

# Creates all tables in the database
# Code from the module website
with app.app_context():
    # Create all tables
    db.create_all()
