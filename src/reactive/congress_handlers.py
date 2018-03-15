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

# this is just for the reactive handlers and calls into the charm.
from __future__ import absolute_import

import charms.reactive
import charms_openstack.charm
from charms_openstack.charm.utils import is_data_changed

# This charm's library contains all of the handler code associated with
# congress -- we need to import it to get the definitions for the charm.
import charm.openstack.congress  # noqa


# Use the charms.openstack defaults for common states and hooks
charms_openstack.charm.use_defaults(
    'charm.installed',
    'amqp.connected',
    'shared-db.connected',
    'identity-service.available',  # enables SSL support
)


@charms.reactive.when('identity-service.connected')
@charms.reactive.when_not('identity-service.available')
def register_endpoints(keystone):
    """Register the endpoints when the identity-service connects.
    Note that this charm doesn't use the default endpoint registration function
    as it needs to register multiple endpoints, and thus needs a custom
    function in the charm.
    """
    with charms_openstack.charm.provide_charm_instance() as congress_charm:
        args = [congress_charm.service_type, congress_charm.region,
                congress_charm.public_url, congress_charm.internal_url,
                congress_charm.admin_url]
        # This function checkes that the data has changed before sending it
        with is_data_changed('charms.openstack.register-endpoints', args) as c:
            if c:
                keystone.register_endpoints(*args)


@charms.reactive.when('shared-db.available',
                      'congress.config.rendered')
def maybe_do_syncdb(shared_db):
    """Sync the database when the shared-db becomes available.  Note that the
    charms.openstack.OpenStackCharm.db_sync() default method checks that only
    the leader does the sync.  As congress uses alembic to do the database
    migration, it doesn't matter if it's done more than once, so we don't have
    to gate it in the charm.
    """
    with charms_openstack.charm.provide_charm_instance() as congress_charm:
        congress_charm.db_sync()


@charms.reactive.when('shared-db.available',
                      'identity-service.available',
                      'amqp.available')
def render_stuff(*args):
    """Render the configuration for Congress when all the interfaces are
    available.
    """
    with charms_openstack.charm.provide_charm_instance() as congress_charm:
        congress_charm.render_with_interfaces(args)
        congress_charm.assess_status()
        charms.reactive.set_state('congress.config.rendered')


@charms.reactive.when('shared-db.available',
                      'identity-service.available',
                      'amqp.available')
@charms.reactive.when('config-changed')
def config_changed(*args):
    """When the configuration is changed, check that we have all the interfaces
    and then re-render all the configuration files.  Note that this means that
    the configuration files won't be written until all the interfaces are
    available and STAY available.
    """
    render_stuff(*args)
