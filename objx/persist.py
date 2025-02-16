# This file is placed in the Public Domain.


"disk persistence"


import datetime
import os
import pathlib
import threading
import typing


from .objects import fqn
from .objects import read as fread
from .objects import write as fwrite


"defines"


p    = os.path.join
lock = threading.RLock()


"exceptions"


class DecodeError(Exception):

    pass


"working directory"


class Workdir:

    wdr  = ""


"paths"


def long(name) -> str:
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def pidname(name) -> str:
    return p(Workdir.wdr, f"{name}.pid")


def skel() -> str:
    path = pathlib.Path(store())
    path.mkdir(parents=True, exist_ok=True)
    return path


def store(pth="") -> str:
    return p(Workdir.wdr, "store", pth)


def strip(pth, nmr=3) -> str:
    return os.sep.join(pth.split(os.sep)[-nmr:])

def types() -> [str]:
    return os.listdir(store())


"cache"


class Cache:

    objs = {}

    @staticmethod
    def add(path, obj) -> None:
        Cache.objs[path] = obj

    @staticmethod
    def get(path) -> typing.Any:
        return Cache.objs.get(path, None)

    @staticmethod
    def typed(matcher) -> [typing.Any]:
        for key in Cache.objs:
            if matcher not in key:
                continue
            yield Cache.objs.get(key)


def cdir(pth) -> None:
    path = pathlib.Path(pth)
    path.parent.mkdir(parents=True, exist_ok=True)


def ident(obj) -> str:
    return p(fqn(obj),*str(datetime.datetime.now()).split())


def read(obj, pth):
    fread(obj, pth)
    

def write(obj, pth=None):
    if pth is None:
        pth = store(ident(obj))
    cdir(pth)
    fwrite(obj, pth)
    Cache.objs[pth] = obj
    return pth


"interface"


def __dir__():
    return (
        'Cache',
        'DecodeError',
        'Workdir',
        'cdir',
        'ident',
        'long',
        'pidname',
        'read',
        'skel',
        'store',
        'strip',
        'types',
        'write'
    )
