import threading
import time
from collections import defaultdict, deque


def extract_bearer_token(authorization_header):
    if not authorization_header:
        return None
    scheme, separator, token = authorization_header.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


class FixedWindowRateLimiter:
    def __init__(self, limit, window_seconds, clock=None):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock or time.monotonic
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key):
        now = self.clock()
        cutoff = now - self.window_seconds
        with self.lock:
            timestamps = self.requests[key]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return False
            timestamps.append(now)
            return True
