# This file is placed in the Public Domain.


"log text"


import time


from objx.locater import find, fntime
from objx.objects import Object
from objx.persist import write
from objr.utility import elapsed


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


def log(event):
    if not event.rest:
        nmr = 0
        for fnm, obj in find('log', event.gets):
            lap = elapsed(time.time() - fntime(fnm))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply('no log')
        return
    obj = Log()
    obj.txt = event.rest
    write(obj)
    event.done()


def __dir__():
    return (
        'log',
    )
