import unittest

from lxml import etree

from app.test_jmx import test_no_invalid_filenames


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_invalid_windows_filename(self):

        file = etree.parse('data/InvalidWindowsFilename.jmx')

        try:
            test_no_invalid_filenames(file)
            raise Exception
        except AssertionError:
            pass

    def test_invalid_linux_filename(self):

        file = etree.parse('data/InvalidLinuxFilename.jmx')

        try:
            test_no_invalid_filenames(file)
            raise Exception
        except AssertionError:
            pass

    def test_valid_filename(self):

        file = etree.parse('data/ValidFileName.jmx')
        # Expecting no assertion error
        test_no_invalid_filenames(file)


if __name__ == '__main__':
    unittest.main()
