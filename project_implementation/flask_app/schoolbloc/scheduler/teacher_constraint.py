from schoolbloc.scheduler.models import *
from schoolbloc.scheduler.classroom_constraint import ClassroomConstraint
import schoolbloc.scheduler.scheduler_util as SchedUtil

class TeacherConstraint:
    def __init__(self, teacher_id):
        self.teacher_id = teacher_id
        self.subject_ids = []

        self.mand_classroom_constraints = []
        self.high_classroom_constraints = []
        self.low_classroom_constraints = []

        self.mand_timeblock_ids = []
        self.high_timeblock_ids = []
        self.low_timeblock_ids = []

        self.calc_subject_ids()
        self.calc_constraints()

    def relax_constraints(self, class_id):
        if len(self.mand_classroom_constraints) == 0:
            if len(self.high_classroom_constraints) > 0:
                SchedUtil.log_note("info", "Scheduler", "Relaxing the teacher->classroom constraints for class {} (teacher: {})".format(
                    class_id, self.teacher_id))
                self.high_classroom_constraints = []
                return 
            else:
                for cc in self.low_classroom_constraints:
                    if cc.can_relax_constraints():
                        cc.relax_constraints(class_id)
                        return

        if len(self.mand_timeblock_ids) == 0 and len(self.high_timeblock_ids) > 0:
                SchedUtil.log_note("info", "Scheduler", "Relaxing the teacher->timeblock constraints for class {} (teacher: {})".format(
                    class_id, self.teacher_id))
                self.high_timeblock_ids = []
                return 

        return False

    def can_relax_constraints(self):
        """
        Returns true if this teacher or its descendants contains high priority constraints that can
        fall back to low priority constraints
        """
        if len(self.mand_classroom_constraints) == 0:
            if len(self.high_classroom_constraints) > 0:
                return True
            else:
                for cc in self.low_classroom_constraints:
                    if cc.can_relax_constraints():
                        return True

        if len(self.mand_timeblock_ids) == 0:
            if len(self.high_timeblock_ids) > 0:
                return True

        return False

    def get_classroom_constraints(self):
        if len(self.mand_classroom_constraints) > 0:
            return self.mand_classroom_constraints
        elif len(self.high_classroom_constraints) > 0:
            return self.high_classroom_constraints
        else:
            return self.low_classroom_constraints

    def get_classroom_ids(self):
        return [ c.classroom_id for c in self.get_classroom_constraints() ]

    def get_timeblock_ids(self):
        if len(self.mand_timeblock_ids) > 0:
            return self.mand_timeblock_ids
        elif len(self.high_timeblock_ids) > 0:
            return self.high_timeblock_ids
        else:
            return self.low_timeblock_ids


    def calc_subject_ids(self):
        ts_list = TeachersSubject.query.filter_by(teacher_id=self.teacher_id).all()
        self.subject_ids = [ cs.subject_id for cs in ts_list ]

    def calc_constraints(self):
        # first calculate the timeblock id lists
        self.mand_timeblock_ids = [ ct.timeblock_id for ct in 
                        TeachersTimeblock.query.filter_by(priority='mandatory', 
                                                            teacher_id=self.teacher_id,
                                                            active=True).all() ]
        self.high_timeblock_ids = [ ct.timeblock_id for ct in 
                        TeachersTimeblock.query.filter_by(priority='high', 
                                                            teacher_id=self.teacher_id,
                                                            active=True).all() ]
        self.low_timeblock_ids = [ ct.timeblock_id for ct in 
                        TeachersTimeblock.query.filter_by(priority='low', 
                                                            teacher_id=self.teacher_id,
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
                               ClassroomsTeacher.query.filter_by(priority='mandatory', 
                                                                 teacher_id=self.teacher_id,
                                                                 active=True).all() ]
        high_classroom_ids = [ ct.classroom_id for ct in 
                               ClassroomsTeacher.query.filter_by(priority='high', 
                                                                 teacher_id=self.teacher_id,
                                                                 active=True).all() ]
        low_classroom_ids = [ ct.classroom_id for ct in 
                               ClassroomsTeacher.query.filter_by(priority='low', 
                                                                 teacher_id=self.teacher_id,
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


