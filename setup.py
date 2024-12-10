from setuptools import setup, find_packages
import os


#  Function to safely read README.md for the long description
def read_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()

long_description = read_file('README.md') if os.path.exists('README.md') else '' # noqa

setup(
    name='lisan',
    version='0.1.7',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django package to add multilingual support to models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nabute/django-lisan',
    author='Daniel Nigusse, Nabute',
    author_email='nabute925@gmail.com',
    install_requires=[
        'django>=5.1',
        'djangorestframework>=3.12',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 5.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
)
