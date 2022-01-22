import unittest

from lxml import etree

from app.test_jmx import test_connect_and_response_timeout_present_if_request_defaults_exist


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_test_connect_and_response_timeout_present_if_request_defaults_exist(self):

        file = etree.parse('data/MissingRequestDefaultValues.jmx')

        try:
            test_connect_and_response_timeout_present_if_request_defaults_exist(file)
            raise Exception
        # Expecting Assertion Error
        except AssertionError:
            pass

    def test_no_request_defaults(self):

        file = etree.parse('data/HttpRequestDefaultsNoExist.jmx')

        # Expecting no exception to be raised
        test_connect_and_response_timeout_present_if_request_defaults_exist(file)

    def test_request_defaults_exists(self):

        file = etree.parse('data/HttpRequestDefaultsSetCorrectly.jmx')

        # Expecting no exception to be raised
        test_connect_and_response_timeout_present_if_request_defaults_exist(file)


if __name__ == '__main__':
    unittest.main()
