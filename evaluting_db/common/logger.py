#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
logger
"""
import os
import logging
import logging.config
import yaml
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def setup_logging(
    default_path=None,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration
    """

    if default_path is None:
        default_path = './conf/logging_conf.yaml'

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO,
                            filename="log_info.log",
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
