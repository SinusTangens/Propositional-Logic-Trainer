import random
import math

from typing import List, Tuple, Sequence, Dict, Optional, Set, Any

from itertools import product
from collections import deque

from Task import Task, TaskType, DifficultySpec, DIFFICULTY_CONFIG

from sympy import symbols, Symbol
from sympy.logic.boolalg import (
    Boolean,
    And,
    Or,
    Not,
    Implies,
    Xor,
    Equivalent,
    to_cnf
)





def random_formula(vars, max_depth: int, allowed_ops: Sequence[str], op_weights: Dict[str, float]) -> Boolean:
    """
    Erzeugt rekursiv eine zufällige SymPy-Formel über 'vars',
    unter Verwendung der erlaubten Operatoren und der übergebenen Gewichte.
    """

    if max_depth == 0:
        v = random.choice(vars)
        return v if random.random() < 0.5 else Not(v)

    # Sichere Extraktion der Gewichte
    weights_map = {op: float(op_weights.get(op, 1.0)) for op in allowed_ops}    #Hier noch Exception falls eine Gewichte und nicht Gewichte für jeden OP
    ops = list(allowed_ops)
    weights = [weights_map.get(op, 1.0) for op in ops]

    # Defensive: falls alle Gewichte ungültig sind
    if all((w == 0 or math.isnan(w)) for w in weights):
        weights = [1.0] * len(weights)

    op = random.choices(ops, weights=weights, k=1)[0]
    
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

    # Fallback
    return left




