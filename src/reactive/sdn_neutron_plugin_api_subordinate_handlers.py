# Copyright 2018 Canonical Ltd
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

import charms.reactive as reactive

import charms_openstack.charm as charm

# This charm's library contains all of the handler code associated with
# sdn_neutron_plugin_api_subordinate
from charm.openstack import (
    sdn_neutron_plugin_api_subordinate as sdn_neutron_plugin_api_subordinate
)

charm.use_defaults(
    'charm.installed',
    'config.changed',
    'update-status')


@reactive.when_not('sdn-neutron-plugin-api-subordinate.installed')
def install_sdn_neutron_plugin_api_subordinate():
    # Do your install here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    reactive.set_flag('sdn-neutron-plugin-api-subordinate.installed')


@reactive.when('neutron-plugin-api-subordinate.available')
def render_config(*args):
    with charm.provide_charm_instance() as (
            sdn_neutron_plugin_api_subordinate_charm):
        sdn_neutron_plugin_api_subordinate_charm.render_with_interfaces(args)
        sdn_neutron_plugin_api_subordinate_charm.assess_status()
    if reactive.any_file_changed([sdn_neutron_plugin_api_subordinate.ML2_CONF]):
        remote_restart(*args)


@reactive.when('neutron-plugin-api-subordinate.connected')
def configure_plugin(api_principle):
    with charm.provide_charm_instance() as (
            sdn_neutron_plugin_api_subordinate_charm):
        (sdn_neutron_plugin_api_subordinate_charm
         .configure_plugin(api_principle))
        sdn_neutron_plugin_api_subordinate_charm.assess_status()


def remote_restart(api_principle):
    api_principle.request_restart()
