import sys
import os
import random


# Projekt-Root zum Pfad hinzufügen (für 'core.*' Imports)
current_dir = os.path.dirname(os.path.abspath(__file__))  # core/tests
core_dir = os.path.dirname(current_dir)                    # core
project_root = os.path.dirname(core_dir)                   # prop-logic-trainer
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.task_generator.generate_tasks import TaskGenerator, print_logical_pretty
from core.task_generator.Task import TaskType, DIFFICULTY_CONFIG, get_all_task_types, get_levels_for_task_type
from core.logic_engine.solver.MarginalSolver import BucketElimination
from core.logic_engine.feedback.FeedbackEngine import FeedbackEngine
from core.logic_engine.feedback.UserInput import UserInput




def main():
    """
    Manuelles Testen des Workflows von der Aufgabengenerierung über das algorithmische Lösen bis hin zur Feedbackgenerierung. 
        - Generierung einer Aufgabe (Zufälliger Aufgabentyp und Level)
        - Vorab lösen der Aufgabe mit dem Solver (Backend)
        - Simulation von Nutzerantworten und Generierung von Feedback durch die FeedbackEngine
        
        Ziel: Sicherstellen, dass alle Komponenten nahtlos zusammenarbeiten und realistische Interaktionen ermöglichen.
        Hinweis: Dieser Test ist eher als "Integrationstest" zu verstehen, da er den gesamten Workflow abdeckt. Er ist nicht automatisiert, sondern dient zur manuellen Überprüfung der Funktionalität. 

        Die Ausgabe 'None' des Solvers steht intern dafür, dass kein konkreter Schluss möglich ist, d.h. die Variable weder wahr noch falsch geschlossen werden kann
    """

    print("=== START INTEGRATION TEST: Workflow ===\n")

    print("1. Generiere Aufgabe...")
    try:

        task_types = get_all_task_types()
        task_type = random.choice(task_types)
        levels = get_levels_for_task_type(task_type)
        level = random.choice(levels)

        task_type = TaskType.CASE_SPLIT

        generator = TaskGenerator(DIFFICULTY_CONFIG) 
        task = generator.generate_task(task_type, level)    # Je nach Aufgabentyp und Level kann die Generierung etwas länger dauern

        
        if not task:
            print("Fehler: Generator konnte keine Aufgabe erstellen.")
            return

        print(f"Typ {task.task_type} – Level {task.level}")
        print(f"   Variablen: {task.variables}")
        print("   Prämissen:")
        for p_enum, p in enumerate(task.premises, start=1):
            print(f"(P{p_enum})", print_logical_pretty(p))
            
    except Exception as e:
        print(f"CRASH bei Generierung: {e}")
        return

    print("\n" + "-"*40 + "\n")


    print("2. Starte Solver (Backend)...")
    try:
        solver = BucketElimination(task)
        solver.solve()
        
        real_solution = solver.get_solution()
        
        if solver.final_consistency is False:
            print("   ACHTUNG: Generierte Aufgabe ist inkonsistent! (Bug im Generator?)")
            return
            
        print("   (Debug) Interne Lösung:", real_solution)
        
    except Exception as e:
        print(f"CRASH beim Solver: {e}")
        return

    print("\n" + "-"*40 + "\n")


    print("3. Simulation: Nutzer antwortet")
    
    explainer = FeedbackEngine(solver)


    for variable in task.variables:
        print(f"\n>> Deine Antwort für Variable '{variable}'?")
        print("   [1] Wahr")
        print("   [2] Falsch")
        print("   [3] Kein konkreter Schluss möglich")
        
        user_choice = input("   Auswahl (1-3): ").strip()
        

        student_input = None
        if user_choice == '1':
            student_input = UserInput.TRUE
        elif user_choice == '2':
            student_input = UserInput.FALSE
        elif user_choice == '3':
            student_input = UserInput.UNKNOWN
        else:
            print("   Ungültige Eingabe, überspringe...")
            continue
            

        feedback = explainer.generate_feedback(variable, student_input)
        
        print(f"\n   FEEDBACK VOM SYSTEM:\n  >> {feedback}")
        print("-" * 20)

    print("\n=== TEST ENDE ===")

if __name__ == "__main__":
    main()