import unittest
import os
from schoolbloc.students.models import Student
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.courses.models import Course
from schoolbloc.testing.testing import BaseTestClass
from schoolbloc.data_import import csv_import


class ImportTests(BaseTestClass):
    def test_something(self):
        self.assertEqual(True, True)

    def test_add_students(self):
        location = os.getcwd()
        filepath = os.path.join(location, 'schoolbloc', 'data_import', 'testing_data', 'students.csv')
        csv_import.students_import(filepath)
        students = Student.query.all()
        student = students.pop()
        self.assertEqual('{} {}'.format(student.first_name, student.last_name), 'amy little')

    def test_add_teachers(self):
        location = os.getcwd()
        filepath = os.path.join(location, 'schoolbloc', 'data_import', 'testing_data', 'teachers.csv')
        csv_import.teachers_import(filepath)
        teachers = Teacher.query.all()
        teacher = teachers.pop()
        self.assertEqual(teacher.first_name + ' ' + teacher.last_name, 'ron weasley')

    def test_add_courses(self):
        location = os.getcwd()
        filepath = os.path.join(location, 'schoolbloc', 'data_import', 'testing_data', 'courses.csv')
        csv_import.courses_import(filepath)
        courses = Course.query.all()
        course = courses.pop()
        self.assertEqual(course.name, 'CIS 1020')

    def test_add_classroom(self):
        location = os.getcwd()
        filepath = os.path.join(location, 'schoolbloc', 'data_import', 'testing_data', 'classrooms.csv')
        csv_import.classrooms_import(filepath)
        classrooms = Classroom.query.all()
        classroom = classrooms.pop()
        self.assertEqual(classroom.room_number, 311)


if __name__ == '__main__':
    unittest.main()
