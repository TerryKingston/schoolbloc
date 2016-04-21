from schoolbloc import app, db
from schoolbloc.users.models import User, Role
from schoolbloc.scheduler.models import *
from schoolbloc.config import config
from random import *
import sys

class SchedulerTestUtilities():
    @staticmethod
    def generate_timeblocks(day_start_time=None, 
                             day_end_time=None, 
                             break_length=None, 
                             lunch_start=None, 
                             lunch_end=None,
                             class_duration=None):
        """
        Creates a list of Timeblock objects and stores them in self.time_block. 
        The Timeblock start and end times are calculated based on the Scheduler attributes
        day_start_time, class_duration, break_length, lunch_start, lunch_end, and day_end_time 
        """
        # if values aren't provided, get the defaults from the config file
        day_start_time = day_start_time or config.school_start_time
        day_end_time = day_end_time or config.school_end_time
        break_length = break_length or config.time_between_classes
        lunch_start = lunch_start or config.lunch_start
        lunch_end = lunch_end or config.lunch_end
        class_duration = class_duration or config.block_size

        # convert the values to integers of the number of minutes from 0:00
        day_start_mins = SchedulerTestUtilities.convert_time_to_minutes(day_start_time)
        day_end_mins = SchedulerTestUtilities.convert_time_to_minutes(day_end_time)
        lunch_start_mins = SchedulerTestUtilities.convert_time_to_minutes(lunch_start)
        lunch_end_mins = SchedulerTestUtilities.convert_time_to_minutes(lunch_end)

        time_blocks = [(815, 905), (910, 1000), (1010, 1100), (1245, 1335), (1340, 1430)] # tuples as (start_time, end_time)

        # cur_time = day_start_mins
        # while cur_time < lunch_start_mins:
        #     start_time = SchedulerTestUtilities.convert_minutes_to_time(cur_time)
        #     end_time = SchedulerTestUtilities.convert_minutes_to_time(cur_time + class_duration)
        #     time_blocks.append((start_time, end_time))
        #     cur_time += class_duration + break_length

        # cur_time = lunch_end_mins
        # while cur_time < day_end_mins:
        #     start_time = SchedulerTestUtilities.convert_minutes_to_time(cur_time)
        #     end_time = SchedulerTestUtilities.convert_minutes_to_time(cur_time + class_duration)
        #     time_blocks.append((start_time, end_time))
        #     cur_time += class_duration + break_length
        
        # Right now, we just support the MW, TT, F timeblock sets
        monday = Day.query.filter_by(name="Monday")[0]
        tuesday = Day.query.filter_by(name="Tuesday")[0]
        wednesday = Day.query.filter_by(name="Wednesday")[0]
        thursday = Day.query.filter_by(name="Thursday")[0]
        friday = Day.query.filter_by(name="Friday")[0]
        for t in time_blocks: 
            mwfTimeblock = Timeblock(start_time=t[0], end_time=t[1])
            ttTimeblock = Timeblock(start_time=t[0], end_time=t[1])
            db.session.add(mwfTimeblock)
            db.session.add(ttTimeblock)
            db.session.flush()
            db.session.add(TimeblocksDay(day_id=monday.id, timeblock_id=mwfTimeblock.id))
            db.session.add(TimeblocksDay(day_id=wednesday.id, timeblock_id=mwfTimeblock.id))
            db.session.add(TimeblocksDay(day_id=tuesday.id, timeblock_id=ttTimeblock.id))
            db.session.add(TimeblocksDay(day_id=thursday.id, timeblock_id=ttTimeblock.id))
            db.session.add(TimeblocksDay(day_id=friday.id, timeblock_id=mwfTimeblock.id))

        db.session.commit()

        return time_blocks

    @staticmethod
    def convert_time_to_minutes(time):
        """
        takes an integer in 24 hr format (eg. 1400 for 2:00PM ) and converts it to an integer
        representing the number of minutes from time=0:00
        """
        hrs = (time / 100)
        mins = time - hrs * 100

        return int(hrs * 60 + mins)

    @staticmethod
    def convert_minutes_to_time(minutes):
        """
        takes an integer representing the number of minutes from time=0:00 and returns an integer
        representing the time in 24hr format (eg. 1400 = 2:00PM)
        """
        hrs = (minutes / 60) * 100
        mins = minutes % 60

        return int(hrs + mins)


    @staticmethod
    def generate_students(n, names=None):
        """ returns n students in a list after saving them to the DB """
        if names:
            if len(names) < n:
                raise ArgumentException("names list must be lenght == n")
        else:
            names = [ ['student_f_%s' % random(), 'student_l_%s' % random()] for i in range(n) ]

        # s_user_list = [ User("{} {}".format(names[i][0], names[i][1]), 'password', 'student') 
        #                 for i in range(n) ]
        
        # for u in s_user_list: db.session.add(u)
        # db.session.flush()

        stud_list = [ Student(first_name=names[i][0], 
                              last_name=names[i][1],
                              uid="{}".format(randint(0, 1000000)))
                      for i in range(n) ]

        for s in stud_list: db.session.add(s)
        db.session.commit()
        return stud_list

    @staticmethod
    def generate_teachers(n, names=None, avail_start_time=None, avail_end_time=None):
        if names:
            if len(names) < n:
                raise ArgumentException("names list must be lenght == n")
        else:
            names = [ ['teacher_f_%s' % random(), 'teacher_l_%s' % random()] for i in range(n) ]

        # t_user_list = [ User("{} {}".format(names[i][0], names[i][1]), 'password', 'teacher') for i in range(n) ]
        # for u in t_user_list: db.session.add(u)
        # db.session.flush()

        teach_list = [ Teacher(first_name=names[i][0], 
                               last_name=names[i][1],
                               uid="{}".format(randint(0, 1000000)),
                               avail_start_time=avail_start_time,
                               avail_end_time=avail_end_time) 
                       for i in range(n) ]

        for t in teach_list: db.session.add(t)
        db.session.commit()
        return teach_list

    def get_names(n):
        """
        Returns a list of up to 350 names, in tuple form (first, last)
        """
        name_file = "schoolbloc/scheduler/student_names.txt"
        name_list = []
        with open(name_file) as names:
            for line in names:
                if len(line) > 0:
                    name_list.append(line.split()[0:2])
                    if len(name_list) >= n:
                        return name_list
        return name_list

    @staticmethod
    def generate_classrooms(n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        rooms = [ Classroom(room_number=randint(0, 1000000), 
                            max_student_count=max_student_count,
                            avail_start_time=avail_start_time,
                            avail_end_time=avail_end_time) 
                  for i in range(n) ]

        for r in rooms:
            db.session.add(r)
        db.session.commit()
        return rooms

    @staticmethod
    def generate_courses(n, max_student_count=None, avail_start_time=None, avail_end_time=None):
        courses = [ Course(name="course {}".format(randint(0, 1000000)),
                           max_student_count=max_student_count,
                           avail_start_time=avail_start_time,
                           avail_end_time=avail_end_time) 
                    for i in range(n) ]

        for r in courses:
            db.session.add(r)
        db.session.commit()
        return courses

    @staticmethod
    def generate_subjects(n, max_student_count=None):
        subjects = [ Subject(name="subject {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in subjects:
            db.session.add(r)
        db.session.commit()
        return subjects

    @staticmethod
    def generate_student_groups(n):
        student_groups = [ StudentGroup(name="student group {}".format(randint(0, 1000000))) for i in range(n) ]

        for r in student_groups:
            db.session.add(r)
        db.session.commit()
        return student_groups