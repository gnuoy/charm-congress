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

from __future__ import absolute_import
from __future__ import print_function

import charm.openstack.congress as congress

import charms_openstack.test_utils as test_utils


class Helper(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()
        self.patch_release(congress.CongressCharm.release)


class TestCongressCharm(Helper):

    def test_get_amqp_credentials(self):
        c = congress.CongressCharm()
        self.assertEqual(c.get_amqp_credentials(), ('congress', 'openstack'))

    def test_get_database_setup(self):
        c = congress.CongressCharm()
        self.assertEqual(
            c.get_database_setup(),
            [dict(database='congress', username='congress')])
