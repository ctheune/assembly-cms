from setuptools import setup, find_packages


setup(name='asm.cmsui',
      version='0.1dev',
      description="Assembly CMS UI",
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
                        'asm.cms',
                        ],
      )
