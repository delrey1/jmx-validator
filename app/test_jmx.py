import glob
import logging
import os.path
from xml.etree import ElementTree

import pytest as pytest
from lxml import etree
from lxml.etree import XMLSyntaxError

LOGGER = logging.getLogger(__name__)

file_location = os.getenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")
data_location = os.getenv("JMX_WILDCARD_LOCATION", "data")


def retrieve_jmx_file_names():
    file_names = glob.glob(file_location)
    return file_names


def retrieve_jmx_file_paths():
    out = []
    for file_path in retrieve_jmx_file_names():
        out.append(os.path.basename(file_path))
    return out


def parse_jmx_file(file_name):
    try:
        parsed_file = etree.parse(file_name)
    except XMLSyntaxError as e:
        LOGGER.error("File %s could not be read" % file_name)
        raise e
    return parsed_file


def retrieve_jmx_files():
    for file_name in retrieve_jmx_file_names():
        yield parse_jmx_file(file_name)


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_connect_and_response_timeout_present_if_request_defaults_exist(file: ElementTree):
    requests_defaults = file.xpath(
        "./hashTree/hashTree/ConfigTestElement[@guiclass='HttpDefaultsGui' and @enabled='true']")
    if requests_defaults:
        for request_default in requests_defaults:
            response_timeout = request_default.find("./stringProp[@name='HTTPSampler.response_timeout']").text
            assert response_timeout not in ["", None], "Did not see a response timeout set - Make sure one is set"
            connect_timeout = request_default.find("./stringProp[@name='HTTPSampler.connect_timeout']").text
            assert connect_timeout not in ["", None], "Did not see a connection timeout set - Make sure one is set"


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_no_invalid_filenames(file: ElementTree):
    invalid_filename_elements = file.xpath(
        ".//stringProp[@name='filename' and (contains(text(), ':') or starts-with(text(), '/') or starts-with(text(), '\\'))]")
    invalid_filenames = []
    if invalid_filename_elements:
        for invalid_filename in invalid_filename_elements:
            LOGGER.warning("Saw invalid filename =>%s<=. Ensure paths in jmeter are relative" % (
                invalid_filename.text
            ))
            invalid_filenames.append(invalid_filename.text)
    assert invalid_filenames == []


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_unix_friendly_file_paths(file: ElementTree):
    potential_invalid_elements = file.xpath(
        r".//stringProp[@name='filename' and (contains(text(), '\'))]")
    invalid_filenames = []
    if potential_invalid_elements:
        for potential_invalid_element in potential_invalid_elements:

            amended_element = str(potential_invalid_element.text).replace("\\\\", "")
            if "\\" in amended_element:
                LOGGER.warning("Saw invalid filename =>%s<=. Ensure paths in jmeter are relative" % (
                    potential_invalid_element.text
                ))
                invalid_filenames.append(potential_invalid_element.text)
            else:
                LOGGER.info("Saw linux friendly file path =>%s<=" % (potential_invalid_element))
    assert invalid_filenames == [], "There were some linux unfriendly filepaths. Make sure all backslashes are escaped (e.g. \\\\), or just use forward slashes"


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_data_is_valid(file: ElementTree):
    if not os.getenv("CHECK_DATA"):
        LOGGER.warning("Not checking data as we did not have a flag for it enabled")
        pytest.skip("Not checking data as we did not have a flag for it enabled")

    filenames = file.xpath(
        r".//stringProp[@name='filename']")
    invalid_datafiles = []
    if filenames:
        for file in filenames:

            file_path = os.path.join(os.getenv("DATA_PARENT_LOCATION"), file.text)

            if os.path.exists(file_path):
                if file.getparent().tag == "CSVDataSet":
                    variable_names: str = file.getparent().find("./stringProp[@name='variableNames']").text
                    delimiter: str = file.getparent().find("./stringProp[@name='delimiter']").text
                    if variable_names:
                        jmeter_expected_cols = len(variable_names.split(","))  # JMeter expects "," delimiter
                        LOGGER.info(
                            "Saw that there were %s variables in %s. Checking to see if this matches with the actual file" % (
                                jmeter_expected_cols, file.text
                            ))
                        with open(file_path) as f:
                            r = f.readline()
                            actual_cols = len(r.split(delimiter))
                            if actual_cols == jmeter_expected_cols:
                                LOGGER.info("Number of columns matched for %s. Continuing" % file.text)
                            else:
                                err = "File =>%s<= had a delimiter of =>%s<= and %s columns were expected by JMeter, but only %s were found" % (
                                    file.text, delimiter, jmeter_expected_cols, actual_cols)
                                LOGGER.warning(err)
                                invalid_datafiles.append(err)
                    else:
                        LOGGER.info("%s did not contain any variable names, skipping checks" % file.text)
                else:
                    LOGGER.info(
                        "File was not part of CSVDataSet, currently do not have any checks in place for this file type"
                    )

            else:
                LOGGER.warning("Did not see file =>%s<=. Does it exist?" % file.text)
                invalid_datafiles.append("Did not see file =>%s<=. Does it exist?" % file.text)

    assert invalid_datafiles == [], "Saw errors around test data - Check to see if they are applicable"


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_fragment_module_no_exist(file: ElementTree):
    """
        Basic check. Can be extended but requires checking siblings. TODO?
        TODO Refactor
    """
    props = set([])
    props_ignore_list = ['workbench']
    module_controller_string_props = file.xpath(
        ".//ModuleController/collectionProp[@name='ModuleController.node_path']/stringProp[not(contains(text(), 'Test Plan'))]")
    for string_prop in module_controller_string_props:
        if string_prop.text.lower() in props_ignore_list:
            continue
        props.add(string_prop.text)

    testname_elements = file.xpath(".//*[@testname]")
    testnames = []
    for testname in testname_elements:
        testnames.append(testname.attrib['testname'])

    for prop in props:
        assert prop in testnames


