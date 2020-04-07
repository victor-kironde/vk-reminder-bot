from botbuilder.core import(
    ActivityHandler,
    ConversationState,
    UserState,
    TurnContext,
    MessageFactory)
from botbuilder.dialogs import Dialog
from helpers import DialogHelper, ReminderHelper
from data_models import WelcomeUserState

from botbuilder.schema import Activity, ConversationReference

from typing import Dict
class ReminderBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
        conversation_references: Dict[str, ConversationReference],
        storage
    ):
        if conversation_state is None:
            raise Exception(
                "[DialogBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        self.user_state_accessor = self.user_state.create_property("WelcomeUserState")
        self.storage = storage
        self.conversation_references = conversation_references


    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context):
        if turn_context.activity.value:
            print("VALUE:", turn_context.activity.value, type(turn_context.activity.value))
            if turn_context.activity.value.get("reminder_id"):
                message = "UPDATE "
                message += turn_context.activity.value["reminder_id"]
                message += f" {turn_context.activity.value['time']}"
                turn_context.activity.text = message
                print("UPDATE MESSAGE:", turn_context.activity.text)
        return await DialogHelper.run_dialog(
        self.dialog,
        turn_context,
        self.conversation_state.create_property("DialogState"),
        )

    async def on_members_added_activity(self, members_added, turn_context):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self._welcome_user(turn_context)

    async def on_conversation_update_activity(self, turn_context):
        self._add_conversation_reference(turn_context.activity)
        await ReminderHelper.remind_user(turn_context, self.storage)
        return await super().on_conversation_update_activity(turn_context)


    async def _welcome_user(self, turn_context: TurnContext):
        welcome_user_state = await self.user_state_accessor.get(
    turn_context, WelcomeUserState
    )
        if not welcome_user_state.did_welcome_user:
            welcome_user_state.did_welcome_user = True
            name = turn_context.activity.from_property.name
            await turn_context.send_activity(
                f"Hello, I'm VK-Reminder-Bot."
            )
            await turn_context.send_activity(
                f"What is your name?"
            )

    def _add_conversation_reference(self, activity: Activity):
        """
        This populates the shared Dictionary that holds conversation references. In this sample,
        this dictionary is used to send a message to members when /api/notify is hit.
        :param activity:
        :return:
        """
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[
            conversation_reference.user.id
        ] = conversation_reference
