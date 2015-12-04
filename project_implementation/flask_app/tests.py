# Import all tests we need to run here
import unittest
from schoolbloc.users.tests import UserTests
from schoolbloc.classrooms.tests import ClassroomTests
from schoolbloc.scheduler.tests import SchedulerTests

if __name__ == '__main__':
    unittest.main()

