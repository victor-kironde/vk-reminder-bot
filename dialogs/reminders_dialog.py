from botbuilder.core import (
    MessageFactory,
    UserState,
    ConversationState,
    MemoryStorage,
    CardFactory,
    TurnContext,
)
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
    DialogTurnStatus,
    DialogContext,
)
from botbuilder.dialogs.prompts import (
    PromptOptions,
    TextPrompt,
    DateTimePrompt,
    ConfirmPrompt,
)
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

import json
import os

from botbuilder.dialogs.choices import Choice
from data_models import Reminder, ActivityMappingState, ReminderLog
from datetime import datetime
from config import DefaultConfig
from botbuilder.azure import CosmosDbStorage, CosmosDbConfig

from resources import HelpCard, ReminderCard

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from azure.cognitiveservices.language.luis.runtime.models import LuisResult
from helpers import LuisHelper, Intent
from .cancel_and_help_dialog import CancelAndHelpDialog
from jsonpickle.unpickler import Unpickler

config = DefaultConfig()


class RemindersDialog(CancelAndHelpDialog):
    def __init__(
        self, user_state: UserState, conversation_state: ConversationState, storage,
    ):
        super(RemindersDialog, self).__init__(RemindersDialog.__name__)

        self.user_state = user_state
        self.conversation_state = conversation_state
        self.REMINDER = "value-reminder"
        self.storage = storage
        self.conversation_state_accessor = self.conversation_state.create_property(
            "ActivityMappingState"
        )
        self.user_reminders_state_accessor = self.conversation_state.create_property(
            "RemindersState"
        )

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
            config.LUIS_APP_ID, config.LUIS_API_KEY, config.LUIS_API_HOST_NAME,
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
        if intent == Intent.SHOW_REMINDERS.value:
            await self._show_reminders(step_context.context)
            return await step_context.end_dialog()

        elif intent == Intent.CREATE_REMINDER.value:
            return await step_context.next(None)

        elif intent == Intent.HELP.value:
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(HelpCard)],
            )
            await step_context.context.send_activity(message)
            return await step_context.end_dialog()
        elif intent == Intent.SNOOZE_REMINDER.value:
            await self._snooze_reminder(step_context.context, recognizer_result)
            return await step_context.end_dialog()
        elif intent == Intent.DELETE_REMINDER.value:
            await self._delete_reminder(step_context.context)
            return await step_context.end_dialog()

        else:
            await step_context.context.send_activity("I didn't get that!")
            await self._send_suggested_actions(step_context.context)
            return await step_context.end_dialog()

    async def reminder_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        if not reminder.title:
            prompt_options = PromptOptions(
                prompt=MessageFactory.text("Please enter Reminder Title:")
            )

            return await step_context.prompt(TextPrompt.__name__, prompt_options)
        else:
            return await step_context.next(None)

    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        if step_context.result:
            reminder.title = step_context.result.title()
        if not reminder.reminder_time:
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
        reminder.reminder_time = (
            step_context.result[0].value
            if not reminder.reminder_time
            else reminder.reminder_time
        )
        await step_context.context.send_activity(f"""I have set the reminder!""")

        ReminderCard["body"][0]["text"] = reminder.title
        ReminderCard["body"][1]["text"] = reminder.reminder_time

        await step_context.context.send_activity(
            Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(ReminderCard)],
            )
        )
        await self._save_reminder(step_context)
        return await step_context.end_dialog()

    async def _save_reminder(self, step_context):
        reminder = step_context.values[self.REMINDER]
        reminder_log = await self.user_reminders_state_accessor.get(
            step_context.context, ReminderLog
        )
        reminder_log.new_reminders.append(reminder)
        await self.user_reminders_state_accessor.set(step_context.context, reminder_log)

    async def _show_reminders(self, turn_context: TurnContext):
        reminder_log = await self.user_reminders_state_accessor.get(
            turn_context, ReminderLog
        )
        reminder_list = reminder_log.new_reminders

        activity_mapping_state = await self.conversation_state_accessor.get(
            turn_context, ActivityMappingState
        )
        for reminder in reminder_list:
            ReminderCard["body"][0]["text"] = (
                reminder.title if hasattr(reminder, "title") else ""
            )
            ReminderCard["body"][1]["text"] = (
                reminder.reminder_time if hasattr(reminder, "reminder_time") else ""
            )
            ReminderCard["actions"][0]["data"]["reminder_id"] = reminder.id
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(ReminderCard)],
            )
            sent_activity = await turn_context.send_activity(message)
            activity_mapping_state.activities[reminder.id] = sent_activity.id

        print("Mapping_state", activity_mapping_state.activities)

    async def _snooze_reminder(self, turn_context: TurnContext, new_reminder):
        reminder_log = await self.user_reminders_state_accessor.get(
            turn_context, ReminderLog
        )
        new_reminders = reminder_log.new_reminders
        reminder = list(
            filter(lambda reminder: reminder.id == new_reminder.id, new_reminders)
        )  # the reminder we want
        reminder.time = new_reminder.reminder_time
        reminder.done = False
        await turn_context.send_activity(f"I have updated the reminder!, or have I?")

        message = Activity(
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(ReminderCard)],
        )

        ReminderCard["body"][0]["text"] = reminder.title
        ReminderCard["body"][1]["text"] = reminder.time
        ReminderCard["actions"][0]["data"]["reminder_id"] = reminder.id
        ReminderCard["actions"][0]["data"]["activity_id"] = message.id

        sent_activity = await turn_context.send_activity(message)

        activity_mapping_state = await self.conversation_state_accessor.get(
            turn_context, ActivityMappingState
        )
        activity_mapping_state.activities[reminder.id] = sent_activity.id

    async def _delete_reminder(self, turn_context: TurnContext):
        raise NotImplementedError

    async def _send_suggested_actions(self, turn_context: TurnContext):
        reply = MessageFactory.text("How can I help you?")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Set Reminder", type=ActionTypes.im_back, value="Set Reminder"
                ),
                CardAction(
                    title="Show All Reminders",
                    type=ActionTypes.im_back,
                    value="Show All Reminders",
                ),
            ]
        )
        return await turn_context.send_activity(reply)
