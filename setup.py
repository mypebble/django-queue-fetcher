from os import path
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

README_FILE = path.join(path.dirname(path.abspath(__file__)), 'README.md')

try:
    import m2r
    LONG_DESCRIPTION = m2r.parse_from_file(README_FILE)
except Exception:
    LONG_DESCRIPTION = ''

setup(
    name='queue-fetcher',
    version='2.0.9',
    description="QueueFetcher makes dealing with SQS queues in Django easier",
    author="SF Software limited t/a Pebble",
    author_email="sysadmin@mypebble.co.uk",
    url="https://github.com/mypebble/django-queue-fetcher",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['six'],
    classifiers=CLASSIFIERS,
    long_description=LONG_DESCRIPTION,
)
