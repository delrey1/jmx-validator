import os
import unittest
from os.path import abspath

from lxml import etree

from app.test_jmx import test_data_is_valid


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_valid_data(self):
        os.environ["DATA_PARENT_LOCATION"] = os.path.join(abspath(os.path.dirname(__file__)))
        os.environ["CHECK_DATA"] = "1"
        file = etree.parse('data/HappyTestData.jmx')

        test_data_is_valid(file)

    def test_flag_not_set(self):  # Test gets skipped as downstream is skipped
        os.environ["DATA_PARENT_LOCATION"] = os.path.join(abspath(os.path.dirname(__file__)))
        file = etree.parse('data/HappyTestData.jmx')

        test_data_is_valid(file)

    def test_invalid_data(self):
        os.environ["DATA_PARENT_LOCATION"] = os.path.join(abspath(os.path.dirname(__file__)))
        os.environ["CHECK_DATA"] = "1"
        file = etree.parse('data/UnhappyTestDataBadVarNames.jmx')

        try:
            test_data_is_valid(file)
            raise Exception
        except AssertionError as e:
            assert "but only 2 were found" in e.args[0]

    def test_data_not_found(self):
        os.environ["DATA_PARENT_LOCATION"] = os.path.join(abspath(os.path.dirname(__file__)))
        os.environ["CHECK_DATA"] = "1"
        file = etree.parse('data/UnhappyTestDataBadFileLocation.jmx')

        try:
            test_data_is_valid(file)
            raise Exception
        except AssertionError as e:
            assert "Did not see file" in e.args[0]


if __name__ == '__main__':
    unittest.main()
