from flask_sqlalchemy import SQLAlchemy
from datetime import time

db = SQLAlchemy()


# -------------------------Admin DataBase ---------------------------
class Admin(db.Model):
  admin_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(50), nullable=False)
  venues = db.relationship("Venue", backref="admin")


class Showvenue(db.Model):
  show_id = db.Column(db.Integer(),
                      db.ForeignKey('show.show_id'),
                      primary_key=True)
  venue_id = db.Column(db.Integer(),
                       db.ForeignKey('venue.venue_id'),
                       primary_key=True)
  n_seat = db.Column(db.Integer())
  d_price = db.Column(db.Integer())


class Venue(db.Model):
  venue_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  venue_name = db.Column(db.String(50), unique=True, nullable=False)
  Place = db.Column(db.String(50), nullable=False)
  Location = db.Column(db.String(50), nullable=False)
  Capacity = db.Column(db.Integer(), nullable=False)
  admin_ = db.Column(db.Integer(), db.ForeignKey('admin.admin_id'))
  shows = db.relationship("Show", secondary="showvenue", backref="venues")


class Show(db.Model):
  show_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  show_name = db.Column(db.String(50), unique=True, nullable=False)
  rating = db.Column(db.String(50), nullable=False)
  start_time = db.Column(db.Time, nullable=False)
  end_time = db.Column(db.Time, nullable=False)
  tags = db.Column(db.String(50), nullable=False)
  # n_seat = db.Column(db.Integer(), nullable=False)
  price = db.Column(db.Integer(), nullable=False)
  # d_price = db.Column(db.Integer(), nullable=False)
  # venue_ = db.Column(db.Integer(), db.ForeignKey('venue.venue_id'))


  # -------------------------User DataBase ---------------------------
class User(db.Model):
  user_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(50), nullable=False)
  bookings = db.relationship("Booking", backref="user")


class Booking(db.Model):
  booking_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
  Number = db.Column(db.Integer(), nullable=False)
  total = db.Column(db.Integer(), nullable=False)
  show_id = db.Column(db.Integer(), nullable=False)
  venue_id = db.Column(db.Integer(), nullable=False)
  user_ = db.Column(db.Integer(), db.ForeignKey('user.user_id'))
