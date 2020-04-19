from data_models import Reminder
from datetime import datetime


class Cards:
    @staticmethod
    def reminder_card(reminder: Reminder):
        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.0",
            "id": "",
            "body": [
                {
                    "type": "TextBlock",
                    "text": reminder.title,
                    "size": "Large",
                    "weight": "Bolder",
                },
                {
                    "type": "TextBlock",
                    "text": datetime.strftime(
                        reminder.reminder_time, "%Y-%m-%d %I:%M %p"
                    ),
                    "isSubtle": True,
                    "spacing": "None",
                },
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Delete",
                    "data": {"action": "delete", "reminder_id": "", "activity_id": ""},
                }
            ],
        }

    @staticmethod
    def snooze_card(reminder: Reminder):
        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.0",
            "speak": "<s>Your  meeting about \"Adaptive Card design session\"<break strength='weak'/> is starting at 12:30pm</s><s>Do you want to snooze <break strength='weak'/> or do you want to send a late notification to the attendees?</s>",
            "body": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": 50,
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": (
                                        reminder.title
                                        if hasattr(reminder, "title")
                                        else ""
                                    ),
                                    "size": "Large",
                                    "weight": "Bolder",
                                },
                                {
                                    "type": "TextBlock",
                                    "text": (
                                        datetime.strftime(
                                            reminder.reminder_time, "%Y-%m-%d %I:%M %p"
                                        )
                                        if hasattr(reminder, "reminder_time")
                                        else ""
                                    ),
                                    "isSubtle": True,
                                    "spacing": "None",
                                },
                                {"type": "TextBlock", "text": "Snooze for"},
                                {
                                    "type": "Input.ChoiceSet",
                                    "id": "snooze",
                                    "value": "5 minutes",
                                    "choices": [
                                        {"title": "5 minutes", "value": "5 minutes"},
                                        {"title": "10 minutes", "value": "10 minutes"},
                                        {"title": "30 minutes", "value": "30 minutes"},
                                    ],
                                },
                            ],
                            "separator": True,
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "horizontalAlignment": "Center",
                            "style": "default",
                            "backgroundImage": {
                                "url": "",
                                "horizontalAlignment": "Center",
                            },
                            "verticalContentAlignment": "Center",
                            "height": "stretch",
                            "spacing": "None",
                            "items": [
                                {"type": "ImageSet"},
                                {
                                    "type": "Image",
                                    "altText": "",
                                    "url": "https://i.ibb.co/RvYB9Gc/bell-200-transparent.gif",
                                },
                            ],
                        },
                    ],
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Snooze",
                    "data": {"action": "snooze", "reminder_id": reminder.id},
                },
                {
                    "type": "Action.Submit",
                    "title": "Dismiss",
                    "data": {
                        "action": "delete",
                        "reminder_id": reminder.id,
                        "activity_id": "",
                    },
                },
            ],
        }

    @staticmethod
    def help_card():
        return {
            "type": "AdaptiveCard",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "Medium",
                    "weight": "Bolder",
                    "text": "Help",
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Set Reminder:", "value": "Sets a reminder"},
                        {
                            "title": "Show all Reminders:",
                            "value": "Displays All reminders",
                        },
                        {"title": "Exit:", "value": "Exit"},
                        {"title": "Cancel:", "value": "Cancels a Dialog"},
                    ],
                },
            ],
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.0",
        }
