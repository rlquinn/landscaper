# Copyright (c) 2017, Intel Research and Development Ireland Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Configuration class for the landscaper.
"""
import ConfigParser
from collections import namedtuple

from landscaper import paths
from landscaper.common import LOG


class ConfigurationManager(object):
    """
    Manages configuration data in the landscaper.
    """
    def __init__(self, config_file=paths.CONF_FILE):
        self.sections = []
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        for section in self.sections:
            self.add_section(section)

    def add_section(self, section):
        """
        Adds a section to the configuration manager. The configuration manager
        only manages configurations for sections that have been added. So  only
        sections that have been added can be retrieved.
        """
        if section not in self.sections:
            setattr(
                self, section, ConfigurationManager.
                _config_section_map(section, self.config))
            self.sections.append(section)

    @staticmethod
    def _config_section_map(section, config_file):
        """
        Returns a dictionary with the configuration values for the specific
        section
        :param section: section to be loaded (string)
        :param config_file: name of the configuration file (string)
        :return: dict
        """
        section_dictionary = dict()
        options = config_file.options(section)
        for option in options:
            section_dictionary[option] = config_file.get(section, option)
        return section_dictionary

    def get_variable(self, section, variable):
        """
        Returns the value of a variable from a given section.
        :param section: section to be loaded (string)
        :param variable: name of the variable (string)
        :return: string
        """
        if variable in self.get_variable_list(section):
            sect = getattr(self, section)
            return sect[variable]
        LOG.info('Config: Cannot find %s in section %s', variable, section)
        return None

    def get_variable_list(self, section):
        """
        Returns the list of the available variables in a section
        :param section: section to be loaded (string)
        :return: list
        """
        try:
            return getattr(self, section)
        except:
            err_msg = 'Config: Section {} not found'.format(section)
            LOG.info(err_msg)
            raise ValueError(err_msg)

    def get_hwloc_folder(self):
        """
        Returns hwloc directory path.
        """
        return self.get_variable('physical_layer', 'hwloc_folder')

    def get_cpuinfo_folder(self):
        """
        Returns cpu info directory path.
        """
        return self.get_variable('physical_layer', 'cpuinfo_folder')

    def get_types_to_filter(self):
        """
        Returns a list of node types to filter from the landscape.
        """
        filter_types = self.get_variable('physical_layer', 'types_to_filter')
        filter_types = filter_types.split(",")
        if filter_types and filter_types[0] == '':
            filter_types = list()
        return filter_types

    def get_machines(self):
        """
        Returns a list of all of the machines in the config file.
        """
        return self.get_variable('physical_layer', 'machines').split(",")

    def get_neo4j_url(self):
        """
        URL of the neo4j database.
        """
        return self.get_variable('neo4j', 'url')

    def get_neo4j_credentials(self):
        """
        Neo4j login security credentials.
        """
        user = self.get_variable('neo4j', 'user')
        password = self.get_variable('neo4j', 'password')
        return user, password

    def get_rabbitmq_info(self):
        """
        RabbitMQ configuration information.
        """
        rabbitMQ = namedtuple('rabbitMQ', 'username password host port topic'
                                          ' queue exchanges')
        username = self.get_variable('rabbitmq', 'rb_name')
        password = self.get_variable('rabbitmq', 'rb_password')
        host = self.get_variable('rabbitmq', 'rb_host')
        port = self.get_variable('rabbitmq', 'rb_port')
        topic = self.get_variable('rabbitmq', 'topic')
        queue = self.get_variable('rabbitmq', 'notification_queue')
        exchanges = self.get_variable('rabbitmq', 'exchanges').split(",")
        return rabbitMQ(username, password, host, port, topic, queue,
                        exchanges)

    def get_collectors(self):
        """
        List of collectors.
        """
        collectors = self.get_variable("general", "collectors").split(",")
        clean_collectors = [collector.strip() for collector in collectors]
        if clean_collectors[0]:
            return clean_collectors
        return []

    def get_event_listeners(self):
        """
        List of event listeners.
        """
        listeners_str = self.get_variable("general", "event_listeners")
        if listeners_str:
            listeners = listeners_str.split(',')
            clean_listeners = [listener.strip() for listener in listeners]
            if clean_listeners[0]:
                return clean_listeners
        return []

    def get_graph_db(self):
        """
        Returns graph database class name.
        """
        return self.get_variable("general", "graph_db")

    def get_flush(self):
        """
        Get boolean flush value, which indicates whether the database should
        be completely deleted and rebuilt before starting the event listeners.
        """
        flush = self.get_variable("general", "flush")
        if flush.lower() == "false":
            return False
        return True