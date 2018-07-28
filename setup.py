from setuptools import setup

setup(name='nsapi',
      version='0.1',
      description='An unofficial package to communicate with the NS API',
      url='https://github.com/Frederic98/ns_api',
      author='Frederic98',
      packages=['nsapi'],
      zip_safe=False,
      install_requires=[
            'requests',
      ],
      extras_require={
            'departures_ui': ['PyQt5'],
            'departures_ui_cluster': ['PyQt5', 'zeroconf'],
      }
      )
