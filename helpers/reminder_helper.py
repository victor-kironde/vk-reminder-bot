from datetime import datetime
from jsonpickle.unpickler import Unpickler
from botbuilder.core import TurnContext, MessageFactory, CardFactory
import asyncio
from resources import SnoozeCard

from botbuilder.schema import (
    ActivityTypes,
    Activity,
    InputHints,
    Attachment,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
    SuggestedActions,
)


class ReminderHelper:
    @staticmethod
    async def remind_user(turn_context: TurnContext, storage):
        while True:
            try:

                now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
                query = f"select * from c where CONTAINS(c.id, 'Reminder') and CONTAINS(c.document.time, '{now}') and not c.document.done"
                store_items = list(
                    storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/", query)
                )

                ReminderLog = sorted(
                    [Unpickler().restore(item["document"]) for item in store_items]
                )
                if len(ReminderLog) > 0:
                    for reminder in ReminderLog:
                        SnoozeCard["body"][0]["columns"][0]["items"][0]["text"] = (
                            reminder.title if hasattr(reminder, "title") else ""
                        )
                        SnoozeCard["body"][0]["columns"][0]["items"][1]["text"] = (
                            reminder.time if hasattr(reminder, "time") else ""
                        )
                        SnoozeCard["actions"][0]["data"]["reminder_id"] = reminder.id
                        SnoozeCard["actions"][1]["data"]["reminder_id"] = reminder.id

                        message = Activity(
                            type=ActivityTypes.message,
                            attachments=[CardFactory.adaptive_card(SnoozeCard)],
                        )
                        await turn_context.send_activity(message)
                        r = reminder
                        r.done = True
                        await storage.write({reminder.id: r})
                await asyncio.sleep(5)
            except Exception as e:
                print("Exception occured in remind_user: ", str(e))
