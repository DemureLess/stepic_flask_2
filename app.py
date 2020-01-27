import json
import random
import re
from datetime import datetime

from flask import Flask
from flask import request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from forms import Leadform, MessageForm, BookingForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stepic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def slugify(s):
    s = transliteration(s)  # Избавляемся от русских букв
    pattern = r'[^\w+]'  # Избавляемся от символов, которые не допускаются в URL
    pattern_2 = r'(-){2,}'  # Подчищаем образовавшиеся двойные дефисы
    slug = re.sub(pattern_2, '-', re.sub(pattern, '-', s))

    return slug


def transliteration(s):
    rus_to_lat = dict(а='a', б='b', в='v', г='g', д='d', е='e', ё='e', ж='zh', з='z', и='i', й='y', к='k', л='l', м='m',
                      н='n', о='o', п='p', р='r', с='s', т='t', у='u', ф='f', х='h', ц='c', ч='cz', ш='sh', щ='scz',
                      ъ='', ы='y', ь='', э='e', ю='u', я='ja')
    for letter in s:
        if rus_to_lat.get(letter):
            s = s.replace(letter, rus_to_lat.get(letter, ""))
    return s


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    about = db.Column(db.Text)
    picture = db.Column(db.String(200))
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float)
    goals = db.Column(db.String(200))
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(200))
    seo_keyword = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)
    bookings = db.relationship("Booking", back_populates="teachers")
    orders = db.relationship("Order", back_populates="teachers")

    def __init__(self, **kwargs):
        super(Teacher, self).__init__(**kwargs)
        self.generate_slug()
        self.seo_title = self.name
        self.seo_description = self.about
        self.seo_keyword = self.name

    def generate_slug(self):
        if self.name:
            self.slug = slugify(self.name.lower())

    def __repr__(self):
        return "{}:{}".format(self.id, self.name)


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    picture = db.Column(db.String(200))
    seo_title = db.Column(db.String(200))
    seo_description = db.Column(db.String(200))
    seo_keyword = db.Column(db.String(200))
    slug = db.Column(db.String(200), unique=True)

    def __init__(self, **kwargs):
        super(Goal, self).__init__(**kwargs)
        self.seo_title = self.name

    def __repr__(self):
        return 'name: {} slug: {}'.format(self.name, self.slug)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    name = db.Column(db.String(200))
    phone = db.Column(db.String(200))
    booking_goal = db.Column(db.String(200))
    booking_time = db.Column(db.String(200))
    booking_day = db.Column(db.String(200))
    teachers = db.relationship("Teacher", back_populates="orders")

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)

    def __repr__(self):
        return 'id: {} name: {}'.format(self.id, self.name)


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    teacher_schedule = db.Column(db.Text)
    teachers = db.relationship("Teacher", back_populates="bookings")

    def __init__(self, **kwargs):
        super(Booking, self).__init__(**kwargs)

    def __repr__(self):
        return 'id:{}'.format(self.id)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    message_time = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)

    def __repr__(self):
        return 'id: {} message: {}'.format(self.id, self.message)


@app.context_processor
def inject_default():
    goals_default = db.session.query(Goal).all()
    image_default = 'https://sun9-69.userapi.com/c856520/v856520447/a3d69/0tCScaKy9eY.jpg'
    site_name = "Tinysteps - Stepic Teachers"

    return dict(goals_default=goals_default, image_default=image_default, site_name=site_name)


@app.route('/', methods=['GET'])
def index():
    teachers_count = request.args.get('teachers_count')
    if teachers_count == 'all':
        teachers = db.session.query(Teacher).all()
    else:
        teachers = random.sample(list(db.session.query(Teacher)), k=6)

    return render_template('index.html', teachers=teachers)


@app.route('/profile/<slug>')
def profile_teacher(slug):
    teacher = db.session.query(Teacher).filter(Teacher.slug == slug).first_or_404()

    for booking in teacher.bookings:
        teacher_schedule = dict(json.loads(booking.teacher_schedule))

    return render_template('profile.html', teacher=teacher, teacher_schedule=teacher_schedule)


