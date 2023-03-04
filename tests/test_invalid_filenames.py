import unittest

from lxml import etree

from app.test_jmx import test_unix_friendly_file_paths


class MyTestCase(unittest.TestCase):

    # def setUpClass(self):
    #     os.putenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")

    def test_invalid_windows_filename(self):

        file = etree.parse('data/LinuxUnfriendlyFilePaths.jmx')

        try:
            test_unix_friendly_file_paths(file)
            raise Exception
        except AssertionError as e:
            pass

    def test_valid_windows_filename(self):

        file = etree.parse('data/LinuxFriendlyFilePaths.jmx')

        test_unix_friendly_file_paths(file)





if __name__ == '__main__':
    unittest.main()
