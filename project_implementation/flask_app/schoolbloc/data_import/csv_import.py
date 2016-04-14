import csv
from schoolbloc import db
from schoolbloc.scheduler.models import Student, Classroom, Teacher, Course, Timeblock, Subject, StudentGroup
from schoolbloc.users.models import User


def students_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    student = Student(first_name=row['first_name'],
                                      last_name=row['last_name'], uid=row['uid'])
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
                    classroom = Classroom(room_number=row['classroom_number'])
                    db.session.add(classroom)
                db.session.commit()
    except:
        db.session.rollback()
        raise

def student_groups_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    studentGroup = StudentGroup(name=row['name'])
                    db.session.add(studentGroup)
                db.session.commit()
    except:
        db.session.rollback()
        raise

def subjects_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    subject = Subject(name=row['name'])
                    db.session.add(subject)
                db.session.commit()
    except:
        db.session.rollback()
        raise

def timeblocks_import(filepath):
    try:
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            with db.session.no_autoflush:
                for row in reader:
                    timeblock = Timeblock(start_time=row['start_time'], end_time=row['end_time'])
                    db.session.add(timeblock)
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
                    teacher = Teacher(first_name=row['first_name'], last_name=row['last_name'],
                                      avail_start_time=row['avail_start_time'], avail_end_time=row['avail_end_time'], uid=row['uid'])
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
                    course = Course(name=row['course_name'],
                                    max_student_count=row['max_student_count'], min_student_count=row['min_student_count'])
                    db.session.add(course)
                db.session.commit()
    except:
        db.session.rollback()
        raise
