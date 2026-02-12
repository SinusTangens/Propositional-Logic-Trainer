import random
import math

from typing import List, Tuple, Sequence, Dict, Set

from itertools import product
from collections import deque

from core.task_generator.Task import Task, TaskType, DifficultySpec

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

    should_stop_early = (random.random() < 0.2) 
    
    if max_depth == 0 or (max_depth > 0 and should_stop_early):
        v = random.choice(vars)
        return v if random.random() < 0.5 else Not(v)

    weights_map = {op: float(op_weights.get(op, 1.0)) for op in allowed_ops}    
    ops = list(allowed_ops)
    weights = [weights_map.get(op, 1.0) for op in ops]

    # Falls alle Gewichte ungültig sind
    if all((w == 0 or math.isnan(w)) for w in weights):
        weights = [1.0] * len(weights)

    op = random.choices(ops, weights=weights, k=1)[0]
    
    if op == "not":
        return Not(random_formula(vars, max_depth -1, allowed_ops, op_weights))

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
    Liefert alle Modelle (Lösungen) der Konjunktion aller Prämissen einer Aufgabe (= bestimmt die Lösung(en) der Aufgabe)
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





def premises_connectivity_summary(premises: List[Boolean]) -> Tuple[bool, bool]:
    """
    Prüft, ob die Prämissen einen zusammenhängenden Graphen bilden. Nur zusammenhängende Prämissen bilden eine didaktisch sinnvolle Aufgabe. 
    Eine Kante existiert zwischen Pi und Pj, wenn sie gemeinsame Variablen nutzen.
    """
    n = len(premises)

    # Einzelne Prämisse ist trivialerweise "verbunden"
    if n <= 1:
        return True, True 

    # Für jede Prämisse wird ein leeres Set angelegt, in dem gespeichert wird welche Prämisse mit dieser jewiligen verbunden ist
    adj = {i: set() for i in range(n)}          
    

    # Die Variablenmenge jeder Prämisse wird in einem Set und alle Sets in einer Liste abgespeichert
    sym_sets: List[Set] = [set(p.free_symbols) for p in premises]

    # Alle Prämissen miteinander vergleichen und doppelte Vergleiche ausschließen (Nicht (P1)(P2) und (P2)(P1))
    found_edge = False
    for i in range(n):
        for j in range(i + 1, n):
            # Schnittmenge der vorkommenden Variablen der Prämissen i und j wird geprüft --> falls ein gemeinsames Element existiert wird eine Kante erzeugt 
            if not sym_sets[i].isdisjoint(sym_sets[j]):
                adj[i].add(j)
                adj[j].add(i)
                found_edge = True


    # Überprüfung, ob über gemeinsame Variablen (hier bildlich gesehen 'Kanten') eine gemeinsame Verbindung über alle Prämissen hergestellt werden
    # Wenn alle Prämissen (über Umwege) miteinander verbunden sind, ist die Aufgabe zusammenhängend und didaktisch sinnvoll und gilt als 'is_connected'
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
    
    
    return is_connected, found_edge





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
            # Klausel bereinigen basierend auf dem, was schon bekannt ist
            
            # Zerlege Klausel in Literale 
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

                else:
                    active_lits.append(lit)
            
            if clause_satisfied:
                continue
            

            # --- UNIT PROPAGATION ---

            # Wenn die Liste kein Element enthält, dann kann auf keine Variable direkt geschlossen werden
            if len(active_lits) == 0:
                return known 
            
            # Wenn ein nur einzelnes Literal in 'active_lits' existiert, dann kann daraus eine direkte Folgerung abgeleitet werden (z.B. A --> A ist wahr) 
            if len(active_lits) == 1:
                unit = active_lits[0]
                if isinstance(unit, Not):
                    s, v = unit.args[0], False
                else:
                    s, v = unit, True
                
                if s not in known:
                    known[s] = v
                    changed = True
            else:
                new_clauses.append(Or(*active_lits))
        
        cnf_clauses = new_clauses

    return known



