import winreg
import urllib
from itertools import count

from registry_utils import RegistryNode

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
                res = RegistryNode(
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