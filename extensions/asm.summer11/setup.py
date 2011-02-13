from setuptools import setup, find_packages


setup(name='asm.summer11',
      version='0.1dev',
      description="Assembly Summer 2011 skin",
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

                        'zope.interface',
                        'asm.cms',
                        'asm.party',
                        'megrok.pagelet',
                        ],
      )
