# -*- coding: UTF-8 -*-
import socket
import select
import traceback

from MyExceptions import MySmtpBaseException
from SmtpServeSession import SmtpServeSession
import logging
logging.basicConfig(level=logging.INFO)  # logging.DEBUG


class BaseServer:
    def __init__(self, master, addr="0.0.0.0", port=10000):
        """
        :param master: upper class that manages mails and forwards messages
        :param port: listen port
        """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._addr = addr
        self._port = port
        self.master = master
        self._sessions = {}

        logger_name = '.'.join([c.__name__ for c in self.__class__.mro()[:1]])  # [-2::-1]
        self._logger = logging.getLogger(logger_name)

        self._logger.info(f"Starting..")

    # @property
    # def _logger(self):
    #     return logging.getLogger(self.__logger_name)

    def _start_sock(self):
        self._logger.info(f"Listening at {self._addr} port {self._port}")

        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)
        self._sock.bind((self._addr, self._port))
        self._sock.listen()

        self._sessions[self._sock] = None

    def run(self):
        try:
            self._start_sock()
            while True:
                try:
                    r_list, w_list, e_list = select.select(self._sessions.keys(), [], [], 1)
                    for event in r_list:
                        if event == self._sock:
                            new_sock, addr = event.accept()
                            print(f"** new connection from {addr[0]}:{addr[1]}")
                            self._logger.info(f"New connection from {addr[0]}:{addr[1]}")
                            self._handle_new_connection(new_sock, addr)
                        else:
                            data = event.recv(1024)
                            if data:
                                self._on_data_read(event, data)
                            else:
                                self._logger.info(f"Connection closed")
                                self._sessions.pop(event)
                except MySmtpBaseException as e:
                    e.obj.shutdown(socket.SHUT_RDWR)
                except Exception:
                    traceback.print_exc()
                    self._reset()
        except KeyboardInterrupt:
            self._logger.info("shutdown..")
        finally:
            self.shutdown()

    def _handle_new_connection(self, new_sock, addr):
        raise NotImplementedError()

    def _on_data_read(self, sock, data: bytes):
        addr = sock.getpeername()
        text = data.decode()

        print(f"C:{repr(text)}")
        session = self._sessions[sock]  # type: SmtpServeSession
        session.on_message_receive(text)

    def send_data(self, session, data):
        print(f"S:{repr(data)}")
        addr = session.conn.getpeername()
        _bytes = data.encode() if type(data) == str else data
        session.conn.send(_bytes)

    def leave_session(self, session):
        session.conn.shutdown(socket.SHUT_RDWR)  # .close()
        print("** session terminated\r\n")

    def _reset(self):
        for sock in self._sessions.keys():
            if sock != self._sock:
                try:
                    sock.send(b"-ERR Server internal error\r\n")
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
        self._logger.warning("Server reset..")
        self._sessions = {self._sock: None}

    def shutdown(self):
        self._sock.close()

    def get_addr(self):
        return f"{self._addr}:{(self._port)}"