def all_models(premises: List[Boolean], vars) -> List[Dict]:
    """
    Liefert alle Modelle (Lösungen) der Konjunktion aller Prämissen einer Aufgabe (=bestimmt die Lösung(en) der Aufgabe)
    """
    models = []
    n = len(vars)

    # Iteriert über alle 2^n möglichen Wahrheitsbelegungen
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        ok = True

        # Prüft, ob alle Prämissen unter dieser Belegung wahr sind
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
    [Grundlegender Ableitungsbeweis]
    Prüft, ob die 'formula' zwingend aus der Menge der 'premises' folgt (Γ ⊨ φ).
    
    Verarbeitung: Iteriert über alle 2^n Belegungen. Sucht nach einem 
    Gegenbeispiel (Modell, das Γ erfüllt, aber φ nicht).
    
    Abgrenzung: Atomarer Wahrheitsbeweis (True/False). Dient als Baustein für 
    die komplexe iterative Ableitung in 'deductive_literal_closure' und 
    den semantischen Kanten-Check.
    """
    n = len(vars)
    # Suche nach einem Gegenbeispiel
    for bits in product([False, True], repeat=n):
        valuation = {vars[i]: bits[i] for i in range(n)}
        
        # 1. Prüfe, ob alle Prämissen wahr sind (Γ erfüllt)
        if all(bool(p.subs(valuation)) for p in premises):
            
            # 2. Prüfe, ob die Folgerung φ falsch ist (Gegenbeispiel)
            if not bool(formula.subs(valuation)):
                return False  # Gegenbeispiel gefunden
    return True  # Kein Gegenbeispiel gefunden, also folgt φ zwingend





def print_logical_pretty(expr) -> str:
    """
    Wandelt Sympy Syntax für Aussagenlogik in die standardmäßige, besser lesbare Darstellung um          
    """
    if isinstance(expr, Symbol):
        return str(expr)

    if isinstance(expr, Not):
        sub = expr.args[0]
        return f"¬{wrap_if_needed(sub)}"

    if isinstance(expr, And):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∧ ".join(parts)

    if isinstance(expr, Or):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ∨ ".join(parts)

    if isinstance(expr, Implies):
        args = list(expr.args)
        if len(args) == 2:
            left, right = args
            return f"{wrap_if_needed(left)} → {wrap_if_needed(right)}"
        else:
            parts = [wrap_if_needed(a) for a in args]
            return " → ".join(parts)

    if isinstance(expr, Equivalent):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ↔ ".join(parts)

    if isinstance(expr, Xor):
        parts = [wrap_if_needed(a) for a in expr.args]
        return " ⊕ ".join(parts)

    return str(expr)


def wrap_if_needed(expr):
    """
    Hilfsfunktion für Klammersetzung bei 'print_logical_pretty'
    """
    if isinstance(expr, (Symbol, Not)):
        return print_logical_pretty(expr)
    return f"({print_logical_pretty(expr)})"





def _premises_connectivity_summary(premises: List[Boolean], used_vars) -> Tuple[bool, bool, bool]:
    """
    [Strukturelle Analyse]
    Baut einen Graphen über die Prämissen (Knoten) und analysiert deren Beziehungen.
    Eine Kante Pi -> Pj existiert bei: 
    a) Syntaktischer Überlappung (gemeinsame Variablen), ODER
    b) Semantischer Verbindung (Pi ⊨ Pj oder Pj ⊨ Pi, mithilfe von 'entails').

    Ausgabe: (is_connected, any_direct_entail, any_edge).

    Abgrenzung: Prüft die innere Struktur des Problems, nicht die Lösung.
    """
    n = len(premises)
    if n <= 1:
        return True, False, False

    adj = {i: set() for i in range(n)}
    #any_entail = False    # Ist irgendeine Kante vorhanden (syntaktisch oder semantisch)?
    direct_entail = False # Ist eine Kante durch semantische Folgerung (Pi ⊨ Pj) entstanden?

    sym_sets: List[Set] = [set(p.free_symbols) for p in premises]

    # Finde Kanten zwischen allen Prämissenpaaren
    for i in range(n):
        for j in range(i + 1, n):
            # 1. Syntaktischer Overlap
            if sym_sets[i] & sym_sets[j]:
                adj[i].add(j)
                adj[j].add(i)
                #any_entail = True
                continue

            # 2. Semantische Verbindung (teuer, da es entails aufruft)
            if entails([premises[i]], premises[j], used_vars):
                adj[i].add(j)
                adj[j].add(i)
                #any_entail = True
                direct_entail = True
                continue

            if entails([premises[j]], premises[i], used_vars):
                adj[i].add(j)
                adj[j].add(i)
                #any_entail = True
                direct_entail = True
                continue

    any_edge = any(len(neis) > 0 for neis in adj.values())
    
    # 3. Zusammenhangsprüfung (BFS/Breitensuche)
    visited = set()
    # Beginne die Suche bei der ersten Prämisse
    queue = deque([0])
    visited.add(0)
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)

    is_connected = (len(visited) == n)
    # is_connected: Stellt sicher, dass das Problem nicht zerfällt (muss True sein).
    # direct_entail: Zeigt Redundanz/einfache Ableitung (muss nicht zwingend True sein).
    # any_edge: Stellt sicher, dass es überhaupt eine Beziehung gibt (muss True sein).
    return is_connected, direct_entail, any_edge




# def deductive_literal_closure(premises: List[Boolean], vars_seq: Sequence[Symbol]) -> Dict[Symbol, bool]:
#     """
#     [Iterative Ableitung]
#     Findet den Fixpunkt aller Literale (v oder ¬v), die durch einfache Kettenableitung 
#     (Modus Ponens, Modus Tollens, etc.) aus den Prämissen folgen. 
#     Dabei werden bereits abgeleitete Literale als zusätzliche Prämissen verwendet.

#     Verarbeitung: Nutzt 'entails' in einer Schleife, um mehrstufige Schlüsse zu finden.
#     Ausgabe: Mapping Symbol -> Wahrheitswert (nur für gefundene Literale).
#     """
#     known: Dict[Symbol, bool] = {}

#     def known_as_formulas() -> List[Boolean]:
#         # Hilfsfunktion zur Umwandlung des aktuellen Wissens in SymPy-Formeln
#         return [s if val else Not(s) for s, val in known.items()]

#     changed = True
#     while changed:
#         changed = False
#         for v in vars_seq:
#             if v in known:
#                 continue
            
