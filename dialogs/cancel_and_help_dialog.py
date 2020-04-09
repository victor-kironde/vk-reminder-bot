# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.schema import Activity, ActivityTypes, InputHints
from botbuilder.core import MessageFactory, CardFactory
from resources import HelpCard


class CancelAndHelpDialog(ComponentDialog):
    def __init__(self, dialog_id: str):
        super(CancelAndHelpDialog, self).__init__(dialog_id)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()
            help_message = Activity(
                type=ActivityTypes.message,
                attachments=[CardFactory.adaptive_card(HelpCard)],
            )

            if text in ("help", "?"):
                await inner_dc.context.send_activity(help_message)
                return DialogTurnResult(DialogTurnStatus.Waiting)

            cancel_message_text = "Cancelled."
            cancel_message = MessageFactory.text(
                cancel_message_text, cancel_message_text, InputHints.ignoring_input
            )

            if text in ("cancel", "quit", "exit"):
                await inner_dc.context.send_activity(cancel_message)
                return await inner_dc.cancel_all_dialogs()

        return None
