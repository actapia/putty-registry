import winreg
import urllib
from itertools import count

from IPython import embed

class PuttyRegistry():
    def __init__(self, session_access=winreg.KEY_ALL_ACCESS):
        self._reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        self._session_key = winreg.OpenKey(
            self._reg,
            r"SOFTWARE\SimonTatham\PuTTY\Sessions"
        )
        self._session_access = session_access
        self._sessions = {}
        self._sessions_iter = self._get_sessions()

    def _get_sessions(self):
        try:
            for i in count(0):
                name = winreg.EnumKey(self._session_key, i)
                k = winreg.OpenKey(
                    self._session_key,
                    name,
                    0,
                    self._session_access
                )
                res = PuttySession(
                    k,
                    name
                )
                self._sessions[name] = res
                yield res
        except OSError:
            pass

    def sessions(self):
        yield from self._sessions
        yield from self._sessions_iter

    def get_session(self, name):
        name = urllib.parse.quote(name)
        try:
            return self._sessions[name]
        except:
            for s in self._sessions_iter:
                if s.name == name:
                    return s
        raise ValueError("No such session {}.".format(name))

    def close(self):
        for s in self._sessions.values():
            s.close()
        self._session_key.Close()
        self._reg.Close()

class PuttySession:
    __slots__ =  ["_name", "_key", "_values", "_value_iter", "closed"]
    datatypes = {
        bytes: winreg.REG_BINARY,
        int: winreg.REG_QWORD,
        str: winreg.REG_SZ
    }
    def __init__(self, key, name):
        #embed()
        self._name = name
        self._key = key
        self._values = {}
        self._value_iter = self._enum_values()
        self.closed = False

    @property
    def name(self):
        return self._name

    def _enum_values(self):
        # print("In enum.")
        try:
            for i in count(0):
                l, v, t = winreg.EnumValue(self._key, i)
                self._values[l] = (i, [v, t])
                yield l
        except OSError:
            pass

    def list_values(self):
        yield from self._values.keys()
        yield from self._enum_values()

    def get_value(self, k):
        if not k in self._values:
            try:
                for l in self._value_iter:
                    if l == k:
                        break
            except StopIteration:
                pass
        return self._values[k][1][0]

    def __getattr__(self, k):
        try:
            return super().__getattr__(k)
        except AttributeError:
            return self.get_value(k)

    def __setattr__(self, k, v):
        if k in self._slots:
            super().__setattr__(k, v)
        else:
            try:
                _ = getattr(self, k)
                self._values[k][1][0] = v
            except AttributeError:
                self._values[k] = (-1, [v, self.datatypes[type(v)]])
            winreg.SetValueEx(self._key, k, 0, self._values[k][1][1], v)


    def close(self):
        if not self.closed:
            self._key.Close()
            self.closed = True

    def __repr__(self):
        return "PuttySession({}, {})".format(self._key, self._name)

    def __dir__(self):
        return list(self._slots.union(set(self.list_values())))

PuttySession._slots = set(PuttySession.__slots__)