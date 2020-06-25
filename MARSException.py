class Error(Exception):
    pass

class MARSException(Error):
    def __init__(self, message):
        self.message = message