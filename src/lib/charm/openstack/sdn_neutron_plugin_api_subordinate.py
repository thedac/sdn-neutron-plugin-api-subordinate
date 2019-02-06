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

import charms_openstack.adapters
import charms_openstack.charm
# import charmhelpers.contrib.openstack.utils as ch_utils


# This subordinate charm will own the ml2_conf.ini file
# Only this charm will edit it. Upon a change to the file
# the primary charm, neutron-api, will be notified to restart the
# neutron-server service. The templete is found in src/templates/ml2_conf.ini
ML2_CONF = '/etc/neutron/plugins/ml2/ml2_conf.ini'
VLAN = 'vlan'
VXLAN = 'vxlan'
GRE = 'gre'
OVERLAY_NET_TYPES = [GRE, VLAN, VXLAN]


# Add specific configuration options
@charms_openstack.adapters.config_property
def overlay_net_types(config):
    overlay_networks = config.overlay_network_type.split()
    for overlay_net in overlay_networks:
        if overlay_net not in OVERLAY_NET_TYPES:
            raise ValueError(
                'Unsupported overlay-network-type {}'.format(overlay_net))
    return ','.join(overlay_networks)


class SDNNeutronPluginApiSubordinateCharm(
        charms_openstack.charm.OpenStackCharm):

    name = 'sdn-neutron-plugin-api-subordinate'
    release = 'queens'
    group = 'neutron'

    packages = ['neutron-common', 'neutron-plugin-ml2']

    required_relations = ['neutron-plugin-api-subordinate']

    restart_map = {ML2_CONF: []}
    adapters_class = charms_openstack.adapters.OpenStackRelationAdapters

    # Custom configure for the class
    service_plugins = 'router,firewall,lbaas,vpnaas,metering'

    def configure_plugin(self, api_principle):
        """Add sections and tuples to insert values into neutron-server's
        neutron.conf
        """
        # This is the method to inject configuration into the
        # /etc/neutron/neutron.conf file. Specify the header a configuration
        # option should be under and the key vaule pairs.
        inject_config = {
            "neutron-api": {
                "/etc/neutron/neutron.conf": {
                    "sections": {
                        'DEFAULT': [
                            ('foo', 'bar')
                        ],
                        'sdn_plugin_example': [
                            ('baz', 'qux')
                        ],
                    }
                }
            }
        }

        api_principle.configure_plugin(
            neutron_plugin='sdn',
            core_plugin='neutron.plugins.ml2.plugin.Ml2Plugin',
            neutron_plugin_config='/etc/neutron/plugins/ml2/ml2_conf.ini',
            service_plugins=self.service_plugins,
            subordinate_configuration=inject_config)


class RockySDNNeutronPluginApiSubordinateCharm(
        SDNNeutronPluginApiSubordinateCharm):
    """For the a specific OpenSTack release we can override values as required
    """

    release = 'rocky'

    packages = ['neutron-common',
                'neutron-plugin-ml2',
                ]

    service_plugins = 'router,firewall,metering'
