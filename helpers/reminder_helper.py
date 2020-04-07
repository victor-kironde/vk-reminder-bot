from datetime import datetime
from jsonpickle.unpickler import Unpickler
from botbuilder.core import TurnContext, MessageFactory, CardFactory
import asyncio
from resources import SnoozeCard
import os

from botbuilder.schema import (
    ActivityTypes,
    Activity,
    InputHints, Attachment, HeroCard, CardImage, CardAction, ActionTypes, SuggestedActions
)

class ReminderHelper:

    def __init__(self, turn_context: TurnContext):
        self.reminder_queue = deque

    @staticmethod
    async def remind_user(turn_context: TurnContext, storage):
        while True:
            try:

                now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
                query = f"select * from c where CONTAINS(c.id, 'Reminder') and CONTAINS(c.document.time, '{now}') and not c.document.done"
                store_items =list(storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/", query))

                ReminderLog = sorted([Unpickler().restore(item["document"]) for item in store_items])
                if len(ReminderLog)>0:
                    fileDir = os.path.dirname(os.path.dirname(__file__))
                    filename = os.path.join(fileDir, 'bell.gif')
                    for reminder in ReminderLog:
                        SnoozeCard["body"][0]["text"] = reminder.title if hasattr(reminder, 'title') else ""
                        SnoozeCard["body"][1]["text"] = reminder.time if hasattr(reminder, 'time') else ""
                        SnoozeCard["body"][2]["url"] = "./bell.gif"
                        SnoozeCard["actions"][0]["card"]["body"][1]["value"] = reminder.id

                        message = Activity(
                                type=ActivityTypes.message,
                                attachments=[CardFactory.adaptive_card(SnoozeCard)],
                                )
                        await turn_context.send_activity(message)
                        r = reminder
                        r.done = True
                        await storage.write({reminder.id: r})
                await asyncio.sleep(1)
            except Exception as e:
                print("Exception occured in remind_user: ", str(e))