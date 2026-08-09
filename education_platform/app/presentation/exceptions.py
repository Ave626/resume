class PresentationError(Exception):
    pass


class AuthenticationError(PresentationError):
    pass


class PermissionDeniedError(PresentationError):
    pass
