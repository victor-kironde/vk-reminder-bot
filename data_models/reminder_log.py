import time
import uuid
from datetime import datetime
from typing import List
from botbuilder.core import StoreItem

import heapq


class ReminderLog(StoreItem):
    """
    Class for storing a log of reminder objects.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.new_reminders = []
        self.old_reminders = []
        self.e_tag = "*"