#             # Die aktuelle Prämissenmenge besteht aus Originalprämissen + dem aktuellen Wissen
#             current_premises = list(premises) + known_as_formulas()
            
#             # Prüfe, ob v folgt (Γ + known ⊨ v)
#             if entails(current_premises, v, list(vars_seq)):
#                 known[v] = True
#                 changed = True
#                 continue

#             # Prüfe, ob ¬v folgt (Γ + known ⊨ ¬v)
#             if entails(current_premises, Not(v), list(vars_seq)):
#                 known[v] = False
#                 changed = True
#                 continue

#     return known


def deductive_literal_closure(premises: List[Boolean], vars_seq: Sequence[Symbol]) -> Dict[Symbol, bool]:
    """
    Simuliert 'direktes' logisches Schließen mittels Unit Propagation.
    Findet nur Variablen, die durch direkte Kettenreaktion (ohne Vorannahmen/Fallunterscheidungen) bestimmt werden können.
    """

    # Jede Prämisse in die Konjungitve Normalform bringen
    cnf_clauses = []
    for p in premises:
        cnf = to_cnf(p, simplify=True)
        if isinstance(cnf, And):
            cnf_clauses.extend(cnf.args)
        else:
            cnf_clauses.append(cnf)

    known: Dict[Symbol, bool] = {}
    

    changed = True
    while changed:
        changed = False
        new_clauses = []
        
        for clause in cnf_clauses:
            # Wir bereinigen die Klausel basierend auf dem, was wir schon wissen
            
            # Zerlege Klausel in Literale (Disjunktion)
            lits = list(clause.args) if isinstance(clause, Or) else [clause]
            
            # Filtere Literale
            active_lits = []
            clause_satisfied = False
            
            for lit in lits:
                # Literal analysieren (Symbol oder Not(Symbol))
                if isinstance(lit, Not):
                    sym, is_neg = lit.args[0], True
                else:
                    sym, is_neg = lit, False
                
                # Wenn wir das Symbol schon kennen:
                if sym in known:
                    val = known[sym]
                    # Wenn Literal wahr ist (z.B. A ist True und wir haben A): Klausel erledigt
                    if (val and not is_neg) or (not val and is_neg):
                        clause_satisfied = True
                        break
                    # Wenn Literal falsch ist (z.B. A ist False und wir haben A): Literal fällt weg
                    # (Wir fügen es nicht zu active_lits hinzu)
                else:
                    active_lits.append(lit)
            
            if clause_satisfied:
                continue
                
            # --- UNIT PROPAGATION ---
            # Wenn nur noch 1 Literal übrig ist, MUSS dieses wahr sein
            if len(active_lits) == 0:
                # Widerspruch (leere Klausel) - sollte bei validen Aufgaben nicht passieren,
                # aber wir brechen hier ab, da wir nur "sicheres Wissen" wollen.
                return known 
                
            if len(active_lits) == 1:
                # Bingo! Wir haben eine neue direkte Folgerung
                unit = active_lits[0]
                if isinstance(unit, Not):
                    s, v = unit.args[0], False
                else:
                    s, v = unit, True
                
                if s not in known:
                    known[s] = v
                    changed = True
            else:
                # Klausel ist noch nicht gelöst, kommt in die nächste Runde
                # Rekonstruiere Or für den nächsten Durchlauf
                new_clauses.append(Or(*active_lits))
        
        cnf_clauses = new_clauses

    return known


