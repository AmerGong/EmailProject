import re
import os
import time
import json
from MyExceptions import *
import logging

logger = logging.getLogger("SmtpSession")
DATA_END = "\r\n.\r\n"


class SmtpServeSession:
    def __init__(self, sock, server, handler: str, send_banner=True):
        self._server = server
        self._peer_domain = ""
        self._sender = ""
        self._recipients = []
        self._mail_data = ""
        self._state = "READY"
        self.conn = sock

        if handler not in ["dump", "popup"]:
            raise MySmtpBaseException(f"Invalid email handler: {handler}")
        self._type = handler

        self._handle_connection(send_banner)
        # self._quit()

    def on_message_receive(self, msg: str):
        logger.debug({"state": self._state, "msg": msg})
        try:
            if self._state != "DATA_RECV" and msg.upper().startswith("HELO"):
                logger.debug("handle FROM")
                self._handle_hello(msg)
            elif self._state != "DATA_RECV" and msg.upper().startswith("MAIL FROM"):
                logger.debug("handle FROM")
                self._handle_sender(msg)
            elif self._state != "DATA_RECV" and msg.upper().startswith("RCPT TO"):
                logger.debug("handle TO")
                self._handle_recipient(msg)
            elif self._state != "DATA_RECV" and msg.upper().startswith("DATA"):
                logger.debug("handle DATA MARK")
                if self._state != "RCPT_DONE":
                    raise InvalidStateException("Incorrect command given.")
                self._state = "DATA_RECV"
                self._response("354 Start mail input; end with " + self._encode_data_end(DATA_END))
            elif self._state == "DATA_RECV":
                logger.debug("handle DATA BODY")
                self._handle_data_recieve(msg)
            elif self._state != "DATA_RECV" and msg.upper().startswith("QUIT"):
                logger.debug("peer QUIT")
                self._quit()
            else:
                raise InvalidCommandException("Incorrect command")
        except MySmtpBaseException as e:
            self._response(f"{e.code} {e.msg}")
            
    def _handle_connection(self, send_banner):
        if send_banner:
            self._response("220 welcome")

    def _handle_hello(self, msg):
        if self._state != "READY":
            raise InvalidStateException("Incorrect command given.")
        nut = re.findall(r"HELO (.*)\s*", msg)
        if not nut:
            raise UserInputException("Invalid hello line", 501)
        self._check_domain_address(nut[0])
        self._peer_domain = nut[0]
        self._state = "START"
        self._response("250 OK")

    def _handle_sender(self, msg):
        if self._state != "START":
            raise InvalidStateException("Incorrect command given.")
        nut = re.findall(r"MAIL FROM:<(.*)\s*>", msg)
        if not nut:
            raise UserInputException("Invalid sender line", 501)
        # self._check_email_address(nut[0])   # allow non-standard mail address (like ip-address)
        self._sender = nut[0]
        self._state = "FROM_DONE"
        self._response("250 OK")

    def _handle_recipient(self, msg):
        if self._state not in ["FROM_DONE", "RCPT_DONE"]:
            raise InvalidStateException("Incorrect command given.")
        nut = re.findall(r"RCPT TO:<(.*)\s*>", msg)
        if not nut:
            raise UserInputException("Invalid recipient line", 501)
        # self._check_email_address(nut[0])   # allow non-standard mail address (like ip-address)
        self._recipients.append(nut[0])
        self._state = "RCPT_DONE"
        self._response("250 OK")

    def _handle_data_recieve(self, msg):
        self._mail_data += msg
        if self._mail_data.endswith(DATA_END):
            self._state = "DATA_DONE"
            self._mail_data = self._mail_data[:-5]
            if self._type == "dump":
                self._dump_email_to_local_file()
            elif self._type == "popup":
                mail = {"msg_from": self._sender, "msg_to": self._recipients, "msg": self._mail_data}
                try:
                    self._server.master.push_message(mail)
                except MySmtpBaseException as e:
                    logger.error(f"{e.msg} - {e.obj[0]}:{e.obj[1]}")
                    self._response(f"550 SMTP Service Unavailable - {e.msg} - {e.obj[0]}:{e.obj[1]}")
            self._response("250 OK")
            self._reset_state()

    def _reset_state(self):
        self._sender = ""
        self._recipients = []
        self._mail_data = ""
        self._state = "READY"

    def _quit(self):
        self._response("221 BYE")
        self._server.leave_session(self)
    
    def _response(self, text):
        self._server.send_data(self, text)
        
    @staticmethod
    def _check_email_address(text: str):
        text = text.strip()
        if not re.match(r".+@.+\..+", text):
            raise InvalidEmailAddress("Incorrect format: " + text, 501)
        # if self._existing_users and text not in self._existing_users:
        #     raise InvalidEmailAddress("email address doesn't exists: " + text, 553)

    @staticmethod
    def _encode_data_end(seq: str):
        repr = re.sub(r"([\r\n]+)", r"<\1>", seq)
        repr = re.sub("\n", "LF", repr)
        repr = re.sub("\r", "CR", repr)
        return repr

    @staticmethod
    def _check_domain_address(text: str):
        pass

    def _dump_email_to_local_file(self):
        timestamp = int(time.time()*1000)
        if not os.path.exists("./mails/"):
            os.mkdir("./mails/")
        the_file = "./mails/{sender}_{timestamp}.json".format(sender=self._sender, timestamp=timestamp)
        the_mail = {
            "sender": self._sender,
            "peer_domain": self._peer_domain,
            "recipients": self._recipients,
            "data": self._mail_data,
            "dt": timestamp
        }
        with open(the_file, "w") as f:
            f.write(json.dumps(the_mail))

        logger.info("email from {sender} saved as {file}".format(sender=self._sender, file=the_file))

    @property
    def state(self):
        return self._state

