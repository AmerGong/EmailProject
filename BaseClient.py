import select
import socket
import logging
import time


class BaseClient:
    """
    Provides general connection management and receive/send data functions
    """
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        logger_name = '.'.join([c.__name__ for c in self.__class__.mro()[:1]])  # [-2::-1]
        self._logger = logging.getLogger(logger_name)

        self._logger.info(f"Starting..")

    def _connect(self):
        self._sock.connect((self._ip, self._port))
        self._sock.setblocking(False)
        self._logger.debug(f"Established connection to {self._ip}:{self._port}")

    def _receive_octets(self, timeout=30, encode=False):
        # This scenario doesn't have long messages (HTTP request line has its maximum lengths)
        pass

    def _delimited_receive(self, buf_size=1024, timeout=10, delimiter="\r\n.\r\n"):
        # delimited receive
        resp = ""
        for i in range(timeout):
            r = self._receive(buf_size, timeout=1, decode=True)
            resp = resp + r if r else resp
            if resp.endswith(delimiter):
                break
        return resp

    def _send_and_delimited_receive(self, send_data, buf_size=1024, timeout=5, delimiter="\r\n.\r\n"):
        self._send(send_data)
        return self._delimited_receive(buf_size=buf_size, timeout=timeout, delimiter=delimiter)

    def _receive(self, buf_size=1024, timeout=30, decode=True):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            response = self._sock.recv(buf_size)
            if decode:
                response = response.decode()
            self._logger.debug(f"S: {repr(response)}")
            return response
        else:
            return None

    def _send_and_receive(self, send_data, buf_size=1024, timeout=30, decode=True):
        self._send(send_data)
        return self._receive(buf_size=buf_size, timeout=timeout, decode=decode)

    def _send(self, send_data):
        if type(send_data) != bytes:
            send_data = send_data.encode()
        self._sock.send(send_data)
        self._logger.debug(f"C: {send_data}")

    def close(self):
        self._sock.close()  # 关闭连接
        self._logger.info("Connection closed")
