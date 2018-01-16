#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
config
"""
import sys
import yaml
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from logger import setup_logging
setup_logging()

class YamlConfigReader(object):
    """
    YamlConfigReader
    """
    def __init__(self, config_file):
        self.logger = logging.getLogger("YamlConfigReader")
        self.config_file = config_file
        self.config_dict = self.load_conf(self.config_file)

    def load_conf(self, config_file):
        """
        load_conf
        """
        try:
            with open(config_file, 'rt') as f:
                config_dict = yaml.load(f)
                return config_dict
        except Exception as e:
            self.logger.exception(e)
            raise Exception

    def get_config_dict(self):
        """
        get_config_dict
        """
        if self.config_dict is not None \
                and isinstance(self.config_dict, dict) \
                and len(self.config_dict) > 0:
            return self.config_dict
        return None

if __name__ == '__main__':
    cr = YamlConfigReader('./conf/db_conf.yaml')
    parms = cr.get_config_dict()
    print parms