def is_good_task_type_direct_inference(premises: List[Boolean], vars) -> bool:
    """
    Prüft, ob alle Prämissen ganzheitlich eine geeignete DIRECT_INFERENCE-Aufgabe bilden, indem 
    verschiedene logische und strukturelle Checks durchgeführt werden.
    """


    # Keine konstanten Prämissen
    for prem in premises:
        if len(prem.free_symbols) == 0:
            return False

    # Jede Variable muss in mindestens einer der Prämissen vorkommen
    all_syms = set()
    for prem in premises:
        all_syms |= prem.free_symbols

    used_vars = [v for v in vars if v in all_syms]
    
    if len(used_vars) != len(vars):
        return False
    used_vars_seq = used_vars[:]  

    # Mindestens eine Prämisse muss 2 Variablen  oder mehr enthalten (vor Allem relevant für Level 1)
    if not any(len(p.free_symbols) >= 2 for p in premises):
        return False

    # Eine Aufgabe soll keine widersprüchlichen Prämissen enthalten (=muss lösbar sein) 
    models = all_models(premises, used_vars)
    
    if len(models) == 0:
        return False

    # # 5) Stabile Literale (mindestens eine Variable muss in allen Modellen den gleichen Wert haben)
    # # Redundanter, aber schneller Vor-Check
    # stable_literals_found = False
    # for v in used_vars:
    #     vals = [m[v] for m in models]
    #     if all(vals) or not any(vals):
    #         stable_literals_found = True
    #         break
    # if not stable_literals_found:
    #     return False

    # # 6) Deduktive Closure prüfen (Kettenableitungen ohne Annahmen)
    # closure = deductive_literal_closure(premises, used_vars_seq)
    
    # # NEU: Threshold aus der Konfiguration laden
    # threshold = spec.closure_threshold_func(len(used_vars_seq))
    
    # # Check 6a: Wurde der Level-spezifische Threshold erreicht?
    # if len(closure) < threshold:
    #     return False


    # Es soll maximal eine Variable existieren, die mittels schrittweise logischem Schließen nicht eindeutig bestimmbar ist
    closure = deductive_literal_closure(premises, used_vars_seq)
    if len(closure) < (len(used_vars) -1):
        return False


    # Eine Aufgabe soll keine redundanten Prämissen enthalten
    # Wenn die Anzahl der möglichen Lösungen beim Entfernen einer Prämisse gleich bleibt, war diese redundant

    for i in range(len(premises)):

        subset_premises = premises[:i] + premises[i+1:]
        subset_models = all_models(subset_premises, used_vars)

        if len(subset_models) == len(models):
            return False
        


    # Alle Prämissen sollen eine zusammenhängende Aufgabe bilden und nicht unabhängig voneinander existieren
    is_connected, direct_entail, any_edge = _premises_connectivity_summary(premises, used_vars)
    if not is_connected or not any_edge:
        return False
    
    # # 7b: Wenn keine direkte semantische Ableitung (Pi ⊨ Pj) gefunden wurde:
    # # Stelle sicher, dass zumindest eine Prämisse allein informativ ist (Startpunkt).
    # if not direct_entail:
    #     informative = False
    #     for Pi in premises:
    #         # Prüfe, ob Pi alleine ein Literal ableitet
    #         for v in used_vars:
    #             if entails([Pi], v, used_vars) or entails([Pi], Not(v), used_vars):
    #                 informative = True
    #                 break
    #         if informative:
    #             break
    #     if not informative:
    #         # Die Aufgabe ist zu vage/schwer zu starten, wenn keine direkte Folgerung
    #         # und keine Prämisse allein informativ ist.
    #         return False




    return True



