"""
Python Logging Setup
"""
import sys
import logging
import warnings


def setup_logging(debug=False, stream=sys.stderr, log_format=None):
    """
    Default logger
    """
    logLevel = logging.DEBUG if debug else logging.INFO
    if log_format is None:
        log_format = "%(asctime)s [%(levelname)s] %(message)s"
    logging.basicConfig(stream=stream, level=logLevel, format=log_format)
    logging.info("Running %s", " ".join(sys.argv))

    def sendWarningsToLog(message, category, filename, lineno):
        """
        Put warnings into logger
        """
        logging.warning('%s:%s: %s:%s', filename, lineno, category.__name__, message)
        return
    warnings.showwarning = sendWarningsToLog
