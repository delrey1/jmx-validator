import unittest

from lxml.etree import XMLSyntaxError

from app.test_jmx import parse_jmx_file


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_malformed_xml(self):

        try:
            file = parse_jmx_file('data/MalformedXML.jmx')
            raise AssertionError("Expected XMLSyntaxError")
        except XMLSyntaxError:
            pass


if __name__ == '__main__':
    unittest.main()
