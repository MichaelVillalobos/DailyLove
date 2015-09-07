class HTTPError(Exception):
    def __init__(self, status_code, message):
        super(HTTPError, self).__init__(status_code, message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return '{} {}'.format(self.status_code, self.message)
