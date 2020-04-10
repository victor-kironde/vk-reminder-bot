"""
Create a reminder store item
"""

import time

# import uuid
from datetime import datetime

# from typing import List
from botbuilder.core import StoreItem


class Reminder(StoreItem):
    def __init__(self, title: str = None, reminder_time: str = None, done=False):
        """
        Creates a reminder store item
        """
        super(Reminder, self).__init__()
        self.title: str = title
        self.reminder_time: str = self._validate_time(reminder_time)
        self.done = done

    def __lt__(self, other):
        return self.datetime > other.datetime

    @property
    def datetime(self):
        """
        get reminder datetime
        """
        return datetime.strptime(self.reminder_time, "%Y-%m-%d %H:%M:%S")

    def _validate_time(self, reminder_time):
        if not reminder_time:
            return
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            stime = ""
            ptime = None
            if ":" in reminder_time and reminder_time.index(":") == 2:
                t = reminder_time.split(":")
                ptime = datetime.now().replace(
                    hour=int(t[0]), minute=int(t[1]), second=0
                )
            elif ":" not in reminder_time:
                ptime = datetime.strptime(reminder_time, "%Y-%m-%d").replace(
                    hour=0, minute=0, second=0
                )
            elif reminder_time.index("-") == 4:
                ptime = datetime.strptime(reminder_time, time_format)
            stime = datetime.strftime(
                self.__datetime_from_utc_to_local(ptime), time_format
            )
            return stime[: stime.rfind(":")]
        except Exception as exception:
            print("Exception occured while Validating Time:", str(exception))

    def __datetime_from_utc_to_local(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
            now_timestamp
        )
        result = utc_datetime + offset
        return result
