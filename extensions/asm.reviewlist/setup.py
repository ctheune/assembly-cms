from setuptools import setup, find_packages


setup(name='asm.reviewlist',
      version='0.1dev',
      description="Review list to show recently changed pages in the CMS",
      author="Webcrew",
      author_email="web@assembly.org",
      url="",
      license="proprietary",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['asm.cms',
                        'setuptools'])
