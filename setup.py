from setuptools import setup, find_packages

setup(
    name='queue-fetcher',
    version='0.0.1',
    description="QueueFetcher makes dealing with SQS queues in Django easier",
    author="SF Software limited t/a Pebble",
    author_email="sysadmin@mypebble.co.uk",
    url="https://github.com/mypebble/django-queue-fetcher",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
