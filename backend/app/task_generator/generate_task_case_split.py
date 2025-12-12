import random
import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Sequence, Dict, Optional, Set, Any, Callable

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
    CASE_SPLIT = "TYPE_3_2"       # Aufgabentyp 3.2


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
    allowed_ops: Sequence[str]
    op_weights: Dict[str, float]
    # Threshold Funktion: Input (n_vars) -> Output (min_closure_count)
    # Bei CASE_SPLIT ist dies None oder irrelevant, da wir spezifische Logik nutzen.
    closure_threshold_func: Optional[Callable[[int], int]] = None


# ---------------------------------------------------------------------------
# Difficulty configuration
# ---------------------------------------------------------------------------

DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {

    # --- DIRECT INFERENCE ---
    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2), num_premises_range=(2, 2), max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=lambda n: 1,
    ),
    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3), num_premises_range=(2, 2), max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=lambda n: max(1, min(2, n)),
    ),
    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4), num_premises_range=(2, 2), max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 0.5, "or": 1.0, "imp": 1.0, "xor": 1.0, "equiv": 1.0},
        closure_threshold_func=lambda n: max(2, n - 1),
    ),
    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4), num_premises_range=(3, 3), max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "and": 0.5, "or": 1.0, "imp": 1.0, "xor": 0.5, "equiv": 0.5},
        closure_threshold_func=lambda n: n,
    ),

    # --- CASE SPLIT (Fallunterscheidung) ---
    # Anforderungen: Mehr Variablen/Prämissen, keine direkte Lösung, Fallunterscheidung nötig
    (TaskType.CASE_SPLIT, 1): DifficultySpec(
        num_vars_range=(3, 3), # Klein anfangen
        num_premises_range=(3, 3), # Etwas mehr Prämissen nötig für Widersprüche
        max_depth=2,
        allowed_ops=["not", "or", "imp", "xor"], # And reduzieren, da es oft direkt auflöst
        op_weights={"not": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "and": 1.0, "equiv": 1.0},
        closure_threshold_func=None, 
    ),
    (TaskType.CASE_SPLIT, 2): DifficultySpec(
        num_vars_range=(3, 4),
        num_premises_range=(3, 5),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "or": 1.2, "imp": 1.2, "xor": 1.0, "and": 0.5, "equiv": 0.8},
        closure_threshold_func=None,
    ),
    (TaskType.CASE_SPLIT, 3): DifficultySpec(
        num_vars_range=(5, 5),
        num_premises_range=(6, 6),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
        op_weights={"not": 1.0, "or": 1.0, "imp": 1.0, "xor": 1.0, "and": 0.5, "equiv": 1.0},
        closure_threshold_func=None,
    ),
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _default_op_weights(allowed_ops: Sequence[str]) -> Dict[str, float]:
    base_scores = {"and": 3.0, "imp": 3.0, "not": 2.0, "or": 1.0, "xor": 0.7, "equiv": 0.6}
    return {op: float(base_scores.get(op, 1.0)) for op in allowed_ops}


def random_formula(vars, max_depth: int, allowed_ops: Sequence[str], op_weights: Dict[str, float]) -> Boolean:
    if max_depth == 0:
        v = random.choice(vars)
        return v if random.random() < 0.5 else Not(v)

    if not op_weights:
        weights_map = _default_op_weights(allowed_ops)
    else:
        weights_map = {op: float(op_weights.get(op, 1.0)) for op in allowed_ops}

    ops = list(allowed_ops)
    weights = [weights_map.get(op, 1.0) for op in ops]

    # Defensive check
    if all((w == 0 or math.isnan(w)) for w in weights): weights = [1.0] * len(weights)

    op = random.choices(ops, weights=weights, k=1)[0]

    if op == "not": return Not(random_formula(vars, max_depth - 1, allowed_ops, op_weights))

    left = random_formula(vars, max_depth - 1, allowed_ops, op_weights)
    right = random_formula(vars, max_depth - 1, allowed_ops, op_weights)

    if op == "and": return And(left, right)
    if op == "or": return Or(left, right)
    if op == "imp": return Implies(left, right)
    if op == "xor": return Xor(left, right)
    if op == "equiv": return Equivalent(left, right)
    return left


