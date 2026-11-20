"""Controlled timing wrapper: the only module allowed to touch time.sleep."""

import time


def pause_briefly(seconds: float) -> None:
    if seconds <= 0:
        return
    time.sleep(min(seconds, 0.05))
