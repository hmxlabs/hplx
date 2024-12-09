import math
import json


class HplResults:

    def __init__(self) -> None:
        self._n = math.nan
        self._nb = math.nan
        self._p = math.nan
        self._q = math.nan
        self._time = math.nan
        self._gflops = math.nan

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, n):
        self._n = n

    @property
    def nb(self):
        return self._nb

    @nb.setter
    def nb(self, nb):
        self._nb = nb

    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, p):
        self._p = p

    @property
    def q(self):
        return self._q

    @q.setter
    def q(self, q):
        self._q = q

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    @property
    def gflops(self):
        return self._gflops

    @gflops.setter
    def gflops(self, gflops):
        self._gflops = gflops

    def __str__(self) -> str:
        return f"n={self.n}, nb={self.nb}, p={self.p}, q={self.q}, time={self.time}, gflops={self.gflops}"

    def to_dict(self):
        return {
            "n": self.n,
            "nb": self.nb,
            "p": self.p,
            "q": self.q,
            "time": self.time,
            "gflops": self.gflops
        }

    def to_json(self):
        return json.dumps(self.to_dict())

