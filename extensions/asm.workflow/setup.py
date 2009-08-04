from setuptools import setup, find_packages


setup(name='asm.workflow',
      version='0.1dev',
      description="Workflow extension for the Assembly CMS",
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
                        'zope.deferredimport',
                        'asm.cms',
                        'zope.component',
                        'zope.event'])
