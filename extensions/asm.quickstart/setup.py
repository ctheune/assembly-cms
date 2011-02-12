from setuptools import setup, find_packages


setup(name='asm.quickstart',
      version='0.1dev',
      description="Assembly CMS quickstart module",
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
                        'asm.cms',
                        'asm.cmsui',
                        'asm.workflow',
                        'zope.interface',
                        'megrok.pagelet',
                        ],
      )
