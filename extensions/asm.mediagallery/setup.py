from setuptools import setup, find_packages


setup(name='asm.mediagallery',
      version='0.1dev',
      description="Media gallery for Assembly CMS",
      author="Webcrew",
      author_email="web@assembly.org",
      url="",
      license="proprietary",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['ZODB3',
                        'asm.cms',
                        'asm.workflow',
                        'grok',
                        'setuptools',
                        'zope.interface',
                        'PIL',
                        'zope.schema'])
