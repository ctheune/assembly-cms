# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import urllib
import sys


page = urllib.urlopen(sys.argv[1]).read()
p = lxml.etree.HTMLParser()
etree = lxml.etree.fromstring(page, p)

print '! Photos'

for i, element in enumerate(etree.xpath('//div[@class="GalleryItemImage"]/a/img')):
    url = 'http://assembly.galleria.fi' + urllib.quote(element.get('src'))
    url = url.replace('bigthumb', '_smaller.jpg')
    out = open('img-%s.jpg' % i, 'w')
    out.write(urllib.urlopen(url).read())
    author = element.get('src').split('/')[3]
    print 'image:img-%s.jpg|author:%s|title: ' % (i, author)
