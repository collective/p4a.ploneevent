# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from xml.dom.minidom import parse

def readversion():
    mdfile = os.path.join(os.path.dirname(__file__), 'p4a', 'ploneevent', 
                          'profiles', 'default', 'metadata.xml')
    metadata = parse(mdfile)
    assert metadata.documentElement.tagName == "metadata"
    return metadata.getElementsByTagName("version")[0].childNodes[0].data

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

setup(name='p4a.ploneevent',
      version=readversion().strip(),
      description="Plone4Artists event extensions for Plone",
      long_description='\n\n'.join([
        read('README.txt'),
        read('CHANGES.txt'),
      ]),
      classifiers=[
          'Framework :: Zope2',
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists recurring events calendar calendaring',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='http://pypi.python.org/pypi/p4a.ploneevent/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'python-dateutil',
          'archetypes.schemaextender',
          'p4a.common',
          'dateable.kalends >= 0.3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
