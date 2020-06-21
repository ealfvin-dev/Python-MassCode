class Error(Exception):
    pass

class PyMacException(Error):
    def __init__(self, message):
        self.message = message