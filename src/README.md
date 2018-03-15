# Overview

This charm provides the Congress Policy service for an OpenStack Cloud.

# Usage

Congress relies on services from the percona-cluster, rabbitmq-server and keystone charms:

    juju deploy congress
    juju deploy keystone
    juju deploy percona-cluster
    juju deploy rabbitmq-server
    juju add-relation congress rabbitmq-server
    juju add-relation congress percona-cluster
    juju add-relation congress keystone

# Bugs

Please report bugs on [Launchpad](https://bugs.launchpad.net/charm-congress/+filebug).

For general questions please refer to the OpenStack [Charm Guide](https://docs.openstack.org/charm-guide/latest/).
