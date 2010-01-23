# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree


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


def title_to_name(title):
    title = title.lower()
    for char in ' /#?':
        title = title.replace(char, '-')
    return title
