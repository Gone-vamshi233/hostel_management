from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="student")  # admin, warden, student

    # relationships
    complaints = db.relationship("Complaint", backref="user", cascade="all, delete-orphan")
    allocation = db.relationship("Allocation", backref="student", uselist=False)

    def is_admin(self):
        return self.role == "admin"

class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=1)
    occupants = db.Column(db.Integer, default=0)
    block = db.Column(db.String(50))
    allocations = db.relationship("Allocation", backref="room", cascade="all, delete-orphan")

    def available_slots(self):
        return self.capacity - self.occupants

class Allocation(db.Model):
    __tablename__ = "allocations"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    since = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="open")  # open, resolved
