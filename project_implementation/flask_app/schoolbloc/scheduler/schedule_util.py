from schoolbloc.scheduler.models import ScheduledClass, ScheduledClassesStudent


class Schedule:
    def __init__(self, class_list):
        self.scheduled_classes = {}
        self.errors = []
        for cls in class_list:
            if cls.course_id not in self.scheduled_classes:
                self.scheduled_classes[cls.course_id] = []
            self.scheduled_classes[cls.course_id].append(cls)

    def __repr__(self):
        rep = "course_id | room_id | teacher_id | time_block | max_students | student_count \n"
        for course_id, class_list in self.scheduled_classes.items():
            for cls in class_list:
                rep += "    {}     |    {}    |     {}      |     {}      |      {}      |      {}\n".format(
                        cls.course_id, cls.room_id, cls.teacher_id, cls.timeblock_index, cls.max_student_count, len(cls.students))
                rep += "      Students: {}\n\n".format([ s.id for s in cls.students] )

        return rep

    def save(self, db_sched, db, time_block_list):
        for course_id, cls_list in self.scheduled_classes.items():
            for c in cls_list:
                start_time = time_block_list[c.timeblock_index].start
                end_time = time_block_list[c.timeblock_index].end
                cls = ScheduledClass(schedule_id=db_sched.id, teacher_id=c.teacher_id, course_id=c.course_id, 
                                     classroom_id=c.room_id, start_time=start_time, end_time=end_time)
                db.session.add(cls)
                db.session.flush()

                # now add the students
                for stud in c.students:
                    cs = ScheduledClassesStudent(student_id=stud.id, scheduled_class_id=cls.id)
                    db.session.add(cs)

        db.session.commit()

    # def schedule_student_required_classes(self, student):
    #     for course_id in student.required_courses:
    #         if not self._add_student_to_course(student, course_id):
    #             msg = "Failed adding course {} to student {}".format(course_id, student.id)
    #             self.errors.append(msg)
    #             return False
    #     return True


    # def schedule_student_optional_classes(self, student):
    #     # dunno if this is a good idea or not, but worth looking into
    #     for course_id in student.optional_courses:
    #         if not self._add_student_to_course(student, course_id):
    #             msg = "Failed adding course {} to student {}".format(course_id, student.id)
    #             self.errors.append(msg)
    #             return False
    #     return True

    def schedule_student(self, student):
        print("placing student {}".format(student.id))
        return self.schedule_student_to_courses(student, 0)
            
    def schedule_student_to_courses(self, student, course_index):
        if course_index >= len(student.required_courses):
            return True
        
        # loop through the list of scheduled classes for each course
        # to find one that is free
        course_id = student.required_courses[course_index]
        collision = None
        for sch_class in self.scheduled_classes[course_id]:
            # if the time block for this class is not already 
            # filled with something else for this student, then use
            # this class and recursively assign the next class
            collision = sch_class.add_student(student)
            if not collision:
                collision = self.schedule_student_to_courses(student, course_index + 1)
                if not collision:
                    return None
                else:
                    sch_class.drop_student(student)
            # else, try the next class
        msg = "Failed adding course {} to student {}".format(course_id, student.id)
        self.errors.append(msg)
        # If we didn't find any classes that would work then return false
        return collision


    # def _add_student_to_course(self, student, course_id):
    #     """
    #     Attempts to add the given student to a course. Returns true if the
    #     student was successfully added to this course, false if the student
    #     could not be added to this course

    #     :param student:
    #     :param course_id:
    #     :return:
    #     """
    #     course_list = self.scheduled_classes[course_id]
    #     for i in range(len(course_list)):
    #         if course_list[i].add_student(student):
    #             # Keep the list ordered from least full to most full classes
    #             try:
    #                 if course_list[i] > course_list[i+1]:
    #                     course_list[i], course_list[i+1] = course_list[i+1], course_list[i]
    #             except IndexError:
    #                 pass
    #             return True

    #     # TODO If a student doesn't fit in this course, so if we can swap around
    #     #      some of their classes so they are in a different place in the
    #     #      schedule, and get this class to fit in their schedule

    #     return False


class ScheduleClass:
    def __init__(self, course_id, room_id, teacher_id, timeblock_index, max_students, min_students):
        self.course_id = course_id
        self.room_id = room_id
        self.teacher_id = teacher_id
        self.timeblock_index = timeblock_index
        self.max_student_count = max_students
        self.min_student_count = min_students
        self.students = []

    def add_student(self, student):
        # Class full or student already schedules during this time
        if len(self.students) >= self.max_student_count:
            print ("class for course {} is full".format(self.course_id))
            return ScheduleCollision(student, self, "full class")
        if student.timeblocks[self.timeblock_index]:
            return ScheduleCollision(student, self, "timeblock")

        self.students.append(student)
        student.timeblocks[self.timeblock_index] = self
        return None

    def drop_student(self, student):
        self.students.remove(student)
        student.timeblocks[self.timeblock_index] = None


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

    def get_avail_timeblocks(self):
        """
        returns a list of timeblock ids that are not assigned to 
        a course.
        """
        time_list = []
        for timeblock_id, course in self.timeblocks:
            if not course:
                time_list.append(timeblock_id)
        return time_list

class ScheduleCollision:
    def __init__(self, student, scheduled_class, collision_type):
        """
        Represents a single collision resulting from an attempt so schedule a student
        :param student: 
        :param scheduled_class:
        :collision_type:
        """
        self.student = student
        self.scheduled_class = scheduled_class
        self.collision_type = collision_type