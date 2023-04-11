from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from database import *
# from apis import *

from datetime import datetime, time
import pytz

now_utc = datetime.utcnow()
# set the timezone to Indian Standard Time
tz = pytz.timezone('Asia/Kolkata')
now_ist = now_utc.astimezone(tz).time()
t = str(now_ist)[0:5]
t = datetime.strptime(str(t), '%H:%M').time()

app = Flask("__name__")
app.secret_key = 'your_secret_key'

# ------------------------- Create App -------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"

db.init_app(app)
# api.init_app(app)
app.app_context().push()

# ------------------- Business Logic ---------------------------


# -------------------Home Page ----------------------------------
@app.route("/")
def index():
  return render_template("welcome.html")


# -------------------Admin Login Page ----------------------------------
@app.route("/adminLogin", methods=["GET", "POST"])
def adminlogin():
  if request.method == "POST":
    name = request.form["username"]
    password = request.form["password"]

    a = Admin.query.filter_by(username=name).first()
    if a:
      if a.password == password:
        return redirect(url_for('dashbord', admin_id=a.admin_id))
      else:
        flash('Incorrect password, please try again.')
        return render_template("adminLogin.html")
    else:
      a = Admin(username=name, password=password)
      db.session.add(a)
      db.session.commit()
      return redirect(url_for("dashbord", admin_id=a.admin_id))
  return render_template("adminLogin.html")


# -------------------User Login Page ----------------------------------
@app.route("/userLogin", methods=["GET", "POST"])
def userlogin():
  if request.method == "POST":
    name = request.form["username"]
    password = request.form["password"]

    u = User.query.filter_by(username=name).first()
    if u and u.password == password:
      return redirect(url_for('userdashbord', user_id=u.user_id))
    else:
      flash('Incorect Username or Password')
      return render_template("Userlogin.html")
  return render_template("Userlogin.html")


# -------------------User Registration Page ----------------------------------
@app.route("/userregistration", methods=["GET", "POST"])
def userregistration():
  if request.method == "POST":
    name = request.form["username"]
    password = request.form["password"]

    u = User.query.filter_by(username=name).first()

    if u:
      flash("This User name Already exist")
      return redirect(url_for("userregistration"))

    u = User(username=name, password=password)
    db.session.add(u)
    db.session.commit()
    return redirect(url_for("userlogin"))
  return render_template("userregistration.html")


# -------------------Admin Dashbord Page ----------------------------------


@app.route("/<int:admin_id>/dashbord")
def dashbord(admin_id):
  a = Admin.query.get(admin_id)
  s = Show.query.all()
  return render_template("admin.html", u=a, s=s)


# -------------------User Dashbord Page ----------------------------------


@app.route("/<int:user_id>/userdashbord", methods=["GET", "POST"])
def userdashbord(user_id):
  u = User.query.get(user_id)
  # Modification 1
  s = Show.query.all()
  if request.method == "POST":
    q = request.form.get('q')
    if Show.query.filter_by(rating=q).all():
      s = Show.query.filter_by(rating=q).all()
    else:
      tag = "%" + q + "%"
      s = Show.query.filter(Show.tags.like(tag)).all()
  return render_template("user.html", u=u, sh=s, current_time=t)


# -------------------Venue Dashbord Page ----------------------------------


@app.route("/<int:user_id>/venues", methods=["GET", "POST"])
def Venues(user_id):
  u = User.query.get(user_id)
  v = Venue.query.all()
  sv = {}
  for i in v:
    d = {}
    for s_ in i.shows:
      sv_ = Showvenue.query.filter(Showvenue.show_id == s_.show_id,
                                   Showvenue.venue_id == i.venue_id).first()
      d[s_.show_id] = sv_
    sv[i.venue_id] = d
  if request.method == "POST":
    loc = request.form.get('q')
    v = Venue.query.filter_by(Location=loc).all()
  return render_template("venues.html", u=u, v=v, sv=sv)


#  ------------for perticular show-----------------------
@app.route("/<int:user_id>/<int:show_id>/venue", methods=["GET", "POST"])
def Venue_(user_id, show_id):
  u = User.query.get(user_id)
  s = Show.query.get(show_id)
  sv = Showvenue.query.filter(Showvenue.show_id == show_id).all()
  v = s.venues
  if request.method == "POST":
    loc = request.form.get('q')
    v = Venue.query.filter_by(Location=loc).all()
  return render_template("venue.html", u=u, v=v, s=s, sv=sv)


# -------------------Venue Create Page ----------------------------------
@app.route("/<int:admin_id>/createVenue", methods=["GET", "POST"])
def createVenue(admin_id):
  a = Admin.query.get(admin_id)
  if request.method == "POST":
    venue = request.form["venue"]
    place = request.form["Place"]
    location = request.form["Location"]
    capacity = request.form["Capacity"]

    v = Venue(venue_name=venue,
              Place=place,
              Location=location,
              Capacity=capacity,
              admin_=admin_id)
    a.venues.append(v)
    db.session.add(v)
    db.session.commit()

    return redirect(url_for("dashbord", admin_id=a.admin_id))
  return render_template("createveneu.html", u=a)


# -------------------Venue Managment ------------------------------
@app.route("/<int:admin_id>/<int:venue_id>/edit", methods=["GET", "POST"])
def editVenue(admin_id, venue_id):
  a = Admin.query.get(admin_id)
  v = Venue.query.get(venue_id)

  if request.method == "POST":
    v.venue_name = request.form["venue"]
    db.session.commit()
    return redirect(url_for("dashbord", admin_id=a.admin_id))
  return render_template("editvenue.html", u=a, v=v)


