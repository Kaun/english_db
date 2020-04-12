from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField, RadioField


import json
import random
import create_json

app = Flask(__name__)
app.secret_key = "randomstring"
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


class BookingForm(FlaskForm):
    # teacher_id = StringField('teacher_id')
    teacher_name = StringField('teacher_name')
    teacher_picture = StringField('teacher_picture')

    #
    client_name = StringField('Вас зовут')
    client_phone = StringField('Ваш телефон')
    client_teacher = HiddenField("clientTeacher")
    client_weekday = HiddenField('clientWeekday')
    name_weekday = HiddenField('nameWeekday')
    client_time = HiddenField("clientTime")
    submit = SubmitField('Записаться на пробный урок')


class RequestForm(FlaskForm):

    client_goal = RadioField('goal', choices=[('travel', 'Для путешествий'), ('study', 'Для учебы'),
                                              ('work', 'Для работы'), ('relocate', 'Для переезда')])
    client_time = RadioField('goal', choices=[('1-2', '1-2 часа в&nbsp;неделю'), ('study', '3-5 часов в&nbsp;неделю'),
                                              ('5-7', '5-7 часов в&nbsp;неделю'), ('7-10', '7-10 часов в&nbsp;неделю')])
    client_name = StringField('Вас зовут')
    client_phone = StringField('Ваш телефон')
    submit = SubmitField('Найдите мне преподавателя')


db.create_all()


db_check = db.session.query(Teacher).get(1)
if db_check is None:
    for teacher in teachers:
        t = Teacher(id=teacher["id"], name=teacher["name"], about=teacher["about"], rating=teacher["rating"],
                    picture=teacher["picture"], price=teacher["price"], goals=str(teacher["goals"]),
                    free=str(teacher["free"]))
        db.session.add(t)
    db.session.commit()


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
    for goal in goals_list:
        goals_names.append(goals[goal])
    return render_template('profile.html', teacher=teacher, week=week, free_time=free_time, goals=goals_names)


@app.route('/booking/<id>/<day>/<hour>', methods=["GET", "POST"])
def rout_booking(id, day, hour):
    id_ = int(id) + 1
    teacher = db.session.query(Teacher).get(id_)
    form = BookingForm(client_teacher=teacher.id, teacher_name=teacher.name, teacher_picture=teacher.picture,
                       client_time=hour, client_weekday=day, name_weekday=week[day])
    if request.method == "POST":
        name = form.client_name.data
        phone = form.client_phone.data
        booking_client = Booking(client_teacher_id=teacher.id, client_name=name, client_phone=phone,
                                 client_time=hour, client_weekday=day)
        db.session.add(booking_client)
        db.session.commit()
        return render_template('booking_done.html', name_weekday=week[day], client_time=hour, name=name, phone=phone)
    else:
        return render_template('booking.html', form=form)


@app.route('/request', methods=["GET", "POST"])
def rout_request():
    form = RequestForm()
    if request.method == "POST":
        name = form.client_name.data
        phone = form.client_phone.data
        goal = form.client_goal.data
        time_ = form.client_time.data
        request_client = RequestClient(client_name=name, client_phone=phone,
                                       client_goal=goal, client_time=time_)
        db.session.add(request_client)
        db.session.commit()
        return render_template('request_done.html', time=time_, name=name, phone=phone, goal=goals[goal])
    else:
        return render_template('request.html', form=form)


if __name__ == '__main__':
    app.run()
