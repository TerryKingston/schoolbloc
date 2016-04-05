from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.teacher_constraint import TeacherConstraint
from schoolbloc.scheduler.classroom_constraint import ClassroomConstraint
import schoolbloc.scheduler.scheduler_util as SchedUtil

class ClassConstraint:
    def __init__(self, course_id, course_name):
        """
        Represents the constraints applied to a single class. These objects are generated by the 
        Scheduler and used to hold known constraints for a class (for example, it's course).
        """
        self.course_id = course_id
        self.course_name = course_name
        self.z3_index = 0
        self.student_count = 0

        self.mand_teacher_constraints = []
        self.high_teacher_constraints = []
        self.low_teacher_constraints = []

        self.mand_classroom_constraints = []
        self.high_classroom_constraints = []
        self.low_classroom_constraints = []

        self.mand_timeblock_ids = []
        self.high_timeblock_ids = []
        self.low_timeblock_ids = []

        self.subject_ids = []

        # now apply the constraints to this class
        self.calc_subject_ids()
        self.calc_constraints()

    def relax_constraints(self):
        #TODO should take a more intellegent approach to this, but for now, blindly grab one and relax it
        if len(self.mand_teacher_constraints) == 0:
            if len(self.high_teacher_constraints) > 0:
                msg = "Relaxing the course->teacher constraints for class {} (course: {} {})".format(
                        self.z3_index, self.course_id, self.course_name)
                SchedUtil.log_note("info", "Scheduler", msg)
                    
                self.high_teacher_constraints = []
                return
            else:
                for tc in self.low_teacher_constraints:
                    if tc.can_relax_constraints():
                        tc.relax_constraints(self.z3_index)
                        return

        if len(self.mand_classroom_constraints) == 0:
            if len(self.high_classroom_constraints) > 0:
                msg = "Relaxing the course->classroom constraints for class {} (course: {} {})".format(
                    self.z3_index, self.course_id, self.course_name)
                SchedUtil.log_note("info", "Scheduler", msg)
                self.high_classroom_constraints = []
                return 
            else:
                for cc in self.low_classroom_constraints:
                    if cc.can_relax_constraints():
                        cc.relax_constraints(self.z3_index)
                        return 

        if len(self.mand_timeblock_ids) == 0 and len(self.high_timeblock_ids) > 0:
            msg = "Relaxing the course->timeblock constraints for class {} (course: {} {})".format(
                    self.z3_index, self.course_id, self.course_name)
            SchedUtil.log_note("info", "Scheduler", msg)
            self.high_timeblock_ids = []
            return 

        return False

    def can_relax_constraints(self):
        """
        Returns true if this class or its descendants contains high priority constraints that can 
        fall back to low priority constraints
        """
        if len(self.mand_teacher_constraints) == 0:
            if len(self.high_teacher_constraints) > 0:
                return True
            else:
                for tc in self.low_teacher_constraints:
                    if tc.can_relax_constraints():
                        return True

        if len(self.mand_classroom_constraints) == 0:
            if len(self.high_classroom_constraints) > 0:
                return True
            else:
                for cc in self.low_classroom_constraints:
                    if cc.can_relax_constraints():
                        return True

        if len(self.mand_timeblock_ids) == 0 and len(self.high_timeblock_ids) > 0:
            return True

        return False

           
    
    def get_teacher_constraints(self):
        if len(self.mand_teacher_constraints) > 0:
            return self.mand_teacher_constraints
        elif len(self.high_teacher_constraints) > 0:
            return self.high_teacher_constraints
        else:
            return self.low_teacher_constraints

    def get_classroom_constraints(self):
        if len(self.mand_classroom_constraints) > 0:
            return self.mand_classroom_constraints
        elif len(self.high_classroom_constraints) > 0:
            return self.high_classroom_constraints
        else:
            return self.low_classroom_constraints

    def get_timeblock_ids(self):
        if len(self.mand_timeblock_ids) > 0:
            return self.mand_timeblock_ids
        elif len(self.high_timeblock_ids) > 0:
            return self.high_timeblock_ids
        else:
            return self.low_timeblock_ids

    def get_teacher_ids(self):
        return [ t.teacher_id for t in self.get_teacher_constraints() ]

    def get_classroom_ids(self):
        return [ c.classroom_id for c in self.get_classroom_constraints() ]
        
    def calc_subject_ids(self):
        course_subject_list = CoursesSubject.query.filter_by(course_id=self.course_id).all()
        self.subject_ids = [ cs.subject_id for cs in course_subject_list ]
    
    def calc_constraints(self):
        # first calculate the timeblock and classroom id lists
        self.mand_timeblock_ids = [ ct.timeblock_id for ct in 
                        CoursesTimeblock.query.filter_by(priority='mandatory', 
                                                            course_id=self.course_id,
                                                            active=True).all() ]
        self.high_timeblock_ids = [ ct.timeblock_id for ct in 
                        CoursesTimeblock.query.filter_by(priority='high', 
                                                            course_id=self.course_id,
                                                            active=True).all() ]
        self.low_timeblock_ids = [ ct.timeblock_id for ct in 
                        CoursesTimeblock.query.filter_by(priority='low', 
                                                            course_id=self.course_id,
                                                            active=True).all() ]
        for subject_id in self.subject_ids:
            self.mand_timeblock_ids += [ st.timeblock_id for st in 
                             SubjectsTimeblock.query.filter_by(priority='mandatory', 
                                                               subject_id=subject_id,
                                                               active=True).all() ]
            self.high_timeblock_ids += [ st.timeblock_id for st in 
                             SubjectsTimeblock.query.filter_by(priority='high', 
                                                               subject_id=subject_id,
                                                               active=True).all() ]
            self.low_timeblock_ids += [ st.timeblock_id for st in 
                             SubjectsTimeblock.query.filter_by(priority='low', 
                                                               subject_id=subject_id,
                                                               active=True).all() ]

        # if our low id set is empty. we assume all timeblocks are in the low set
        if len(self.low_timeblock_ids) == 0: 
            self.low_timeblock_ids = [ t.id for t in Timeblock.query.all() ]


        # now calculate the classrooms
        mand_classroom_ids = [ ct.classroom_id for ct in 
                               ClassroomsCourse.query.filter_by(priority='mandatory', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        high_classroom_ids = [ ct.classroom_id for ct in 
                               ClassroomsCourse.query.filter_by(priority='high', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        low_classroom_ids = [ ct.classroom_id for ct in 
                               ClassroomsCourse.query.filter_by(priority='low', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        for subject_id in self.subject_ids:
            mand_classroom_ids += [ cs.classroom_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='mandatory', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]
            high_classroom_ids += [ cs.classroom_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='high', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]
            low_classroom_ids += [ cs.classroom_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='low', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]
        
        # if our low id set is empty. we assume all timeblocks are in the low set
        if len(low_classroom_ids) == 0:
            low_classroom_ids = [ c.id for c in Classroom.query.all() ]

        # now make a set of ClassroomConstraints from each list
        self.mand_classroom_constraints = [ ClassroomConstraint(c_id) for c_id in mand_classroom_ids ]
        self.high_classroom_constraints = [ ClassroomConstraint(c_id) for c_id in high_classroom_ids ]
        self.low_classroom_constraints = [ ClassroomConstraint(c_id) for c_id in low_classroom_ids ]

        # now calculate the Teacher ids
        mand_teacher_ids = [ ct.teacher_id for ct in 
                               CoursesTeacher.query.filter_by(priority='mandatory', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        high_teacher_ids = [ ct.teacher_id for ct in 
                               CoursesTeacher.query.filter_by(priority='high', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        low_teacher_ids = [ ct.teacher_id for ct in 
                               CoursesTeacher.query.filter_by(priority='low', 
                                                                 course_id=self.course_id,
                                                                 active=True).all() ]
        for subject_id in self.subject_ids:
            mand_teacher_ids += [ cs.teacher_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='mandatory', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]
            high_teacher_ids += [ cs.teacher_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='high', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]
            low_teacher_ids += [ cs.teacher_id for cs in 
                                    ClassroomsSubject.query.filter_by(priority='low', 
                                                                      subject_id=subject_id,
                                                                      active=True).all() ]

        # if our low id set is empty. we assume all timeblocks are in the low set
        if len(low_teacher_ids) == 0:
            low_teacher_ids = [ c.id for c in Classroom.query.all() ]


        # now make a set of TeacherConstraints from each list
        self.mand_teacher_constraints = [ TeacherConstraint(t_id) for t_id in mand_teacher_ids ]
        self.high_teacher_constraints = [ TeacherConstraint(t_id) for t_id in high_teacher_ids ]
        self.low_teacher_constraints = [ TeacherConstraint(t_id) for t_id in low_teacher_ids ]
