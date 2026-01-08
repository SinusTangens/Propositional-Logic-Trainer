from enum import Enum, auto

class StudentInput(Enum):
    TRUE = auto()       # Student sagt: "Muss Wahr sein"
    FALSE = auto()      # Student sagt: "Muss Falsch sein"
    UNKNOWN = auto()    # Student sagt: "Kein konkreter Schluss möglich"

    def to_bool_or_none(self):
        if self == StudentInput.TRUE: return True
        if self == StudentInput.FALSE: return False
        return None # UNKNOWN