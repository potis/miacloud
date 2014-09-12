from setuptools import setup

setup(name='MIAcloud',
      version='1.0',
      description='This is a demo application to demonstrate how to transfer medical image analysis algorithms to the cloud',
      author='Korfiatis Panagiotis',
      author_email='korfiatisp@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
     install_requires=['Flask','six','numpy', 'pydicom','nibabel', 'Flask-Mail','Flask-HTTPAuth', 'Flask-Login'],
     )

