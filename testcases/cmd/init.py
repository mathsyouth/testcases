# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import shutil
import sys

from cliff import command
from oslo_config import generator
from oslo_log import log as logging
from testrepository import commands

LOG = logging.getLogger(__name__)

TESTR_CONF = """[DEFAULT]
test_command=OS_STDOUT_CAPTURE=${OS_STDOUT_CAPTURE:-1} \\
    OS_STDERR_CAPTURE=${OS_STDERR_CAPTURE:-1} \\
    OS_TEST_TIMEOUT=${OS_TEST_TIMEOUT:-500} \\
    ${PYTHON:-python} -m subunit.run discover -t %s %s $LISTOPT $IDOPTION
test_id_option=--load-list $IDFILE
test_list_option=--list
group_regex=([^\.]*\.)*
"""


def get_testcases_default_config_dir():
    """Get default config directory of testcases

    There are 2 dirs that get tried in priority order. First is /etc/testcases,
     if that doesn't exist it tries for a
    ~/.testcases/etc directory. If none of these exist a ~/.testcases/etc
    directory will be created.

    :return: default config dir
    """
    global_conf_dir = '/etc/testcases'
    user_global_path = os.path.join(os.path.expanduser('~'), '.testcases/etc')
    if os.path.isdir(global_conf_dir):
        return global_conf_dir
    elif os.path.isdir(user_global_path):
        return user_global_path
    else:
        os.makedirs(user_global_path)
        return user_global_path


class TestcasesInit(command.Command):
    """Setup a local working environment for running tempest"""

    def get_parser(self, prog_name):
        parser = super(TestcasesInit, self).get_parser(prog_name)
        parser.add_argument('dir', nargs='?', default=os.getcwd(),
                            help="The path to the workspace directory. If you "
                            "omit this argument, the workspace directory is "
                            "your current directory")
        return parser

    def generate_testr_conf(self, local_path):
        testr_conf_path = os.path.join(local_path, '.testr.conf')
        top_level_path = os.path.dirname(os.path.dirname(__file__))
        discover_path = os.path.join(top_level_path, 'test_discover')
        testr_conf = TESTR_CONF % (top_level_path, discover_path)
        with open(testr_conf_path, 'w+') as testr_conf_file:
            testr_conf_file.write(testr_conf)

    def copy_config(self, etc_dir, config_dir):
        if os.path.isdir(config_dir):
            shutil.copytree(config_dir, etc_dir)
        else:
            LOG.warning("Global config dir %s can't be found" % config_dir)

    def generate_sample_config(self, local_dir):
        conf_generator = os.path.join(os.path.dirname(__file__),
                                      'config-generator.testcases.conf')
        output_file = os.path.join(local_dir, 'etc/testcases.conf.sample')
        if os.path.isfile(conf_generator):
            generator.main(['--config-file', conf_generator, '--output-file',
                            output_file])
        else:
            LOG.warning("Skipping sample config generation because global "
                        "config file %s can't be found" % conf_generator)

    def create_working_dir(self, local_dir, config_dir):
        # make sure we are working with abspath however tempest init is called
        local_dir = os.path.abspath(local_dir)
        # Create local dir if missing
        if not os.path.isdir(local_dir):
            LOG.debug('Creating local working dir: %s' % local_dir)
            os.mkdir(local_dir)
        elif not os.listdir(local_dir) == []:
            raise OSError("Directory you are trying to initialize already "
                          "exists and is not empty: %s" % local_dir)

        etc_dir = os.path.join(local_dir, 'etc')
        log_dir = os.path.join(local_dir, 'logs')
        testr_dir = os.path.join(local_dir, '.testrepository')
        # Create log dir
        if not os.path.isdir(log_dir):
            LOG.debug('Creating log dir: %s' % log_dir)
            os.mkdir(log_dir)
        # Create and copy local etc dir
        self.copy_config(etc_dir, config_dir)
        # Generate the sample config file
        self.generate_sample_config(local_dir)
        # Generate a testr conf file
        self.generate_testr_conf(local_dir)
        # setup local testr working dir
        if not os.path.isdir(testr_dir):
            commands.run_argv(['testr', 'init', '-d', local_dir], sys.stdin,
                              sys.stdout, sys.stderr)

    def take_action(self, parsed_args):
        config_dir = get_testcases_default_config_dir()
        self.create_working_dir(parsed_args.dir, config_dir)
