# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import Image
import StringIO
import ZODB.blob
import asm.cms.page
import asm.cms.utils
import asm.mediagallery.externalasset
import sys
import urllib
import zope.app.component.hooks
import transaction

gallery = sys.argv[1]
file = sys.argv[2]

#locate site and gallery
steps = gallery.split('/')[1:]
obj = root
while steps:
    obj = obj[steps.pop(0)]
    try:
        zope.app.component.hooks.setSite(obj)
    except AttributeError:
        pass
gallery = obj

def get_thumbnail(data, target=(77.0,165.0), crop=True):
    im = Image.open(data)
    width, height = im.size
    orig_ratio = float(width)/height
    target_ratio = float(target[1])/target[0]

    if orig_ratio > target_ratio:
        width = width / (height/target[0])
        height = target[0]
    else:
        height = height / (width/target[1])
        width = target[1]

    im = im.resize((width, height), Image.ANTIALIAS)
    width, height = im.size

    width_delta = (width-target[1])/2
    height_delta = (height-target[0])/2

    if crop:
        im = im.crop((
                  width_delta,
                  height_delta,
                  width-width_delta,
                  height-height_delta))
        im = im.crop((0, 0, int(target[1]), int(target[0])))
        im.load()
    output = StringIO.StringIO()
    im.save(output, format='png')
    return output


def update_location(locations, name, value):
    for location in locations:
        if location.service_id == name:
            location.id = value
            return True
    return False

def create_service(name, value):
    service = asm.mediagallery.externalasset.HostingServiceChoice()
    service.service_id = name
    service.id = value
    return service

def update_external(section, name, data):
    edition = section[name].page.editions.next()
    locations = ()

    if 'youtube' in data:
        locations += (create_service('youtube', data['youtube']),)
    if 'sceneorg' in data:
        locations += (create_service('sceneorg', data['sceneorg']),)
    if 'sceneorgvideo' in data:
        locations += (create_service('sceneorg', data['sceneorgvideo'] + u"|HQ video"),)

    edition.locations = locations
    return edition

def create_external(name, data):
    section[name] = p = asm.cms.page.Page('externalasset')
    edition = p.editions.next()
    edition.title = data['title']
    yt = asm.mediagallery.externalasset.HostingServiceChoice()
    yt.service_id = 'youtube'
    yt.id = data['youtube']
    edition.locations = (yt,)
    img = StringIO.StringIO(urllib.urlopen(data['thumbnail']).read())
    return edition, img


def create_asset(name, data):
    section[name] = p = asm.cms.page.Page('asset')
    edition = p.editions.next()
    img = open(data['image'], 'rb')
    edition.content = ZODB.blob.Blob()
    f = edition.content.open('w')
    f.write(get_thumbnail(img, (330.0, 560.0), crop=False).getvalue())
    img.seek(0)
    return edition, img


for line in open(file, 'r'):
    line = line.strip()
    line = line.decode('utf-8')
    if not line:
        continue
    if line.startswith('#'):
        continue
    if line.startswith('!'):
        section_title = line[1:].strip()
        section_name = asm.cms.utils.normalize_name(section_title)
        if section_name not in gallery:
            gallery[section_name] = p = asm.cms.page.Page('mediagallery')
            section = p.editions.next()
            section.title = section_title
            asm.workflow.workflow.publish(section)
            print "Created gallery", section_title

        section = gallery[section_name]
    else:
        data = {}
        for field in line.split('|'):
            try:
                data.__setitem__(*field.split(':', 1))
            except TypeError:
                print field
                raise
        orig_name = data['title']
        if 'author' in data:
            orig_name += ' by ' + data['author']
        name = orig_name = asm.cms.utils.normalize_name(orig_name)

        edition = update_external(section, name, data)
        edition.title = data['title']
        edition_galleryinfo = asm.mediagallery.interfaces.IMediaGalleryAdditionalInfo(edition)
        edition_galleryinfo.author = data.get('author')
        edition_galleryinfo.ranking = int(data.get('position'))

        if asm.workflow.WORKFLOW_DRAFT in edition.parameters:
            asm.workflow.workflow.publish(edition)

        print "Updated", edition.title


transaction.commit()

