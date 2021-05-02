import logging
import re

import MyExceptions
from MyExceptions import InvalidCommandException, UserInputException

logger = logging.getLogger(__name__)


class Pop3ServeSession:
    def __init__(self, sock, server, send_banner=True, use_auth=False):
        self._server = server
        self.conn = sock
        self._tmp_mails = []
        self._state = "READY"

        if use_auth:
            raise NotImplementedError("Auth not implemented")

        self._handle_connection(send_banner)

    def _handle_list(self):
        self._tmp_mails = self._server.mails.copy()
        response_for_list = []
        response = ""
        for mail in self._tmp_mails:  # assert that the index in mails are ascending
            response += f"{mail['idx']} {len(mail['data'])}\r\n"
        self._state = "MAILS_READY"
        self._response(f"+OK {len(self._tmp_mails)} messages\r\n")
        self._response(response)
        self._response("\r\n.\r\n")

    def _handle_retrieve(self, msg):
        nut = re.findall(r"RETR (\d+)\s*", msg)
        if not nut:
            raise UserInputException("Invalid RETR line\r\n")
        mail_idx = int(nut[0])
        try:
            if mail_idx<1:
                raise IndexError
            mail = self._tmp_mails[mail_idx-1]  # type: dict
            body = mail['data'].encode()
            self._response(f"+OK {len(body)} octets\r\n")
            self._response(body)
            self._response("\r\n.\r\n")
        except IndexError:
            self._response(f"-ERR Mail {mail_idx} doesn't exist\r\n")

    def _handle_delete(self, msg):
        nut = re.findall(r"DELE (\d+)\s*", msg)
        if not nut:
            raise UserInputException("Invalid DELE line\r\n")
        mail_idx = int(nut[0])
        try:
            if mail_idx<1:
                raise IndexError
            mail = self._tmp_mails[mail_idx-1]  # type: dict
            result = self._server.delete_mail(mail)
            if result == "OK":
                self._response(f"+OK message {mail_idx} deleted\r\n")
            else:
                self._response(f"-ERR {result}\r\n")
        except IndexError:
            self._response(f"-ERR Mail {mail_idx} doesn't exist\r\n")


    def _handle_connection(self, send_banner):
        if send_banner:
            self._response("+OK POP3 server ready\r\n")

    def _handle_quit(self):
        self._response("+OK BYE\r\n")
        self._server.leave_session(self)

    def on_message_receive(self, msg: str):
        logger.debug({"state": self._state, "msg": msg})
        try:
            if self._state == "READY" and msg.upper().startswith("USER"):
                logger.warning("USER not implemented")
                self._response("-ERR Auth not implemented, please proceed LIST\r\n")
            elif self._state == "READY" and msg.upper().startswith("LIST"):
                logger.debug("handle LIST")
                self._handle_list()
            elif self._state == "MAILS_READY" and msg.upper().startswith("RETR"):
                logger.debug("handle RETR")
                self._handle_retrieve(msg)
            elif self._state == "MAILS_READY" and msg.upper().startswith("DELE"):
                logger.debug("handle FROM")
                self._handle_delete(msg)
            elif msg.upper().startswith("QUIT"):
                logger.debug("handle QUIT")
                self._handle_quit()
            else:
                raise InvalidCommandException("Incorrect command")
        except (InvalidCommandException, MyExceptions.MyPop3BaseException) as e:
            self._response(f"-ERR {e.msg}\r\n")

    def _response(self, data):
        if type(data) == str:
            data = data.encode()
        self._server.send_data(self, data)

