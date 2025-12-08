import random
import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Sequence, Dict, Optional, Set

from itertools import product
from collections import deque

from sympy import symbols, Symbol
from sympy.logic.inference import satisfiable
from sympy.logic.boolalg import (
    Boolean,
    And,
    Or,
    Not,
    Implies,
    Xor,
    Equivalent,
)


# ---------------------------------------------------------------------------
# Grundstrukturen
# ---------------------------------------------------------------------------

class TaskType(Enum):
    DIRECT_INFERENCE = "TYPE_3_1"  # Aufgabentyp 3.1
    CASE_SPLIT = "TYPE_3_2"       # Aufgabentyp 3.2 (noch nicht vollständig implementiert)


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
    allowed_ops: Sequence[str]  # ["not","and","or","imp","xor","equiv"]
    require_unique: bool = False  # falls True: nur Aufgaben mit genau einem Modell akzeptieren
    op_weights: Optional[Dict[str, float]] = None  # relative Wahrscheinlichkeiten für Operatoren


# ---------------------------------------------------------------------------
# Default Difficulty Config (Beispiel). Passe op_weights / require_unique pro Level an.
# ---------------------------------------------------------------------------

DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {
    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2),
        num_premises_range=(2, 2),
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],   # kein "and" auf Level 1 (Beispiel)
        require_unique=False,
        op_weights={"imp": 1.5, "not": 1.5, "or": 1.0, "xor": 1.0, "equiv": 1.0},
    ),
    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        require_unique=False,
        op_weights={"and": 3.0, "imp": 2.5, "not": 1.5, "or": 1.0, "xor": 0.6, "equiv": 0.5},
    ),
    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        require_unique=False,
        op_weights={"and": 4.0, "imp": 3.0, "not": 1.8, "or": 1.0, "xor": 0.5, "equiv": 0.4},
    ),
    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        require_unique=True,
        op_weights={"and": 1.25, "imp": 1.25, "not": 1.25, "or": 1.0, "xor": 1.0, "equiv": 1.0},
    ),
}


# ---------------------------------------------------------------------------
# Operator weight utilities and weighted random formula generator
# ---------------------------------------------------------------------------

def _default_op_weights(allowed_ops: Sequence[str]) -> Dict[str, float]:
    """
    Heuristische Default-Wichtung — stärker einschränkende Operatoren bekommen
    größere Werte.
    """
    base_scores = {
        "and": 3.0,
        "imp": 3.0,
        "not": 2.0,
        "or": 1.0,
        "xor": 0.7,
        "equiv": 0.6,
    }
    weights = {}
    for op in allowed_ops:
        weights[op] = float(base_scores.get(op, 1.0))
    return weights


def random_formula(vars, max_depth: int, allowed_ops: Sequence[str], op_weights: Optional[Dict[str, float]] = None) -> Boolean:
    """
    Erzeugt rekursiv eine zufällige SymPy-Formel.
    - op_weights (optional): Dict mit relativen Wahrscheinlichkeiten für Operatoren.
      Falls None, werden heuristische Defaults verwendet.
    """
    # Basisfall: Literal
    if max_depth == 0:
        v = random.choice(vars)
        return v if random.random() < 0.5 else Not(v)

    # Bestimme Gewichte
    if op_weights is None:
        weights_map = _default_op_weights(allowed_ops)
    else:
        weights_map = {op: float(op_weights.get(op, 1.0)) for op in allowed_ops}

    ops = list(allowed_ops)
    weights = [weights_map.get(op, 1.0) for op in ops]

    # Defensive: falls alle Gewichte ungültig sind
    if all((w == 0 or math.isnan(w)) for w in weights):
        weights = [1.0] * len(weights)

    op = random.choices(ops, weights=weights, k=1)[0]

    # Unärer Operator
    if op == "not":
        return Not(random_formula(vars, max_depth - 1, allowed_ops, op_weights))

    # Binäre Operatoren
    left = random_formula(vars, max_depth - 1, allowed_ops, op_weights)
    right = random_formula(vars, max_depth - 1, allowed_ops, op_weights)

    if op == "and":
        return And(left, right)
    if op == "or":
        return Or(left, right)
    if op == "imp":
        return Implies(left, right)
    if op == "xor":
        return Xor(left, right)
    if op == "equiv":
        return Equivalent(left, right)

    # Fallback
    return left


# ---------------------------------------------------------------------------
# Semantik: all_models und entails (Brute-force Wahrheitstabelle)
# ---------------------------------------------------------------------------

def all_models(premises: List[Boolean], vars) -> List[Dict]:
    """
    Liefert alle Modelle der Konjunktion der Prämissen als Liste von Valuations.
    Brute-force über alle 2^n Belegungen (n = len(vars)).
    """
    models = []
    n = len(vars)
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        ok = True
        for prem in premises:
            val = prem.subs(valuation)
            if not bool(val):
                ok = False
                break
        if ok:
            models.append(valuation)
    return models


