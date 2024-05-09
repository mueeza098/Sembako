class outOfstokError(Exception):
    def __init__(self, message):
        super().__init__(message)

class Unauthorized(Exception):
    def __init__(self, message):
        super().__init__(message)

class ValueError(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class DatabaseError(Exception):
    def __init__(self, message):
        super().__init__(message)