@app.route('/goals/<goal>')
def goals_teachers(goal):
    filtered_teachers = db.session.query(Teacher).filter(Teacher.goals.contains(goal)).order_by(Teacher.price.asc())
    filtered_goals = db.session.query(Goal).filter(Goal.slug == goal).first()

    if not filtered_teachers:
        return render_template('404.html')

    return render_template('goal.html', teachers=filtered_teachers, goal=filtered_goals.name)


@app.route('/message/<slug>', methods=['POST', 'GET'])
def message_teacher(slug):
    form = MessageForm()
    teacher = db.session.query(Teacher).filter(Teacher.slug == slug).first_or_404()

    if form.validate_on_submit():
        new_message = Message(teacher_id=teacher.id, name=form.username.data, phone=form.phone.data,
                              message=form.message.data)
        db.session.add(new_message)
        db.session.commit()

    return render_template('message.html', teacher=teacher, form=form)


@app.route('/request', methods=['POST', 'GET'])
def lead_request():
    form = Leadform()
    print(form.data)
    if form.validate_on_submit():
        new_lead = Order(name=form.username.data, phone=form.phone.data, booking_goal=form.booking_goal.data,
                         booking_time=form.booking_time.data)
        db.session.add(new_lead)
        db.session.commit()
    return render_template('pick.html', form=form)


@app.route('/search', methods=['GET'])
def search_teacher():
    search_sting = request.args.get('s')

    return render_template('search.html', search_sting=search_sting)


@app.route('/booking/<slug>', methods=['POST', 'GET'])
def booking_teacher(slug):
    form = BookingForm()
    teacher = db.session.query(Teacher).filter(Teacher.slug == slug).first()
    print(form.data)
    if form.validate_on_submit():
        for booking in teacher.bookings:
            teacher_schedule = dict(json.loads(booking.teacher_schedule))

        teacher_schedule[form.booking_day.data][form.booking_time.data] = False

        update_booking = Booking.query.get(teacher.id)
        update_booking.teacher_schedule = json.dumps(teacher_schedule)
        db.session.add(update_booking)

        new_lead = Order(name=form.username.data, teacher_id=teacher.id, phone=form.phone.data,
                         booking_time=form.booking_time.data, booking_day=form.booking_day.data)
        db.session.add(new_lead)
        db.session.commit()

    day_of_week = {'mon': 'понедельник', 'tue': 'вторник', 'wed': 'среда', 'thu': 'четверг',
                   'fri': 'пятница', 'sat': 'суббота', 'sun': 'воскресенье'}

    booking_day = request.args.get('day')  # День и время брони, берем из параметров.
    booking_hour = request.args.get('hour')
    booking = request.form

    return render_template('booking.html', teacher=teacher, form=form, booking=booking, booking_day=booking_day,
                           booking_hour=booking_hour, day_of_week=day_of_week)


@app.errorhandler(404)
def page_not_fount(e):
    return render_template('404.html')


# if process.env.FIRST_STAT == True:
#     goals = data.goals
#     teachers = data.teachers
#
#     for slug, name in goals.items():
#         new_goal = Goal(name=name, slug=slug)
#         db.session.add(new_goal)
#     db.session.commit()
#
#     for teacher in teachers.values():
#         new_teacher = Teacher(name=teacher['name'], about=teacher.get('about', ''), picture=teacher.get('picture', ''),
#                               rating=teacher.get('rating', ''), goals='//'.join(teacher.get('goals', '')),
#                               price=teacher.get('price', ''))
#         db.session.add(new_teacher)
#
#         new_teacher_schedule = json.dumps(teacher.get('free'))
#         booking = Booking(teacher_schedule=new_teacher_schedule, teachers=new_teacher)
#         db.session.add(booking)
#     db.session.commit()
#
#     process.env.FIRST_STAT = 0


if __name__ == '__main__':
    app.run(debug=True)

db.create_all()
