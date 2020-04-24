[![Coverage Status](https://coveralls.io/repos/github/victor-kironde/vk_reminder_bot/badge.svg?branch=master)](https://coveralls.io/github/victor-kironde/vk_reminder_bot?branch=master)
[![Build Status](https://travis-ci.org/victor-kironde/vk_reminder_bot.svg?branch=master)](https://travis-ci.org/victor-kironde/vk_reminder_bot)
# VK-Reminder-Bot

#### A Reminder Bot build with the [Microsoft Bot Framework](https://dev.botframework.com).


## Prerequisites

  - Install Python 3.8

## Running the Bot Locally
- Clone this repository
- Set `DEBUG=True` in `config.py`. This will make bot state use `MemoryStorage`
- Run `pip install -r requirements.txt` to install all dependencies
- Run `python app.py`

## Running the Bot Online
- You can test the bot online [here](https://webchat.botframework.com/embed/vk_reminder_bot?s=376s13dNyqs.-TOrhd3zlpXJz3EbzDuI55FTd-g89O01aXutuIpCIpI).


## Running the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the Bot Framework Emulator version 4.3.0 or greater from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- Enter a Bot URL of `http://localhost:3978/api/messages`

You can view the project board [here](https://trello.com/b/9WHqZss3)
