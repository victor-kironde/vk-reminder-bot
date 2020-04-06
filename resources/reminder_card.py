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
    "speak": "<s>Your  meeting about \"Adaptive Card design session\"<break strength='weak'/> is starting at 12:30pm</s><s>Do you want to snooze <break strength='weak'/> or do you want to send a late notification to the attendees?</s>",
    "body": [
        {
            "type": "TextBlock",
            "text": "Adaptive Card design session",
            "size": "Large",
            "weight": "Bolder"
        },
        {
            "type": "TextBlock",
            "text": "12:30 PM - 1:30 PM",
            "isSubtle": True,
            "spacing": "None"
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Done",
            "data": {
                "action": "done"
            },
            "iconUrl": ""
        },
        {
            "type": "Action.Submit",
            "title": "Delete",
            "data": {
                "action": "delete"
            }
        }
    ]
}