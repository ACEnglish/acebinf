"""
Simplified command running
"""
import os
import time
import signal
import logging
import datetime
import subprocess
from collections import namedtuple


class Alarm(Exception):

    """ Alarm Class for command timeouts """
    pass


def alarm_handler(signum, frame=None):  # pylint: disable=unused-argument
    """ Alarm handler for command timeouts """
    raise Alarm

cmd_result = namedtuple("cmd_result", "ret_code stdout stderr run_time")


def cmd_exe(cmd, timeout=-1):
    """
    Executes a command through the shell.
    timeout in minutes! so 1440 mean is 24 hours.
    -1 means never
    returns namedtuple(ret_code, stdout, stderr, datetime)
    where ret_code is the exit code for the command executed
    stdout/err is the Standard Output Error from the command
    and datetime is a datetime object of the execution time
    """
    t_start = time.time()
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, close_fds=True,
                            preexec_fn=os.setsid)
    signal.signal(signal.SIGALRM, alarm_handler)
    if timeout > 0:
        signal.alarm(int(timeout * 60))
    try:
        stdoutVal, stderrVal = proc.communicate()
        signal.alarm(0)  # reset the alarm
    except Alarm:
        logging.error(("Command was taking too long. "
                       "Automatic Timeout Initiated after %d"), timeout)
        os.killpg(proc.pid, signal.SIGTERM)
        proc.kill()
        return 214, None, None, datetime.timedelta(seconds=int(time.time() - t_start))
    t_end = time.time()

    stdoutVal = bytes.decode(stdoutVal)
    retCode = proc.returncode
    ret = cmd_result(retCode, stdoutVal, stderrVal, datetime.timedelta(seconds=int(t_end - t_start)))
    return ret
