from datetime import datetime
from jsonpickle.unpickler import Unpickler
from botbuilder.core import TurnContext, MessageFactory
import asyncio


class ReminderHelper:
    @staticmethod
    async def remind_user(turn_context: TurnContext, storage):
        while True:
            try:
                now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
                store_items =list(storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/",f"select * from c where CONTAINS(c.id, 'Reminder') and CONTAINS(c.document.time, '{now}')"))
                ReminderLog = sorted([Unpickler().restore(item["document"]) for item in store_items])
                # print("ReminderLog:", ReminderLog)
                # reminders = sorted(list(filter(lambda x: x.time == now, ReminderLog)))
                print("REMINDERS:",ReminderLog)
                if len(ReminderLog)>0:
                    for reminder in reminders:
                        await turn_context.send_activity(MessageFactory.text(reminder))
                await asyncio.sleep(1)
            except Exception as e:
                print("Exception occured in remind_user: ", str(e))