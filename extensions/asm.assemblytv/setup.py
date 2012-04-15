from setuptools import setup, find_packages


setup(name='asm.assemblytv',
      version='0.1dev',
      description="AssemblyTV skin",
      author="Webcrew",
      author_email="assemblytv@assemblytv.net",
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
                        'megrok.pagelet',
                        ],
      )
