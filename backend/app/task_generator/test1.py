import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Sequence, Dict

from itertools import product

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
    CASE_SPLIT = "TYPE_3_2"       # Aufgabentyp 3.2 (hier noch nicht sauber implementiert)


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
    op_weights : Dict[str, float]  # {"not": 1.5, "and": 1.5, "or": 1.0, "imp": 1.5, "xor": 1.0, "equiv": 1.0}      
    # Gewichtung sorgt dafür, dass einschränkende Operatoren eher gewählt werden, damit mehr Aufgaben mit eindeutiger Lösung erzeugt werden


DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {
   
    # Typ DIRECT_INFERENCE – Level 1: 1 Prämisse, wenige Variablen, einfache Form
    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2),
        num_premises_range=(2, 2),
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],   #,"and"
        op_weights= {"not": 1.5, "or": 1.0, "imp": 1.5, "xor": 1.0, "equiv": 1.0} #"and": 1.5,
    ),
    # Typ DIRECT_INFERENCE – Level 2: Mehr Prämissen, mehr Variablen
    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights= {"not": 1.5, "and": 1.5, "or": 1.0, "imp": 1.5, "xor": 1.0, "equiv": 1.0} 
    ),
    # Typ DIRECT_INFERENCE – Level 3: Mehr Prämissen, mehr Variablen
    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights= {"not": 1.5, "and": 1.5, "or": 1.0, "imp": 1.5, "xor": 1.0, "equiv": 1.0} 
    ),
    # Typ 3.1 – Level 4: Mehr Verschachtelung
    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights= {"not": 1.5, "and": 1.5, "or": 1.0, "imp": 1.5, "xor": 1.0, "equiv": 1.0} 
    ),
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen: Formeln & Semantik
#   -> eigene Wahrheitstabellen-Enumeration (brute force) über die gewählten Variablen
# ---------------------------------------------------------------------------

def random_formula(vars, max_depth: int, allowed_ops: Sequence[str], op_weights: Dict[str, float]) -> Boolean:
    """
    Erzeugt rekursiv eine zufällige SymPy-Formel über 'vars',
    unter Verwendung der erlaubten Operatoren.
    """

    if max_depth == 0:
        v = random.choice(vars)
        if random.random() < 0.5:
            return v
        else:
            return Not(v)

    op_weights_extracted = [op_weights[op] for op in allowed_ops]
    op = random.choices(allowed_ops, weights=op_weights_extracted)[0]       #[0], weil random.choices immer eine Liste zurückgibt

    if op == "not":
        return Not(random_formula(vars, max_depth - 1, allowed_ops, op_weights))

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

    # Fallback (sollte praktisch nicht vorkommen)
    return left


def all_models(premises: List[Boolean], vars) -> List[Dict]:
    """
    Liefert alle Modelle der Konjunktion der Prämissen als Liste von Valuations.
    Man geht brute-force alle 2^n Belegungen über 'vars' durch und behält 
    nur die, in denen alle Prämissen wahr sind.
    """
    models = []
 
    for bits in product([False, True], repeat=len(vars)):       #Erzeugt kartesisches Produkt (True, True, True); (True, True, False); ...
        valuation = {vars[i]: bits[i] for i in range(len(vars))}        #Baut Dict, dass jeder Var. einen Wahrheitswert zuordnet
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
    for bits in product([False, True], repeat=n):           #Valuation wie bei "all_model"
        valuation = {vars[i]: bits[i] for i in range(n)}
        
        if all(bool(p.subs(valuation)) for p in premises):
            # Wenn in so einer Belegung φ falsch ist -> keine logische Folgerung
            if not bool(formula.subs(valuation)):
                return False
    return True





def print_logical_pretty(expr) -> str:
    """
    Gibt eine SymPy-Formel in standardmäßiger logischer Syntax zurück.
    """
    # 1. Atomare Variablen
    if isinstance(expr, Symbol):
        return str(expr)

    # 2. Not
    if isinstance(expr, Not):
        sub = expr.args[0]
        return f"¬{wrap_if_needed(sub)}"

    # 3. AND und OR sind n-stellige Operatoren
    if isinstance(expr, And):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∧ ".join(parts)

    if isinstance(expr, Or):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∨ ".join(parts)

    # 4. Binäre / n-stellige Operatoren: →, ↔, ⊕
    if isinstance(expr, Implies):
        # Implies ist in SymPy eigentlich binär, aber wir sind defensiv:
        args = list(expr.args)
        if len(args) == 2:
            left, right = args
            return f"{wrap_if_needed(left)} → {wrap_if_needed(right)}"
        else:
            # Kette: a → b → c
            parts = [wrap_if_needed(a) for a in args]
            return " → ".join(parts)

    if isinstance(expr, Equivalent):
        # Equivalent kann n-stellig sein: Equivalent(a, b, c, ...)
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ↔ ".join(parts)

    if isinstance(expr, Xor):
        # Xor kann ebenfalls n-stellig sein
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ⊕ ".join(parts)

    # 5. Fallback (z. B. True / False)
    return str(expr)


