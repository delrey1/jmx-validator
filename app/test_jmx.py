import glob
import logging
import os.path
from xml.etree import ElementTree

import pytest as pytest
from lxml import etree
from lxml.etree import XMLSyntaxError

LOGGER = logging.getLogger(__name__)

file_location = os.getenv("JMX_WILDCARD_LOCATION", "scripts/*.jmx")


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
            assert response_timeout not in ["", None]
            connect_timeout = request_default.find("./stringProp[@name='HTTPSampler.connect_timeout']").text
            assert connect_timeout not in ["", None]


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
def test_fragment_module_no_exist(file: ElementTree):
    """
        Basic check. Can be extended but requires checking siblings. TODO?
        TODO Refactor
    """
    props = set([])
    module_controller_string_props = file.xpath(
        ".//ModuleController/collectionProp[@name='ModuleController.node_path']/stringProp[not(contains(text(), 'Test Plan'))]")
    for string_prop in module_controller_string_props:
        props.add(string_prop.text)

    testname_elements = file.xpath(".//*[@testname]")
    testnames = []
    for testname in testname_elements:
        testnames.append(testname.attrib['testname'])

    for prop in props:
        assert prop in testnames


def test_file_names_greater_than_zero():
    LOGGER.info("Searching for JMX files with =>%s<=" % (file_location))
    file_names = retrieve_jmx_file_names()
    LOGGER.info("Found %s files" % len(file_names))

    if len(file_names) == 0:
        LOGGER.warning("Did not find any files. Outputting some additional information to support any investigation")
        LOGGER.warning("Current dir %s" % (glob.glob("*")))
        LOGGER.warning("Scripts loc dir %s" % (glob.glob(file_location)))

    assert len(retrieve_jmx_file_names()) > 0
