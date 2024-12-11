from datetime import datetime
from app import db, app
from flask import flash, redirect, url_for, session

class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String, nullable=False)

    # Relationships for followers and following
    followers = db.relationship(
        'Follow', foreign_keys='Follow.followed_id', backref='followed', lazy='dynamic')
    following = db.relationship(
        'Follow', foreign_keys='Follow.follower_id', backref='follower', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')

    def is_following(self, user):
        return Follow.query.filter(
            Follow.follower_id == self.username,
            Follow.followed_id == user.username).count() > 0

    def is_followed_by(self, user):
        return Follow.query.filter(
            Follow.follower_id == user.username,
            Follow.followed_id == self.username).count() > 0

    def has_liked_post(self, post):
        return Like.query.filter(
            Like.user_id == self.username,
            Like.post_id == post.id).count() > 0

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    username = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    likes = db.Column(db.Integer, default=0)  # Ensure this is updated manually
    likers = db.relationship('Like', backref='post', lazy='dynamic')


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.String, db.ForeignKey('user.username'))
    followed_id = db.Column(db.String, db.ForeignKey('user.username'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
