#!/usr/bin/python
#
# Copyright (c) 2016 All rights reserved
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0

"""
Test server create operation
"""

import json
import netaddr
import re
from tempest.lib.common.utils import test_utils
from tempest.lib import exceptions

from testcases.common.utils import data_utils
from testcases.common import waiters
from testcases import config
from testcases import test
from testcases.vim import base

CONF = config.CONF


class TestServerCreateOp(base.ScenarioTest):

    """The test case for server create operation

    This test case follows this basic set of operations:
     * Create a keypair for use in launching an instance
     * Create a security group to control network access in instance
     * Add simple permissive rules to the security group
     * Launch an instance
     * Verify that the created server should be in the list of all servers
     * Verify that the created server should be in the detailed list of all
       servers
     * Verify server details
     * Perform ssh to instance
     * Verify that the number of vcpus reported by the instance matches the
       amount stated by the flavor
     * Verify the instance host name is the same as the server name
     * Verify metadata service
     * Verify metadata on config_drive
     * Verify network data on config_drive
     * Terminate the instance
    """

    def setUp(self):
        super(TestServerCreateOp, self).setUp()
        self.image_ref = CONF.compute.image_ref
        self.flavor_ref = CONF.compute.flavor_ref
        self.run_ssh = CONF.validation.run_validation
        self.ssh_user = CONF.validation.image_ssh_user

    def verify_list_servers(self):
        # The created server should be in the list of all servers
        body = self.servers_client.list_servers()
        servers = body['servers']
        found = any([i for i in servers if i['id'] == self.instance['id']])
        self.assertTrue(found)

    def verify_list_servers_with_detail(self):
        # The created server should be in the detailed list of all servers
        body = self.servers_client.list_servers(detail=True)
        servers = body['servers']
        found = any([i for i in servers if i['id'] == self.instance['id']])
        self.assertTrue(found)

    def verify_server_details(self):
        # Verify the specified server attributes are set correctly
        self.assertEqual(self.accessIPv4, self.instance['accessIPv4'])
        # NOTE(maurosr): See http://tools.ietf.org/html/rfc5952 (section 4)
        # Here we compare directly with the canonicalized format.
        self.assertEqual(self.instance['accessIPv6'],
                         str(netaddr.IPAddress(self.accessIPv6)))
        self.assertEqual(self.name, self.instance['name'])
        self.assertEqual(self.image_ref, self.instance['image']['id'])
        self.assertEqual(self.flavor_ref, self.instance['flavor']['id'])
        self.assertEqual(self.md, self.instance['metadata'])

    def verify_ssh(self, keypair):
        if self.run_ssh:
            # Obtain a floating IP
            self.fip = self.create_floating_ip(self.instance)['ip']
            # Check ssh
            self.ssh_client = self.get_remote_client(
                ip_address=self.fip,
                username=self.ssh_user,
                private_key=keypair['private_key'])

    def verify_created_server_vcpus(self):
        if self.run_ssh:
            # Verify that the number of vcpus reported by the instance matches
            # the amount stated by the flavor
            flavor = self.flavors_client.show_flavor(self.flavor_ref)['flavor']
            self.assertEqual(flavor['vcpus'], self.ssh_client.
                             get_number_of_vcpus())

    def verify_host_name_is_same_as_server_name(self):
        if self.run_ssh:
            # Verify the instance host name is the same as the server name
            hostname = self.ssh_client.get_hostname()
            msg = ('Failed while verifying servername equals hostname. '
                   'Expected hostname "%s" but got "%s".' % (self.name,
                                                             hostname))
            self.assertEqual(self.name.lower(), hostname, msg)

    def verify_metadata(self):
        if self.run_ssh and CONF.compute_feature_enabled.metadata_service:
            # Verify metadata service
            md_url = 'http://169.254.169.254/latest/meta-data/public-ipv4'

            def exec_cmd_and_verify_output():
                cmd = 'curl ' + md_url
                result = self.ssh_client.exec_command(cmd)
                if result:
                    msg = ('Failed while verifying metadata on server. Result '
                           'of command "%s" is NOT "%s".' % (cmd, self.fip))
                    self.assertEqual(self.fip, result, msg)
                    return 'Verification is successful!'

            if not test_utils.call_until_true(exec_cmd_and_verify_output,
                                              CONF.compute.build_timeout,
                                              CONF.compute.build_interval):
                raise exceptions.TimeoutException('Timed out while waiting to '
                                                  'verify metadata on server. '
                                                  '%s is empty.' % md_url)

    def _mount_config_drive(self):
        cmd_blkid = 'blkid | grep -i config-2'
        result = self.ssh_client.exec_command(cmd_blkid)
        dev_name = re.match('([^:]+)', result).group()
        self.ssh_client.exec_command('sudo mount %s /mnt' % dev_name)

    def _unmount_config_drive(self):
        self.ssh_client.exec_command('sudo umount /mnt')

    def verify_metadata_on_config_drive(self):
        if self.run_ssh and CONF.compute_feature_enabled.config_drive:
            # Verify metadata on config_drive
            self._mount_config_drive()
            cmd_md = 'sudo cat /mnt/openstack/latest/meta_data.json'
            result = self.ssh_client.exec_command(cmd_md)
            self._unmount_config_drive()
            result = json.loads(result)
            self.assertIn('meta', result)
            msg = ('Failed while verifying metadata on config_drive on server.'
                   ' Result of command "%s" is NOT "%s".' % (cmd_md, self.md))
            self.assertEqual(self.md, result['meta'], msg)

    def verify_networkdata_on_config_drive(self):
        if self.run_ssh and CONF.compute_feature_enabled.config_drive:
            # Verify network data on config_drive
            self._mount_config_drive()
            cmd_md = 'sudo cat /mnt/openstack/latest/network_data.json'
            result = self.ssh_client.exec_command(cmd_md)
            self._unmount_config_drive()
            result = json.loads(result)
            self.assertIn('services', result)
            self.assertIn('links', result)
            self.assertIn('networks', result)
            # TODO(clarkb) construct network_data from known network
            # instance info and do direct comparison.

    @test.idempotent_id('7fff3fb3-91d8-4fd0-bd7d-0204f1f180ba')
    @test.attr(type='smoke')
    @test.services('compute', 'network')
    def test_server_create_op(self):
        keypair = self.create_keypair()
        security_group = self._create_security_group()
        self.md = {'meta1': 'data1', 'meta2': 'data2', 'metaN': 'dataN'}
        self.accessIPv4 = '1.1.1.1'
        self.accessIPv6 = '0000:0000:0000:0000:0000:babe:220.12.22.2'
        self.name = data_utils.rand_name(self.__class__.__name__ + '-server')
        self.password = data_utils.rand_password()
        self.instance = self.create_server(
            image_id=self.image_ref,
            flavor=self.flavor_ref,
            key_name=keypair['name'],
            security_groups=[{'name': security_group['name']}],
            config_drive=CONF.compute_feature_enabled.config_drive,
            metadata=self.md,
            accessIPv4=self.accessIPv4,
            accessIPv6=self.accessIPv6,
            name=self.name,
            adminPass=self.password,
            wait_until='ACTIVE')
        self.verify_list_servers()
        self.verify_list_servers_with_detail()
        self.verify_server_details()
        self.verify_ssh(keypair)
        self.verify_created_server_vcpus()
        self.verify_host_name_is_same_as_server_name()
        self.verify_metadata()
        self.verify_metadata_on_config_drive()
        self.verify_networkdata_on_config_drive()
        self.servers_client.delete_server(self.instance['id'])
        waiters.wait_for_server_termination(
            self.servers_client, self.instance['id'], ignore_error=False)
