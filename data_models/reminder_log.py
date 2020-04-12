from botbuilder.core import StoreItem


class ReminderLog(StoreItem):
    """
    Class for storing a log of reminder objects.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.new_reminders = []
        self.old_reminders = []
        self.e_tag = "*"
