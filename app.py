from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField

import json
import random
import create_json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///teachers.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

week = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота",
        "sun": "Воскресенье"}
icons = {"travel": "✈", "study": "🏫", "work": "🏢", "relocate": "🚗", "programming": "⌨"}

with open("teachers.json", "r") as f:
    teachers = json.load(f)

with open("goals.json", "r") as f:
    goals = json.load(f)


class Teacher(db.Model):
    __tablename__ = "teachers"

    id_teacher = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String, nullable=False)
    free = db.Column(db.String, nullable=False)
    reservation = db.relationship('Booking', back_populates="client")


class Booking(db.Model):
    __tablename__ = "booking"

    id_client = db.Column(db.Integer, primary_key=True)
    client_teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id_teacher"))
    client = db.relationship("Teacher", back_populates="reservation")
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_time = db.Column(db.String, nullable=False)
    client_weekday = db.Column(db.String, nullable=False)


class RequestClient(db.Model):
    __tablename__ = "requests_clients"

    id_client = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String, nullable=False)
    client_phone = db.Column(db.String, nullable=False)
    client_goal = db.Column(db.String, nullable=False)
    client_time = db.Column(db.String, nullable=False)



db.create_all()

# Не знаю как выполнить этот кусок кода один раз

db_check = db.session.query(Teacher).get(1)
if db_check is None:
    for teacher in teachers:
        t = Teacher(id=teacher["id"], name=teacher["name"], about=teacher["about"], rating=teacher["rating"],
                    picture=teacher["picture"], price=teacher["price"], goals=str(teacher["goals"]),
                    free=str(teacher["free"]))
        db.session.add(t)
    db.session.commit()


# for teacher in teachers:
#     t = Teacher(id=teacher["id"], name=teacher["name"], about=teacher["about"], rating=teacher["rating"],
#                 picture=teacher["picture"], price=teacher["price"], goals=str(teacher["goals"]),
#                 free=str(teacher["free"]))
#     db.session.add(t)


# db.session.commit()


@app.route('/')
def route_index():
    teachers_ = db.session.query(Teacher).all()
    teachers_random = random.sample(teachers_, 6)
    return render_template('index.html', icons=icons, goals=goals, teachers=teachers_random)


@app.route('/allprofile')
def route_allprofile():
    return render_template('index.html', icons=icons, goals=goals, teachers=teachers)


@app.route('/goal/<goal>')
def route_goal(goal):
    # goals_str = teacher.goals
    # goals_list = json.loads(goals_str.replace("'", '"'))
    # teachers_query = db.session.query(Teacher).filter(Teacher.goals == goals[goal])
    teachers_goals = []
    # teachers = teachers_query.all()
    # print(teachers)
    for teacher in teachers:
        if goal in teacher["goals"]:
            teachers_goals.append(teacher)
    # sorting by rating
    teachers_goals = sorted(teachers_goals, key=lambda teacher: teacher["rating"], reverse=True)
    return render_template('goal.html', icon=icons[goal], teachers=teachers_goals, goal=goals[goal])
    # return ''


@app.route('/profiles/<id>')
def rout_profiles(id):
    id_ = int(id) + 1
    teacher = db.session.query(Teacher).get(id_)
    free_dict = eval(teacher.free)
    free_time = {}
    for day, hours in free_dict.items():
        free_hours = {}
        for hour, stat in hours.items():
            if stat:
                free_hours[hour] = stat
        free_time[day] = free_hours
    goals_names = []
    goals_str = teacher.goals
    goals_list = json.loads(goals_str.replace("'", '"'))
    # print(type(goals_list))
    for goal in goals_list:
        goals_names.append(goals[goal])
    return render_template('profile.html', teacher=teacher, week=week, free_time=free_time, goals=goals_names)
    # return ''


@app.route('/booking/<id>/<day>/<hour>')
def rout_booking(id, day, hour):
    teacher = teachers[int(id)]
    return render_template('booking.html', teacher=teacher, week=week, day=day, hour=hour)


@app.route('/booking_done', methods=['POST'])
def rout_booking_done():
    booking_client = Booking(client_teacher_id=request.form["clientTeacher"], client_name=request.form["clientName"],
                             client_phone=request.form["clientPhone"], client_time=request.form["clientTime"],
                             client_weekday=request.form["clientWeekday"])
    db.session.add(booking_client)
    db.session.commit()
    # booking = {}
    # booking["clientTeacher"] = request.form["clientTeacher"]
    # booking["clientName"] = request.form["clientName"]
    # booking["clientPhone"] = request.form["clientPhone"]
    # booking["clientTime"] = request.form["clientTime"]
    # booking["clientWeekday"] = request.form["clientWeekday"]
    # with open("booking.json", "a") as file:
    #     json.dump(booking, file)
    #     file.write(",")
    return render_template('booking_done.html', day=week[request.form["clientWeekday"]],
                           hour=request.form["clientTime"], name=request.form["clientName"],
                           phone=request.form["clientPhone"])


@app.route('/request')
def rout_request():
    return render_template('request.html')


@app.route('/request_done', methods=['POST'])
def rout_request_done():
    request_client = RequestClient(client_name=request.form["clientName"], client_phone=request.form["clientPhone"],
                                   client_goal=request.form["goal"], client_time=request.form["time"])

    db.session.add(request_client)
    db.session.commit()
    # request_user = {}
    # request_user["clientName"] = request.form["clientName"]
    # request_user["clientPhone"] = request.form["clientPhone"]
    # request_user["goal"] = request.form["goal"]
    # request_user["time"] = request.form["time"]
    # with open("request.json", "a") as fr:
    #     json.dump(request_user, fr)
    #     fr.write(",")
    return render_template('request_done.html', goal=goals[request.form["goal"]],
                           time=request.form["time"], name=request.form["clientName"],
                           phone=request.form["clientPhone"])


if __name__ == '__main__':
    app.run()
