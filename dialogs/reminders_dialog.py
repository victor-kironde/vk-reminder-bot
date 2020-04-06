from botbuilder.core import MessageFactory, UserState, MemoryStorage, CardFactory, TurnContext
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
    DialogTurnStatus,
    DialogContext
)
from botbuilder.dialogs.prompts import (
    PromptOptions,TextPrompt,
    DateTimePrompt,
    ConfirmPrompt)
from botbuilder.schema import (
    ActivityTypes,
    Activity,
    InputHints, Attachment, HeroCard, CardImage, CardAction, ActionTypes, SuggestedActions
)

import json
import os

from botbuilder.dialogs.choices import Choice
from data_models import Reminder, ReminderLog
from datetime import datetime
from config import DefaultConfig
from botbuilder.azure import CosmosDbStorage, CosmosDbConfig

from resources import HelpCard, ReminderCard

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from azure.cognitiveservices.language.luis.runtime.models import LuisResult
from helpers import LuisHelper
from .cancel_and_help_dialog import CancelAndHelpDialog
from jsonpickle.unpickler import Unpickler
config = DefaultConfig()

class RemindersDialog(CancelAndHelpDialog):
    def __init__(self, user_state: UserState, storage):
        super(RemindersDialog, self).__init__(RemindersDialog.__name__)

        self.user_state = user_state
        self.REMINDER = "value-reminder"
        self.storage = storage

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(DateTimePrompt(DateTimePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.choice_step,
                    self.reminder_step,
                    self.time_step,
                    self.confirm_step,
                ],
            )
        )

        self.initial_dialog_id = "WFDialog"

        luis_application = LuisApplication(
            config.LUIS_APP_ID,
            config.LUIS_API_KEY,
            config.LUIS_API_HOST_NAME,
        )
        luis_options = LuisPredictionOptions(
            include_all_intents=True, include_instance_data=True
        )
        self.recognizer = LuisRecognizer(luis_application, luis_options, True)


    async def choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        intent, recognizer_result = await LuisHelper.execute_luis_query(
        self.recognizer, step_context.context
        )
        step_context.values[self.REMINDER] = recognizer_result
        if intent == "ShowReminders":
            await self._show_reminders(step_context.context)
            return await step_context.end_dialog()

        elif intent == "CreateReminder":
            return await step_context.next(None)

        elif intent == "Help":
            message = Activity(type=ActivityTypes.message,
                                attachments=[CardFactory.adaptive_card(HelpCard)])
            await step_context.context.send_activity(message)
            return await step_context.end_dialog()

        else:
            await step_context.context.send_activity("I didn't get that!")
            await self._send_suggested_actions(step_context.context)
            return await step_context.end_dialog()

    async def reminder_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        if not reminder.title:
            prompt_options = PromptOptions(
                prompt=MessageFactory.text("What would you like me to remind you about?")
            )

            return await step_context.prompt(TextPrompt.__name__, prompt_options)
        else:
            return await step_context.next(None)


    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        if step_context.result:
            reminder.title = step_context.result
        if not reminder.time:
            prompt_options = PromptOptions(
                prompt=MessageFactory.text("When should I remind you?"),
                retry_prompt=MessageFactory.text("Please enter a valid time:"),

            )
            return await step_context.prompt(DateTimePrompt.__name__, prompt_options)
        else:
            return await step_context.next(None)


    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        reminder: Reminder = step_context.values[self.REMINDER]
        reminder.time = step_context.result[0].value if not reminder.time else reminder.time
        await step_context.context.send_activity(f"""I have set the reminder!""")

        ReminderCard["body"][0]["text"] = reminder.title
        ReminderCard["body"][1]["text"] = reminder.time

        await step_context.context.send_activity(Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(ReminderCard)],
            ))
        await self._save_reminder(step_context)
        return await step_context.end_dialog()


    async def _save_reminder(self, step_context):
        reminder = step_context.values[self.REMINDER]
        try:
            await self.storage.write({reminder.id: reminder})
        except Exception as exception:
            await step_context.context.send_activity(f"Sorry, something went wrong storing your message! {str(exception)}")

    async def _show_reminders(self, turn_context: TurnContext):
        store_items =list(self.storage.client.QueryItems("dbs/w1hKAA==/colls/w1hKAJ-o+vY=/","select * from c where CONTAINS(c.id, 'Reminder')"))
        reminder_list = [Unpickler().restore(item["document"]) for item in store_items]
        for reminder in reminder_list:
            ReminderCard["body"][0]["text"] = reminder.title if hasattr(reminder, 'title') else ""
            ReminderCard["body"][1]["text"] = reminder.time if hasattr(reminder, 'time') else ""
            message = Activity(
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(ReminderCard)],
            )
            await turn_context.send_activity(message)

    async def _send_suggested_actions(self, turn_context: TurnContext):
        """
        Creates and sends an activity with suggested actions to the user. When the user
        clicks one of the buttons the text value from the "CardAction" will be displayed
        in the channel just as if the user entered the text. There are multiple
        "ActionTypes" that may be used for different situations.
        """

        reply = MessageFactory.text("How can I help you?")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(title="Set Reminder", type=ActionTypes.im_back, value="Set Reminder"),
                CardAction(title="Show Reminders", type=ActionTypes.im_back, value="Show Reminders"),
                CardAction(title="Exit", type=ActionTypes.im_back, value="Exit"),
            ]
        )
        return await turn_context.send_activity(reply)