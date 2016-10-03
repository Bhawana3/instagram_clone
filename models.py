from . import db
from passlib.hash import sha256_crypt
from sqlalchemy import UniqueConstraint
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(100))
    profile_pic = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean)

    def __init__(self, username, email, password,profile_pic=None, is_verified=False):
        self.username = username
        self.email = email
        self.password = sha256_crypt.encrypt(password)

        if profile_pic is None:
            self.profile_pic = profile_pic

    def __repr__(self):
        return '<User %r>' % self.email

    def save(self):
        db.session.add(self)
        db.session.commit()


class Followers(db.Model):
    __tablename__ = "followers"
    id = db.Column(db.Integer, primary_key=True)
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    __table_args__ = (UniqueConstraint('to_id', 'from_id', name='to_from'),)

    def __init__(self,to_id,from_id):
        self.to_id = to_id
        self.from_id = from_id

    def __repr__(self):
        return "to_id %r , from_id %r" %(self.to_id,self.from_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Photo_details(db.Model):
    __tablename__ = "photo_details"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_path = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)

    def __init__(self,user_id,photo_path, timestamp=None):
        self.user_id = user_id
        self.photo_path = photo_path

        if timestamp is None:
            self.timestamp = datetime.utcnow()

    def __repr__(self):
        return "photo path %r" % self.photo_path

    def save(self):
        db.session.add(self)
        db.session.commit()

class Likes(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo_details.id'))
    timestamp = db.Column(db.DateTime)

    def __init__(self, user_id, photo_id, timestamp=None):
        self.user_id = user_id
        self.photo_id = photo_id

        if timestamp is None:
            self.timestamp = datetime.utcnow()

    def __repr__(self):
        return "user %r likes %r" %(self.user_id, self.photo_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo_details.id'))
    comment = db.column(db.String(1000))
    timestamp = db.Column(db.DateTime)

    def __init__(self,user_id,photo_id,comment=None,timestamp=None):
        self.user_id = user_id
        self.photo_id = photo_id

        if timestamp is None:
            self.timestamp = datetime.utcnow()

        if comment is None:
            self.comment = comment

    def __repr__(self):
        return "comment %r" % self.comment

    def save(self):
        db.session.add(self)
        db.session.commit()