"""
Logging module for Pyjamas, mimicking CPython's logging module.

Usage example::

    from pyjamas import logging
    log = logging.getConsoleLogger()
    log.debug('This is a debug message')
"""
__author__ = 'Peter Bittner <peter.bittner@gmx.net>'

from pyjamas.logging.handlers import \
    AlertHandler, AppendHandler, ConsoleHandler, NullHandler
# blatantly copy everything from CPython's logging (was: `from logging import *` replaced due to Python 2.6 issues)
from logging import getLogger, Formatter, StreamHandler, DEBUG, BASIC_FORMAT

# a handy replacement for BASIC_FORMAT printing nothing but the plain text
PLAIN_FORMAT = '%(message)s'

def getLoggerForHandler(handler, name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """Use this function to easily include new loggers in your application,
    e.g. <code>log = logging.getLoggerForHandler(NullHandler())</code>"""
    formatter = Formatter(fmt)
    handler.setFormatter(formatter)
    logger = getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def getAlertLogger(name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """A logger that shows any log message in a browser's alert popup dialog."""
    return getLoggerForHandler(AlertHandler(), name, level, fmt)

def getAppendLogger(name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """A logger that appends text to the end of the HTML document body."""
    return getLoggerForHandler(AppendHandler(name), name, level, fmt)

def getConsoleLogger(name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """A logger that uses Firebug's console.log() function."""
    return getLoggerForHandler(ConsoleHandler(), name, level, fmt)

def getNullLogger(name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """A logger that does nothing. Use it to disable logging."""
    return getLoggerForHandler(NullHandler(), name, level, fmt)

def getPrintLogger(name=__name__, level=DEBUG, fmt=BASIC_FORMAT):
    """A logger that prints text to cerr, the default error output stream."""
    return getLoggerForHandler(StreamHandler(), name, level, fmt)

