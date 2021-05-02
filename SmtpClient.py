from MyExceptions import *
from BaseClient import BaseClient


class SmtpClient(BaseClient):
    def __init__(self, ip, port, enforce_banner=True, banner_wait_time=5):
        super().__init__(ip, port)
        self._ENFORCE_BANNER = enforce_banner
        self._BANNER_WAIT_TIME = banner_wait_time

        self._connect()
        self._get_banner()

    def _get_banner(self):
        self._logger.debug(f"Waiting for banner..")
        banner = self._receive(timeout=self._BANNER_WAIT_TIME)
        if banner:
            if not banner.startswith("220"):
                raise SmtpClientHandshakeFailureException(f"Failed to connect: Unexpected banner: {banner}")
        else:
            if self._ENFORCE_BANNER:
                self._logger.error("Failed to connect: Waiting for banner timeout, and option `enforce_banner` is set.")
                self.close()
            else:
                self._logger.warning("Waiting for banner timeout, continue sending process.")
        self._logger.info(f"Successfully connected")

    def send_message(self, email: dict, domain="localhost"):
        endmsg = '\r\n.\r\n'
        cmds_sequence = [
            # "_INIT",  # 220
            (f"HELO {domain}", "250"),
            (f"MAIL FROM:<{email['msg_from']}>", "250")] + \
            [(f"RCPT TO:<{rcpt}>", "250") for rcpt in email['msg_to']] + \
            [("DATA", "354"), ("_BODY", "250"), ("QUIT", "221")]
        try:
            for cmd in cmds_sequence:
                _to_send = (email['msg'] + endmsg) if cmd[0] == "_BODY" else cmd[0]
                resp = self._send_and_receive(_to_send, timeout=30)
                if resp.startswith("550"):
                    self._logger.error("Post message failed: " + resp)
                    return 501, resp
                if not resp.startswith(cmd[1]):
                    self._logger.error("Post message failed: " + resp)
                    return 501, "Failed to post message:" + resp
            return 200, "OK"
        finally:
            self.close()


if __name__ == '__main__':
    import logging
    """
    Simple code to test our Smtp system with scenario between AE <--> BE
    """

    logging.basicConfig(level=logging.DEBUG)  # logging.INFO
    mail = {  # A mail received by AE (from AU)
        "msg_from": "127.0.0.1:10080",  # AE's address
        "msg_to": ["127.0.0.1:10079"],  # BE's address
        "msg": "This is a sample message to test mixed server"}

    serv_addr, serv_port = mail['msg_to'][0].split(":")  # get BE's address
    client = SmtpClient(serv_addr, int(serv_port))  # try to connect to the Smtp server on BE
    client.send_message(mail)
