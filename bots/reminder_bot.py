from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext, MessageFactory
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper
from data_models import Reminder


class ReminderBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
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
        self.reminder_accessor = self.user_state.create_property("Reminder")

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context):
        return await DialogHelper.run_dialog(
        self.dialog,
        turn_context,
        self.conversation_state.create_property("DialogState"),
        )

    async def on_members_added_activity(self, members_added, turn_context):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello! I'm VK-Reminder Bot."
                )
        return await DialogHelper.run_dialog(
        self.dialog,
        turn_context,
        self.conversation_state.create_property("DialogState"),
        )
