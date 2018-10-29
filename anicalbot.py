import sys
import time
import bisect
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import per_chat_id, create_open, pave_event_space
import datetime as dt

"""
$ python3 anicalbot.py <token>
"""
class StoreWeight(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(StoreWeight, self).__init__(*args, **kwargs)
        self._weight_list = {}

    def showlist(self, user, days_str):
        try:
            days = int(days_str)
        except ValueError:
            self.sender.sendMessage("Invalid number of days [{0:s}]".format(
                days_str))
            return
        if days <= 0:
            self.sender.sendMessage("Invalid number of days [{0:d}]".format(
                days))

        if user not in self._weight_list:
            self.sender.sendMessage("Empty list for user @{0:s}".format(user))
            return
        """
        Get the samples that were stored since "days" days ago
        """
        diff = dt.timedelta(days=days)
        
        date = dt.datetime.today() - diff
        dates_list = [x[0] for x in self._weight_list[user]]

        lo = bisect.bisect_left(dates_list, date)
        
        message = ""
        for idx in range(lo,len(dates_list)):
            message += "{0:s},{1:.1f}\n".format(
                    dt.datetime.strftime(self._weight_list[user][idx][0],
                    "%Y-%m-%d %H:%M:%S"),
                    self._weight_list[user][idx][1])
        self.sender.sendMessage(message)

    def processcommand(self, msg, entity):
        txt = msg["text"]
        command = txt[entity["offset"]:entity["length"]]
        days = txt[entity["length"]:].strip()
        user = msg["from"]["username"]
        print("Command [{0:s}]; arguments [{1:s}], for user [{2:s}]".format(
            command,
            days,
            user))
        if command == "/list":
            self.showlist(user, days)
        else:
            self.sender.sendMessage("Command not recognized [{0:s}]".format(
                command))

    def on_chat_message(self, msg):
        print(msg)
        """
        In case it contains a command, but it is not at offset 0 do not do
        anything.
        """
        if "entities" in msg:
            for entity in msg["entities"]:
                if entity["type"] == "bot_command":
                    if entity["offset"] > 0:
                        message = "You should only specify one command, and "
                        message += "it should be the first thing in the "
                        message += "message."
                        self.sender.sendMessage(message)
                    else:
                        self.processcommand(msg, entity)
                        """ Process only the first command that is found """
                    return

        user = msg["from"]["username"]
        try:
            weight = float(msg["text"])
        except ValueError:
            message = "[ERROR] The weight should be numeric"
            self.sender.sendMessage(message)
            return

        date = dt.datetime.utcfromtimestamp(msg["date"])
        record = (date, weight)

        if user not in self._weight_list:
            self._weight_list[user] = []
        self._weight_list[user].append(record)
        message = "Record {0:s} stored for user {1:s}.".format(
                str(record), user)

        self.sender.sendMessage(message)

"""
Get the token from the command-line
"""
TOKEN = sys.argv[1]

"""
Get the folder where the data will be stored.
"""
# data_folder = sys.argv[2]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, StoreWeight, timeout=10),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while True:
    time.sleep(10)
