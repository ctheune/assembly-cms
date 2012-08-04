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

    def assertIn(self, needle, haystack, msg=None):
        """Same as Python 2.7's assertIn function."""
        if needle not in haystack:
            raise self.failureException, \
                (msg or "%s is not in %s" % (needle, haystack))

    def assertIsNone(self, expr, msg=None):
        """Same as Python 2.7's assertIsNone function."""
        if expr is not None:
            raise self.failureException, \
                (msg or "%s is not None" % (expr))
