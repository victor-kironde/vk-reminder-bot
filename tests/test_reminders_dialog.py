import pytest
from typing import Dict
from botbuilder.core.adapters import TestAdapter
from bots import ReminderBot
from dialogs import RemindersDialog
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
    UserState,
    MemoryStorage,
)
from botbuilder.schema import Activity, ActivityTypes, ConversationReference

from botbuilder.testing import DialogTestClient

from unittest.mock import Mock, MagicMock
import aiounittest
from helpers import Messages

MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)
ACCESSOR = USER_STATE.create_property("RemindersState")
DIALOG = RemindersDialog(USER_STATE, CONVERSATION_STATE, ACCESSOR)


class TestRemindersDialog(aiounittest.AsyncTestCase):
    async def test_show_reminders_with_no_reminders(self):
        testClient = DialogTestClient("test", DIALOG)
        reply = await testClient.send_activity("show reminders")
        assert reply.text == "You don't have any reminders!"

    async def test_create_reminder(self):
        testClient = DialogTestClient("test", DIALOG)
        reply = await testClient.send_activity("remind me to go in 10 seconds")

        assert reply.text == "I have set the reminder!"
