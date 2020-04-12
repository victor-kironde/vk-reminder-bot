# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from data_models import Reminder

from datetime import datetime
from .datetime_helper import DatetimeHelper


class Intent(Enum):
    CREATE_REMINDER = "CreateReminder"
    SHOW_REMINDERS = "ShowReminders"
    HELP = "Help"
    SNOOZE_REMINDER = "Snooze"
    DELETE_REMINDER = "DeleteReminder"
    NONE_INTENT = None


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            intent = LuisRecognizer.top_intent(recognizer_result)
            print("INTENT", intent)

            if intent == Intent.CREATE_REMINDER.value:
                result = Reminder()
                reminder_entities = recognizer_result.entities.get("$instance", {}).get(
                    "Calendar_Message", []
                )
                if len(reminder_entities) > 0:
                    result.title = reminder_entities[0]["text"].title()
                else:
                    result.title = None

                date_entities = recognizer_result.entities.get("datetime", [])

                if date_entities:
                    timex = date_entities[0]["timex"]

                    if timex:
                        result.reminder_time = DatetimeHelper.format_datetime(timex[0])

                else:
                    result.reminder_time = None
            elif intent == Intent.SNOOZE_REMINDER.value:
                text = turn_context.activity.text
                result = Reminder()
                result.id = text.split()[1]

                date_entities = recognizer_result.entities.get("datetime", [])

                if date_entities:
                    timex = date_entities[0]["timex"]

                    if timex:
                        result.reminder_time = DatetimeHelper.format_datetime(timex[0])

        except Exception as exception:
            print(exception)

        return intent, result
