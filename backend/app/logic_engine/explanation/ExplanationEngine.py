import os
import sys
from typing import Dict, Any, Optional
from sympy import Symbol


current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
if app_dir not in sys.path:
    sys.path.append(app_dir)

from solver.MarginalSolver import BucketElimination
from solver.BooleanTable import BooleanTable
from StudentInput import StudentInput




class ExplanationEngine:
    def __init__(self, solver: 'BucketElimination'):
        self.solver = solver
        # Sicherstellen, dass der Solver gelaufen ist
        if not self.solver.is_solved:
            self.solver.solve()
        
        # Die korrekte Lösung abrufen (Wahr/Falsch/None)
        self.correct_solution = self.solver.get_solution()

    def generate_feedback(self, variable: Symbol, student_input: StudentInput) -> str:
        """
        Hauptmethode: Vergleicht Eingabe mit Lösung und generiert Feedback.
        """
        # 1. Was ist die logische Realität?
        solutions = self.correct_solution

        if solutions is None:
             return "Das System enthält Widersprüche und ist nicht lösbar."

        # Jetzt weiß Pylance sicher: 'solutions' ist ein Dict, kein None.
        correct_val = solutions.get(variable)        

        # 2. Was hat der Student eingegeben?
        student_val = student_input.to_bool_or_none()

        # Fall A: Student hat recht
        if student_val == correct_val:
            return "Korrekt! Deine Schlussfolgerung stimmt exakt mit den logischen Regeln überein."

        # Fall B: Fehler Stufe 3 (Student legt sich fest, obwohl es 'Unbekannt' ist)
        if correct_val is None and student_val is not None:
            return self._explain_unnecessary_assumption(variable, student_val)

        # Fall C: Student sagt 'Unbekannt', aber es ist festgelegt (Stufe 2 - Indirekt)
        if correct_val is not None and student_val is None:
             return f"Nicht ganz. Aus den Regeln lässt sich zwingend herleiten, dass {variable} {self._fmt(correct_val)} sein muss."

        # Fall D: Harter Widerspruch (Student sagt Wahr, ist aber Falsch) - Stufe 1/2
        if correct_val != student_val:
            return f"Das stimmt nicht. Die Regeln erzwingen, dass {variable} {self._fmt(correct_val)} ist (und nicht {self._fmt(student_val)})."

        return "Unbekannter Fehler."



    def _explain_unnecessary_assumption(self, variable: Symbol, student_assertion: bool) -> str:
        """
        Erklärung für Stufe 3: Generiert ein Gegenbeispiel (Counter-Model).
        """
        # Der Student behauptet: Variable MUSS 'student_assertion' sein.
        # Wir beweisen: Variable KANN auch das GEGENTEIL ('counter_val') sein.
        counter_val = not student_assertion
        
        # Wir suchen ein konkretes Szenario (eine Belegung aller Variablen),
        # in dem unsere Variable den 'counter_val' annimmt und trotzdem alle Regeln gelten.
        scenario = self._find_consistent_scenario(variable, counter_val)
        
        if not scenario:
            # Fallback, falls wir kein Szenario finden (sollte bei correct_val=None nicht passieren)
            return f"Das ist nicht zwingend. {variable} könnte auch {self._fmt(counter_val)} sein."

        # Den Text zusammenbauen
        text = (
            f"Du hast angegeben, dass **{variable} zwingend {self._fmt(student_assertion)}** sein muss.\n"
            f"Das stimmt aber nicht. Es ist logisch möglich, dass **{variable} {self._fmt(counter_val)}** ist, "
            f"ohne dass irgendeine Regel verletzt wird.\n\n"
            f"Hier ist ein mögliches Szenario als Beweis:\n"
        )
        
        # Das Szenario schön auflisten
        scenario_strings = []
        for var, val in scenario.items():
            # Wir heben die betreffende Variable fett hervor
            val_str = "Wahr" if val else "Falsch"
            if var == variable:
                scenario_strings.append(f"- **{var}: {val_str}** (Gegenbeweis)")
            else:
                scenario_strings.append(f"- {var}: {val_str}")
        
        text += "\n".join(scenario_strings)
        text += "\n\nIn diesem Szenario sind alle Prämissen erfüllt, obwohl deine Annahme falsch ist."
        
        return text

    def _find_consistent_scenario(self, target_var: Symbol, target_val: bool) -> Dict[Symbol, bool]:
        """
        Erzeugt eine vollständige, gültige Variablenbelegung, in der target_var = target_val ist.
        Nutzt den Backward-Pass-Ansatz, aber wählt deterministisch EINE Option aus.
        """
        # 1. Start: Wir fixieren die Zielvariable auf den Gegenwert
        scenario = {target_var: target_val}
        
        # Die Löschreihenfolge rückwärts durchgehen (wie in get_solution)
        deletion_order = list(self.solver.task.variables)
        
        for var in reversed(deletion_order):
            # Wenn wir die Variable schon im Szenario haben (z.B. unsere target_var), überspringen
            if var in scenario:
                continue
                
            bucket = self.solver.history_buckets.get(var, [])
            
            if not bucket:
                # Variable ist komplett frei -> wir wählen einfach False (oder True, egal)
                scenario[var] = False 
                continue

            # Bucket kombinieren
            combined = bucket[0]
            for t in bucket[1:]:
                combined = BooleanTable.combine(combined, t)
            
            # Conditioning auf das, was wir im Szenario schon wissen
            current_view = combined
            for known_var, known_val in scenario.items():
                current_view = current_view.condition(known_var, known_val)
            
            # Jetzt schauen wir, welcher Wert für 'var' noch erlaubt ist
            can_be_true = current_view.condition(var, True).is_consistent()
            can_be_false = current_view.condition(var, False).is_consistent()
            
            # Entscheidung für das Szenario (wir brauchen nur EINEN gültigen Pfad)
            if can_be_true:
                scenario[var] = True
            elif can_be_false:
                scenario[var] = False
            else:
                # Sollte nicht passieren, wenn das System konsistent ist
                return {} 
                
        return scenario

    def _fmt(self, val: bool) -> str:
        """Kleiner Helfer für schöne Textausgabe"""
        return "Wahr" if val else "Falsch"