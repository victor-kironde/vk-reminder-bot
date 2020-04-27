from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
import dotenv

dotenv.load_dotenv()
from config import DefaultConfig


class ReminderRecognizer(LuisRecognizer):
    def __init__(self):

        config = DefaultConfig()

        luis_application = LuisApplication(
            config.LUIS_APP_ID, config.LUIS_API_KEY, config.LUIS_API_HOST_NAME,
        )
        luis_options = LuisPredictionOptions(
            include_all_intents=True, include_instance_data=True
        )
        super().__init__(luis_application, luis_options, True)