def all_models(premises: List[Boolean], vars) -> List[Dict]:
    models = []
    n = len(vars)
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        ok = True
        for prem in premises:
            if not bool(prem.subs(valuation)):
                ok = False
                break
        if ok: models.append(valuation)
    return models


def entails(premises: List[Boolean], formula: Boolean, vars) -> bool:
    # Prüft Γ ⊨ φ (per Brute Force über alle Belegungen)
    n = len(vars)
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        if all(bool(p.subs(valuation)) for p in premises):
            if not bool(formula.subs(valuation)):
                return False
    return True


def print_logical_pretty(expr) -> str:
    if isinstance(expr, Symbol): return str(expr)
    if isinstance(expr, Not): return f"¬{wrap_if_needed(expr.args[0])}"
    if isinstance(expr, And): return " ∧ ".join([wrap_if_needed(a) for a in expr.args])
    if isinstance(expr, Or): return " ∨ ".join([wrap_if_needed(a) for a in expr.args])
    if isinstance(expr, Implies):
        args = list(expr.args)
        return f"{wrap_if_needed(args[0])} → {wrap_if_needed(args[1])}" if len(args) == 2 else " → ".join([wrap_if_needed(a) for a in args])
    if isinstance(expr, Equivalent): return " ↔ ".join([wrap_if_needed(a) for a in expr.args])
    if isinstance(expr, Xor): return " ⊕ ".join([wrap_if_needed(a) for a in expr.args])
    return str(expr)

def wrap_if_needed(expr):
    if isinstance(expr, (Symbol, Not)): return print_logical_pretty(expr)
    return f"({print_logical_pretty(expr)})"


def _premises_connectivity_summary(premises: List[Boolean], used_vars) -> Tuple[bool, bool, bool]:
    n = len(premises)
    if n <= 1: return True, False, False

    adj = {i: set() for i in range(n)}
    any_entail = False
    direct_entail = False
    sym_sets: List[Set] = [set(p.free_symbols) for p in premises]

    for i in range(n):
        for j in range(i + 1, n):
            # Syntaktisch
            if sym_sets[i] & sym_sets[j]:
                adj[i].add(j); adj[j].add(i)
                any_entail = True
                continue
            # Semantisch
            try:
                if entails([premises[i]], premises[j], used_vars):
                    adj[i].add(j); adj[j].add(i)
                    any_entail = True; direct_entail = True; continue
            except: pass
            try:
                if entails([premises[j]], premises[i], used_vars):
                    adj[i].add(j); adj[j].add(i)
                    any_entail = True; direct_entail = True; continue
            except: pass

    any_edge = any(len(neis) > 0 for neis in adj.values())
    
    # BFS Zusammenhang
    visited = set([0]); queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in visited: visited.add(v); queue.append(v)

    return (len(visited) == n), direct_entail, any_edge


def deductive_literal_closure(premises: List[Boolean], vars_seq: Sequence[Symbol]) -> Dict[Symbol, bool]:
    known: Dict[Symbol, bool] = {}
    def known_as_formulas() -> List[Boolean]:
        return [s if val else Not(s) for s, val in known.items()]

    changed = True
    while changed:
        changed = False
        for v in vars_seq:
            if v in known: continue
            current_premises = list(premises) + known_as_formulas()
            if entails(current_premises, v, list(vars_seq)):
                known[v] = True; changed = True; continue
            if entails(current_premises, Not(v), list(vars_seq)):
                known[v] = False; changed = True; continue
    return known


# ---------------------------------------------------------------------------
# Gütebedingung 1: DIRECT_INFERENCE (bekannt)
# ---------------------------------------------------------------------------

