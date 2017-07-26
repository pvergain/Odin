class Error(Exception):
    """
    Base class for exceptions
    """
    pass


class PollingError(Error):
    """
    Exception raised when polling towards the Grader has failed
    """

    def __init__(self, message):
        self.message = message
