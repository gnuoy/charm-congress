import amulet

from congressclient.v1 import client as congress_client

from charmhelpers.contrib.openstack.amulet.deployment import (
    OpenStackAmuletDeployment
)

from charmhelpers.contrib.openstack.amulet.utils import (
    OpenStackAmuletUtils,
    DEBUG,
)

# Use DEBUG to turn on debug logging
u = OpenStackAmuletUtils(DEBUG)


class CongressBasicDeployment(OpenStackAmuletDeployment):
    """Amulet tests on a basic Congress deployment.

    Note that these tests don't attempt to do a functional test on Congress,
    merely to demonstrate that the relations work and that they transfer the
    correct information across them.

    A functional test will be performed by a mojo or tempest test.
    """

    def __init__(self, series, openstack=None, source=None, stable=False):
        """Deploy the entire test environment.
        """
        super(CongressBasicDeployment, self).__init__(
            series, openstack, source, stable)
        self._keystone_version = '2'
        self._add_services()
        self._add_relations()
        self._configure_services()
        self._deploy()

        u.log.info('Waiting on extended status checks...')
        exclude_services = []
        self._auto_wait_for_status(exclude_services=exclude_services)

        self._initialize_tests()

    def _add_services(self):
        """Add services

           Add the services that we're testing, where congress is local,
           and the rest of the service are from lp branches that are
           compatible with the local charm (e.g. stable or next).
           """
        this_service = {'name': 'congress'}
        other_services = [
            {'name': 'percona-cluster',
             'constraints': {'mem': '3072M'}},
            {'name': 'rabbitmq-server'},
            {'name': 'keystone'},
        ]
        super(CongressBasicDeployment, self)._add_services(
            this_service, other_services)

    def _add_relations(self):
        """Add all of the relations for the services."""
        relations = {
            'congress:shared-db': 'percona-cluster:shared-db',
            'congress:amqp': 'rabbitmq-server:amqp',
            'congress:identity-service': 'keystone:identity-service',
            'keystone:shared-db': 'percona-cluster:shared-db',
        }
        super(CongressBasicDeployment, self)._add_relations(relations)

    def _configure_services(self):
        """Configure all of the services."""
        keystone_config = {
            'admin-password': 'openstack',
            'admin-token': 'ubuntutesting',
        }
        configs = {
            'keystone': keystone_config,
        }
        super(CongressBasicDeployment, self)._configure_services(configs)

    def _initialize_tests(self):
        """Perform final initialization before tests get run."""
        # Access the sentries for inspecting service units
        self.congress_sentry = self.d.sentry['congress'][0]
        self.percona_cluster_sentry = self.d.sentry['percona-cluster'][0]
        self.keystone_sentry = self.d.sentry['keystone'][0]
        self.rabbitmq_sentry = self.d.sentry['rabbitmq-server'][0]
        u.log.debug('openstack release val: {}'.format(
            self._get_openstack_release()))
        u.log.debug('openstack release str: {}'.format(
            self._get_openstack_release_string()))

        # Authenticate admin with keystone endpoint
        self.keystone_session, self.keystone = u.get_default_keystone_session(
            self.keystone_sentry,
            openstack_release=self._get_openstack_release())

        self.congress = congress_client.Client(
            session=self.keystone_session,
            auth=None,
            interface='publicURL',
            service_type='policy',
            region_name='RegionOne')

    def test_100_services(self):
        """Verify the expected services are running on the corresponding
           service units."""
        u.log.debug('Checking system services on units...')

        congress_svcs = [
            'congress-server',
        ]

        service_names = {
            self.congress_sentry: congress_svcs,
        }

        ret = u.validate_services_by_name(service_names)
        if ret:
            amulet.raise_status(amulet.FAIL, msg=ret)

        u.log.debug('OK')

    def test_200_test_congress_api(self):
        assert self.congress.list_api_versions()
