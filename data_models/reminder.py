from typing import List


class Reminder:
    def __init__(
        self, title: str = None, time: str = None):
        self.title: str = title
        self.time: int = time
