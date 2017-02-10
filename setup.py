# Copyright (c) 2016 Huawei
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO - DO NOT EDIT
import os
from setuptools import find_packages
from setuptools import setup


this_dir = os.path.dirname(__file__)


def get_version():
    with open(os.path.join(this_dir, 'testcases', 'cmd', 'main.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_long_description():
    with open('README.rst') as f:
        return f.read()


setup(
    name='testcases',
    version=get_version(),
    description='OPNFV Functional Testing',
    long_description=get_long_description(),
    author='OPNFV',
    author_email='opnfv@opnfv.org',
    url='http://wiki.opnfv.org',
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'testcases = testcases.cmd.main:main',
            'skip-tracker = tempest.lib.cmd.skip_tracker:main',
            'check-uuid = tempest.lib.cmd.check_uuid:run'
        ],
        'testcases.cm': [
            'run = testcases.cmd.run:TestcasesRun',
            'init = testcases.cmd.init:TestcasesInit'
        ],
        'oslo.config.opts': [
            'testcases.config = testcases.config:list_opts'
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    package_data={
        'testcases': ['cmd/*.conf']
    },
    data_files=[('/etc/testcases',
                 ['etc/logging.conf.sample', 'etc/testcases.conf'])
                ]
)
