# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import re
import time

def rewrite_urls(content, visitor):
    """Rewrite URLs using a visitor.

    Visitors are expected to be callables that except a URL and return a new
    URL.
    """
    # Hrgh. Why is there no obvious simple way to do this?
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainerwrappercafebabe>%s</stupidcontainerwrappercafebabe>' %
        content)
    document = lxml.etree.fromstring(document, parser)

    for (locator, attribute) in [('//a', 'href'),
                                 ('//img', 'src')]:
        for element in document.xpath(locator):
            old = element.get(attribute)
            if old is None:
                continue
            new = visitor(old)
            element.set(attribute, new if new is not None else old)

    result = lxml.etree.tostring(
        document.xpath('//stupidcontainerwrappercafebabe')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainerwrappercafebabe>', '')
    result = result.replace('</stupidcontainerwrappercafebabe>', '')
    return result.strip()


def normalize_name(title):
    result = title.lower()
    result = re.sub("[^\.a-z0-9]", "-", result)
    # Normalize multiple dashes and then remove them from beginning and end.
    result = re.sub("-+", "-", result)
    result = result.strip("-")
    return result


def datetime_to_http_timestamp(datetime_raw):
    """Converts an datetime object to HTTP timestamp."""

    # This is probably the shortest way to do this with the standard libraries
    # when assuming that datetime_raw is in UTC time.
    assert(datetime_raw.utcoffset() is not None)
    assert(datetime_raw.utcoffset().seconds == 0)

    time_raw = time.asctime(datetime_raw.timetuple())
    # There can be multiple spaces when day does not have two numbers.
    wday, month, day, daytime, year = re.split(" +", time_raw)

    result = "%s, %s %s %s %s GMT" % (wday, day, month, year, daytime)
    return result
