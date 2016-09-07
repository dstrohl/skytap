
class BaseSkytapException(Exception):
    _template = 'Skytap Error: {}'

    def __init__(self, *args, **kwargs):
        self.message = self._template.format(*args, **kwargs)


class SkytapBaseApiError(BaseSkytapException):
    _template = 'Skytap API {code}:\n    URL: {url}\n    Error: {desc}\n    Data: ({data})\n'
    _desc = ''

    def __init__(self, response):
        self.response = response
        super(SkytapBaseApiError, self).__init__(
            url=response.request.url,
            code=response.status_code,
            desc=self._desc,
            data=self.response.text)

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message

class SkytapMaxAttempsExceededError(SkytapBaseApiError):
    _template = 'Skytap API Max attempts exceeded:\n    URL: {url}\n'


class Skytap401UnauthorizedError(SkytapBaseApiError):
    _desc = 'Unauthorized'


class Skytap404NotFoundError(SkytapBaseApiError):
    _desc = 'Object not found'


class Skytap409ConflictError(SkytapBaseApiError):
    _desc = 'Conflict'


class Skytap422InvalidParamError(SkytapBaseApiError):
    _desc = 'Invalid Parameter'


class Skytap423BusyError(SkytapBaseApiError):
    _desc = 'Resource Busy'


class Skytap429TooManyRequestsError(SkytapBaseApiError):
    _desc = 'Too many HTTP requests'


class Skytap500SystemError(SkytapBaseApiError):
    _desc = 'System Error'


class SkytapOtherSystemError(SkytapBaseApiError):
    _desc = 'Unknown Error'
