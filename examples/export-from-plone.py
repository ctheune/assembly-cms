# This script can be used as a normal "Script (Python)" in ZMI.
# However, the following security changes have to be made to your Zope server:
#
# from AccessControl import allow_module
# allow_module('base64')
# allow_module('cgi')


import base64
import cgi

type_map = {
    'Document': 'htmlpage',
    'Image': 'asset',
    'File': 'asset',
}

context.REQUEST.RESPONSE.setHeader(
    'Content-Disposition', 'attachment;filename=plone.xml')
print '<?xml version="1.0" encoding="utf-8"?>'
print '<import base="%s">' % (
    container.portal_url.getPortalObject().absolute_url_path())

objects = list(container.portal_catalog(portal_type='Document'))
objects.extend(container.portal_catalog(portal_type='Image'))
objects.extend(container.portal_catalog(portal_type='File'))


def export_data(item, language, workflow):
    if edition.portal_type == 'Document':
        cdata = edition.CookedBody(stx_level=2)
    elif edition.portal_type in ['File', 'Image']:
        cdata = edition.get_data()
    print '<edition parameters="lang:%s workflow:%s"' % (language, workflow)
    print '         title="%s"' % cgi.escape(edition.Title())
    print '         tags="%s"' % cgi.escape(' '.join(edition.Subject()))
    print '         created="%s"' % edition.CreationDate()
    print '         modified="%s">' % edition.ModificationDate()
    print '<![CDATA[%s]]>' % base64.encodestring(cdata)
    print '</edition>'
    return printed

for object in objects:
    object = object.getObject()
    path = object.getPhysicalPath()[2:]
    if context.plone_utils.isDefaultPage(object):
        path = path[:-1]
    page_type = type_map[object.portal_type]
    print '<%s path="%s">' % (page_type, '/'.join(path))
    for lang in object.getTranslationLanguages():
        edition = object.getTranslation(lang)
        print export_data(edition, lang, 'draft')
        status = context.portal_workflow.getInfoFor(
            edition, 'review_state', '')
        if status == 'published':
            print export_data(edition, lang, 'public')
    print '</%s>' % page_type

print '</import>'
return printed
