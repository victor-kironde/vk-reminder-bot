from typing import List
from botbuilder.core import StoreItem


class Reminder(StoreItem):
    def __init__(
        self, title: str = None, time: str = None):
        self.title: str = title
        self.time: int = time

class ReminderLog(StoreItem):
    """
    Class for storing a log of reminders (text of messages) as a list.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.reminder_list = []
        self.turn_number = 0
        self.e_tag = "*"