@app.route("/<int:admin_id>/<int:venue_id>/delete", methods=["GET", "POST"])
def deleteVenue(admin_id, venue_id):
  a = Admin.query.get(admin_id)
  v = Venue.query.get(venue_id)
  b = Booking.query.filter_by(venue_id=venue_id).all()
  if request.method == "POST":
    for s in v.shows:
      S = Show.query.get(s.show_id)
      db.session.delete(S)
    if b:
      for b_ in b:
        db.session.delete(b_)
        db.session.commit()
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for("dashbord", admin_id=a.admin_id))
  return redirect(url_for("dashbord", admin_id=a.admin_id))


# -------------------Show Create Page ----------------------------------
@app.route("/<int:admin_id>/<int:venue_id>/createshow",
           methods=["GET", "POST"])
def createshow(admin_id, venue_id):
  a = Admin.query.get(admin_id)
  v = Venue.query.get(venue_id)

  if request.method == "POST":
    show = request.form["show"]
    rating = request.form["rating"]
    start_time = request.form["start_time"]
    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = request.form["end_time"]
    end_time = datetime.strptime(end_time, '%H:%M').time()
    tags = request.form["tags"]
    price = request.form["price"]

    s = Show(show_name=show,
             rating=rating,
             start_time=start_time,
             end_time=end_time,
             tags=tags,
             price=price)

    v.shows.append(s)
    db.session.add(s)
    db.session.commit()

    sv = Showvenue.query.filter(Showvenue.show_id == s.show_id,
                                Showvenue.venue_id == venue_id).first()
    sv.n_seat = v.Capacity
    sv.d_price = s.price
    db.session.commit()
    return redirect(url_for("dashbord", admin_id=a.admin_id))

  return render_template("createshow.html", u=a, v=v)


# -------------------Show Managment ------------------------------
@app.route("/<int:admin_id>/<int:venue_id>/<int:show_id>/editshow",
           methods=["GET", "POST"])
def editShow(admin_id, venue_id, show_id):
  a = Admin.query.get(admin_id)
  v = Venue.query.get(venue_id)
  s = Show.query.get(show_id)
  if request.method == "POST":
    s.show_name = request.form["show"]
    start_time = request.form["start_time"]
    s.start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = request.form["end_time"]
    s.end_time = datetime.strptime(end_time, '%H:%M').time()
    db.session.commit()
    return redirect(url_for("dashbord", admin_id=a.admin_id))
  return render_template("editshow.html", u=a, v=v, s=s)


@app.route("/<int:admin_id>/<int:venue_id>/<int:show_id>/deleteshow",
           methods=["GET", "POST"])
def deleteShow(admin_id, venue_id, show_id):
  a = Admin.query.get(admin_id)
  s = Show.query.get(show_id)
  b = Booking.query.filter_by(show_id=show_id).all()
  if request.method == "POST":
    db.session.delete(s)
    if b:
      for b_ in b:
        db.session.delete(b_)
        db.session.commit()
    db.session.commit()
    return redirect(url_for("dashbord", admin_id=a.admin_id))
  return redirect(url_for("dashbord", admin_id=a.admin_id))


# /Modify
@app.route("/<int:admin_id>/<int:venue_id>/<int:show_id>/addshow")
def addshow(admin_id, show_id, venue_id):
  a = Admin.query.get(admin_id)
  s = Show.query.get(show_id)
  v = Venue.query.get(venue_id)
  v.shows.append(s)
  db.session.commit()
  sv = Showvenue.query.filter(Showvenue.show_id == s.show_id,
                              Showvenue.venue_id == venue_id).first()
  sv.n_seat = v.Capacity
  sv.d_price = s.price
  db.session.commit()
  return redirect(url_for("dashbord", admin_id=a.admin_id))


# ------------------- Booking a Show  ------------------------------
@app.route("/<int:user_id>/<int:venue_id>/<int:show_id>/booking",
           methods=["GET", "POST"])
def booking(user_id, venue_id, show_id):
  u = User.query.get(user_id)
  v = Venue.query.get(venue_id)
  s = Show.query.get(show_id)
  sv = Showvenue.query.filter(Showvenue.show_id == show_id,
                              Showvenue.venue_id == venue_id).first()
  b = Booking.query.filter_by(show_id=s.show_id).first()
  if request.method == "POST":
    Number = request.form["n"]
    remaining = sv.n_seat - int(Number)
    if remaining < 0:
      sv.n_seat = 0
      Number = int(Number) + remaining
    else:
      sv.n_seat = remaining
    price = s.price
    total = int(sv.d_price) * int(Number)

    # ----------------- Dynamic Price --------------------------
    if (sv.n_seat / v.Capacity) <= 0.5:
      price += price * (1 - (sv.n_seat / v.Capacity))
      sv.d_price = price

    b = Booking(Number=Number, total=total, show_id=show_id, venue_id=venue_id)
    u.bookings.append(b)
    db.session.add(b)
    db.session.commit()
    return redirect(url_for("booked", user_id=user_id))
  return render_template("book.html", u=u, v=v, s=s, sv=sv)


# ----------------------------User Profile Page ----------------------------------
@app.route("/<int:user_id>/profile")
def booked(user_id):
  u = User.query.get(user_id)
  b = Booking.query.filter_by(user_=user_id).all()
  s = []
  v = []
  if b:
    for b in u.bookings:
      S = Show.query.get(b.show_id)
      V = Venue.query.get(b.venue_id)
      if S:
        s.append(S)
        v.append(V)
      else:
        db.session.delete(b)
        db.session.commit()
  return render_template("profile.html", u=u, s=s, v=v, current_time=t)


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