def wrap_if_needed(expr):
    """
    Setzt Klammern um Ausdrücke, die keine atomare Variable sind.
    """
    if isinstance(expr, (Symbol, Not)):
        return print_logical_pretty(expr)
    return f"({print_logical_pretty(expr)})"


# ---------------------------------------------------------------------------
# Gütebedingung für Aufgabentyp DIRECT_INFERENCE
# ---------------------------------------------------------------------------

from collections import deque
from typing import Set, Tuple, List

# ---------------------------------------------------------------------------
# Helper: Build graph of premises and analyze connectivity + entailment
# ---------------------------------------------------------------------------
def _premises_connectivity_summary(premises: List[Boolean], used_vars) -> Tuple[bool, bool, bool]:
    """
    Baut einen ungerichteten Graphen über Prämissen:
      - Kante zwischen Pi und Pj, falls
          a) Pi und Pj gemeinsame Variablen haben (syntactic overlap), OR
          b) Pi ⊨ Pj oder Pj ⊨ Pi (semantische Verbindung).
    Liefert (is_connected, any_direct_entailment, any_semantic_or_syntactic_edge)

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

    # Precompute var-sets
    sym_sets: List[Set] = [set(p.free_symbols) for p in premises]

    for i in range(n):
        for j in range(i + 1, n):
            # syntactic overlap -> Kante
            if sym_sets[i] & sym_sets[j]:
                adj[i].add(j)
                adj[j].add(i)
                any_entail = True  # treat syntactic overlap as an "edge"
                continue

            # keine gemeinsame Variable -> prüfen auf semantische Verbindung
            # Falls entails wirft aus irgendeinem Grund, fangen wir's ab und
            # fahren weiter (robust gegen unerwartete Ausnahmen)
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

    # Prüfe, ob überhaupt Kanten existieren (any_edge)
    any_edge = any(len(neis) > 0 for neis in adj.values())

    # BFS/DFS zur Überprüfung der Zusammenhangskomponente (beginne bei 0)
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
# Überarbeitete is_good_task_type_3_1 (zusammenhangspflichtig für alle Level)
# ---------------------------------------------------------------------------

def is_good_task_type_3_1(premises: List[Boolean], vars, level) -> bool:
    """
    Prüft, ob Prämissen eine geeignete DIRECT_INFERENCE-Aufgabe bilden.
    Änderungen: Konnektivitäts- und semantische Prüfungen werden für alle Level erzwungen.
    Parameter:
      - premises: Liste von SymPy-Boolean-Ausdrücken
      - vars: Tuple/List der erwarteten Variablen (Symbol-Objekte)
      - level: wird weiterhin übergeben (kann für feinere Heuristiken genutzt werden)
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

    # 3) Enthält eine Aufgabe nur eine Prämisse, muss diese >=2 Var. enthalten
    # if len(premises) == 1 and len(premises[0].free_symbols) < 2:
    #     return False

    # 4) bei mehreren Prämissen: mindestens eine Prämisse mit >=2 Variablen
    #if len(premises) > 1:
    if not any(len(p.free_symbols) >= 2 for p in premises):
        return False

    # 5) Modelle: erfüllbar & nicht trivial
    models = all_models(premises, used_vars)
    if not models:
        return False
    if len(models) == 2 ** len(used_vars):
        return False

    # 6) stabile Literale (direkte Konsequenzen) müssen existieren
    stable_literals = []
    for v in used_vars:
        vals = [m[v] for m in models]
        if all(vals):
            stable_literals.append(v)
        elif not any(vals):
            stable_literals.append(Not(v))
    if not stable_literals:
        return False

    # 7) **NEU & WICHTIG**: Konnektivitäts- und semantikprüfung für alle Level
    #    - Graph muss zusammenhängend (via syntactic overlap OR semantic entail)
    #    - zusätzlich muss es mindestens eine semantische Bindung (entails)
    #      oder mindestens eine syntaktische Kante (shared var) geben
    is_connected, direct_entail, any_edge = _premises_connectivity_summary(premises, used_vars)

    # Wir fordern, dass der Premise-Graph zusammenhängend ist:
    if not is_connected:
        return False

    # Zusätzlich: es muss mindestens irgendeine Kante / semantische Verbindung existieren
    if not any_edge:
        return False

    # Wünschenswert: wenigstens eine gerichtete semantische Verbindung (Pi ⊨ Pj)
    #  -> falls du das zu streng findest, entferne die folgende Prüfung.
    #  Aktuell fordern wir: entweder direktes Pi ⊨ Pj (direct_entail True) OR
    #  wenigstens, dass mindestens eine Prämisse alleine informativ ist (entails Literal).
    if not direct_entail:
        # prüfe, ob mindestens eine einzelne Prämisse allein ein Literal erzwingt
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

    # Alle Checks bestanden -> gültige Aufgabe
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

            if is_good_task_type_3_1(premises, vars, level):
                return Task(
                    task_type=task_type,
                    level=level,
                    premises=premises,
                    variables=list(vars),
                )

        raise RuntimeError("Es konnte keine passende Aufgabe generiert werden!")


# ---------------------------------------------------------------------------
# Beispielverwendung
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    generator = TaskGenerator(DIFFICULTY_CONFIG)
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
        
