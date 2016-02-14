## Constraint Prioity Meaning
This list describes the scheduling behavior for each fact-fact constraint mapping. We also list how the schedule behaves in the absense of **any** constraint mappings between a given fact-fact pair. This is specified by the '(none)' item in each list.

### Course-Student
Courses are assigned to students either directly through Course-Student constraint and/or indirectly through Subject-Student, Course-StudentGroup and StudentGroup-Subject. Courses are assigned indirectly to the student by these constraints as follows:

* **Subject-Student** : At least one of the courses in the subject is assigned to the student. This constraint is satisfied when there is at least one Course-Student constraint for a course in the subject.
* **Course-StudentGroup** : The course is assigned to each student in the student group
* **Subject-StudentGroup** : At least one of the courses in the subject is assigned to each student in the student group. This constraint is satisfied for a student when there is at least one Course-Student constraint for the student and a course in the subject.

#### Course-Student Priorities
* **mandatory** : The student **must** be assigned to the course. The set of mandatory courses for a student is the union of the sets of mandatory courses from Course-Student, Subject-Student, Course-StudentGroup, and StudentGroup-Subject constraints. If a student has more mandatory assignments than can fit in a single schedule the scheduler precheck will fail.  

*TODO: The administrator needs to be able to designate the set of courses that the student can choose from. This would likely be done on the Subject-StudentGroup constraint. For example, the 9th grade math classes are not available to the 7th grade student group.*

*TODO: The student needs to be able to specify his/her 1st, 2nd, 3rd, etc.. choice for extra courses. This should probably be specified on Course-Student constraints (how many levels should we allow? or maybe we set an int and just order them and don't care about setting a limit?)*
 
* **(none)** : If there are no courses assigned to a student either directly or indirectly the scheduler assumes any course can be selected to fill all available timeblocks for the student.

### Course-Teacher
* **mandatory** : The teacher **must** be assigned to the class as much as possible. If the teacher cannot be assigned to the course for at least one class then the scheduler should fail. 
* **high** : The teacher is prefered for the course over teachers without a mandatory constraint to the course.
* **low** : The teacher is prefered for the course over teachers without any constraints to the course.
* **(none)** : If there are no Course-Teacher constraints for the course and teacher then the scheduler assumes any teacher can be assigned to the course.

*TODO: We need to be able to specify the set of courses available to be chosen for a teacher. Some teachers are not allowed to teach some subjects.*

### Course-Timeblock, Teacher-Timeblock, Classroom-Timeblock, Student-Timeblock
Timeblock constriaints define the sets of timeblocks that must be used when the scheduler is creating classes for the given object. The priorities define the ordering the scheduler must follow when choosing timeblocks from the set. For example, if the scheduler decides that four classes of course x are needed, and there are two mandatory constraints, one high constraint and two low constraint, then the scheduler must use both mandatory timeblocks, then the one high timeblock and finally one of the two low timeblocks . If the scheduler needs more timeblocks than there are constraints of any priority, the scheduler is free to choose any timeblock.

**Note:** Courses, Teachers, Classrooms, and Students have the properties 'avail_start_time' and 'avail_end_time' which define the overall start and end time assignments. If either of these properties are set the timeblocks occuring within the available time represent the set of timeblocks that **can be** assigned to the course, teacher, classroom, or student.

### Classroom-Course
* **mandatory** : The course **must** be assigned to the classroom. Multiple mandatory constraints define the set of classrooms that are available to the course.
* **high** : The scheduler should prefer the classroom over low priority and classrooms without constraints to the course when scheduling the course. 
* **low** : The scheduler should prefer the the classroom over classrooms without constraints to the course when scheduling the course.
* **(none)** : If the set of Classroom-Course constraints for the classroom and course is empty, then the scheduler is free to choose any classroom for the course

### Classroom-Teacher
* **mandatory** : The teacher **must** be assigned to the classroom. Multiple mandatory constraints define the set of classrooms that are available to the teacher.
* **high** : The scheduler should prefer the classroom over low priority and classrooms without constraints to the teacher when scheduling the teacher. 
* **low** : The scheduler should prefer the the classroom over classrooms without constraints to the teacher when scheduling the teacher.
* **(none)** : If the set of Classroom-Teacher constraints for the classroom and teacher is empty, then the scheduler is free to choose any classroom for the teacher

### Student-StudentGroup
This constraint means the student is a member of the student group. Priorities are not relevant in this constraint.

*TODO: Is this true? do priorities make sense here?*

### Course-Subject
This constraint means the course is part of the subject. Priorities are not relevant in this constraint.

*TODO: Is this true? do priorities make sense here?*



