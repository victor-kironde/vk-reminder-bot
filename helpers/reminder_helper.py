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

            # db = list(storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/",f"select * from c where contains(c.id, 'Reminder') and c.document.time <= '{now}'"))
            # dba = Unpickler().restore(db[0]["document"])

            ReminderLog = [Unpickler().restore(item["document"]) for item in store_items]
            # print("OUR ITEM", dba)
            print("ReminderLog:", ReminderLog)
            # reminder_list = ReminderLog.reminder_list # get one hour
            # reminder_list = store_items.reminder_list
            # print("REMINDER IS WORKING:", len(reminder_list))
            # reminders = sorted(list(filter(lambda x: x.time[:x.time.rfind(":")] == now, map(lambda x: Reminder(**x), reminder_list))))
            reminders = sorted(list(filter(lambda x: x.time[:x.time.rfind(":")] == now, ReminderLog)))
            print("REMINDERS:",reminders)
            if len(reminders)>0:
                for reminder in reminders:
                    await turn_context.send_activity(MessageFactory.text(reminder))
            await asyncio.sleep(10)