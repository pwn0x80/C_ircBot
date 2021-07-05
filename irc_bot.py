#!/usr/bin/env python3
import config
import logging
from consts import *
import socket
import ssl
import logging
import threading
import queue
import time
import command
IRC_EVENT_MESSGE = "MESSAGE"

IRC_EVENT_DISCONNECT = "DISCONNECT"


class IRCEvent():
    def __init__(self, e_ty, ev_da=None):
        self.type = e_ty
        self.data = ev_da

    def __repr__(self):
        return "IRCeventType(%s, %s)" % (self.type, repr(self.data))


class IRCException(Exception):
    pass


class IRC:
    def __init__(self, conf):
        self.conf = conf
        self.s = None  # Socket
        self.raw_s = None  # socket

        self.handling_th = threading.Thread(target=self.handling_thread_run)

        self.handling_th.daemon = True
        self.handling_th.start()

    def connect(self):
        if self.conf["ssl"]:
            return self.connect_no_ssl()
        else:
            return self.connect_no_ssl()

    def disconnect(self):
        if self.conf["ssl"]:
            return self.disconnect_nossl()
        else:
            return self.disconnect_nossl()

# https://stackoverflow.com/questions/409783/socket-shutdown-vs-socket-close

    def disconnect_ssl(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    def disconnect_nossl(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    def connect_ssl(self):
        logging.info("connecting - %s:%i (SSL) ...",
                     self.conf["host"], self.conf["port"])

        self.raw_s = socket.create_connection(
            (self.conf["host"], self.conf["port"]))
        self.ssl_connect = ssl.create_default_context()
        self.s = self.ssl_connect.wrap_socket(
            self.raw_s, server_hostname=self.conf["host"])
        logging.info("connection established!")
        return True

    def connect_no_ssl(self):
        logging.info("Connecting - %s:%i (NO SSL)...",
                     self.conf["host"], self.conf["port"])
        print(self.conf["host"])
        print(self.conf["port"])
        print("-----------")
        self.s = socket.create_connection(
            (self.conf["host"], self.conf["port"]))
        # self.s = socket.create_connection(("irc.freenode.net", 7000))
        logging.info("connection established!")

        return True

    def sender_thread_run(self):
        while not self.end_thre.is_set() and not self.end_sender_receiver.is_set():
            try:
                msg = self.sender_queue.get(block=True, timeout=0.5)
                print(msg)

            except queue.Empty:
                continue
            # The "8" shows that it's an 8-bit character encoding. It uses 1-4 bytes for each character.

            self.s.sendall(bytes(msg, "utf-8") + b"\n")

    def receiver_thread_run(self):

        buffers = []
        data = ""

        while not self.end_thre.is_set() and not self.end_sender_receiver.is_set():

            try:
                data = self.s.recv(4096).decode('utf-8')
                print(data)
            except socket.timeout:
                continue
            if data == "":
                self.recv_queue.put(
                    IRCEvent(IRC_EVENT_DISCONNECT))
                return
            if data.find('hi!!') != -1:

                self.sender_queue.put(command.chat["hello"])

            if data.find("!memory") != -1:
                with open("/proc/meminfo", "r") as f:
                    lines = f.readlines()
                self.sender_queue.put(command.chat["memory"].format(lines[0]))
                self.sender_queue.put(command.chat["memory"].format(lines[0]))

            buffers.append(data)


# lifo from queue


    def handling_thread_run(self):
        login = True
        self.end_thre = threading.Event()   # unset
        self.sender_queue = queue.Queue()  # queue sync
        self.recv_queue = queue.Queue()
        while not self.end_thre.is_set():

            if not self.connect():
                logging.warning("fail to connect retrying in few  sec")
                time.sleep(config.IRC_CONFIG["reconnect_timeout"])
                # continue

            self.s.settimeout(0.5)

            self.end_sender_receiver = threading.Event()

           # check sender_reveriver running
            self.sender_thre = threading.Thread(
                target=self.receiver_thread_run)

            self.sender_thre.daemon = True
            self.sender_thre.start()

            self.receiver_th = threading.Thread(
                target=self.sender_thread_run)
            self.receiver_th.daemon = True
            self.receiver_th.start()

            while not self.end_thre.is_set():
                while not self.end_sender_receiver.is_set():
                    # login once
                    if(login):

                        self.sender_queue.put(self.conf["nickname"])
                        self.sender_queue.put(self.conf["password"])
                        self.sender_queue.put(self.conf["username"])
                        time.sleep(5)
                        self.sender_queue.put(self.conf["channel"])
                        login = False

                b = self.end_thre.is_set()
                print(b)
                try:
                    event = self.recv_queue.get(block=True, timeout=0.5)
                except queue.Empty:
                    continue
                logging.debug("Event %s", repr(event))  # todo remove thos

                if event.type == IRC_EVENT_DISCONNECT:
                    break

                print(self.end_sender_receiver.is_set())

            # clean up connection
            self.end_sender_receiver.set()
            self.sender_thre.join()
            self.receiver_th.join()
            self.disconnect()
            time.sleep(config.IRC_CONFIG["reconnect_timeout"])


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    IRC(config.IRC_NETWORKS["freenode"])
    time.sleep(100)
