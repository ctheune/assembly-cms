from setuptools import setup, find_packages


setup(name='asm.schedule',
      version='0.1dev',
      description="Schedule micro-application for Assembly CMS",
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
                        'icalendar',
                        'setuptools',
                        'zope.interface',
                        'zope.schema'])
