ReminderCard = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.0",
    "id": "",
    "body": [
        {"type": "TextBlock", "text": "", "size": "Large", "weight": "Bolder"},
        {"type": "TextBlock", "text": "", "isSubtle": True, "spacing": "None"},
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Delete",
            "data": {"action": "delete", "reminder_id": "", "activity_id": ""},
        }
    ],
}


SnoozeCard = {
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
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Reminder",
                            "size": "Large",
                            "weight": "Bolder",
                        },
                        {
                            "type": "TextBlock",
                            "text": "Time",
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
                        "url": "https://i.ibb.co/RvYB9Gc/bell-200-transparent.gif",
                        "horizontalAlignment": "Center",
                    },
                    "verticalContentAlignment": "Center",
                    "height": "stretch",
                    "spacing": "None",
                },
            ],
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Snooze",
            "data": {"action": "snooze", "reminder_id": ""},
        },
        {
            "type": "Action.Submit",
            "title": "Dismiss",
            "data": {"action": "delete", "reminder_id": "", "activity_id": ""},
        },
    ],
}
