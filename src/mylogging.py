#! python2
# -*- coding: utf-8 -*-

import logging
FORMAT = '%(message)s'
logging.basicConfig(format=FORMAT)
_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)


def log(msg):
    _logger.debug(msg)

def info(msg):
    _logger.info(msg)

def warn(msg):
    _logger.warning(msg)

def exception(msg):
    _logger.exception(msg)
