import logging
import unittest

from lxml import etree

from app.test_jmx import test_multiple_configurations_dont_exist

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_duplicate_configurations(self):

        file = etree.parse('data/MultiConfigExpectedToFail.jmx')

        try:
            test_multiple_configurations_dont_exist(file)
            raise Exception
        # Expecting Assertion Error
        except AssertionError:
            pass

    def test_no_duplicate_configurations(self):

        file = etree.parse('data/MultiConfigExpectedNoDuplicates.jmx')

        test_multiple_configurations_dont_exist(file)


if __name__ == '__main__':
    unittest.main()
