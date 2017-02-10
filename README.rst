Testcases - The OPNFV Test Suite
==============================================

This is a set of functional tests to be run against a live OPNFV
cluster. Testcases has batteries of tests for OpenStack API validation,
Scenarios, and other specific tests useful in validating an OPNFV deployment.

Quickstart
----------

To run Testcases, you first need to create a configuration file that will tell
Testcases where to find the various OpenStack services and other testing behavior switches. Where the configuration file lives and how you interact with it depends on how you'll be running Testcases. For this section we'll cover the method.

#. You first need to install Testcases. This is done with pip after you check
   out the Testcases repo::

    $ pip install testcases/

   This can be done within a venv, but the assumption for this guide is that the Testcases cli entry point will be in your shell's PATH.

#. Setup a local working directory. This is done by using the testcases init
   command::

    $ testcases init working_dir

   which also works the same as::

    $ mkdir working_dir && cd working_dir && testcases init

   You will find that etc/testcases.conf.sample, .testr.conf, .testrepository are created in the directory working_dir. Then modify testcases.conf.sample located in the etc/ subdir. Testcases is expecting a testcases.conf file in etc/ so if only a sample exists you must rename or copy it to testcases.conf before making any changes to it otherwise Testcase will not know how to load it. For details on configuring testcases refer to `tempest-configuration`_.

#. Once the configuration is done you're now ready to run Testcases. This can
   be done by either running::

    $ testcases run

   from the newly created working directory. Or::

    $ testcases run --config-file True

   if you skip the last step, create directories working_dir/etc/, generate testcases.conf.sample by tox and create testcases.conf.

   There is also the option to use testr directly, or any `testr`_ based test
   runner, like `ostestr`_. For example, from the workspace dir run::

    $ ostestr --regex '(?!.*\[.*\bslow\b.*\])(^testcases\.(vim))'

   will run the same set of tests as the default gate jobs.

.. _testr: https://testrepository.readthedocs.org/en/latest/MANUAL.html
.. _ostestr: http://docs.openstack.org/developer/os-testr/
.. _tempest-configuration:
http://docs.openstack.org/developer/tempest/configuration.html

Configuration
-------------

Detailed configuration of Testcases is beyond the scope of this document. See `tempest-configuration`_ for more details on configuring Testcases. The etc/testcases.conf.sample attempts to be a self-documenting version of the configuration.

You can generate a new sample testcases.conf file, run the following
command from the top level of the testcases directory::

    $ tox -e genconfig

The most important pieces that are needed are the user ids, openstack
endpoint, and basic flavors and images needed to run tests.

.. _tempest-configuration:
http://docs.openstack.org/developer/tempest/configuration.html
