from enum import Enum, auto

class UserInput(Enum):
    """
    Klasse zur Repräsentation der möglichen Nutzereingaben 
    """

    TRUE = auto()       # Nutzer sagt: "Muss Wahr sein"
    FALSE = auto()      # Nutzer sagt: "Muss Falsch sein"
    UNKNOWN = auto()    # Nutzer sagt: "Kein konkreter Schluss möglich"


    def to_bool_or_none(self):
        """
        
        """

        if self == UserInput.TRUE: return True
        if self == UserInput.FALSE: return False
        return None # UNKNOWN