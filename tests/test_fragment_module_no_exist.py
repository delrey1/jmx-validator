import unittest

from lxml import etree

from app.test_jmx import test_connect_and_response_timeout_present_if_request_defaults_exist, \
    test_fragment_module_no_exist


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_sample_test_fragment_module_exists(self):

        file = etree.parse('data/SampleTestFragmentModuleExists.jmx')

        test_fragment_module_no_exist(file)

    def test_test_connect_and_response_timeout_present_if_request_defaults_exist(self):

        file = etree.parse('data/SampleFragmentModuleNoExist.jmx')

        try:
            test_fragment_module_no_exist(file)
            raise Exception
        # Expecting Assertion Error
        except AssertionError as e:
            pass



if __name__ == '__main__':
    unittest.main()
