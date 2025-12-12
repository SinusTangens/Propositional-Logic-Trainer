from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Sequence, Dict, Callable
from sympy.logic.boolalg import Boolean



class TaskType(Enum):
    DIRECT_INFERENCE = "Direktes Schließen aller Variablenbelegungen auf Basis weniger Prämissen"  
    CASE_SPLIT = "Durchführung einer initialen Fallunterscheidung, um alle Variablenbelegungen auf Basis vieler Prämissen zu bestimmen"       


@dataclass
class Task:
    task_type: TaskType
    level: int
    premises: List[Boolean]   # SymPy-Formeln
    variables: List           # SymPy-Symbole (A, B, C, ...)


@dataclass
class DifficultySpec:
    num_vars_range: Tuple[int, int]
    num_premises_range: Tuple[int, int]
    max_depth: int
    allowed_ops: Sequence[str]  # ["not", "and", "or", "imp", "xor", "equiv"]
    op_weights: Dict[str, float]  # {"not": 1.5, "and": 1.5, "or": 1.0, ...}
    closure_threshold_func: Callable[[int], int]        # Funktion bei der Generierung einer Aufgabe abgrenzen soll, wie viele Variablen eindeutig bestimmbar sind



# ---------------------------------------------------------------------------
# Regelbasierte Konfiguration des Schwierigkeisgrad über die Aufgabentypen und Levels hinweg
# ---------------------------------------------------------------------------

DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {

    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2),
        num_premises_range=(2, 2),
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        # Level 1: Mindestens 1 Variable muss lösbar sein
        closure_threshold_func=lambda n: 1, 
    ),
    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        # Level 2: Mindestens 2 Variablen müssen lösbar sein
        closure_threshold_func=lambda n: max(1, min(2, n)),
    ),
    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 0.5, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        # Level 3: Fast alle Variablen müssen lösbar sein (erlaubt 1 ungelöste Variable)
        closure_threshold_func=lambda n: max(2, n - 1),
    ),
    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 0.5, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        # Level 4: Alle Variablen MÜSSEN lösbar sein (eindeutige Lösung)
        closure_threshold_func=lambda n: max(2, n-1),
    ),



    (TaskType.CASE_SPLIT, 1): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(3, 4),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=None,        #Bei diesem Aufgabentyp muss jede Variable eindeutig bestimmbar sein 
    ),
    (TaskType.CASE_SPLIT, 2): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(4, 5),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=None,
    ),
    (TaskType.CASE_SPLIT, 3): DifficultySpec(
        num_vars_range=(5, 5),
        num_premises_range=(5, 6),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 0.5, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=None,
    ),
}
