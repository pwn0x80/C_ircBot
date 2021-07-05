#!/usr/bin/env python3
import config
from consts import *


chat = {
    # hi!!
    "hello": 'PRIVMSG ' + config.chat["channels"] + ' hello',
    # memory info
    'memory': 'PRIVMSG ' + config.chat["channels"] + " {}"

}


print(config.IRC_NETWORKS["freenode"]["channel"])
