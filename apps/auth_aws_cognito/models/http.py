# -*- coding: utf-8 -*-

import os
import random
import time


def session_gc(session_store):
    if random.random() < 0.001:
        # we keep session one week
        last_day = time.time() - 60*60*24
        for fname in os.listdir(session_store.path):
            path = os.path.join(session_store.path, fname)
            try:
                if os.path.getmtime(path) < last_day:
                    os.unlink(path)
            except OSError:
                pass
