import sys
import os



current_dir = os.path.dirname(os.path.abspath(__file__))
logic_engine_dir = os.path.dirname(current_dir)
app_dir = os.path.dirname(logic_engine_dir)
if app_dir not in sys.path:
    sys.path.append(app_dir)

from task_generator.Task import Task, TaskType
from logic_engine.solver.BooleanTable import BooleanTable

from typing import List, Dict, Any, Tuple, Optional
import itertools
import numpy as np
from sympy import Symbol, symbols, Not, Or, And





class BucketElimination:
    """
    Implementiert den Shenoy-Shafer Algorithmus (Bucket Elimination) für aussagenlogische Aufgaben.
    Dieser Solver nutzt Boolean Arrays (Tabellen), um logische Abhängigkeiten zu verwalten.
    """

    def __init__(self, task: Task):

        self.task = task
        
        self.tables: List[BooleanTable] = self._init_tables_from_premises(task.premises)            # Initiale Umwandlung der Prämissen in boolesche Tabellen
        
        self.history_buckets: Dict[Symbol, List[BooleanTable]] = {}         # Speicher für den Deletion-Prozess (ein Bucket beinhaltet alle Tabellen, in denen die jeweilige Variable vorkommt)
        
        self.is_solved = False
        self.final_consistency: Optional[bool] = None



    def _init_tables_from_premises(self, premises) -> List[BooleanTable]:
        """
        Wandelt SymPy-Formeln in BooleanTables um.
        """

        tables = []
        
        for idx, premise in enumerate(premises):

            relevant_vars = list(premise.free_symbols)
            relevant_vars.sort(key=lambda s: s.name)
            
            n = len(relevant_vars)
            if n == 0:  # Fall sollte nicht eintreten, da der Aufgabengenerator keine konstanten Prämissen erzeugt
                
                if bool(premise): 
                    continue # True -> ignorieren
                else:
                    # False -> Widerspruchstabelle erzeugen 
                    tables.append(BooleanTable([], np.array(False), source_indices={idx}))
                    continue
            
            # Brute Force Tabelle erstellen
            dims = (2,) * n
            data = np.zeros(dims, dtype=bool)
            
            # Tabelle mit Wahrheitswerten befüllen
            for bits in itertools.product([False, True], repeat=n):
                assignment = {v: b for v, b in zip(relevant_vars, bits)}
                is_valid = bool(premise.subs(assignment))
                
                # Index berechnen (True -> 1, False -> 0)
                coords = tuple(1 if b else 0 for b in bits)
                data[coords] = is_valid
                
            tables.append(BooleanTable(relevant_vars, data, source_indices={idx}))
            
        return tables



    def solve(self):
        """
        Forward Pass (Variable Elimination):
        Füllt self.history_buckets und bestimmt die globale Lösbarkeit (final_consistency).
        """

        if self.is_solved:
            return

        current_tables = list(self.tables)
        # Löschreihenfolge: Hier einfach die Listen-Reihenfolge der Variablen.
        deletion_order = list(self.task.variables)
        
        for var in deletion_order:
            # Bucket bilden: Alle Tabellen sammeln, die 'var' enthalten
            bucket = [t for t in current_tables if var in t.variables]
            other_tables = [t for t in current_tables if var not in t.variables]
            
            if not bucket:      #Fall kann unter folgenden Bedingungen eintreten: 1. Variable wurde definiert, die in keiner der Prämissen vorkommt; 2. Durch Entstehung einer Tautologie hat sich das Problem bereits aufgelöst (current_tables leer); 3. Entstehung konstanter Widerspruchstabelle (current_tables = [False]) 
                current_tables = other_tables
                self.history_buckets[var] = []
                continue

            # Speichern für Backward Pass 
            self.history_buckets[var] = list(bucket)
            
            # Alle Tabellen im Bucket miteinander verknüpfen (= logisches UND anwenden)
            combined_t = bucket[0]
            for t in bucket[1:]:
                combined_t = BooleanTable.combine(combined_t, t)
            
            # 'var' aus der kombinierten Tabelle entfernen (= logisches ODER anwenden)
            marginalized_t = combined_t.marginalize(var)
            
            # Neue Tabelle speichern
            if not np.all(marginalized_t.data):         # Tabelle wird nicht gespeichert, wenn sie nur 1en enthält (enthält keine weiter nutzbaren Informationen)
                 other_tables.append(marginalized_t)
            elif not marginalized_t.is_consistent():    # 
                 # Widerspruch (T_0) muss erhalten bleiben
                 other_tables.append(marginalized_t)
            
            current_tables = other_tables
            
        self.is_solved = True
        
        # Wenn current_tables am Ende leer ist, dann ist die Aufgabe lösbar 
        if not current_tables:
            self.final_consistency = True

        else: # Falls current_tables am Ende nicht leer ist, werden die restlichen Tabellen kombiniert und geprüft, ob mindestens eine Variablenbelegung die Aufgabe erfüllt (im Normalfall ist die Aufgabe dann nicht lösbar)
            res = current_tables[0]
            for t in current_tables[1:]:
                res = BooleanTable.combine(res, t)
            self.final_consistency = res.is_consistent()



    def get_solution(self) -> Optional[Dict[Symbol, Any]]:
        """
        Backward Pass:
        Bestimmt konkrete Lösungen der Variablen oder setzt sie auf None, wenn man aus ihnen nichts konkretes schließen kann.
        """

        if not self.is_solved:
            self.solve()
            
        if self.final_consistency is False:
            return None 
            
        solution = {}
        deletion_order = list(self.task.variables)
        
        # Ermittlung der Variablenbelegung in umgekehrter Löschreihenfolge
        for var in reversed(deletion_order):
            bucket = self.history_buckets.get(var, [])
            
            if not bucket:          # Existiert kein Bucket für diese Variable hat sie keine eindeutige Wahrheitsbelegung
                solution[var] = None 
                continue

            # Bucket kombinieren
            combined = bucket[0]
            for t in bucket[1:]:
                combined = BooleanTable.combine(combined, t)
            
            # Conditioning auf bereits bekannte Werte
            current_view = combined
            for known_var, known_val in solution.items():
                if known_val is not None:
                    current_view = current_view.condition(known_var, known_val)
            
            # Prüfen was möglich ist
            can_be_true = current_view.condition(var, True).is_consistent()
            can_be_false = current_view.condition(var, False).is_consistent()
            
            if can_be_true and can_be_false:
                solution[var] = None # Beliebig
            elif can_be_true:
                solution[var] = True
            elif can_be_false:
                solution[var] = False
            else:
                # Sollte nicht passieren, wenn final_consistency=True
                raise RuntimeError(f"Inkonsistenz bei Variable {var} trotz konsistentem Solver-Status.")
                
        return solution



# if __name__ == "__main__":
#     A, B, C, D = symbols('A B C D')
#     vars_list = [A, B, C, D]

#     # Beispielaufgabe:
#     # P1: Nicht(B oder Nicht D) -> B=False, D=True impliziert
#     p1 = Not(Or(B, Not(D))) 
#     # P2: (A oder Nicht D) UND ... -> Wenn D=True, muss A=True sein
#     p2 = And(Or(A, Not(D)), Or(C, Not(D)))

#     task = Task(
#         task_type=TaskType.DIRECT_INFERENCE,
#         level=2,
#         premises=[p1, p2],
#         variables=vars_list
#     )

#     print("Starte Solver...")
#     solver = BucketElimination(task=task)
    
#     solver.solve()
#     print(f"Aufgabe ist lösbar: {solver.final_consistency}")
    
#     if solver.final_consistency:
#         sol = solver.get_solution()
#         print("Gefundene Lösung:", sol)
#         # Erwartet: A:True, B:False, D:True, C:True oder None (da C nur mit D verknüpft war)