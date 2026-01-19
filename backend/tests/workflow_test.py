import sys
import os
import random


current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.task_generator.generate_tasks import TaskGenerator, print_logical_pretty
from app.task_generator.Task import TaskType, DIFFICULTY_CONFIG
from app.logic_engine.solver.MarginalSolver import BucketElimination
from app.logic_engine.feedback.FeedbackEngine import FeedbackEngine
from app.logic_engine.feedback.UserInput import UserInput




def main():
    """
    Manuelles Testen des Workflows von der Aufgabengenerierung über das algorithmische Lösen bis hin zur Feedbackgenerierung 
    """

    print("=== START INTEGRATION TEST: Workflow ===\n")

    print("1. Generiere Aufgabe...")
    try:

        task_type = random.choice([TaskType.CASE_SPLIT, TaskType.DIRECT_INFERENCE])
        if task_type is TaskType.CASE_SPLIT:
            level = random.randint(1,3)
        elif task_type is TaskType.DIRECT_INFERENCE:
            level = random.randint(1,4)
        else:
            raise ValueError("Unbekannter Aufgabentyp.")

        generator = TaskGenerator(DIFFICULTY_CONFIG) 
        task = generator.generate_task(task_type, level)    # Je nach Aufgabentyp und Level kann die Generierung etwas länger dauern
        task = generator.generate_task(TaskType.CASE_SPLIT, 3)    # Je nach Aufgabentyp und Level kann die Generierung etwas länger dauern

        
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