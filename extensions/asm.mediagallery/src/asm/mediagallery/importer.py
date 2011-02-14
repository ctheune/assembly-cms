import asm.cms.importer
import asm.mediagallery.interfaces
import asm.mediagallery.externalasset
import asm.mediagallery.gallery
import urllib

def import_mediagalleryadditionalinfo(self, edition, node):
    media_info = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)

    media_info.author = node.get('author', None)
    media_info.description = urllib.unquote_plus(node.get('description', None))
    media_info.ranking = node.get('ranking', None)
    if media_info.ranking is not None:
        media_info.ranking = int(media_info.ranking)

    media_info.ranking = node.get('ranking', None)

    if node.text is not None and len(node.text) > 0:
        media_info.thumbnail = asm.cms.importer.base64_to_blob(node.text)


def import_mediagallery(self, edition, edition_node):
    for info_node in edition_node:
        assert info_node.tag == 'mediagalleryadditionalinfo'
        import_mediagalleryadditionalinfo(self, edition, info_node)


def import_location(self, edition, node):
    service_type = node.get('type')

    service = asm.mediagallery.externalasset.HostingServiceChoice()

    service.service_id = service_type
    service.id = node.text

    locations = list(edition.locations)
    locations.append(service)
    edition.locations = tuple(locations)

def import_externalasset(self, edition, edition_node):
    for info_node in edition_node:
        if info_node.tag == 'mediagalleryadditionalinfo':
            import_mediagalleryadditionalinfo(self, edition, info_node)
        elif info_node.tag == 'location':
            import_location(self, edition, info_node)
        else:
            assert False, "Encountered unknown node '%s'." % info_node.tag


# Monkey patch to support external assets and galleries in importer.

setattr(
    asm.cms.importer.Importer,
    'import_%s' % asm.mediagallery.externalasset.TYPE_EXTERNAL_ASSET,
    import_externalasset)
setattr(
    asm.cms.importer.Importer,
    'import_%s' % asm.mediagallery.gallery.TYPE_MEDIA_GALLERY,
    import_mediagallery)
setattr(
    asm.cms.importer.Importer,
    'import_mediagalleryadditionalinfo',
    import_mediagalleryadditionalinfo)
