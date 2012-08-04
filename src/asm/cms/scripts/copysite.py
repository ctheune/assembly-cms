import argparse
import asm.cms.cms
import transaction
import zope.app.component.hooks
import zope.copypastemove.interfaces


def get_new_page(new_root, old_page):
    # Construct path of the old page
    path = []
    needle = old_page
    while not isinstance(needle, asm.cms.cms.CMS):
        path.insert(0, needle.__name__)
        needle = needle.__parent__
    # Traverse path in the new root and construct pages that don't exist along
    # the way.
    new_page = new_root
    p = path[:]
    while p:
        name = p.pop(0)
        if name not in new_page:
            new_page[name] = asm.cms.page.Page(old_page.type)
        new_page = new_page[name]
    new_page.type = old_page.type
    return new_page, path


parser = argparse.ArgumentParser(
    description='Create a new site as a copy of an existing site.')

parser.add_argument('old', help='the ID of the existing site')
parser.add_argument('new', help='the ID of the new site')

args = parser.parse_args()

old_site = root[args.old] # NOQA
new_site = root[args.new] = asm.cms.cms.CMS() # NOQA

transaction.savepoint()
zope.app.component.hooks.setSite(new_site)
# XXX Why do we have to do this here? This is similar to
# cleanup_initial_edition
intids = zope.component.getUtility(zope.intid.IIntIds)
intids.register(new_site)

old_pages = [old_site]
while old_pages:
    old_page = old_pages.pop(0)
    new_page, path = get_new_page(new_site, old_page)
    print 'Copying', '/' + '/'.join(path)
    for edition in list(new_page.editions):
        del new_page[edition.__name__]
    for old_edition in old_page.editions:
        new_edition = new_page.addEdition(old_edition.parameters)
        new_edition.copyFrom(old_edition)
    old_pages.extend(old_page.subpages)

transaction.commit()
