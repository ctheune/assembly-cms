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

def get_thumbnail(url):
    # Get thumbnail, scale down
    data = StringIO.StringIO(
        urllib.urlopen('http://dl.dropbox.com/u/8355/assembly2010.png').read())
    im = Image.open(data)
    width, height = im.size

    orig_ratio = float(width)/height
    target_ratio = float(165)/77

    if orig_ratio > target_ratio:
        width = width / (height/77)
        height = 77
    else:
        height = height / (width/165)
        width = 165

    im2 = im.resize((width, height), Image.ANTIALIAS)
    width, height = im2.size

    width_delta = (width-165)/2
    height_delta = (height-77)/2

    im3 = im2.crop((
              width_delta,
              height_delta,
              width-width_delta,
              height-height_delta))
    im4 = im3.crop((0, 0, 165, 77))
    im4.load()
    output = StringIO.StringIO()
    im4.save(output, format='png')
    return output

for line in open(file, 'r'):
    line = line.strip()
    if line.startswith('!'):
        section_title = line[1:].strip()
        section_name = asm.cms.utils.normalize_name(section_title)
        if section_name not in gallery:
            gallery[section_name] = asm.cms.page.Page('mediagallery')
            gallery.editions.next().title = section_title
            print "Created gallery", section_title
        section = gallery[section_name]
    else:
        data = {}
        for field in line.split('|'):
            data.__setitem__(*field.split(':', 1))
        section[asm.cms.utils.normalize_name(data['title'])] = p = asm.cms.page.Page('externalasset')
        edition = p.editions.next()
        edition.title = data['title']
        yt = asm.mediagallery.externalasset.HostingServiceChoice()
        yt.service_id = 'youtube'
        yt.id = data['youtube']
        edition.locations = (yt,)

        edition.thumbnail = ZODB.blob.Blob()
        f = edition.thumbnail.open('w')
        f.write(get_thumbnail(data['thumbnail']).getvalue())
        f.close()

        print "Imported", edition.title

 #       publish content object

transaction.commit()

