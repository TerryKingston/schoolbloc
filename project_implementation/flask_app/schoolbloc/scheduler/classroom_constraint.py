from schoolbloc.scheduler.models import *
import schoolbloc.scheduler.scheduler_util as SchedUtil

class ClassroomConstraint:
    def __init__(self, classroom_id):
        self.classroom_id = classroom_id
        self.subject_ids = []

        self.mand_timeblock_ids = []
        self.high_timeblock_ids = []
        self.low_timeblock_ids = []

        self.calc_subject_ids()
        self.calc_timeblock_constraints()


    def relax_constraints(self, class_id):
        if len(self.mand_timeblock_ids) == 0 and len(self.high_timeblock_ids) > 0:
            SchedUtil.log_note("info", "Scheduler", "Relaxing the classroom->timeblock constraints for class {} (classroom: {})".format(
                    class_id, self.classroom_id))
            self.high_classroom_ids = []
            return 

        return False

    def can_relax_constraints(self):
        """
        Returns true if this teacher or its descendants contains high priority constraints that can
        fall back to low priority constraints
        """

        if len(self.mand_timeblock_ids) == 0 and len(self.high_timeblock_ids) > 0:
                return True

        return False

    def get_timeblock_ids(self):
        if len(self.mand_timeblock_ids) > 0:
            return self.mand_timeblock_ids
        elif len(self.high_timeblock_ids) > 0:
            return self.high_timeblock_ids
        else:
            return self.low_timeblock_ids

    def calc_subject_ids(self):
        cs_list = ClassroomsSubject.query.filter_by(classroom_id=self.classroom_id).all()
        self.subject_ids = [ cs.subject_id for cs in cs_list ] 

    def calc_timeblock_constraints(self, input_mand_ids=None, input_high_ids=None, input_low_ids=None):

        self.mand_timeblock_ids = [ ct.timeblock_id for ct in 
                        ClassroomsTimeblock.query.filter_by(priority='mandatory', 
                                                            classroom_id=self.classroom_id,
                                                            active=True).all() ]
        self.high_timeblock_ids = [ ct.timeblock_id for ct in 
                        ClassroomsTimeblock.query.filter_by(priority='high', 
                                                            classroom_id=self.classroom_id,
                                                            active=True).all() ]
        self.low_timeblock_ids = [ ct.timeblock_id for ct in 
                        ClassroomsTimeblock.query.filter_by(priority='low', 
                                                            classroom_id=self.classroom_id,
                                                            active=True).all() ]
        not_timeblock_ids = [ ct.timeblock_id for ct in 
                        ClassroomsTimeblock.query.filter_by(priority='not', 
                                                            classroom_id=self.classroom_id,
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
            not_timeblock_ids += [ st.timeblock_id for st in 
                             SubjectsTimeblock.query.filter_by(priority='not', 
                                                               subject_id=subject_id,
                                                               active=True).all() ]

        # if our low id set is empty. we assume all timeblocks are in the low set
        if len(self.low_timeblock_ids) == 0: 
            self.low_timeblock_ids = [ t.id for t in Timeblock.query.all() ]

        self.mand_timeblock_ids = set(self.mand_timeblock_ids) - set(not_timeblock_ids)
        self.high_timeblock_ids = set(self.high_timeblock_ids) - set(not_timeblock_ids)
        self.low_timeblock_ids = set(self.low_timeblock_ids) - set(not_timeblock_ids)