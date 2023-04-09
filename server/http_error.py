from .response import Response


class HTTPError(Exception):
    def __init__(self, error, error_message, connection_host, message=None):
        self.num_error = error
        self.error_message = error_message
        self.message = message
        self.connection_host = connection_host
        Response(self.num_error, self.error_message, connection_host).send_response()

    def __str__(self):
        return f"Num error: {self.num_error}, Error message: {self.error_message}"
