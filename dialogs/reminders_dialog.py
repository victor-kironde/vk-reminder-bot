from botbuilder.core import MessageFactory, UserState, MemoryStorage, StoreItem, CardFactory
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
    ChoicePrompt,
    ConfirmPrompt)
from botbuilder.schema import (
    ChannelAccount,
    CardAction,
    ActionTypes,
    SuggestedActions,
    ActivityTypes,
    Activity,
    InputHints, HeroCard, CardImage, Attachment
)

import json
import os

from botbuilder.dialogs.choices import Choice

from data_models import Reminder

from recognizers_date_time import recognize_datetime, Culture
from datetime import datetime


from config import DefaultConfig

from botbuilder.azure import CosmosDbStorage, CosmosDbConfig

config = DefaultConfig()

cosmos_config = CosmosDbConfig(
        endpoint=config.COSMOSDB_SERVICE_ENDPOINT,
        masterkey=config.COSMOSDB_KEY,
        database=config.COSMOSDB_DATABASE_ID,
        container=config.COSMOSDB_CONTAINER_ID
    )


class ValidationResult:
    def __init__(
        self, is_valid: bool = False, value: object = None, message: str = None
    ):
        self.is_valid = is_valid
        self.value = value
        self.message = message

class ReminderLog(StoreItem):
    """
    Class for storing a log of reminders (text of messages) as a list.
    """

    def __init__(self):
        super(ReminderLog, self).__init__()
        self.reminder_list = []
        self.turn_number = 0
        self.e_tag = "*"

class RemindersDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(RemindersDialog, self).__init__(RemindersDialog.__name__)

        self.user_state = user_state
        self.REMINDER = "value-reminder"
        self.storage = CosmosDbStorage(cosmos_config)

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(DateTimePrompt(DateTimePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.action_step,
                    self.title_step,
                    self.time_step,
                    self.confirm_step,
                    self.acknowledgement_step

                ],
            )
        )

        self.initial_dialog_id = "WFDialog"


    async def action_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values[self.REMINDER] = Reminder()

        prompt_options = PromptOptions(
            prompt=MessageFactory.text("How may I help you?"),
            choices=[Choice("Set Reminder"), Choice("Show All Reminders"), Choice("Exit")]
        )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)

    async def title_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        action = step_context.result.value.lower()

        if action == "set reminder":
            prompt_options = PromptOptions(
                prompt=MessageFactory.text("What would you like me to remind you about?")
            )
            return await step_context.prompt(TextPrompt.__name__, prompt_options)

        elif action == "show all reminders":
            store_items = await self.storage.read(["ReminderLog"])
            reminder_list = store_items["ReminderLog"]["reminder_list"]
            for reminder in reminder_list:
                message = Activity(
                type=ActivityTypes.message,
                attachments=[self._create_adaptive_card_attachment(reminder)],
                )

                await step_context.context.send_activity(message)
            return await step_context.end_dialog()

        elif action == "exit":
            await step_context.context.send_activity(MessageFactory.text("Bye!"))
            return await step_context.end_dialog()


    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        reminder.title = step_context.result

        prompt_options = PromptOptions(
            prompt=MessageFactory.text("When should I remind you?"),
            retry_prompt=MessageFactory.text("Please enter a valid time:"),

        )
        return await step_context.prompt(DateTimePrompt.__name__, prompt_options)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        reminder: Reminder = step_context.values[self.REMINDER]
        reminder.time = step_context.result[0].value
        result = step_context.result
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(f"""I have set the reminder.
            \nWould you like to do anything else?""")
            )
        await step_context.context.send_activity(Activity(
                type=ActivityTypes.message,
                text=MessageFactory.text(f"""I have set the reminder.
            \nWould you like to do anything else?"""),
                attachments=[self._create_adaptive_card_attachment(reminder.__dict__)],
            ))

        return await step_context.prompt(ConfirmPrompt.__name__, prompt_options)

    async def acknowledgement_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await self._save_reminder(step_context)
        if step_context.result:
            await step_context.context.send_activity(MessageFactory.text("okay"))
            return await step_context.begin_dialog(self.id)
        else:
            await step_context.context.send_activity(MessageFactory.text("Okay, bye!."))
        return await step_context.end_dialog()


    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result
        return await super(RemindersDialog, self).on_continue_dialog(inner_dc)


    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()
            card_path = os.path.join(os.getcwd(), "resources/help_card.json")
            with open(card_path, "rb") as in_file:
                card_data = json.load(in_file)

            message = Activity(type=ActivityTypes.message, attachments=[CardFactory.adaptive_card(card_data)])

            if text in ("help", "?"):
                await inner_dc.context.send_activity(message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            cancel_message_text = "Cancelled."
            cancel_message = MessageFactory.text(
                cancel_message_text, cancel_message_text, InputHints.ignoring_input
            )

            if text in ("cancel", "quit"):
                await inner_dc.context.send_activity(cancel_message)
                return await inner_dc.cancel_all_dialogs()

        return None


    async def _save_reminder(self, step_context):
        reminder = step_context.values[self.REMINDER]
        store_items = await self.storage.read(["ReminderLog"])
        if "ReminderLog" not in store_items:
            print("ReminderLog Missing")
            print(reminder)
            reminder_log = ReminderLog()
            reminder_log.reminder_list.append(reminder.__dict__)
            reminder_log.turn_number = 1
        else:
            reminder_log: ReminderLog = store_items["ReminderLog"]
            reminder_log['reminder_list'].append(reminder.__dict__)
            reminder_log['turn_number'] = reminder_log['turn_number'] + 1
        try:
            changes = {"ReminderLog": reminder_log}
            await self.storage.write(changes)
        except Exception as exception:
            await step_context.context.send_activity(f"Sorry, something went wrong storing your message! {str(exception)}")


    def _create_adaptive_card_attachment(self, reminder) -> Attachment:
        card_path = os.path.join(os.getcwd(), "resources/reminder_card.json")

        with open(card_path, "rb") as in_file:
            card_data = json.load(in_file)
            card_data["body"][0]["text"] = reminder['title']
            card_data["body"][1]["text"] = reminder['time']

        return CardFactory.adaptive_card(card_data)
