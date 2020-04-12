"""
Create a reminder store item
"""

import uuid
from datetime import datetime
import pytz
from botbuilder.core import StoreItem


class Reminder(StoreItem):
    def __init__(self, title: str = None, reminder_time: str = None, done=False):
        """
        Creates a reminder store item
        """
        super(Reminder, self).__init__()
        self.title: str = title
        self.reminder_time: str = reminder_time
        self.done = done
        self.id = "Reminder-" + str(uuid.uuid4())

    def __lt__(self, other):
        return self.reminder_time > other.reminder_time

    @property
    def reminder_time(self):
        return self._reminder_time

    @reminder_time.setter
    def reminder_time(self, reminder_time):
        self._reminder_time = self._validate_time(reminder_time)

    def _validate_time(self, reminder_time=None):
        if not reminder_time or not isinstance(reminder_time, str):
            return reminder_time
        try:
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
                ptime = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")
            return self.__datetime_from_utc_to_local(ptime)
        except Exception as exception:
            print("Exception occured while Validating Time:", str(exception))

    def __datetime_from_utc_to_local(self, utc_datetime):
        timezone = pytz.timezone("Africa/Nairobi")
        result = timezone.localize(utc_datetime)
        return result
