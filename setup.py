from setuptools import setup

setup(name='nsapi',
      version='2.0',
      description='An unofficial package to communicate with the NS API',
      url='https://github.com/Frederic98/ns_api',
      author='Frederic98',
      packages=['nsapi'],
      zip_safe=False,
      install_requires=[
            'requests',
      ]
      )
