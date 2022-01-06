#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from glob import glob
from shutil import rmtree
from pathlib import Path

from setuptools.config import read_configuration
from setuptools import find_packages, setup, Command
from setuptools.command.install import install
from subprocess import check_call, check_output

# HACK to ignore wheel building from pip and just to source distribution
if 'bdist_wheel' in sys.argv:
    sys.exit(0)

setup_cfg = read_configuration("setup.cfg")
metadata = setup_cfg['metadata']

# Package meta-data.
NAME = 'sre-bot-zabbix'
BOTS_PATH = "sre-bots/" + NAME # e.g. /var/lib/sre-bot/sre-bots/sre-bot-zabbix

# What packages are required for this module to be executed?
REQUIRED = [
    "sre-bot", "py_zabbix",
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = metadata['DESCRIPTION']

# Load the package's __version__.py module as a dictionary.
about = {}
if not metadata['version']:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = metadata['version']


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def clear_builds(self):
        for path in ['dist', 'build', NAME.replace("-", "_") + ".egg-info"]:
            try:
                self.status(f'Removing previous builds from {path}')
                rmtree(os.path.join(here, path))
            except OSError:
                pass

    def run(self):
        self.clear_builds()

        self.status('Building Source…')
        os.system('{0} setup.py sdist'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

        self.clear_builds()

        sys.exit()

class InstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)

        self._add_bots_path()

    def _add_bots_path(self):
        path = Path(self.install_lib) / NAME.replace("-", "_")
        check_call(["sre", "add-bot-path", path])

setup(
    version=about['__version__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    data_files=[
        (BOTS_PATH, glob(NAME.replace("-", "_") + "/*")),
    ],
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
        'install': InstallCommand,
    },
)
