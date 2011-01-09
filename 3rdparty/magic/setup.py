from setuptools import setup, find_packages

setup(name='magic',
      version='0.1',
      description='determines a file type by its magic number',
      author='Jason Patrone',
      author_email='jp_py@jsnp.net',
      long_description="""Determines the mime type of a file using magic
      numbers. Can also operate on arbitrary data streams.

      Much like the Unix file(1) program.""",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='mime magic file',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      zip_safe=False)
