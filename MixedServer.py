# -*- coding: UTF-8 -*-
import json
import os
import select
import glob

from BaseServer import BaseServer
from MyExceptions import MySmtpBaseException
from SmtpServeSession import SmtpServeSession
from Pop3ServeSession import Pop3ServeSession


class MixedServer(BaseServer):
    def __init__(self, addr="0.0.0.0", port=10080):
        super().__init__(None, addr=addr, port=port)
        # self._mails = []  # list of mail dicts

    def _handle_new_connection(self, new_sock, addr):
        r_list, w_list, e_list = select.select([new_sock], [], [], 10)
        if r_list:   # if there's a msg from client
            command = r_list[0].recv(1024)
        else:
            raise MySmtpBaseException("Client read timeout", obj=new_sock)
        if command.startswith(b"HELO"):
            self._sessions[new_sock] = SmtpServeSession(new_sock, self, "dump", send_banner=False)
        else:
            self._sessions[new_sock] = Pop3ServeSession(new_sock, self, send_banner=False)
        self._on_data_read(new_sock, command)

    @property
    def mails(self):
        mails = []
        mail_files = glob.glob("./mails/*.json")
        for idx, mail in enumerate(mail_files):
            with open(mail, "r") as fp:
                mailobj = json.load(fp)
                mailobj['file'] = mail
                mailobj['idx'] = idx+1
                mails.append(mailobj)
        return mails

    def delete_mail(self, mail):
        try:
            os.remove(mail['file'])
            self._logger.debug(f"Mail {mail['idx']}: {mail['data']} deleted")
            return "OK"
        except FileNotFoundError:
            self._logger.error(f"Mail {mail['idx']}: {mail['file']} doesn't exist")
            return "Mail {mail['idx']} doesn't exist (or may have already deleted)"


if __name__ == '__main__':
    """Test code"""
    server = MixedServer(addr="127.0.0.1", port=10079)
    server.run()
