import csv
import os
import sys
from schoolbloc import app, db
from schoolbloc.students.models import Student
from schoolbloc.classrooms.models import Classroom
from schoolbloc.teachers.models import Teacher
from schoolbloc.courses.models import Course
from schoolbloc.users.models import User


def students_import():
    _location_ = os.getcwd()
    try:
        with open(os.path.join(_location_, 'students.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                u = User(username=row['first_name'], password=row['last_name'], role_type='student')
                student = Student(first_name=row['first_name'], last_name=row['last_name'], user_id=u.id)
                db.session.add(u)
                db.session.add(student)
            db.session.commit()
    except:
        db.session.rollback()


def classrooms_import():
    _location_ = os.getcwd()
    try:
        with open(os.path.join(_location_, 'classrooms.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                classroom = Classroom(room_number=row['classroom_number'], max_student_count=row['max_student_count'])
                db.session.add(classroom)
            db.session.commit()
    except:
        db.session.rollback()


def teachers_import():
    _location_ = os.getcwd()
    try:
        with open(os.path.join(_location_, 'teachers.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                u = User(username=row['last_name'], password=row['first_name'], role_type='teacher')
                teacher = Teacher(first_name=row['first_name'], last_name=row['last_name'], user_id=u.id)
                db.session.add(u)
                db.session.add(teacher)
            db.session.commit()
    except:
        db.session.rollback()


def courses_import():
    _location_ = os.getcwd()
    course_id = 0
    try:
        with open(os.path.join(_location_, 'courses.csv')) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                course = Course(name=row['course_name'], duration=row['duration'],  max_student_count=row['max_student_count'], min_student_count=row['min_student_count'])
                db.session.add(course)
                course_id += 1
            db.session.commit()
    except:
        db.session.rollback()
