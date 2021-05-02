# -*- coding: UTF-8 -*-
from BaseServer import BaseServer
from SmtpServeSession import SmtpServeSession
import logging

logger = logging.getLogger("SmtpServer")


class SmtpServer(BaseServer):
    def __init__(self, master, handler: str, addr="0.0.0.0", port=10080):
        super().__init__(master, addr, port)
        self._type = handler  # ["dump", "popup"]

    def _handle_new_connection(self, new_sock, addr):
        self._sessions[new_sock] = SmtpServeSession(new_sock, self, self._type)


logging.basicConfig(level=logging.INFO)  # logging.DEBUG
if __name__ == '__main__':
    # A simple test code here
    server = SmtpServer(None, "dump", addr="127.0.0.1", port=10079)  # dump mode doesn't require a master object
    server.run()
