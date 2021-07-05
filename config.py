#!/usr/bin/env python3
from consts import *
# freenode.net/kb/anser/chat

nick = "pwn0x80"   # Enter your nickname
channel = "#pwn0x80" # Enter channel name
password = "ENTER YOUR PASSWORD" # Enter password here
username = "USER pwn pwn0 pwn0: rainbow pie" # Enter username

IRC_CONFIG = {
    "reconnect_timeout": 0.5,
}

# config.IRC_NETWORKS["freenode"]["channel"]
IRC_NETWORKS = {
    "freenode": {
        "host": "irc.freenode.net",
        "port": 6665,

        "ssl": False,
        "nickname": "NICK " + nick,
        "password": "PASS " + password,
        "channel": "JOIN " + channel,
        "username": "USER  " + user name
    }
}

chat = {
    "channels": channel

}


ADMINS = {
    "lol world": {
        "level": USER_LEVEL_ADMIN
    }
}
