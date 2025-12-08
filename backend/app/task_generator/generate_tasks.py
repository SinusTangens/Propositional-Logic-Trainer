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


DIFFICULTY_CONFIG: Dict[Tuple[TaskType, int], DifficultySpec] = {
   
    # Typ DIRECT_INFERENCE – Level 1: 1 Prämisse, wenige Variablen, einfache Form
    (TaskType.DIRECT_INFERENCE, 1): DifficultySpec(
        num_vars_range=(2, 2),
        num_premises_range=(2, 2),
        max_depth=1,
        allowed_ops=["not", "or", "imp", "xor", "equiv"],   #"and"
    ),
    # Typ DIRECT_INFERENCE – Level 2: Mehr Prämissen, mehr Variablen
    (TaskType.DIRECT_INFERENCE, 2): DifficultySpec(
        num_vars_range=(3, 3),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
    ),
    # Typ DIRECT_INFERENCE – Level 3: Mehr Prämissen, mehr Variablen
    (TaskType.DIRECT_INFERENCE, 3): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=2,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
    ),
    # Typ 3.1 – Level 4: Mehr Verschachtelung
    (TaskType.DIRECT_INFERENCE, 4): DifficultySpec(
        num_vars_range=(4, 4),
        num_premises_range=(2, 2),
        max_depth=3,
        allowed_ops=["not", "and", "or", "imp", "xor", "equiv"],
    ),
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen: Formeln & Semantik
#   -> eigene Wahrheitstabellen-Enumeration (brute force) über die gewählten Variablen
# ---------------------------------------------------------------------------

def random_formula(vars, max_depth: int, allowed_ops: Sequence[str]) -> Boolean:
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

    op = random.choice(allowed_ops)

    if op == "not":
        return Not(random_formula(vars, max_depth - 1, allowed_ops))

    left = random_formula(vars, max_depth - 1, allowed_ops)
    right = random_formula(vars, max_depth - 1, allowed_ops)

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

def is_good_task_type_3_1(premises: List[Boolean], vars) -> bool:
    """
    Typ 3.1: Direkte logische Schlüsse ohne Vorannahmen.

    Bedingungen:
    - Keine konstante Prämisse (True/False).
    - Alle gewählten Variablen kommen in den Prämissen vor.
    - Wenn es nur eine Prämisse gibt, enthält sie >= 2 verschiedene Variablen.
    - Wenn es mehr als eine Prämisse gibt, enthält mindestens eine Prämisse
      >= 2 verschiedene Variablen (sonst zu trivial wie ~A, ~(B & ~B)).
    - Prämissen sind erfüllbar, aber nicht trivial (nicht alle Belegungen).
    - Es existiert mindestens ein stabiles Literal (Variable oder Negation),
      das in allen Modellen denselben Wahrheitswert hat (direkte Konsequenz).
    - Wenn es mehr als eine Prämisse gibt, existiert ein Paar (Pi, Pj)
      mit Pi ⊨ Pj (Schritt-für-Schritt-Schließen).
    """
    # 1) Konstante Prämissen ausschließen (z.B. True, False)
    for prem in premises:
        if len(prem.free_symbols) == 0:
            return False

    # 2) Tatsächlich verwendete Variablen bestimmen
    all_syms = set()
    for prem in premises:
        all_syms |= prem.free_symbols

    used_vars = [v for v in vars if v in all_syms]

    if not used_vars:
        return False

    # Alle gewählten Variablen sollen verwendet werden (wenn [A,B,C], dann soll auch jede Var. mindestens ein Mal vorkommen)
    if len(used_vars) != len(vars):
        return False

    # 3) Aufgaben mit nur einer Prämisse dürfen nicht weniger als zwei Variablen enthalten (Lösung sonst trivial)
    if len(premises) == 1:
        if len(premises[0].free_symbols) < 2:
            return False

    # 4) Wenn es mehr als eine Prämisse gibt, muss mindestens eine
    # Prämisse zwei oder mehr unterschiedliche Variablen enthalten.
    if len(premises) > 1:
        if not any(len(p.free_symbols) >= 2 for p in premises):
            return False

    # 5) Modelle der Prämissen berechnen (d.h. prüfen welche Variablenbelegungen die Prämisse(n) erfüllen)
    models = all_models(premises, used_vars)
    if not models:              # Prämissen müssen erfüllbar sein, sonst Fehler
        return False

    # Trivial, wenn alle 2^n Belegungen Modelle sind
    if len(models) == 2 ** len(used_vars):
        return False

    # 6) Direkte Konsequenzen über stabile Literale (nur über verwendete Variablen)
    stable_literals = []
    for v in used_vars:
        vals = [m[v] for m in models]
        if all(vals):
            stable_literals.append(v)        # v immer wahr
        elif not any(vals):
            stable_literals.append(Not(v))   # v immer falsch

    if not stable_literals:
        return False  # keine direkten Schlüsse möglich

    # 7) Schritt-für-Schritt-Beziehung zwischen Prämissen:
    # Prmämissen müssen zusammenhängend sein. D.h. eine Prämisse muss logisch auf eine andere folgen.             
    #  Mindestens ein Paar (Pi, Pj) mit Pi ⊨ Pj 
    if len(premises) > 1:
        chain_exists = False
        for i in range(len(premises)):
            for j in range(len(premises)):
                if i == j:
                    continue
                if entails([premises[i]], premises[j], used_vars):
                    chain_exists = True
                    break
            if chain_exists:
                break
        if not chain_exists:
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
                random_formula(vars, spec.max_depth, spec.allowed_ops)
                for _ in range(num_premises)
            ]

            if is_good_task_type_3_1(premises, vars):
                return Task(
                    task_type=task_type,
                    level=level,
                    premises=premises,
                    variables=list(vars),
                )

        raise RuntimeError("Keine passende Aufgabe gefunden; Parameter ggf. anpassen.")


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