def is_good_task_type_case_split(premises: List[Boolean], vars) -> bool:
    """
    Prüft, ob alle Prämissen ganzheitlich eine geeignete CASE_SPLIT-Aufgabe bilden, indem 
    verschiedene logische und strukturelle Checks durchgeführt werden.
    """


    # Keine konstanten Prämissen
    for prem in premises:
        if len(prem.free_symbols) == 0: 
            return False
    
    # Jede Variable muss in mindestens einer der Prämissen vorkommen
    all_syms = set()
    for prem in premises: 
        all_syms |= prem.free_symbols

    used_vars = [v for v in vars if v in all_syms]
    
    if len(used_vars) != len(vars): 
        return False
    used_vars_seq = used_vars[:]

    
    # Die Aufgabe muss genau eine eindeutige Lösung besitzen
    models = all_models(premises, used_vars)
    if len(models) != 1: 
        return False 

    # Keine Variablenbelegung soll ohne eine initale Fallunterscheidung bestimmbar sein
    initial_closure = deductive_literal_closure(premises, used_vars_seq)
    if len(initial_closure) > 0: 
        return False 


    # Lösbarkeit durch eine simulierte Fallunterscheidung prüfen
    # Es muss mindestens EINE Variable exisitieren, bei der eine Annahme zu einer Lösung und die gegenteilige Annahme zu einem Widerspruch führt
    split_useful = False
    
    for v in used_vars:
        
        # Angenommen v ist Wahr
        models_true = all_models(premises + [v], used_vars)
        
        # Angenommen v ist Falsch
        models_false = all_models(premises + [Not(v)], used_vars)
        

        if (len(models_true) == 0 and len(models_false) == 1) or \
           (len(models_true) == 1 and len(models_false) == 0):
            split_useful = True
            break
            
    if not split_useful:
        return False 


    # Eine Aufgabe soll keine redundanten Prämissen enthalten
    # Wenn die Anzahl der möglichen Lösungen beim Entfernen einer Prämisse gleich bleibt, war diese redundant
    for i in range(len(premises)):
        subset_premises = premises[:i] + premises[i+1:]
        subset_models = all_models(subset_premises, used_vars)
        
        if len(subset_models) == len(models):
            return False


    # Alle Prämissen sollen eine zusammenhängende Aufgabe bilden und nicht unabhängig voneinander existieren
    is_connected, _, any_edge = _premises_connectivity_summary(premises, used_vars)
    if not is_connected or not any_edge:
        return False


    return True




class TaskGenerator:

    def __init__(self, config: Dict[Tuple[TaskType, int], DifficultySpec]):
        self.config = config

    def generate_task(self, task_type: TaskType, level: int) -> Task:

        if (task_type, level) not in self.config:
             raise ValueError(f"Konfiguration für {task_type} Level {level} nicht gefunden.")

        spec = self.config[(task_type, level)]

        # Variablen erzeugen
        num_vars = random.randint(*spec.num_vars_range)
        var_names = ["A", "B", "C", "D", "E", "F", "G", "H"][:num_vars]
        vars_tuple = symbols(" ".join(var_names))
        vars = (vars_tuple,) if num_vars == 1 else vars_tuple   # SymPy gibt bei nur 1 Variable kein Tupel zurück

        # Erzeugungsloop, bis passende Aufgabe gefunden wurde
        # Anzahl an Iterationen frei gewählt
        for attempt in range(5000):
            num_premises = random.randint(*spec.num_premises_range)
            premises = [
                random_formula(vars, spec.max_depth, spec.allowed_ops, spec.op_weights)
                for _ in range(num_premises)
            ]

            if task_type == TaskType.DIRECT_INFERENCE:
                if is_good_task_type_direct_inference(premises, list(vars)):
                    return Task(
                        task_type=task_type,
                        level=level,
                        premises=premises,
                        variables=list(vars)
                    )

            if task_type == TaskType.CASE_SPLIT:
                if is_good_task_type_case_split(premises, list(vars)):
                    return Task(
                        task_type=task_type,
                        level=level,
                        premises=premises,
                        variables=list(vars)    
                    )
        raise RuntimeError(f"Keine Aufgabe für {task_type.name} Level {level} gefunden.")




if __name__ == "__main__":

    generator = TaskGenerator(DIFFICULTY_CONFIG)

    task = generator.generate_task(TaskType.DIRECT_INFERENCE, 2)
    print(f"Typ {task.task_type} – Level {task.level}")
    print("Variablen:", task.variables)
    print("Prämissen:")
    for p_enum, p in enumerate(task.premises, start=1):
        print(f"(P{p_enum})", print_logical_pretty(p))

    solutions = all_models(task.premises, task.variables)

    print("\nLösung(en):")
    for solution in solutions:
        print(solution)

    closure = deductive_literal_closure(task.premises, task.variables)
    print(f"\nInitiale Closure (ohne Annahme): {closure}")
    