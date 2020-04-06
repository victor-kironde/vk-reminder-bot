from typing import List
from botbuilder.core import StoreItem
from datetime import datetime
import time


class Reminder(StoreItem):
    def __init__(
        self, title: str = None, time: str = None, done=False, _id=None, type=None):
        self.title: str = title
        self.time: str = self._validate_time(time)
        self.type = "Reminder"
        self._id = ""
        self.done = done

    def __lt__(self, other):
        return self.datetime < other.datetime

    @property
    def datetime(self):
        return datetime.strptime(self.time, "%Y-%m-%d %H:%M")

    def _validate_time(self, reminder_time):
        if not reminder_time:
            return
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            stime = ""
            ptime=None
            if ":" in reminder_time and reminder_time.index(":") ==  2:
                t = reminder_time.split(":")
                ptime=datetime.now().replace(hour=int(t[0]), minute=int(t[1]), second=0)
            elif ":" not in reminder_time:
                ptime = datetime.strptime(reminder_time, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            elif reminder_time.index("-") == 4:
                ptime = datetime.strptime(reminder_time, time_format)
            stime = datetime.strftime(self.__datetime_from_utc_to_local(ptime), time_format)
            return stime[:stime.rfind(":")]
        except Exception as e:
            print("Exception occured while Validating Time:", str(e))

    def __datetime_from_utc_to_local(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
            now_timestamp
        )
        result = utc_datetime + offset
        return result



class ReminderLog(StoreItem):
    """
    Class for storing a log of reminders (text of messages) as a list.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.reminder_list = []
        self.turn_number = 0
        self.e_tag = "*"
