from MixedServer import MixedServer
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)  # logging.DEBUG
    mixed_server = MixedServer(addr="0.0.0.0", port=10079)  # pop3 server + smtp server
    mixed_server.run()
