from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='p4a.ploneevent',
      version=version,
      description="Plone4Artists event extensions for Plone",
      long_description="""p4a.ploneevent is a calendaring add-on for the
Plone CMS.""",
      classifiers=[
          'Framework :: Zope3',
          'Framework :: Plone',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='Plone4Artists ',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='http://www.plone4artists.org/products/plone4artistscalendar',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'dateutil',
          'archetypes.schemaextender',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