def is_good_task_type_3_1(premises: List[Boolean], vars, level, spec: DifficultySpec) -> bool:
    # 1-3) Basischecks
    for prem in premises:
        if len(prem.free_symbols) == 0: return False
    
    all_syms = set()
    for prem in premises: all_syms |= prem.free_symbols
    used_vars = [v for v in vars if v in all_syms]
    
    if len(used_vars) != len(vars): return False
    if not any(len(p.free_symbols) >= 2 for p in premises): return False

    # 4) Modelle
    models = all_models(premises, used_vars)
    if not models or len(models) == 2 ** len(used_vars): return False
    
    # 5) Stabile Literale Check
    stable_literals_found = False
    for v in used_vars:
        vals = [m[v] for m in models]
        if all(vals) or not any(vals):
            stable_literals_found = True; break
    if not stable_literals_found: return False

    # 6) Deduktive Closure Check
    used_vars_seq = used_vars[:]
    closure = deductive_literal_closure(premises, used_vars_seq)
    
    # Threshold nutzen (falls definiert, sonst Standard)
    threshold = spec.closure_threshold_func(len(used_vars_seq)) if spec.closure_threshold_func else 1
    if len(closure) < threshold: return False
    
    # 6b) Redundanz-Check (Closure-basiert)
    current_knowledge_count = len(closure)
    for i in range(len(premises)):
        subset_premises = premises[:i] + premises[i+1:]
        subset_closure = deductive_literal_closure(subset_premises, used_vars_seq)
        if len(subset_closure) >= current_knowledge_count: return False

    # 7) Struktur
    is_connected, direct_entail, any_edge = _premises_connectivity_summary(premises, used_vars)
    if not is_connected or not any_edge: return False

    if not direct_entail:
        informative = False
        for Pi in premises:
            for v in used_vars:
                if entails([Pi], v, used_vars) or entails([Pi], Not(v), used_vars):
                    informative = True; break
            if informative: break
        if not informative: return False

    return True


# ---------------------------------------------------------------------------
# NEU: Gütebedingung 2: CASE_SPLIT
# ---------------------------------------------------------------------------

def is_good_task_type_case_split(premises: List[Boolean], vars, level) -> bool:
    """
    Prüft, ob Prämissen eine geeignete CASE_SPLIT-Aufgabe bilden.
    Anforderungen:
      1. Eindeutige Lösung (1 Modell).
      2. Initial KEINE (oder fast keine) direkten Schlüsse möglich (Closure ~ 0).
      3. Durch Annahme (Fallunterscheidung) wird die Aufgabe lösbar.
      4. Keine Redundanz (jede Prämisse wird benötigt, um die Eindeutigkeit zu sichern).
    """
    # 1) Basischecks (Konstanten, Variablenverwendung)
    for prem in premises:
        if len(prem.free_symbols) == 0: 
            return False
    
    all_syms = set()
    for prem in premises: all_syms |= prem.free_symbols
    used_vars = [v for v in vars if v in all_syms]
    
    # Alle Variablen müssen verwendet werden
    if len(used_vars) != len(vars): 
        return False
    used_vars_seq = used_vars[:]

    # 2) Eindeutige Lösung (Requirement 2)
    models = all_models(premises, used_vars)
    if len(models) != 1: 
        return False # Muss genau 1 Lösung haben

    # 3) Keine direkten logischen Schlüsse (Requirement 1)
    # Die initiale Closure muss leer sein (oder sehr klein, z.B. 0).
    # Das bedeutet: Ohne Annahme weiß man nichts.
    initial_closure = deductive_literal_closure(premises, used_vars_seq)
    if len(initial_closure) > 0: 
        return False # Zu einfach! Man kann direkt etwas ableiten.

    # 4) Lösbarkeit durch Fallunterscheidung prüfen (Simulation)
    # Prüfen, ob es mind. EINE Variable gibt, bei der eine Annahme zu einer Lösung
    # oder einem Widerspruch führt.
    split_useful = False
    
    for v in used_vars:
        # Versuch 1: Angenommen v ist Wahr
        # Wir fügen 'v' temporär zu den Prämissen hinzu
        assumed_true_premises = premises + [v]
        closure_true = deductive_literal_closure(assumed_true_premises, used_vars_seq)
        
        # Versuch 1: Angenommen v ist Wahr
        models_true = all_models(premises + [v], used_vars)
        
        # Versuch 2: Angenommen v ist Falsch
        models_false = all_models(premises + [Not(v)], used_vars)
        
        # Eine Fallunterscheidung ist dann gut, wenn einer der Fälle 
        # zu einem Widerspruch führt (0 Modelle) und der andere zur Lösung (1 Modell).
        if (len(models_true) == 0 and len(models_false) == 1) or \
           (len(models_true) == 1 and len(models_false) == 0):
            split_useful = True
            break
            
    if not split_useful:
        return False # Keine Variable gefunden, die einen klaren Split ermöglicht

    # 5) Redundanz-Check (Requirement 4)
    # Bei eindeutigen Aufgaben ist eine Prämisse redundant, wenn man sie weglassen kann
    # und die Lösung EINDEUTIG bleibt.
    # (Wenn ich eine Prämisse entferne und es gibt plötzlich 2 Modelle, war sie wichtig).
    for i in range(len(premises)):
        subset_premises = premises[:i] + premises[i+1:]
        subset_models = all_models(subset_premises, used_vars)
        
        # Wenn das Subset immer noch genau 1 Lösung hat, war die Prämisse unnötig -> Redundant
        if len(subset_models) == 1:
            return False

    # 6) Struktur (Requirement 3)
    is_connected, _, any_edge = _premises_connectivity_summary(premises, used_vars)
    if not is_connected or not any_edge:
        return False

    return True


