from datetime import datetime
import pytz
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
    CardAction,
    ActionTypes,
    SuggestedActions,
)
from data_models import Reminder, ActivityMappingState, ReminderLog
from config import DefaultConfig
from resources import Cards

from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from helpers import LuisHelper, Intent, Messages
from .cancel_and_help_dialog import CancelAndHelpDialog

config = DefaultConfig()


class RemindersDialog(CancelAndHelpDialog):
    def __init__(
        self,
        user_state: UserState,
        conversation_state: ConversationState,
        reminders_accessor,
    ):
        super(RemindersDialog, self).__init__(RemindersDialog.__name__)

        self.user_state = user_state
        self.conversation_state = conversation_state
        self.REMINDER = "value-reminder"
        self.conversation_state_accessor = self.conversation_state.create_property(
            "ActivityMappingState"
        )
        self.reminders_accessor = reminders_accessor
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
        text = (
            step_context.context.activity.text
            if step_context.context.activity.text
            else ""
        ).lower()
        if intent == Intent.SNOOZE_REMINDER.value:
            await self._snooze_reminder(step_context.context, recognizer_result)
            return await step_context.end_dialog()
        elif text.startswith("delete"):
            await self._delete_reminder(step_context.context)
            return await step_context.end_dialog()
        elif text.startswith("show"):
            await self._show_reminders(step_context.context)
            return await step_context.end_dialog()

        elif intent == Intent.CREATE_REMINDER.value:
            return await step_context.next(None)

        elif intent == Intent.HELP.value:
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(Cards.help_card())],
            )
            await step_context.context.send_activity(message)
            return await step_context.end_dialog()
        else:
            await step_context.context.send_activity(Messages.missed)
            await self._send_suggested_actions(step_context.context)
            return await step_context.end_dialog()

    async def reminder_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        reminder = step_context.values[self.REMINDER]
        if not reminder.title:
            prompt_options = PromptOptions(
                prompt=MessageFactory.text(Messages.get_title)
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
                prompt=MessageFactory.text(Messages.get_time),
                retry_prompt=MessageFactory.text(Messages.time_retry),
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

        if reminder.reminder_time < datetime.now().astimezone(
            pytz.timezone("Africa/Nairobi")
        ):
            await step_context.context.send_activity(Messages.bad_time)
            return await step_context.end_dialog()
        await step_context.context.send_activity(Messages.done)
        reminder_card = Cards.reminder_card(reminder)
        await step_context.context.send_activity(
            Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(reminder_card)],
            )
        )
        await self._save_reminder(step_context)
        return await step_context.end_dialog()

    async def _save_reminder(self, step_context):
        reminder = step_context.values[self.REMINDER]
        reminder_log = await self.reminders_accessor.get(
            step_context.context, ReminderLog
        )
        reminder_log.new_reminders.append(reminder)

    async def _show_reminders(self, turn_context: TurnContext):
        reminder_log = await self.reminders_accessor.get(turn_context, ReminderLog)
        reminder_list = reminder_log.new_reminders + reminder_log.old_reminders
        if len(reminder_list) == 0:
            await turn_context.send_activity(Messages.no_reminders)

        activity_mapping_state = await self.conversation_state_accessor.get(
            turn_context, ActivityMappingState
        )
        for reminder in reminder_list:
            reminder_card = Cards.reminder_card(reminder)
            message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(reminder_card)],
            )
            sent_activity = await turn_context.send_activity(message)
            activity_mapping_state.activities[reminder.id] = sent_activity.id

    async def _snooze_reminder(self, turn_context: TurnContext, new_reminder):
        reminder_log = await self.reminders_accessor.get(turn_context, ReminderLog)
        old_reminders = reminder_log.old_reminders
        reminder = list(
            filter(lambda reminder: reminder.id == new_reminder.id, old_reminders)
        )[0]

        new_reminder.title = reminder.title
        new_reminder.done = False
        reminder_log.new_reminders.append(new_reminder)

        await turn_context.send_activity(Messages.done)
        reminder_card = Cards.reminder_card(new_reminder)
        message = Activity(
            type=ActivityTypes.message,
            attachments=[CardFactory.adaptive_card(reminder_card)],
        )
        sent_activity = await turn_context.send_activity(message)

        activity_mapping_state = await self.conversation_state_accessor.get(
            turn_context, ActivityMappingState
        )
        activity_mapping_state.activities[reminder.id] = sent_activity.id

    async def _delete_reminder(self, turn_context: TurnContext):
        activity_mapping_state = await self.conversation_state_accessor.get(
            turn_context, ActivityMappingState
        )
        reminder_id = turn_context.activity.text.split()[1]
        activity_id = activity_mapping_state.activities.get(reminder_id)
        await turn_context.delete_activity(activity_id)

    async def _send_suggested_actions(self, turn_context: TurnContext):
        reply = MessageFactory.text(Messages.help)

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
