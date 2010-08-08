from setuptools import setup, find_packages


setup(name='asm.cmsui',
      version='0.1dev',
      description="The CMS UI Assembly CMS",
      author="Webcrew",
      author_email="web@assembly.org",
      url="",
      license="ZPL 2.1",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['asm.cms',
                        'grok',
                        'gocept.selenium',
                        'setuptools'])
