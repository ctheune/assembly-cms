from setuptools import setup, find_packages


setup(name='asm.cms',
      version='0.1.4dev',
      description="Assembly Website CMS",
      author="Assembly Webcrew",
      author_email="web@assembly.org",
      url="",
      license="ZPL 2.1",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',

                        'ZODB3',
                        'megrok.pagelet',
                        'zc.sourcefactory',
                        'zope.app.container',
                        'zope.app.form',
                        'zope.app.generations',
                        'zope.deferredimport',
                        'zope.event',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.schema',
                        'zope.traversing',
			'zope.app.undo',
                        'lxml',
                        'BareNecessities',
                        'hurry.zoperesource',
                        'hurry.tinymce',
                        'hurry.query',
                        'z3c.baseregistry',
                        'gocept.selenium>0.3'])
