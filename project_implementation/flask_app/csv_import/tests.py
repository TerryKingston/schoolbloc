import unittest
import csv_import
from schoolbloc.students.models import Student
from schoolbloc.teachers.models import Teacher
from schoolbloc.classrooms.models import Classroom
from schoolbloc.courses.models import Course
from schoolbloc.testing.testing import BaseTestClass


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_add_students(self):
        csv_import.students_import()
        students = Student.query.all()
        #print("Students: \n")
        #for student in students:
            #print(student.first_name, student.last_name)
        student = students.pop()
        self.assertEqual(student.first_name + ' ' + student.last_name, 'mary jones')

    def test_add_teachers(self):
        csv_import.teachers_import()
        teachers = Teacher.query.all()
        teacher = teachers.pop()
        #print("Teachers: \n")
        #for teacher in teachers:
        #    print(teacher.first_name, teacher.last_name)

        self.assertEqual(teacher.first_name + ' ' + teacher.last_name, 'braiden paulson')

    def test_add_courses(self):
        csv_import.courses_import()
        courses = Course.query.all()
        course = courses.pop()
        self.assertEqual(course.name, 'CIS 1020')

    def test_add_classroom(self):
        csv_import.classrooms_import()
        classrooms = Classroom.query.all()
        classroom = classrooms.pop()
        self.assertEqual(classroom.room_number, 311)


if __name__ == '__main__':
    unittest.main()
