from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# username inside a room should be unique
class Video(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer)
    videoname = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    videos = db.relationship('Video')

class Room(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    roomName = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    users = db.relationship('User')