from schoolbloc import db, User
from schoolbloc.classrooms.models import Classroom
from schoolbloc.courses.models import Course
from schoolbloc.schedules.models import Schedule, ScheduledClass, \
    ScheduledClassesStudent
from schoolbloc.students.models import Student
from schoolbloc.teachers.models import Teacher

if __name__ == '__main__':
# teachers
    u = User('ssname', 'pottersuxs', 'teacher')
    db.session.add(u)
    db.session.flush()
    teacher1 = Teacher(first_name='Severus', last_name='Snape', user_id=u.id)
    db.session.add(teacher1)
    db.session.flush()

    u = User('adombledoor', 'potterisalright', 'teacher')
    db.session.add(u)
    db.session.flush()
    teacher2 = Teacher(first_name='Avlis', last_name='Doubledoor', user_id=u.id)
    db.session.add(teacher2)
    db.session.flush()

# classrooms
    classroom1 = Classroom(room_number=101, max_student_count=15)
    db.session.add(classroom1)
    db.session.flush()

    classroom2 = Classroom(room_number=102, max_student_count=15)
    db.session.add(classroom2)
    db.session.flush()

# courses
    course1 = Course(name='Remedial Potions', duration=90, max_student_count=20,
                     min_student_count=2)
    db.session.add(course1)
    db.session.flush()

    course2 = Course(name='Defense Against the Dark Args', duration=90, max_student_count=20,
                     min_student_count=2)
    db.session.add(course2)
    db.session.flush()

# students
    u = User('hpotter', 'potterrules', 'student')
    db.session.add(u)
    db.session.flush()
    student1 = Student(first_name='Harry', last_name='Potter', user_id=u.id)
    db.session.add(student1)
    db.session.flush()

    u = User('rweasley', 'letsgonuts!', 'student')
    db.session.add(u)
    db.session.flush()
    student2 = Student(first_name='Ron', last_name='Weasly', user_id=u.id)
    db.session.add(student2)
    db.session.flush()

    u = User('llovegood', 'tralalala', 'student')
    db.session.add(u)
    db.session.flush()
    student3 = Student(first_name='Luna', last_name='Lovegood', user_id=u.id)
    db.session.add(student3)
    db.session.flush()

    u = User('hgranger', 'iwillgetALLtheAs', 'student')
    db.session.add(u)
    db.session.flush()
    student4 = Student(first_name='Hermione', last_name='Granger', user_id=u.id)
    db.session.add(student4)
    db.session.flush()

# Schedule
#schedule = Schedule(name='Spring 2016')
#db.session.add(schedule)
#db.session.flush()
#
## Scheduled classes
#sc1 = ScheduledClass(schedule_id=schedule.id, course_id=course1.id, classroom_id=classroom1.id,
#                     teacher_id=teacher1.id, start_time=900, end_time=1030)
#db.session.add(sc1)
#db.session.flush()
#
#sc2 = ScheduledClass(schedule_id=schedule.id, course_id=course2.id, classroom_id=classroom2.id,
#                     teacher_id=teacher2.id, start_time=900, end_time=1030)
#db.session.add(sc2)
#db.session.flush()
#
##  Add students to scheduled classes
#scs = ScheduledClassesStudent(scheduled_class_id=sc1.id, student_id=student1.id)
#db.session.add(scs)
#db.session.flush()
#scs = ScheduledClassesStudent(scheduled_class_id=sc1.id, student_id=student2.id)
#db.session.add(scs)
#db.session.flush()
#scs = ScheduledClassesStudent(scheduled_class_id=sc2.id, student_id=student3.id)
#db.session.add(scs)
#db.session.flush()
#scs = ScheduledClassesStudent(scheduled_class_id=sc2.id, student_id=student4.id)
#db.session.add(scs)
#db.session.flush()

# Commit everything
    print('hit1')
    db.session.commit()
    print('hit2')
