import traceback
from datetime import datetime
from typing import Dict
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes, ConversationReference
from config import DefaultConfig
from botbuilder.azure import CosmosDbStorage, CosmosDbConfig
from dialogs import RemindersDialog
from bots import ReminderBot
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    ConversationState,
    TurnContext,
    UserState,
)

import uuid

# from .helpers import DialogHelper, ReminderHelper

CONFIG = DefaultConfig()


APP_ID = CONFIG.APP_ID if CONFIG.APP_ID else uuid.uuid4()

SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}")
    traceback.print_exc()

    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error


# cosmos_config = CosmosDbConfig(
#     endpoint=CONFIG.COSMOSDB_SERVICE_ENDPOINT,
#     masterkey=CONFIG.COSMOSDB_KEY,
#     database=CONFIG.COSMOSDB_DATABASE_ID,
#     container=CONFIG.COSMOSDB_CONTAINER_ID,
# )
# USE MEMORY STORAGE TO SIMPLIFY DEV
from botbuilder.core import MemoryStorage

MEMORY = MemoryStorage()  # CosmosDbStorage(cosmos_config)
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)
ACCESSOR = USER_STATE.create_property("RemindersState")
DIALOG = RemindersDialog(USER_STATE, CONVERSATION_STATE, MEMORY)
CONVERSATION_REFERENCES: Dict[str, ConversationReference] = dict()

BOT = ReminderBot(
    CONVERSATION_STATE, USER_STATE, DIALOG, CONVERSATION_REFERENCES, MEMORY
)


async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        print("ADAPTER RESPONSE")
        print(response.json())
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=201)
    except Exception as exception:
        raise exception


async def notify(req: Request) -> Response:  # pylint: disable=unused-argument
    await _send_proactive_message()
    # await
    return Response(status=201, text="Proactive messages have been sent")


CONVERSATION_REFERENCES: Dict[str, ConversationReference] = dict()


async def _send_proactive_message():
    print("GETTING SOMEWHERE")
    prinnt("conversation_REFs", CONVERSATION_REFERENCES)
    for conversation_reference in CONVERSATION_REFERENCES.values():
        print("conversation_REF: ", conversation_reference)
        return await ADAPTER.continue_conversation(
            conversation_reference, remind_user, APP_ID,
        )


async def remind_user(turn_context: TurnContext, storage):
    # message = Activity(
    #     type=ActivityTypes.message, attachments=[CardFactory.adaptive_card(SnoozeCard)],
    # )

    await turn_context.send_activity("HEY!!!")


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/api/notify", notify)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
