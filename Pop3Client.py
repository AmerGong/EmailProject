# import re
import socket
import traceback

from MyExceptions import *
from BaseClient import BaseClient


class Pop3Client(BaseClient):
    def __init__(self, ip, port, enforce_banner=True, delete_after_retrieve=True, banner_wait_time=5):
        super().__init__(ip, port)
        self._ENFORCE_BANNER = enforce_banner
        self._DELETE_AFTER_RETR = delete_after_retrieve
        self._BANNER_WAIT_TIME = banner_wait_time

        self._connect()
        self._get_banner()

    def _get_banner(self):
        self._logger.debug(f"Waiting for banner..")
        banner = self._receive(timeout=self._BANNER_WAIT_TIME)
        if banner:
            if not banner.startswith("+OK"):
                raise SmtpClientHandshakeFailureException(f"Failed to connect: Unexpected banner: {banner}")
        else:
            if self._ENFORCE_BANNER:
                self._logger.error("Failed to connect: Waiting for banner timeout, and option `enforce_banner` is set.")
                raise MyPop3BaseException("Failed to connect: Waiting for banner timeout")
            else:
                self._logger.warning("Waiting for banner timeout, continue fetching process.")
        self._logger.info(f"Successfully connected")

    def auth(self, auth_user="anonymous", auth_pass="anonymous"):
        self._logger.debug(f"sending credentials to auth as {auth_user}")
        cmd_login = [(f"user {auth_user}", "+OK"), (f"pass {auth_pass}", "+OK")]
        for cmd in cmd_login:
            resp = self._send_and_receive(cmd[0])
            if not (resp and resp.startswith(cmd[1])):
                raise Pop3ClientRuntimeException(f"Failed to auth: server said: {resp}")
        self._logger.info(f"Auth successfully as {auth_user}")

    def delete_message(self, idx):
        return self._send_and_receive(f"DELE {idx}\r\n")

    def fetch_message(self):
        try:
            resp = self._send_and_delimited_receive("LIST\r\n")
            if not resp.startswith("+OK"):
                raise Pop3ClientRuntimeException(resp)
            lines = resp.split("\r\n")[1:-3]
            msgs = []
            for i in range(len(lines)):
                msg = self._send_and_delimited_receive(f"RETR {i+1}\r\n")
                msg = msg.strip().split("\r\n")
                if not msg[0].startswith("+OK"):
                    self._logger.error("error fetch message: "+msg[0])
                    raise Pop3ClientRuntimeException(msg[0])
                msgs.append("\r\n".join(msg[1:-1]))

            if self._DELETE_AFTER_RETR:
                for i in range(len(lines)):
                    resp = self.delete_message(i+1)
                    if not resp.startswith("+OK"):
                        self._logger.error(f"Fail to delete mail {i}: {resp}")
                        raise Pop3ClientRuntimeException(resp)

            self._sock.shutdown(socket.SHUT_RDWR)
            return "OK", msgs

        except Exception as e:
            traceback.print_exc()
            return str(e), None


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    client = Pop3Client("127.0.0.1", 10079, enforce_banner=False)
    # client.auth("test", "password")
    client.fetch_message()
