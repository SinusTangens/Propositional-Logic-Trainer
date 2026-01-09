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
from .UserInput import UserInput




class FeedbackEngine:


    def __init__(self, solver: 'BucketElimination'):

        self.solver = solver
        if not self.solver.is_solved:
            self.solver.solve()
        
        self.correct_solution = self.solver.get_solution()


    def generate_feedback(self, variable: Symbol, student_input: UserInput) -> str:
        """
        Hauptmethode: Vergleicht Eingabe mit Lösung und generiert Feedback.
        """

        solutions = self.correct_solution

        if solutions is None:
             return "Das System enthält Widersprüche und ist nicht lösbar."

        correct_val = solutions.get(variable)        

        # Eingabe in booleans oder 'None' transformieren
        student_val = student_input.to_bool_or_none()

        # Fall A: Student hat recht
        if student_val == correct_val:
            return "Korrekt! Deine Schlussfolgerung stimmt exakt mit den logischen Regeln überein."

        # Fall B: Student legt sich fest, obwohl es 'Unbekannt' ist
        if correct_val is None and student_val is not None:
            return self._explain_unnecessary_assumption(variable, student_val)

        # Fall C: Student sagt 'Unbekannt', aber es ist festgelegt 
        if correct_val is not None and student_val is None:
             return f"Nicht ganz. Aus den Regeln lässt sich zwingend herleiten, dass {variable} {self._fmt(correct_val)} sein muss."

        # Fall D: Student sagt Wahr, ist aber Falsch
        if correct_val != student_val:
            return f"Das stimmt nicht. Die Regeln erzwingen, dass {variable} {self._fmt(correct_val)} ist (und nicht {self._fmt(student_val)})."

        return "Unbekannter Fehler."



    def _explain_unnecessary_assumption(self, variable: Symbol, student_assertion: bool) -> str:

        """
        Generierung einer Feedbackausgabe, wenn der Nutzer sich auf True/False festlegt, obwohl kein konkreter Schluss möglich ist.
        Nutzung eines Gegenbeispiels, das dem Nutzer verdeutlicht warum die Antwort nicht korrekt war.
        """
     
        counter_val = not student_assertion
        
        # Suche nach einenm konkreten Szenario, in dem die Nutzereingabe den 'counter_val' annimmt und trotzdem alle Regeln gelten (= Generierung Gegenbeispiel)
        scenario = self._find_consistent_scenario(variable, counter_val)
        
        if not scenario:
            # Fallback, falls kein Szenario gefunden wird (sollte bei correct_val=None nicht passieren)
            return f"Das ist nicht zwingend. {variable} könnte auch {self._fmt(counter_val)} sein."


        text = (
            f"Du hast angegeben, dass **{variable} zwingend {self._fmt(student_assertion)}** sein muss.\n"
            f"Das stimmt aber nicht. Es ist logisch möglich, dass **{variable} {self._fmt(counter_val)}** ist, "
            f"ohne dass irgendeine Regel verletzt wird.\n\n"
            f"Hier ist ein mögliches Szenario als Beweis:\n"
        )
        

        scenario_strings = []
        for var, val in scenario.items():

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
        
        # Die Zielvariable auf den Gegenwert fixieren
        scenario = {target_var: target_val}
        
        # Die Löschreihenfolge rückwärts durchgehen (wie in get_solution)
        deletion_order = list(self.solver.task.variables)
        
        for var in reversed(deletion_order):
            # Wenn die Variable schon im Szenario vorhanden (z.B. unsere target_var), überspringen
            if var in scenario:
                continue
                
            bucket = self.solver.history_buckets.get(var, [])
            
            if not bucket:
                # Variable ist komplett frei -> einfach False wählen (oder True, egal)
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
        """
        Kleiner Helfer für schöne Textausgabe
        """

        return "Wahr" if val else "Falsch"