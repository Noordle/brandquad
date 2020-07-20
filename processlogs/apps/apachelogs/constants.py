import enum


@enum.unique
class HTTPMethods(enum.Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    CONNECT = 'CONNECT'
    TRACE = 'TRACE'

    UNKNOWN = 'UNKNOWN'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
