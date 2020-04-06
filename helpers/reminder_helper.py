from datetime import datetime
from jsonpickle.unpickler import Unpickler
from botbuilder.core import TurnContext
import asyncio


class ReminderHelper:
    @staticmethod
    async def remind_user(turn_context: TurnContext, storage):
        while True:
            now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
            store_items =list(storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/","select * from c where CONTAINS(c.id, 'Reminder')"))
            ReminderLog = [Unpickler().restore(item["document"]) for item in store_items]
            print("ReminderLog:", ReminderLog)
            reminders = sorted(list(filter(lambda x: x.time[:x.time.rfind(":")] == now, ReminderLog)))
            print("REMINDERS:",reminders)
            if len(reminders)>0:
                for reminder in reminders:
                    await turn_context.send_activity(MessageFactory.text(reminder))
            await asyncio.sleep(10)