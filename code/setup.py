#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='newspaperclassifier',
      version='1.0',
      description='Classifiers for newspaper images',
      author='Hölzl Edoardo / Gauchoux Lucas',
      install_requires=['boto3', 'click', 'dask', 'google-cloud-vision', 'botocore', 'pandas', 'pysolr', 'tqdm',
                        'numpy'],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      dependency_links=["https://git@github.com/impresso/impresso-pycommons/archive/master.zip"],
      entry_points={
          'console_scripts': ["impresso_classify=newspaperclassifier.scripts.classify:main",
                              "impresso_merge_labels=newspaperclassifier.scripts.merge:main",
                              "impresso_replica=newspaperclassifier.scripts.similar_images:main",
                              "evaluate_labels=newspaperclassifier.scripts.evaluate:main",
                              "dump_labels=newspaperclassifier.scripts.dump_results:main"]
          }
      )
