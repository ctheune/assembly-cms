from setuptools import setup, find_packages


setup(name='asm.schedule',
      version='0.1',
      description="Schedule micro-application for Assembly CMS",
      author="Webcrew",
      author_email="web@assembly.org",
      url="",
      license="proprietary",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'zope.html',
                        'ZODB3',
                        'asm.workflow',
                        'zope.interface',
                        'zope.schema',
                        ],
      )
