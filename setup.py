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


try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    long_description = ''

setup(
    name='queue-fetcher',
    version='1.8.0',
    description="QueueFetcher makes dealing with SQS queues in Django easier",
    author="SF Software limited t/a Pebble",
    author_email="sysadmin@mypebble.co.uk",
    url="https://github.com/mypebble/django-queue-fetcher",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['six'],
    classifiers=CLASSIFIERS,
    long_description=long_description,
)
