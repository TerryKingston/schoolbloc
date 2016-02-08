

class Schedule:
    def __init__(self, course_list):
        self.courses = {}
        self.errors = []
        for course in course_list:
            if course.id not in self.courses:
                self.courses[course.id] = []
            self.courses[course.id].append(course)

    def __repr__(self):
        rep = "course_id | room_id | teacher_id | time_block | max_students | student_count \n"
        for course_id, class_list in self.courses.items():
            for cls in class_list:
                rep += "    {}     |    {}    |     {}      |     {}      |      {}      |      {}\n".format(
                        cls.id, cls.room_id, cls.teacher_id, cls.timeblock_index, cls.max_student_count, len(cls.students))
                rep += "      Students: {}\n\n".format([ s.id for s in cls.students] )

        return rep


    def schedule_student_required_classes(self, student):
        for course_id in student.required_courses:
            if not self._add_student_to_course(student, course_id):
                msg = "Failed adding course {} to student {}".format(course_id, student.id)
                self.errors.append(msg)
                return False
        return True


    def schedule_student_optional_classes(self, student):
        # dunno if this is a good idea or not, but worth looking into
        for course_id in student.optional_courses:
            if not self._add_student_to_course(student, course_id):
                msg = "Failed adding course {} to student {}".format(course_id, student.id)
                self.errors.append(msg)
                return False
        return True


    def _add_student_to_course(self, student, course_id):
        """
        Attempts to add the given student to a course. Returns true if the
        student was successfully added to this course, false if the student
        could not be added to this course

        :param student:
        :param course_id:
        :return:
        """
        course_list = self.courses[course_id]
        for i in range(len(course_list)):
            if course_list[i].add_student(student):
                # Keep the list ordered from least full to most full classes
                try:
                    if course_list[i] > course_list[i+1]:
                        course_list[i], course_list[i+1] = course_list[i+1], course_list[i]
                except IndexError:
                    pass
                return True

        # TODO If a student doesn't fit in this course, so if we can swap around
        #      some of their classes so they are in a different place in the
        #      schedule, and get this class to fit in their schedule

        return False


class Course:
    def __init__(self, id, room_id, teacher_id, timeblock_index, max_students, min_students):
        self.id = id
        self.room_id = room_id
        self.teacher_id = teacher_id
        self.timeblock_index = timeblock_index
        self.max_student_count = max_students
        self.min_student_count = min_students
        self.students = []

    def add_student(self, student):
        # Class full or student already schedules during this time
        if len(self.students) == self.max_student_count:
            return False
        if student.timeblocks[self.timeblock_index]:
            return False

        self.students.append(student)
        student.timeblocks[self.timeblock_index] = self
        return True


class Student:
    def __init__(self, id, num_of_timeblocks, required_courses, optional_courses):
        """
        Student object for building a schedules

        :param id: the student model's id
        :param num_of_timeblocks:  number of blocks in a day
        :param required_courses:   list of required courese ids
        :param optional_courses:   list of optional course ids
        :return:
        """
        self.id = id
        self.timeblocks = {}
        for i in range(num_of_timeblocks):
            self.timeblocks[i] = None
        self.required_courses = required_courses
        self.optional_courses = optional_courses
