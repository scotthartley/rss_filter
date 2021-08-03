from setuptools import setup, find_packages


def readme():
    with open("README.rst", encoding='utf8') as file:
        return file.read()


exec(open('rss_filter/_version.py').read())

setup(name='rss_filter',
      version=__version__,
      description='Filters duplicates and unwanted items from rss feeds',
      # long_description=readme(),
      author='Scott Hartley',
      author_email='scott.hartley@miamioh.edu',
      url='https://hartleygroup.org',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'rss_filter = rss_filter:rss_filter',
          ]
      },
      install_requires=[
          'PyYAML',
          'lxml'
          ],
      python_requires=">=3.6",
      )
