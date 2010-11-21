import lxml.etree
import grok
import asm.cms.interfaces

@grok.subscribe(asm.cms.interfaces.IHTMLPage, grok.IObjectModifiedEvent)
def paragraph_checking(page, event=None):
    page.content = check_paragraphs(page.content)
    page.content = title_in_content(page.title, page.content)

@grok.subscribe(asm.cms.interfaces.IHTMLPage, grok.IObjectAddedEvent)
def initial_paragraph_checking(page, even=None):
    page.content = check_paragraphs(page.content)
    page.content = title_in_content(page.title, page.content)

def remove_empty_paragraph(element):
    text = element.text
    if len(element) == 0:
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
    htmltags =  ['pre','script','object','embed','param','div','img','body','html','head','javascript','stupidcontainer']
    for element in document.getiterator():
        if not element.tag in htmltags:
            element.text = normalize_whitespaces(element.text)
            remove_empty_paragraph(element)

    result = lxml.etree.tostring(document.xpath('//stupidcontainer')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainer>', '')
    result = result.replace('</stupidcontainer>', '')
    result = result.replace('<stupidcontainer/>', '') #This is the case when there's nothing to return
    return result.strip()

def title_in_content(title, content): 
    parser = lxml.etree.HTMLParser()
    document = (
        '<stupidcontainer>%s</stupidcontainer>' % content)
    document = lxml.etree.fromstring(document, parser)
    for element in document.xpath('//h1'):
        print element.text
        if element.text in title:
            element.getparent().remove(element)

    result = lxml.etree.tostring(document.xpath('//stupidcontainer')[0],
        pretty_print=True)
    result = result.replace('<stupidcontainer>', '')
    result = result.replace('</stupidcontainer>', '')
    result = result.replace('<stupidcontainer/>', '') #This is the case when there's nothing to return
    return result.strip()
