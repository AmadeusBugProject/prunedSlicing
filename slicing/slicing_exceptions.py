class InconsistentExecutionTraceException(Exception):
    def __init__(self, message):
        self.message = message

class SlicingException(Exception):
    def __init__(self, message):
        self.message = message