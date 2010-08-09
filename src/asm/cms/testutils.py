import unittest
import xml.etree.ElementTree as etree
import xml.parsers.expat

class TestCase(unittest.TestCase):
    """Python's unittest.TestCase extended with additional assert functions."""

    def assertValidXml(self, xmldata, msg=None):
        try:
            etree.fromstring(xmldata)
        except xml.parsers.expat.ExpatError, e:
            raise self.failureException, (msg or e.message)

    def assertIsIn(self, needle, haystack, msg=None):
        if needle not in haystack:
            raise self.failureException, \
                (msg or "%s is not in %s" % (needle, haystack))
