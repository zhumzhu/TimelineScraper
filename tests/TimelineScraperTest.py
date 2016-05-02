import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from TimelineScraper import *

'''
TEST CLASSES
'''
import unittest
class TimelineScraperStatusTest(unittest.TestCase):
    class TimelineScraperStub(object):
        def __init__(self,name,workspace):
            self._name = name
            self.workspace = workspace

    def setUp(self):
        print("setting up test")

    # @unittest.skip("skip one")
    def test01(self):
        tcStub = TimelineScraperStatusTest.TimelineScraperStub("hello","../data/")
        status = TimelineScraperStatus(tcStub)
        print(status)
        
    def test2(self):
        tcStub = TimelineScraperStatusTest.TimelineScraperStub("hello2","../data/")
        status = TimelineScraperStatus(tcStub, statusDict = {
            'max_id_i_have': 10,
            'request_to': 11,
            'request_since': 12,
            'min_id_i_have' : 13})
        status.save()

        returnedStatus = TimelineScraperStatus(tcStub)
        self.assertEqual(returnedStatus.request_to, 11)
        print(returnedStatus)

if __name__ == '__main__':
    unittest.main()