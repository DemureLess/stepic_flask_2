import json
import random
from datetime import datetime

from flask import Flask, request, render_template

import data

goals = data.goals
teachers = data.teachers

for id in teachers:
    teachers[id]['url'] = id  # устанавливаем в качестве url - id учителя
    teachers[id]['id'] = id  # так же, добавляем id учителя "внутрь словаря"

#
# Чтение данных из файла data.py. Обогощения словаря id, url, сохранение в json.
#
# teachers = data.teachers
# for id in teachers:
#     teachers[id]['url'] = id  # устанавливаем в качестве url - id учителя
#     teachers[id]['id'] = id  # так же, добавляем id учителя "внутрь словаря"
#
#  with open('teachers.json', 'w', encoding='utf-8') as f:
#      save_teachers = json.dumps(teachers)
#      f.write(save_teachers)
#
# Использование json в качестве словаря данных
#
# with open('teachers.json', 'r', encoding='utf-8') as f:
#     contents = f.read()
#     teachers = json.loads(contents)
#


app = Flask(__name__)


@app.context_processor
def inject_goals():
    image_default = 'https://sun9-69.userapi.com/c856520/v856520447/a3d69/0tCScaKy9eY.jpg'
    return dict(goals=goals, image_default=image_default)


@app.template_filter('my_random_teachers')
def my_random(random_teachers, quantity=0):
    # Кастомный фильтр, для рандомного вывода репетиторов
    keys = list(random_teachers)
    random.shuffle(keys)

    if quantity == 0:
        quantity = len(keys)
    elif quantity > len(keys):
        quantity = len(keys)

    keys = keys[:quantity]
    result = {}
    for id in keys:
        result[id] = random_teachers[id]
    return result


@app.template_filter('named_dic_to_noname')
def my_named_dic_to_noname_dic(named_dic):
    # Вспомогательный фильтр, переводящий именовыанный словарь в неименованный
    return named_dic.values()


@app.route('/', methods=['GET'])
def main_teachers_count():
    # Предусмотрено состояние вывода всех репетиторов
    teachers_count = request.args.get('teachers_count')
    if teachers_count == 'all':
        quantity = 0
    else:
        quantity = 6

    return render_template('index.html', teachers=teachers, quantity=quantity)


@app.route('/profile/<int:id>')
def profile_teacher(id):
    teacher = {}
    for teacher_id in teachers.keys():
        if teacher_id == id:
            teacher = teachers[id]

    return render_template('profile.html', teacher=teacher)


@app.route('/goals/<goal>')
def goals_teachers(goal):
    filtered_teachers = {}
    for teacher in teachers:
        if goal in teachers[teacher]['goals']:
            filtered_teachers[teacher] = teachers[teacher]

    return render_template('goal.html', teachers=filtered_teachers, goal=goal)


@app.route('/message/<int:id>', methods=['POST', 'GET'])
def message_teacher(id):
    teacher = {}
    for teacher_id in teachers.keys():
        if teacher_id == id:
            teacher = teachers[id]
    message = request.form

    return render_template('message.html', teacher=teacher, message=message)


@app.route('/request', methods=['POST', 'GET'])
def lead_request():
    lead_form = request.form

    if lead_form:
        with open('request.json', 'r', encoding='utf-8') as f:
            contents = f.read()
            lead_form_request = json.loads(contents)

        with open('request.json', 'w', encoding='utf-8') as f:
            request_number = str(datetime.now().timestamp())  # В качестве уникального ключа берем timestamp
            order_date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")  # Время дата для заказа - это норм

            lead_form_request.update({request_number: {'order_date': order_date, 'first_name': lead_form['first_name'],
                                                       'phone': lead_form['phone'], 'goal': lead_form['goal'],
                                                       'time': lead_form['time']}})
            save_contents = json.dumps(lead_form_request)
            f.write(save_contents)

    return render_template('pick.html', thank_page=lead_form)


@app.route('/search', methods=['GET'])
def search_teacher():
    # страница зарезервирована и доступна по адресу /search?s=123
    search_sting = request.args.get('s')

    return render_template('search.html', search_sting=search_sting)


@app.route('/booking/<int:id>', methods=['POST', 'GET'])
def booking_teacher(id):
    # Шаблоне вывода реализовано три состояния:
    # 1) Если обратиться напрямую /booking/12 - напомнит пользователю что не выбрано время. Педложит перейти в профиль
    # 2) Если в url есть параметры, выведет их в форме
    # 3) Спасибо за заявку

    teacher = {}
    for teacher_id in teachers.keys():
        if teacher_id == id:
            teacher = teachers[id]

    day_of_week = {'mon': 'понедельник', 'tue': 'вторник', 'wed': 'среда', 'thu': 'четверг',
                   'fri': 'пятница', 'sat': 'суббота', 'sun': 'воскресенье'}

    booking_day = request.args.get('day')  # День и время брони, берем из параметров.
    booking_hour = request.args.get('hour')
    booking = request.form

    if booking:
        with open('booking.json', 'r', encoding='utf-8') as f:
            contents = f.read()
            order = json.loads(contents)

        with open('booking.json', 'w', encoding='utf-8') as f:
            order_number = str(datetime.now().timestamp())  # В качестве уникального ключа берем timestamp
            order_date = datetime.strftime(datetime.now(),
                                           "%Y-%m-%d %H:%M:%S")  # Время дата для заказа - это норм практика

            order.update({order_number: {'order_date': order_date, 'first_name': booking['first_name'],
                                         'phone': booking['phone'],
                                         'day': booking['day'], 'hour': booking['hour'],
                                         'teacher': booking['teacher_id']}})
            save_contents = json.dumps(order)
            f.write(save_contents)

    return render_template('booking.html', teacher=teacher, booking=booking, booking_day=booking_day,
                           booking_hour=booking_hour, day_of_week=day_of_week)


if __name__ == '__main__':
    app.run(debug=True)
