import sys
import asyncio
import telepot
from telepot.delegate import per_chat_id
from telepot.async.delegate import create_open

"""
$ python3.4 anicalbot.py <token>
"""

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)

    @asyncio.coroutine
    def on_message(self, msg):
        if "text" in msg:
            yield from self.sender.sendMessage(msg[::-1])

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
