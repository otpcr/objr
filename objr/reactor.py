# This file is placed in the Public Domain.


"callback engine"


import queue
import threading
import time
import _thread


from .threads import launch


cblock      = threading.RLock()
displaylock = threading.RLock()


class Default:

    def __contains__(self, key):
        return key in dir(self)

    def __getattr__(self, key):
        return self.__dict__.get(key, "")

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Config(Default):

    pass


class Message(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr   = None
        self.ctime  = time.time()
        self.result = {}
        self.type   = "event"
        self.txt    = ""

    def done(self) -> None:
        self.reply("ok")

    def ready(self) -> None:
        self._ready.set()

    def reply(self, txt) -> None:
        self.result[time.time()] = txt

    def wait(self) -> None:
        self._ready.wait()
        if self._thr:
            self._thr.join()


class Reactor:

    def __init__(self):
        self.cbs     = {}
        self.queue   = queue.Queue()
        self.ready   = threading.Event()
        self.stopped = threading.Event()

    def callback(self, evt) -> None:
        with cblock:
            func = self.cbs.get(evt.type, None)
            if func:
                try:
                    evt._thr = launch(func, evt, name=evt.cmd or evt.txt)
                except Exception:
                    evt.ready()

    def loop(self) -> None:
        evt = None
        while not self.stopped.is_set():
            try:
                evt = self.poll()
                if evt is None:
                    break
                evt.orig = repr(self)
                self.callback(evt)
            except (KeyboardInterrupt, EOFError):
                if evt:
                    evt.ready()
                _thread.interrupt_main()
        self.ready.set()

    def poll(self) -> Message:
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put(evt)

    def register(self, typ, cbs) -> None:
        self.cbs[typ] = cbs

    def start(self) -> None:
        self.stopped.clear()
        self.ready.clear()
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()
        self.queue.put(None)

    def wait(self) -> None:
        self.ready.wait()


class Client(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        Fleet.add(self)

    def raw(self, txt) -> None:
        raise NotImplementedError("raw")

    def say(self, channel, txt) -> None:
        self.raw(txt)


class Fleet:

    bots = {}

    @staticmethod
    def add(bot) -> None:
        Fleet.bots[repr(bot)] = bot

    @staticmethod
    def announce(txt) -> None:
        for bot in Fleet.bots.values():
            bot.announce(txt)

    @staticmethod
    def display(evt) -> None:
        with displaylock:
            for tme in sorted(evt.result):
                text = evt.result[tme]
                Fleet.say(evt.orig, evt.channel, text)
            evt.ready()

    @staticmethod
    def first() -> None:
        bots =  list(Fleet.bots.values())
        res = None
        if bots:
            res = bots[0]
        return res

    @staticmethod
    def get(orig) -> None:
        return Fleet.bots.get(orig, None)

    @staticmethod
    def say(orig, channel, txt) -> None:
        bot = Fleet.get(orig)
        if bot:
            bot.say(channel, txt)

    @staticmethod
    def wait() -> None:
        for bot in Fleet.bots.values():
            if "wait" in dir(bot):
                bot.wait()


def __dir__():
    return (
        'Client',
        'Config',
        'Default',
        'Fleet',
        'Message',
        'Reactor'
    )