def test_number_of_file_names_greater_than_zero():
    LOGGER.info("Searching for JMX files with =>%s<=" % (file_location))
    file_names = retrieve_jmx_file_names()
    LOGGER.info("Found %s files" % len(file_names))

    if len(file_names) == 0:
        LOGGER.warning("Did not find any files. Outputting some additional information to support any investigation")
        LOGGER.warning("Current dir %s" % (glob.glob("*")))
        LOGGER.warning("Scripts loc dir %s" % (glob.glob(file_location)))

    assert len(retrieve_jmx_file_names()) > 0


@pytest.mark.parametrize("file", retrieve_jmx_files(), ids=retrieve_jmx_file_paths())
def test_multiple_configurations_dont_exist(file: ElementTree):
    """
        Purpose of this test is to see if there are multiple user defined variables active under the main test plan.
            The assumption is that there should only be 1.
        This test considers that there may be multiple user defined variable elements in the tree, but assumes that
            if there is a duplicate then a mistake has been made.
        As such, if there are two user defined variable elements active with different values in each, it will not fail
    :return:
    """

    # TODO - Add logic to check whether the value is also duplicate,
    #  if it is we could ignore it as it doesn't affect the test?

    arguments = {}

    user_defined_variables = file.xpath(".//hashTree/hashTree/Arguments[@enabled='true']")

    fail = False

    for element in user_defined_variables:

        element_name = element.attrib.get("testname")

        for argument in element.xpath(".//stringProp[@name='Argument.name']/text()"):
            if argument in arguments:
                fail = True
                arguments[argument]['total_count'] += 1
                if element_name in arguments[argument]:
                    arguments[argument][element_name] += 1
                    LOGGER.warning("Saw duplicate of argument =>%s<= in =>%s<=. Total occurrences: %s" % (
                        argument,
                        element_name,
                        arguments[argument]['elements']
                    ))
                else:
                    arguments[argument][element_name] = 1
                    arguments[argument]['elements'].append(element_name)
                    LOGGER.warning("Saw duplicate of argument =>%s<= in =>%s<= as well as %s" % (
                        argument,
                        element_name,
                        arguments[argument]['elements']
                    ))
            else:
                arguments[argument] = {
                    "total_count": 1,
                    element_name: 1,
                    "elements": [element_name]
                }

    assert fail is False, "Saw duplicates when not expected - Check Logs =>%s" % arguments
