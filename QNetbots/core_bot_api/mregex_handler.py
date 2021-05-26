"""
Defines a matrix bot handler that uses regex to determine if message should be handled
"""
import re
import os
os.path.dirname(os.path.abspath(__file__)+'/../../')
from QNetbots.core_bot_api.mhandler import MHandler


class MRegexHandler(MHandler):

    # regex_str - Regular expression to test message against
    #
    # handle_callback - Function to call if messages matches regex
    def __init__(self, regex_str, handle_callback):
        MHandler.__init__(self, self.test_regex, handle_callback)
        self.regex_str = regex_str

    def test_regex(self, room, event):
        print(event)
        # Test the message and see if it matches the regex
        if event['type'] == "m.room.message":
            if 'content' in event and 'body' in event['content']:
                if re.search(self.regex_str, event['content']['body']):
                    # The message matches the regex, return true
                    print('recognized')
                    return True

        return False
