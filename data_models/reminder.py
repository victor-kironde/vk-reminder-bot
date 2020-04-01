from typing import List
from botbuilder.core import StoreItem
from datetime import datetime


class Reminder(StoreItem):
    def __init__(
        self, title: str = None, time: str = None):
        self.title: str = title
        self.time: str = self._validate_time(time)
        # self.type = "Reminder"

    def __lt__(self, other):
        # print("OTHER.TIME", other.time)
        return self.datetime < other.datetime

    @property
    def datetime(self):
        return datetime.strptime(self.time, "%Y-%m-%d %H:%M")

    def _validate_time(self, time):
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            stime = ""
            if ":" in time and time.index(":") ==  2:
                t = time.split(":")
                ptime=datetime.now().replace(hour=int(t[0]), minute=int(t[1]), second=0)
                stime = datetime.strftime(ptime, time_format)
            elif ":" not in time:
                ptime = datetime.strptime(time, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
                stime = datetime.strftime(ptime, time_format)
            elif time.index("-") == 4:
                ptime = datetime.strptime(time, time_format)
                stime = datetime.strftime(ptime, time_format)
            return stime[:stime.rfind(":")]
        except Exception as e:
            # return time
            print("Exception", time)



class ReminderLog(StoreItem):
    """
    Class for storing a log of reminders (text of messages) as a list.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.reminder_list = []
        self.turn_number = 0
        self.e_tag = "*"
