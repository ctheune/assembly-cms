# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import re

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

def remove_empty_paragraph(element):
    text = element.text
    if text is None:
        element.getparent().remove(element)
    if text == '':
        element.getparent().remove(element)

def normalize_whitespaces(text):
    if text is None:
        return text
    return text.strip()

def check_paragraphs(html):
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainer>%s</stupidcontainer>' % html)
    document = lxml.etree.fromstring(document, parser)
    htmltags =  ['//pre','//head','//javascript']
    for locator in htmltags:
        for element in document.xpath(locator):
            element.text = normalize_whitespaces(element.text)
            remove_empty_paragraph(element)

    result = lxml.etree.tostring(document.xpath('//stupidcontainer')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainer>', '')
    result = result.replace('</stupidcontainer>', '')
    result = result.replace('<stupidcontainer/>', '') #This is the case when there's nothing to return
    return result.strip()
