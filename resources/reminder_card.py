ReminderAudioCard = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.0",
    "type": "AdaptiveCard",
    "speak": "Your flight is confirmed for you and 3 other passengers from San Francisco to Amsterdam on Friday, October 10 8:30 AM",
    "body": [
        {
            "type": "TextBlock",
            "text": "{reminder['title']}",
            "weight": "bolder",
            "isSubtle": False
        },
        {
            "type": "TextBlock",
            "text": "{reminder['time']}",
            "separator": False
        }
    ]
}


ReminderCard= {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.0",
    "id": "",
    "body": [
        {
            "type": "TextBlock",
            "text": "",
            "size": "Large",
            "weight": "Bolder"
        },
        {
            "type": "TextBlock",
            "text": "",
            "isSubtle": True,
            "spacing": "None"
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Delete",
            "data": {
                "action": "delete"
            }
        }
    ]
}


SnoozeCard = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "TextBlock",
            "size": "Medium",
            "weight": "Bolder",
            "text": "{title}"
        },
        {
            "type": "TextBlock",
            "size": "Medium",
            "weight": "small",
            "text": "{title}"
        },
        {
            "type": "Image",
            "style": "Person",
            "url": "{creator.profileImage}",
            "size": "Small"
        }
    ],
    "actions": [
        {
            "type": "Action.ShowCard",
            "title": "Snooze",
            "card": {
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "Input.Text",
                        "id": "time",
                        "placeholder": "When can I remind you?"
                    },
                    {
                        "type": "Input.Text",
                        "id": "reminder_id",
                        "placeholder": "reminder_id",
                        "isMultiline": False,
                        "isVisible": False,
                        "value": ""
                    }
                ],
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "OK"
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json"
            }
        },
        {
            "type": "Action.Submit",
            "title": "Dismiss"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.0"
}