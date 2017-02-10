Test Cases Design
==================

1. Test server create operation
---------------------------------

1.1. Test server create basic operation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This test case follows this basic set of operations:

#. Create a keypair for use in launching an instance
#. Create a security group to control network access in instance
#. Add simple permissive rules to the security group
#. Launch an instance
#. Verify the following stuffs:
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
#. Terminate the instance

1.2. Test server create operation with the scheduler hint "group"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This test case follows this basic set of operations:

#. Create a keypair for use in launching an instance
#. Create a security group to control network access in instance
#. Add simple permissive rules to the security group
#. Create a server with the scheduler hint "group"
#. Verify the following stuffs:
   * Verify server details
   * List servers (or with details)
   * Verify that the number of vcpus reported by the instance matches the
     amount stated by the flavor
   * Verify the instance host name is the same as the server name
   * Verify that the networks order given at the server creation is preserved
     within the server
   * (alternative Verify that server creation does not fail when more than one
     nic is created on the same network)
   * Verify that the ephemeral disk is created when creating server
   * Perform ssh to instance
   * Verify metadata service
   * Verify metadata on config_drive
#. Terminate the instance


2. Test resizing a volume-backed instance
-------------------------------------------
#. Create a keypair for use in launching an instance
#. Create a security group to control network access in instance
#. Add simple permissive rules to the security group
#. Launch an instance
#. Resize the instance
   * Verify the above stuffs again


3. Test Sequence suspend resume instance
------------------------------------------
#. Create a keypair for use in launching an instance
#. Create a security group to control network access in instance
#. Add simple permissive rules to the security group
#. Launch an instance
#. Suspend the instance
   * Verify the above stuffs again
#. Resume the instance
   * Verify the above stuffs again


4. Test server resart operations
----------------------------------
#. Create a keypair for use in launching an instance
#. Create a security group to control network access in instance
#. Add simple permissive rules to the security group
#. Launch an instance
#. Restart the instance
   * Verify the above stuffs again


5. Test server delete operation
---------------------------------

5.1. Delete a server while it's VM state is Building
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.2. Delete a server while it's VM state is active
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.3. Delete a server while it's VM state is Shutoff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.4. Delete a server while it's VM state is Pause
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.5. Delete a server while it's VM state is Suspended
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.6. Delete a server while it's VM state is Verify_resize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.7. Delete a server while a volume is attached to it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance

5.8. Delete a server while it's VM state is error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Create the instance
* Delete the instance
* List servers
* Perform ssh to the instance


Test network CRUD operations
----------------------------

Test network CRUD operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For a freshly-booted VM with an IP address ("port") on a given
network:

* the testcases host can ping the IP address.  This implies, but does not
  guarantee (see the ssh check that follows), that the VM has been assigned
  the correct IP address and has connectivity to the testcases host.

* the testcases host can perform key-based authentication to an ssh server
  hosted at the IP address.  This check guarantees that the IP address is
  associated with the target VM.

* the testcases host can ssh into the VM via the IP address and successfully
  execute the following:

  - ping an external IP address, implying external connectivity.
  - ping an external hostname, implying that dns is correctly configured.
  - ping an internal IP address, implying connectivity to another VM on the
    same network.

* detach the floating-ip from the VM and verify that it becomes unreachable
* associate detached floating ip to a new VM and verify connectivity.
  VMs are created with unique keypair so connectivity also asserts that
  floating IP is associated with the new VM instead of the old one

Verifies that floating IP status is updated correctly after each change

Test connectivity between VMs on different networks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For a freshly-booted VM with an IP address ("port") on a given network:

* the testcases host can ping the IP address.
* the testcases host can ssh into the VM via the IP address and successfully
  execute the following:

  - ping an external IP address, implying external connectivity.
  - ping an external hostname, implying that dns is correctly configured.
  - ping an internal IP address, implying connectivity to another VM on the
    same network.

* Create another network on the same tenant with subnet, create an VM on the
  new network.
* Ping the new VM from previous VM failed since the new network was not
  attached to router yet.
* Attach the new network to the router, Ping the new VM from previous VM
  succeed.


Test hotplug network interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Create a network and a VM.
#. Check connectivity to the VM via a public network.
#. Create a new network, with no gateway.
#. Bring up a new interface
#. check the VM reach the new network


Test to update admin state up of router
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Check public connectivity before updating admin_state_up attribute of router
   to False
#. Check public connectivity after updating admin_state_up attribute of router
   to False
#. Check public connectivity after updating admin_state_up attribute of router
   to True


Tests that subnet's extra configuration details are affecting VMs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This test relies on non-shared, isolated tenant networks.

NOTE: Neutron subnets push data to servers via dhcp-agent, so any update in
subnet requires server to actively renew its DHCP lease.

#. Configure subnet with dns nameserver
#. retrieve the VM's configured dns and verify it matches the one configured
   for the subnet.
#. update subnet's dns
#. retrieve the VM's configured dns and verify it matches the new one
   configured for the subnet.

add host_routes

any resolution check would be testing either:

* l3 forwarding (tested in test_network_basic_ops)


Test to update admin_state_up attribute of instance port
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#. Check public connectivity before updating admin_state_up attribute of
   instance port to False
#. Check public connectivity after updating admin_state_up attribute of
   instance port to False
#. Check public connectivity after updating admin_state_up attribute of
   instance port to True


Test preserve pre-existing port
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tests that a pre-existing port provided on server boot is not deleted if the
server is deleted.

Nova should unbind the port from the instance on delete if the port was not
created by Nova as part of the boot request.

We should also be able to boot another server with the same port.


Tests that router can be removed from agent and add to a new agent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Verify connectivity
#. Remove router from all l3-agents
#. Verify connectivity is down
#. Assign router to new l3-agent (or old one if no new agent is available)
#. Verify connectivity


