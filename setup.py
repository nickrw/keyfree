from setuptools import setup, find_packages
import os

setup_dir = os.path.dirname(__file__)
version_path = os.path.join(setup_dir, 'keyfree/version.py')
requirements_path = os.path.join(setup_dir, "requirements.txt")
requirements_dev_path = os.path.join(setup_dir, "requirements-dev.txt")
requirements_setup_path = os.path.join(setup_dir, "requirements-setup.txt")

__version__ = None
with open(version_path) as f:
    code = compile(f.read(), version_path, 'exec')
    exec(code)

with open(requirements_path) as req_file:
    requirements = req_file.read().splitlines()

with open(requirements_dev_path) as req_file:
    requirements_dev = req_file.read().splitlines()

with open(requirements_setup_path) as req_file:
    requirements_setup = req_file.read().splitlines()

setup(
    name='keyfree',
    version=__version__,
    author='Nicholas Robinson-Wall',
    author_email='nick@robinson-wall.com',
    packages=find_packages(),
    url='https://github.com/nickrw/keyfree',
    description='An authentication proxy for Amazon Elasticsearch Service',
    setup_requires=requirements_setup,
    long_description_markdown_filename='README.md',
    install_requires=requirements,
    tests_require=requirements_dev,
    package_data={'keyfree': ['requirements.txt', 'requirements-dev.txt']},
    entry_points={
        'console_scripts': ['keyfree-proxy-test=keyfree.proxy:main'],
    },
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
    ],
)
