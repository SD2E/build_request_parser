from setuptools import setup, find_packages

setup(name='build_request_parser',
      version='0.1',
      description='',
      url='https://gitlab.sd2e.org/rmoseley/build_request_parser',
      author='Robert C. Moseley',
      author_email='robert.moseley@duke.edu',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'':'src'},
      zip_safe=False)
