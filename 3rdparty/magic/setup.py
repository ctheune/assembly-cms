from setuptools import setup, find_packages

setup(name='magic',
      version = '0.1dev',
      description="magic file type identification",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      zip_safe=False)
