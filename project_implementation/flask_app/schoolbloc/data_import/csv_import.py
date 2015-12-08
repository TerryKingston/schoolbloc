import csv
import os
import sys
from schoolbloc import app, db
from schoolbloc.students.models import Student
from schoolbloc.classrooms.models import Classroom
from schoolbloc.teachers.models import Teacher
from schoolbloc.courses.models import Course
from schoolbloc.users.models import User


def students_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    u = User(username=row['first_name'], password=row['last_name'],
                             role_type='student')
                    db.session.add(u)
                    db.session.flush()
                    student = Student(first_name=row['first_name'],
                                      last_name=row['last_name'], user_id=u.id)
                    db.session.add(student)
                db.session.commit()
    except:
        db.session.rollback()
        raise


def classrooms_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    classroom = Classroom(room_number=row['classroom_number'], max_student_count=row['max_student_count'])
                    db.session.add(classroom)
                db.session.commit()
    except:
        db.session.rollback()
        raise


def teachers_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    u = User(username=row['last_name'], password=row['first_name'], role_type='teacher')
                    db.session.add(u)
                    db.session.flush()
                    teacher = Teacher(first_name=row['first_name'], last_name=row['last_name'], user_id=u.id)
                    db.session.add(teacher)
                db.session.commit()
    except:
        db.session.rollback()
        raise


def courses_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    course = Course(name=row['course_name'], duration=row['duration'],  max_student_count=row['max_student_count'], min_student_count=row['min_student_count'])
                    db.session.add(course)
                db.session.commit()
    except:
        db.session.rollback()
        raise