def entails(premises: List[Boolean], formula: Boolean, vars) -> bool:
    """
    Entailment per Wahrheitstabelle:
    Γ ⊨ φ genau dann, wenn es keine Belegung gibt,
    in der alle Prämissen wahr sind und φ falsch ist.
    """
    n = len(vars)
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        if all(bool(p.subs(valuation)) for p in premises):
            if not bool(formula.subs(valuation)):
                return False
    return True


# ---------------------------------------------------------------------------
# Pretty-printer für logische Formeln (schön lesbar)
# ---------------------------------------------------------------------------

def print_logical_pretty(expr) -> str:
    """
    Gibt eine SymPy-Formel in standardmäßiger logischer Syntax zurück.
    """
    # Atomare Variable
    if isinstance(expr, Symbol):
        return str(expr)

    # Not
    if isinstance(expr, Not):
        sub = expr.args[0]
        return f"¬{wrap_if_needed(sub)}"

    # And / Or (n-stellig)
    if isinstance(expr, And):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∧ ".join(parts)
    if isinstance(expr, Or):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∨ ".join(parts)

    # Implies (defensiv n-stellig behandeln)
    if isinstance(expr, Implies):
        args = list(expr.args)
        if len(args) == 2:
            left, right = args
            return f"{wrap_if_needed(left)} → {wrap_if_needed(right)}"
        else:
            parts = [wrap_if_needed(a) for a in args]
            return " → ".join(parts)

    # Equivalent (n-stellig)
    if isinstance(expr, Equivalent):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ↔ ".join(parts)

    # Xor (n-stellig)
    if isinstance(expr, Xor):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ⊕ ".join(parts)

    return str(expr)


def wrap_if_needed(expr):
    """
    Setzt Klammern um Ausdrücke, die keine atomare Variable oder Not sind.
    """
    if isinstance(expr, (Symbol, Not)):
        return print_logical_pretty(expr)
    return f"({print_logical_pretty(expr)})"


# ---------------------------------------------------------------------------
# Helper: Build graph of premises and analyze connectivity + entailment
# ---------------------------------------------------------------------------

def _premises_connectivity_summary(premises: List[Boolean], used_vars) -> Tuple[bool, bool, bool]:
    """
    Baut einen ungerichteten Graphen über Prämissen:
      - Kante zwischen Pi und Pj, falls
          a) Pi und Pj gemeinsame Variablen haben (syntactic overlap), OR
          b) Pi ⊨ Pj or Pj ⊨ Pi (semantische Verbindung).

    Liefert (is_connected, any_direct_entailment, any_edge)
    - is_connected: True wenn alle Prämissen im Graphen verbunden sind
    - any_direct_entailment: True falls mindestens ein gerichtetes Pi ⊨ Pj existiert
    - any_edge: True falls mindestens irgendeine Kante im Graph existiert (syntaktisch oder semantisch)
    """
    n = len(premises)
    if n <= 1:
        return True, False, False

    adj = {i: set() for i in range(n)}
    any_entail = False
    direct_entail = False

    sym_sets: List[Set] = [set(p.free_symbols) for p in premises]

    for i in range(n):
        for j in range(i + 1, n):
            # syntactic overlap -> Kante
            if sym_sets[i] & sym_sets[j]:
                adj[i].add(j)
                adj[j].add(i)
                any_entail = True
                continue

            # sonst prüfen auf semantische Verbindung (entails)
            try:
                if entails([premises[i]], premises[j], used_vars):
                    adj[i].add(j)
                    adj[j].add(i)
                    any_entail = True
                    direct_entail = True
                    continue
            except Exception:
                pass
            try:
                if entails([premises[j]], premises[i], used_vars):
                    adj[i].add(j)
                    adj[j].add(i)
                    any_entail = True
                    direct_entail = True
                    continue
            except Exception:
                pass

    any_edge = any(len(neis) > 0 for neis in adj.values())

    # BFS für Zusammenhang (beginne bei 0)
    visited = set()
    queue = deque([0])
    visited.add(0)
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)

    is_connected = (len(visited) == n)
    return is_connected, direct_entail, any_edge


# ---------------------------------------------------------------------------
# Gütebedingung für Aufgabentyp DIRECT_INFERENCE (zusammenhangspflichtig)
# ---------------------------------------------------------------------------

