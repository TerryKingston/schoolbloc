from schoolbloc.scheduler.models import Timeblock, ScheduledClass, Schedule, ScheduledClassesStudent, Day
from schoolbloc import db
from datetime import datetime

class ScheduleData:
    def __init__(self, class_list):
        self.scheduled_classes = {}
        self.errors = []

        self.timeblocks = {}
        for timeblock in Timeblock.query.all():
            self.timeblocks[timeblock.id] = timeblock

        for cls in class_list:
            if cls.course_id not in self.scheduled_classes:
                self.scheduled_classes[cls.course_id] = []
            self.scheduled_classes[cls.course_id].append(cls)

    def __repr__(self):
        rep = "course_id | room_id | teacher_id | time_block | max_students | student_count \n"
        for course_id, class_list in self.scheduled_classes.items():
            for cls in class_list:
                rep += "    {}     |    {}    |     {}      |     {}      |      {}      |      {}\n".format(
                        cls.course_id, cls.room_id, cls.teacher_id, cls.timeblock_id, cls.max_student_count, len(cls.students))
                rep += "      Students: {}\n\n".format([ s.id for s in cls.students] )

        return rep

    def save(self):
        db_schedule = Schedule(name="Sample Schedule", created_at=datetime.now())
        db.session.add(db_schedule)
        db.session.flush()
        

        for course_id, cls_list in self.scheduled_classes.items():
            for c in cls_list:
                start_time = self.timeblocks[c.timeblock_id].start_time
                end_time = self.timeblocks[c.timeblock_id].end_time
                days = []
                for td in self.timeblocks[c.timeblock_id].timeblocks_days:
                    days.append(Day.query.get(td.day_id).name)
                
                sorted_days = []
                if "Monday" in days:
                    sorted_days.append("Monday")
                if "Tuesday" in days:
                    sorted_days.append("Tuesday")
                if "Wednesday" in days:
                    sorted_days.append("Wednesday")
                if "Thursday" in days:
                    sorted_days.append("Thursday")
                if "Friday" in days:
                    sorted_days.append("Friday")
                if "Saturday" in days:
                    sorted_days.append("Saturday")

                days_string = ", ".join(sorted_days)

                cls = ScheduledClass(schedule_id=db_schedule.id, teacher_id=c.teacher_id, course_id=c.course_id, 
                                     classroom_id=c.room_id, start_time=start_time, end_time=end_time, days=days_string)
                db.session.add(cls)
                db.session.flush()

                # now add the students
                for stud in c.students:
                    cs = ScheduledClassesStudent(student_id=stud.id, scheduled_class_id=cls.id)
                    db.session.add(cs)

        db.session.commit()


    # def schedule_student_required_classes(self, student):
    #     for course_id in student.required_course_ids:
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

    def schedule_student(self, student_id, required_course_ids, optional_course_ids):
        student = ScheduleStudent(student_id, required_course_ids, optional_course_ids, self.timeblocks)        
        collisions = self.schedule_student_to_courses(student, 0)
        return collisions

    def clear_all_students(self):
        for course_id, class_list in self.scheduled_classes.items():
            for sch_class in class_list:
                sch_class.drop_all_students()
            
    def schedule_student_to_courses(self, student, course_index):
        """
        returns a list of collisions that occurred when attempting to schedule the student
        to the course. If the student is scheduled successfully, an empty list is returned
        """
        if course_index >= len(student.required_course_ids):
            return []
        
        collisions = []
        # loop through the list of scheduled classes for each course
        # to find one that is free
        course_id = student.required_course_ids[course_index]
        if course_id not in self.scheduled_classes:
            raise Exception("student {}, course {} not in scheduled classes".format(student.id, course_id))
        for sch_class in self.scheduled_classes[course_id]:
            # if the time block for this class is not already 
            # filled with something else for this student, then use
            # this class and recursively assign the next class
            collision = sch_class.add_student(student)
            if collision:
                collisions.append(collision)
                # add the collision to the list, then try the next class
            else:
                col_list = self.schedule_student_to_courses(student, course_index + 1)
                if len(col_list) == 0:
                    # Success!, now reorder the scheduled class list to move this one to the end
                    # if its student count is greater than min and greater than 3/4 max size
                    s_count = len(sch_class.students)
                    if s_count > sch_class.min_student_count and s_count > int(0.75 * sch_class.max_student_count):
                        self.scheduled_classes[course_id].remove(sch_class)
                        self.scheduled_classes[course_id].append(sch_class)
                    return [] # return an empty list to indicate the student was placed
                else:
                    sch_class.drop_student(student)
                    collisions += col_list
            # else, try the next class
        # If we didn't find any classes that would work then return false
        return collisions

    def min_student_counts_satisfied(self):
        """
        Returns true if the min student counts of all classes have been met. False otherwise
        """
        for course_id, sch_class_list in self.scheduled_classes.items():
            for sch_class in sch_class_list:
                if len(sch_class.students) < sch_class.min_student_count:
                    return False
        return True

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
    def __init__(self, course_id, room_id, teacher_id, timeblock_id, max_students, min_students):
        self.course_id = course_id
        self.room_id = room_id
        self.teacher_id = teacher_id
        self.timeblock_id = timeblock_id
        self.max_student_count = max_students
        self.min_student_count = min_students
        self.students = []

    def add_student(self, student):
        # Class full or student already schedules during this time
        if len(self.students) >= self.max_student_count:
            # print("course {} count= {} max={}".format(self.course_id, len(self.students), self.max_student_count))
            return ScheduleCollision(student, self, "full class")
        if student.timeblock_to_course[self.timeblock_id]:
            return ScheduleCollision(student, self, "timeblock")

        self.students.append(student)
        student.timeblock_to_course[self.timeblock_id] = self
        return None

    def drop_student(self, student):
        self.students.remove(student)
        student.timeblock_to_course[self.timeblock_id] = None

    def drop_all_students(self):
        self.students = []

class ScheduleStudent:
    def __init__(self, id, required_course_ids, optional_course_ids, timeblocks):
        """
        Student object for building a schedules

        :param id: the student model's id
        :param num_of_timeblocks:  number of blocks in a day
        :param required_courses:   list of required courese ids
        :param optional_courses:   list of optional course ids
        :return:
        """
        self.id = id
        self.required_course_ids = required_course_ids
        self.optional_course_ids = optional_course_ids
        # map timeblocks to classes
        self.timeblock_to_course = {}
        for t_id, timeblock in timeblocks.items():
            self.timeblock_to_course[t_id] = None 

    # def get_avail_timeblocks(self):
    #     """
    #     returns a list of timeblock ids that are not assigned to 
    #     a course.
    #     """
    #     time_list = []
    #     for timeblock_id, course in self.timeblocks.items():
    #         if not course:
    #             time_list.append(timeblock_id)
    #     return time_list

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