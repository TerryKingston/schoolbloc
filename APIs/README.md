## Constraint Prioity Meaning
This list describes the scheduling behavior for each fact-fact constraint mapping. the constraint priorities are 'mandatory', 'high' and 'low'. We also list how the schedule behaves in the absense of **any** constraint mappings between a given fact-fact pair. This is specified by the '(none)' item in each list.
### Course-Student
* mandatory : the student **must** be assigned to the course
* high : the **student prefers** the course
* low : (not used)
* (none) : the student can be assigned to any course

*TODO: do we want a setting that means 'the student cannot be assigned to the course'?*

### Course-StudentGroup
* mandatory : 
* high
* low

### Course-Subject
* mandatory
* high
* low

### Course-Teacher
* mandatory
* high
* low

### Course-Timeblock
* mandatory
* high
* low

### Classroom-Course
* mandatory
* high
* low

### Classroom-Teacher
* mandatory
* high
* low

### Classroom-Timeblock
* mandatory
* high
* low

### StudentGroup-Subject
* mandatory
* high
* low

### Student-StudentGroup
* mandatory
* high
* low

### Student-Subject
* mandatory
* high
* low

### Students-Timeblock
* mandatory
* high
* low

### StudentGroup-Timeblock
* mandatory
* high
* low

### Subject-Timeblock
* mandatory
* high
* low

### Teacher-Timeblock
* mandatory
* high
* low
