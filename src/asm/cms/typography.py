import lxml.etree
import grok
import asm.cms.interfaces

# These tags are never filtered.
WHITELIST_TAGS =  ['pre', 'script', 'object', 'embed', 'param', 'div',
                   'img', 'body', 'html', 'head', 'javascript',
                   'stupidcontainer']

@grok.subscribe(asm.cms.interfaces.IHTMLPage, grok.IObjectModifiedEvent)
@grok.subscribe(asm.cms.interfaces.IHTMLPage, grok.IObjectAddedEvent)
def paragraph_checking(page, event=None):
    clean_typography(page)


def remove_empty_paragraph(page, element):
    if len(element):
        return
    if element.text in (None, ''):
        element.getparent().remove(element)


def normalize_whitespaces(page, element):
    if element.text is None:
        return
    element.text = element.text.strip()


def remove_repeated_title_from_content(page, element):
    if element.tag != 'h1':
        return
    h1 = element.text.strip().lower()
    title = page.title.strip().lower()
    if h1 == title:
        element.getparent().remove(element)


def clean_typography(page):
    html = page.content
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainer>%s</stupidcontainer>' % html)
    document = lxml.etree.fromstring(document, parser)
    for element in document.getiterator():
        if element.tag in WHITELIST_TAGS:
            continue
        for filter in [normalize_whitespaces,
                       remove_empty_paragraph,
                       remove_repeated_title_from_content]:
            filter(page, element)

    result = lxml.etree.tostring(document.xpath('//stupidcontainer')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainer>', '')
    result = result.replace('</stupidcontainer>', '')
    # This is the case when there's nothing to return
    result = result.replace('<stupidcontainer/>', '')
    result = result.strip()
    page.content = result