def is_good_task_type_direct_inference(premises: List[Boolean], vars, level) -> bool:
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

    # Mindestens eine Prämisse muss 2 Variablen oder mehr enthalten (vor Allem relevant für Level 1)
    if not any(len(p.free_symbols) >= 2 for p in premises):
        return False

    # Eine Aufgabe soll keine widersprüchlichen Prämissen enthalten (=muss lösbar sein) und keine triviale Lösung besitzen (jede Variable beliebig)
    models = all_models(premises, used_vars)
    
    if len(models) == 0 or len(models) == 2**len(used_vars):
        return False
    
    # Einzelne Prämisse darf nicht zu viele Variablen erschließen (sonst ist die Aufgabe zu trivial)
    # Erst wirklich relevant für Level 3 und Level 4 Aufgaben
    for p in premises:

        p_syms = list(p.free_symbols)
        if not p_syms: 
            continue
        
        local_closure = deductive_literal_closure([p], p_syms)
        
        if len(local_closure) >= 3:
            return False



    # Ab Level 3 soll eine Prämisse nicht nur noch aus einer Variable bestehen drürfen (sonst zu trivial)
    if level >= 3:
        for p in premises:
            if isinstance(p, Symbol):
                return False
            
            if isinstance(p, Not) and isinstance(p.args[0], Symbol):
                return False
    

    #Level 2 Aufgaben sollen auf Grund des Schwierigkeitsgrades eine triviale Prämisse enthalten (z.B. (P1) A)
    if level == 2:

        has_trivial_premise = False
        for p in premises:
            if isinstance(p, Symbol) or (isinstance(p, Not) and isinstance(p.args[0], Symbol)):
                has_trivial_premise = True
                break
        
        if not has_trivial_premise:
            return False
        




    # Aus didaktischen Gründen soll bei diesem Aufgabentyp auf maximal eine Variable nicht automatisch geschlossen werden können
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
    is_connected, found_edge = premises_connectivity_summary(premises)
    if not is_connected or not found_edge:
        return False
    

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
    # Es müssen mindestens ZWEI Variable exisitieren, bei der eine Annahme zu einer Lösung und die gegenteilige Annahme zu einem Widerspruch führt
    split_useful_count = 0
    
    for v in used_vars:
        
        # Angenommen v ist Wahr
        models_true = all_models(premises + [v], used_vars)
        
        # Angenommen v ist Falsch
        models_false = all_models(premises + [Not(v)], used_vars)
        

        if (len(models_true) == 0 and len(models_false) == 1) or \
           (len(models_true) == 1 and len(models_false) == 0):
            split_useful_count =+ 1
            break
            
    if split_useful_count > 1:
        return False 


    # Eine Aufgabe soll keine redundanten Prämissen enthalten
    # Wenn die Anzahl der möglichen Lösungen beim Entfernen einer Prämisse gleich bleibt, war diese redundant
    for i in range(len(premises)):
        subset_premises = premises[:i] + premises[i+1:]
        subset_models = all_models(subset_premises, used_vars)
        
        if len(subset_models) == len(models):
            return False


    # Alle Prämissen sollen eine zusammenhängende Aufgabe bilden und nicht unabhängig voneinander existieren
    is_connected, found_edge = premises_connectivity_summary(premises)
    if not is_connected or not found_edge:
        return False


    return True




class TaskGenerator:
    """
    Klasse für die Erstellung eines Aufgabengenerators auf Basis vordefinierter Regeln
    """

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
        for _ in range(20000):
            num_premises = random.randint(*spec.num_premises_range)
            premises = [
                random_formula(vars, spec.max_depth, spec.allowed_ops, spec.op_weights)
                for _ in range(num_premises)
            ]

            if task_type == TaskType.DIRECT_INFERENCE:
                if is_good_task_type_direct_inference(premises, list(vars), level):
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

    