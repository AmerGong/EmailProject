import MyExceptions
from SmtpServer import SmtpServer
from SmtpClient import SmtpClient
import logging
logger = logging.getLogger("AE")


class AE:
    def __init__(self, addr, port):
        self.smtp_server = SmtpServer(self, handler="popup", addr=addr, port=port)

    def run(self):
        self.smtp_server.run()

    def push_message(self, msg):
        inet_addr, port = msg['msg_to'][0].split(":")
        logger.info(f"forward message to BE {msg['msg_to'][0]}: {str(msg)}")  # BE
        try:
            client = SmtpClient(inet_addr, int(port), enforce_banner=False, banner_wait_time=1)  # BE's smtp server address
        except ConnectionRefusedError as e:
            raise MyExceptions.MySmtpBaseException(e.strerror, obj=(inet_addr, port))
        client.send_message(msg, domain="example.com")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)  # logging.DEBUG
    ae = AE(addr="0.0.0.0", port=10080)
    ae.run()