def is_good_task_type_3_1(premises: List[Boolean], vars, level: int = 1) -> bool:
    """
    Prüft, ob Prämissen eine geeignete DIRECT_INFERENCE-Aufgabe bilden.
    Die Prüfung verlangt u.a.:
      - keine konstanten Prämissen,
      - alle vorgegebenen Variablen müssen verwendet werden,
      - erfüllbar & nicht trivial,
      - stabile Literale existieren (direkte Konsequenzen),
      - Premise-Graph ist zusammenhängend (syntaktisch oder semantisch),
      - mindestens eine semantische Verbindung (entails) oder eine informative Prämisse.
    """
    # 1) Keine konstanten Prämissen (z.B. True / False)
    for prem in premises:
        if len(prem.free_symbols) == 0:
            return False

    # 2) verwendete Variablen ermitteln
    all_syms = set()
    for prem in premises:
        all_syms |= prem.free_symbols
    used_vars = [v for v in vars if v in all_syms]
    if not used_vars:
        return False

    # 2b) alle vorgegebenen Variablen sollten vorkommen
    if len(used_vars) != len(vars):
        return False

    # 3) bei mehreren Prämissen: mindestens eine Prämisse mit >=2 Variablen
    if not any(len(p.free_symbols) >= 2 for p in premises):
        return False

    # 4) Modelle: erfüllbar & nicht trivial
    models = all_models(premises, used_vars)
    if not models:
        return False
    if len(models) == 2 ** len(used_vars):
        return False

    # 5) stabile Literale (direkte Konsequenzen)
    stable_literals = []
    for v in used_vars:
        vals = [m[v] for m in models]
        if all(vals):
            stable_literals.append(v)
        elif not any(vals):
            stable_literals.append(Not(v))
    if not stable_literals:
        return False

    # 6) Konnektivitäts- & Semantikprüfung (für alle Level)
    is_connected, direct_entail, any_edge = _premises_connectivity_summary(premises, used_vars)

    if not is_connected:
        return False
    if not any_edge:
        return False

    # Wenn kein direktes Pi ⊨ Pj gefunden wurde: akzeptiere nur wenn mindestens
    # eine Prämisse alleine informativ ist (entails Literal).
    if not direct_entail:
        informative = False
        for Pi in premises:
            for v in used_vars:
                if entails([Pi], v, used_vars) or entails([Pi], Not(v), used_vars):
                    informative = True
                    break
            if informative:
                break
        if not informative:
            return False

    return True


# ---------------------------------------------------------------------------
# Generator-Klasse (für Typ DIRECT_INFERENCE)
# ---------------------------------------------------------------------------

class TaskGenerator:
    def __init__(self, config: Dict[Tuple[TaskType, int], DifficultySpec]):
        self.config = config

    def generate_task(self, task_type: TaskType, level: int) -> Task:
        if task_type is not TaskType.DIRECT_INFERENCE:
            raise NotImplementedError("Aktuell ist nur TaskType.DIRECT_INFERENCE (3.1) implementiert.")

        spec = self.config[(task_type, level)]

        # Variablen erzeugen
        num_vars = random.randint(*spec.num_vars_range)
        var_names = ["A", "B", "C", "D", "E", "F", "G", "H"][:num_vars]
        vars = symbols(" ".join(var_names))
        if num_vars == 1:
            vars = (vars,)

        # Mehrfach versuchen, bis eine passende Aufgabenstruktur gefunden wird
        for _ in range(5000):
            num_premises = random.randint(*spec.num_premises_range)
            premises = [
                random_formula(vars, spec.max_depth, spec.allowed_ops, spec.op_weights)
                for _ in range(num_premises)
            ]

            # 1) generelle Gütebedingung (zusammenhang etc.)
            if not is_good_task_type_3_1(premises, vars, level):
                continue

            # 2) falls eindeutiges Modell verlangt: prüfe Anzahl Modelle
            if spec.require_unique:
                # benutze die tatsächlich verwendeten Variablen
                all_syms = set()
                for p in premises:
                    all_syms |= p.free_symbols
                used_vars = [v for v in vars if v in all_syms]
                models = all_models(premises, used_vars)
                if len(models) != 1:
                    continue

            # Alles okay -> Task erstellen
            return Task(
                task_type=task_type,
                level=level,
                premises=premises,
                variables=list(vars),
            )

        raise RuntimeError("Es konnte keine passende Aufgabe generiert werden!")


# ---------------------------------------------------------------------------
# Beispielverwendung / Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    generator = TaskGenerator(DIFFICULTY_CONFIG)

    # Beispiel: versuche eine Aufgabe für Level 4
    task_3_1 = generator.generate_task(TaskType.DIRECT_INFERENCE, 4)

    print(f"Typ {task_3_1.task_type} – Level {task_3_1.level}")
    print("Variablen:", task_3_1.variables)
    print("Prämissen:")
    for p_enum, p in enumerate(task_3_1.premises, start=1):
        print(f"(P{p_enum})", print_logical_pretty(p))


    solutions = list(satisfiable(And(*task_3_1.premises), all_models=True))

    print("\nMögliche Belegungen (Lösungen):")
    for solution in solutions:
        print(solution)
