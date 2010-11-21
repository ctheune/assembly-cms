from setuptools import setup, find_packages

setup(name='asm.party',
      version='0.1dev',
      description="Extensions to manage Assembly party-related content",
      author="Webcrew",
      author_email="web@assembly.org",
      url="",
      license="ZPL",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['asm.cms',
                        'asm.cmsui',
                        'setuptools'])
