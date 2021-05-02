class MySmtpBaseException(Exception):
    def __init__(self, msg, code=554, obj=None):
        self.msg = msg
        self.code = code
        self.obj = obj

    def __str__(self):
        return self.msg


class MyPop3BaseException(Exception):
    def __init__(self, msg, code=400, obj=None):
        self.msg = msg
        self.code = code
        self.obj = obj

    def __str__(self):
        return self.msg


class InvalidStateException(MySmtpBaseException):
    def __init__(self, msg, code=503):
        super().__init__(msg)
        self.code = code


class InvalidCommandException(MySmtpBaseException):
    def __init__(self, msg, code=502):
        super().__init__(msg)
        self.code = code


class UserInputException(MySmtpBaseException):
    """
    this is user's Exception for reporting the correctness of user input
    """
    pass


class InvalidEmailAddress(MySmtpBaseException):
    pass


class SmtpClientHandshakeFailureException(MySmtpBaseException):
    def __init__(self, msg="Smtp handshake failed", code=500):
        self.msg = msg
        self.code = code


class SmtpClientRuntimeException(MySmtpBaseException):
    def __init__(self, msg="Smtp client error", code=501):
        self.msg = msg
        self.code = code


class Pop3ClientHandshakeFailureException(MyPop3BaseException):
    def __init__(self, msg="Smtp handshake failed", code=500):
        self.msg = msg
        self.code = code


class Pop3ClientRuntimeException(MyPop3BaseException):
    def __init__(self, msg="Smtp client error", code=501):
        self.msg = msg
        self.code = code

