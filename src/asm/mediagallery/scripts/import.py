from asm.mediagallery.interfaces import IMediaGalleryAdditionalInfo
import Image
import ImageFile
import StringIO
import ZODB.blob
import asm.cms.page
import asm.cms.utils
import asm.mediagallery.externalasset
import os.path
import re
import sys
import transaction
import urllib
import zope.app.component.hooks

# Workaround for JPEG encoding:
# http://mail.python.org/pipermail/image-sig/1999-August/000816.html
ImageFile.MAXBLOCK = 4000000

gallery = sys.argv[1]
file = sys.argv[2]

#locate site and gallery
steps = gallery.split('/')[1:]
obj = root  # NOQA
while steps:
    obj = obj[steps.pop(0)]
    try:
        zope.app.component.hooks.setSite(obj)
    except AttributeError:
        pass
gallery = obj


def create_image_id(image_format, data):
    # Assume we only have images here.
    if 'key' in data:
        image_name = data['key'] + "." + image_format
    else:
        image_name = os.path.basename(data['image'])
        image_name = asm.cms.utils.normalize_name(image_name)
        image_name = re.sub("[^.]+$", image_format, image_name, re.M)

    orig_name = data['title']
    if 'author' in data:
        orig_name += ' by ' + data['author']

    return image_name, (u"%s|%s" % (image_name, orig_name))


def get_smallest_format(image):
    output_png = StringIO.StringIO()
    image.save(output_png, format='png', optimize=1)
    output_jpeg = StringIO.StringIO()
    image.convert('RGB').save(output_jpeg, format='jpeg', optimize=1)
    output_png = output_png.getvalue()
    output_jpeg = output_jpeg.getvalue()
    if len(output_jpeg) < len(output_png):
        return output_jpeg, 'jpeg'
    return output_png, 'png'


def get_thumbnail(data, target=(77.0, 165.0), crop=True):
    im = Image.open(data)
    width, height = im.size
    orig_ratio = float(width) / height

    target_height, target_width = (float(x) for x in target)
    target_ratio = target_width / target_height

    if orig_ratio > target_ratio:
        width = width / (height / target_height)
        height = target_height
    else:
        height = height / (width / target_width)
        width = target_width

    im = im.resize((width, height), Image.ANTIALIAS)
    width, height = im.size

    width_delta = (width - target_width) / 2
    height_delta = (height - target_height) / 2

    if crop:
        im = im.crop((
                  width_delta,
                  height_delta,
                  width - width_delta,
                  height - height_delta))
        im = im.crop((0, 0, int(target_width), int(target_height)))
        im.load()
    return get_smallest_format(im)


def resize_image_to_width(data, target_width):
    im = Image.open(data)
    width, height = im.size
    target_height = int(float(height) * (float(target_width) / width))

    im = im.resize((target_width, target_height), Image.ANTIALIAS)
    return get_smallest_format(im)


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
    section[name] = p = asm.cms.page.Page('externalasset')
    edition = p.editions.next()
    edition.title = data['title']

    img = open(data['image'], 'rb')
    target_width = 560.0
    output, image_format = resize_image_to_width(img, target_width)

    external = asm.mediagallery.externalasset.HostingServiceChoice()
    external.service_id = 'image'
    image_name, external.id = create_image_id(image_format, data)

    edition.locations = (external,)

    p[image_name] = image_page = asm.cms.page.Page('asset')
    image_edition = image_page.editions.next()

    image_edition.content = ZODB.blob.Blob()
    f = image_edition.content.open('w')
    f.write(output)
    img.seek(0)
    asm.workflow.workflow.publish(image_edition)
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
        if section_name in gallery:
            del gallery[section_name]
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

        if 'key' in data:
            name = orig_name = data['key']
        else:
            orig_name = data['title']
            if 'author' in data:
                orig_name += ' by ' + data['author']
            name = orig_name = asm.cms.utils.normalize_name(orig_name)

        edition, img = locals()['create_' + data.get('type')](name, data)
        edition.title = data.get('title')
        edition_galleryinfo = IMediaGalleryAdditionalInfo(edition)
        edition_galleryinfo.author = data.get('author')
        if data.get('position', None) is not None:
            edition_galleryinfo.ranking = int(data.get('position'))
        edition_galleryinfo.thumbnail = ZODB.blob.Blob()

        f = edition_galleryinfo.thumbnail.open('w')
        output, format = get_thumbnail(img)
        f.write(output)
        f.close()
        del img

        asm.workflow.workflow.publish(edition)
        print "Imported", edition.title


transaction.commit()
