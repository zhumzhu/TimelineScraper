import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import unittest
from TimelineScraperManager import create_scraper_from_config
from TimelineScraperManager import get_results_store

class TimelineScraperManagerTest(unittest.TestCase):

    def test_create_scraper_from_config(self):
        config = {
            "name" : "my_beautiful_scraper",
            "engine" : {
                "name" : "TwitterTsEngine",
                "query" : "middle east",
                "appkey" : "dsakdjsafhdsf",
                "accesstoken" : "dsadasdsadajgight"
            },
            "results_store" : {
                "name" : "FileSystemResultsStore",
                "rollover_enabled": True,
                "rollover_trigger_size": 1e6
            }
        }

        create_scraper_from_config(config)

    def test_get_results_stores(self):
        print get_results_store()



if __name__ == '__main__':
    unittest.main()