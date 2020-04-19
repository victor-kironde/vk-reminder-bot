from datetime import datetime
import pytz
from botbuilder.core import TurnContext, CardFactory
from resources import Cards
from data_models import ReminderLog
from botbuilder.schema import ActivityTypes, Activity


class ReminderHelper:
    @staticmethod
    async def remind_user(turn_context: TurnContext, accessor):
        reminder_log = await accessor.get(turn_context, ReminderLog)
        timezone = pytz.timezone("Africa/Nairobi")
        now_local = datetime.now().astimezone(timezone)
        now = datetime.strftime(now_local, "%Y-%m-%d %I:%M")
        if len(reminder_log.new_reminders) > 0:
            reminder_time = datetime.strftime(
                sorted(reminder_log.new_reminders)[0].reminder_time,
                "%Y-%m-%d %I:%M %p",
            )
            if now in reminder_time:
                reminder = reminder_log.new_reminders.pop(0)
                snooze_card = Cards.snooze_card(reminder)
                message = Activity(
                    type=ActivityTypes.message,
                    attachments=[CardFactory.adaptive_card(snooze_card)],
                )
                reminder.done = True
                reminder_log.old_reminders.append(reminder)
                await turn_context.send_activity(message)
