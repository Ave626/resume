class PresentationError(Exception):
    default_message : str = "Presentation_error"
    code : str = "PRESENTATION_ERROR"
    def __init__(self, message : str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)