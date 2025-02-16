# This file is placed in the Public Domain.


"show uptime/version"


import time


from objr.package import STARTTIME
from objr.utility import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))


def __dir__():
    return (
        'upt',
    )
