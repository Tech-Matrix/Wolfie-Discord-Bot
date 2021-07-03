from os import getenv
    # reading env variables
from dotenv import load_dotenv
    # loading env variables from env file
import discord
    # discord API wrapper
import json
    # parse json file
import asyncio
    # asynchronous programming

load_dotenv()
    # load env variables from env file

config = json.load(open('../config.json'))
    # load config


class Command_handler():
    # handles command events

    _next_listener_id = 0
        # id of the next listener

    # constructor
    def __init__(self):
        self._listeners = {}
            # maps command to its listeners
        self._default_listeners = []
            # maps command to default listeners

    # add listener
    def add_listener(self, command, callback):

        # map command to array of listeners
        listener_id = self._next_listener_id
        self._next_listener_id += 1
        if command not in self._listeners:
            self._listeners[command] = [{
                    'id': listener_id,
                    'callback': callback
            }]
        else:
            self._listeners.get(command).append({
                'id': listener_id,
                'callback': callback
            })

        return listener_id 
            # unique id

    # add default listener
    def add_default_listener(self, callback):

        listener_id = self._next_listener_id
        self._next_listener_id += 1

        # add default listeners
        self._default_listeners.append({
            'id': listener_id,
            'callback': callback
        })

        return listener_id
                
    # remove listener
    def remove_listener(self, command, remove_id):

        for index, listeners in enumerate(self._listeners.get(command)):
            if listeners['id'] == remove_id:
                self._listeners.get(command).pop(index)
                break
        if not self._listeners.get(command):
                # no listeners for command
            self._listeners.pop(command)

    def remove_default_listener(self, remove_id):

        for index, listener in enumerate(self._default_listeners):
            if listener['id'] == remove_id:
                self._default_listeners.pop(index)
                break
        
    # remove all listeners for event
    def remove_all_listeners(self, command):
        self._listeners.pop(command)

    def remove_all_default_listeners(self):
        self._default_listeners = []

    # call listeners
    def emit(self, command, ctx, action):
        if not self._listeners.get(command):
                # no listeners for the command, 
                # call default listeners
            for listener in self._default_listeners:
                asyncio.create_task(
                    listener['callback'](ctx)
                )
            return

        # run all listeners asynchronously
        for listener in self._listeners.get(command):
            asyncio.create_task(
                listener['callback'](ctx, action)
            )


class Bot(discord.Client):

    def __init__(self, bot_prefix):
        discord.Client.__init__(self)
        self.bot_prefix = bot_prefix
        self._command_handler = Command_handler()

    
    # add commands
    def add_commands(self, commands):
        for command in commands:
            self._command_handler.add_listener(
                command['command_name'],
                command['callback']
            )


    # add default command
    def add_default_command(self, default_command):
        self._command_handler.add_default_listener(default_command)


    # notify that we've connected
    async def on_ready(self):
        print('Logged on as', self.user)


    async def on_message(self, message):

        # don't respond to ourselves
        if message.author == self.user:
            return

        # if user is instructing us
        if message.content.startswith(self.bot_prefix):

            command = (
                message.content[len(self.bot_prefix):].split()
                    and message.content[len(self.bot_prefix):].split()[0]
            )

            if not command:

                # incomplete command
                await message.reply(
                    'No command specified..\n'
                    f"**type** {self.bot_prefix} help\n"
                    'for help'
                )
            else:
                ctx = {}
                ctx['message'] = message
                ctx['bot'] = self
                action = message.content[len(self.bot_prefix):].strip()
                self._command_handler.emit(command, ctx, action)


wolfie_bot = Bot(config['bot_prefix'])
from commands import commands, default_command
wolfie_bot.add_commands(commands)
wolfie_bot.add_default_command(default_command)
wolfie_bot.run(getenv('bot_token'))
