# This file is placed in the Public Domain.


"objects"


import datetime
import pathlib
import json
import os
import typing
import threading


lock = threading.RLock()
p    = os.path.join



class Error(Exception):

    pass


class Object:

    def __contains__(self, key):
        return key in dir(self)

    def __iter__(self):
        return iter(self.__dict__)


    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)



def construct(obj, *args, **kwargs) -> None:
    if args:
        val = args[0]
        if isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        elif isinstance(val, Object):
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def edit(obj, setter, skip=False) -> None:
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def fmt(obj, args=None, skip=None, plain=False) -> str:
    if args is None:
        args = keys(obj)
    if skip is None:
        skip = []
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt += f'{key}="{value}" '
        else:
            txt += f'{key}={value} '
    return txt.strip()


def fqn(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def ident(obj) -> str:
    return p(fqn(obj),*str(datetime.datetime.now()).split())


def items(obj) -> [(str,typing.Any)]:
    if isinstance(obj,type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> [str]:
    if isinstance(obj, type({})):
        return obj.keys()
    return list(obj.__dict__.keys())


def update(obj, data) -> None:
    if not isinstance(data, type({})):
        obj.__dict__.update(vars(data))
    else:
        obj.__dict__.update(data)


def values(obj) -> [typing.Any]:
    return obj.__dict__.values()



class Decoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def decode(self, s, _w=None) -> typing.Any:
        val = json.JSONDecoder.decode(self, s)
        if isinstance(val, dict):
            return hook(val)
        return val


def hook(objdict) -> Object:
    obj = Object()
    construct(obj, objdict)
    return obj


def load(fpt, *args, **kw) -> Object:
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.load(fpt, *args, **kw)


def loads(string, *args, **kw) -> Object:
    kw["cls"] = Decoder
    kw["object_hook"] = hook
    return json.loads(string, *args, **kw)


def read(obj, pth):
    with lock:
        with open(pth, "r") as fpt:
            try:
                data = load(fpt)
            except json.decoder.JSONDecodeError as ex:
                raise Error(pth) from ex
            update(obj, data)



class Encoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o) -> str:
        if isinstance(o, dict):
            return o.items()
        if issubclass(type(o), Object):
            return vars(o)
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(obj, fpt, *args, **kw) -> str:
    kw["cls"] = Encoder
    return json.dump(obj, fpt, *args, **kw)


def dumps(*args, **kw) -> str:
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def write(obj, pth):
    with lock:
        cdir(pth)
        with open(pth, "w") as fpt:
            dump(obj, fpt, indent=4)



def cdir(path):
    if not os.path.exists(os.path.dirname(path)):
        pth = pathlib.Path(path)
        pth.parent.mkdir(parents=True, exist_ok=True)



def __dir__():
    return (
        'Error',
        'Object',
        'construct',
        'dumps',
        'edit',
        'fmt',
        'fqn',
        'items',
        'keys',
        'loads',
        'read',
        'update',
        'values',
        'write'
    )
