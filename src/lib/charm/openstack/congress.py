# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# The congress handlers class

# bare functions are provided to the reactive handlers to perform the functions
# needed on the class.
from __future__ import absolute_import

import collections

import charms_openstack.charm
import charms_openstack.adapters
import charms_openstack.ip as os_ip

PACKAGES = ['congress-server',
            'congress-common',
            'python-antlr3',
            'python-pymysql',
            'python-apt',  # for subordinate neutron-openvswitch if needed.
            ]

CONGRESS_DIR = '/etc/congress/'
CONGRESS_CONF = CONGRESS_DIR + "congress.conf"

# select the default release function and ssl feature
charms_openstack.charm.use_defaults('charm.default-select-release')

###
# Implementation of the Congress Charm classes


class CongressCharm(charms_openstack.charm.HAOpenStackCharm):
    """CongressCharm provides the specialisation of the OpenStackCharm
    functionality to manage a congress unit.
    """

    release = 'ocata'
    name = 'congress'
    packages = PACKAGES
    api_ports = {
        'congress-server': {
            os_ip.PUBLIC: 1789,
            os_ip.ADMIN: 1789,
            os_ip.INTERNAL: 1789,
        },
    }
    service_type = 'congress'

    default_service = 'congress-server'
    services = ['congress-server']

    # Note that the hsm interface is optional - defined in config.yaml
    required_relations = ['shared-db', 'amqp', 'identity-service']

    restart_map = {
        CONGRESS_CONF: services,
    }

    # This is the command to sync the database
    sync_cmd = ['congress-db-manage', '--config-file', CONGRESS_CONF,
                'upgrade', 'head']

    # Package for release version detection
    release_pkg = 'congress-common'

    # Package codename map for congress-common
    package_codenames = {
        'congress-common': collections.OrderedDict([
            ('4', 'newton'),
            ('5', 'ocata'),
            ('6', 'pike'),
            ('7', 'queens'),
            ('8', 'rocky'),
        ]),
    }

    ha_resources = ['vips', 'haproxy', 'dnsha']

    def get_amqp_credentials(self):
        """Provide the default amqp username and vhost as a tuple.

        :returns (username, host): two strings to send to the amqp provider.
        """
        return ('congress', 'openstack')

    def get_database_setup(self):
        """Provide the default database credentials as a list of 3-tuples

        returns a structure of:
        [
            {'database': <database>,
             'username': <username>,
             'hostname': <hostname of this unit>
             'prefix': <the optional prefix for the database>, },
        ]

        :returns [{'database': ...}, ...]: credentials for multiple databases
        """
        return [
            dict(
                database='congress',
                username='congress', )
        ]