# ---------------------------------------------------------------------------
# Generator-Klasse
# ---------------------------------------------------------------------------

class TaskGenerator:
    def __init__(self, config: Dict[Tuple[TaskType, int], DifficultySpec]):
        self.config = config

    def generate_task(self, task_type: TaskType, level: int) -> Task:
        # Config laden
        if (task_type, level) not in self.config:
             raise ValueError(f"Konfiguration für {task_type} Level {level} nicht gefunden.")
        
        spec = self.config[(task_type, level)]

        # Variablen erzeugen (Generisch für alle Typen)
        num_vars = random.randint(*spec.num_vars_range)
        var_names = ["A", "B", "C", "D", "E", "F", "G", "H"][:num_vars]
        vars_tuple = symbols(" ".join(var_names))
        vars = (vars_tuple,) if num_vars == 1 else vars_tuple

        # Loop
        for attempt in range(5000):
            num_premises = random.randint(*spec.num_premises_range)
            premises = [
                random_formula(vars, spec.max_depth, spec.allowed_ops, spec.op_weights)
                for _ in range(num_premises)
            ]

            # --- VERZWEIGUNG NACH AUFGABENTYP ---
            if task_type == TaskType.DIRECT_INFERENCE:
                # Nutze die bestehende Logik für Typ 1
                if is_good_task_type_3_1(premises, list(vars), level, spec):
                    return Task(task_type, level, premises, list(vars))
            
            elif task_type == TaskType.CASE_SPLIT:
                # Nutze die NEUE Logik für Typ 2
                if is_good_task_type_case_split(premises, list(vars), level):
                    return Task(task_type, level, premises, list(vars))

        raise RuntimeError(f"Keine Aufgabe für {task_type.name} Level {level} gefunden.")


# ---------------------------------------------------------------------------
# Main Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    generator = TaskGenerator(DIFFICULTY_CONFIG)

    try:
        print("--- Generiere CASE_SPLIT (Level 1) ---")
        # Hinweis: Case Split dauert evtl. länger zu generieren, da die Bedingungen sehr spezifisch sind (0 Closure aber 1 Modell)
        task_cs = generator.generate_task(TaskType.CASE_SPLIT, 3)
        
        print(f"Typ {task_cs.task_type} – Level {task_cs.level}")
        print("Variablen:", task_cs.variables)
        print("Prämissen:")
        for i, p in enumerate(task_cs.premises, 1):
            print(f"(P{i}) {print_logical_pretty(p)}")

        # Check
        used_vars = [v for v in task_cs.variables if v in set().union(*[p.free_symbols for p in task_cs.premises])]
        
        # 1. Closure Check (sollte leer sein)
        closure = deductive_literal_closure(task_cs.premises, used_vars)
        print(f"\nInitiale Closure (ohne Annahme): {closure} (Sollte leer sein)")
        
        # 2. Modell Check (Sollte genau 1 sein)
        sols = all_models(task_cs.premises, used_vars)
        print(f"Anzahl Modelle: {len(sols)}")
        print("Lösung:", sols[0] if sols else "Keine")

    except RuntimeError as e:
        print(e)