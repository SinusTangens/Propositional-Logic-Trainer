import sys
import os
import pytest
from sympy import symbols, And, Or, Not, Implies, Xor, Equivalent, satisfiable

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from core.task_generator.Task import Task, TaskType
from core.logic_engine.solver.MarginalSolver import BucketElimination





def verify_solution_against_sympy(premises, solver_solution, is_consistent):
    """
    Vergleicht das Ergebnis des eigenen BucketElimination-Solvers mit der SymPy Ground Truth.
    """


    full_expression = And(*premises)
    

    sympy_models_iter = satisfiable(full_expression, all_models=True)
    sympy_models = list(sympy_models_iter)
    sympy_is_satisfiable = (sympy_models != [False])
    
    # CHECK A: Prüft, ob sowhohl der BucketElmimination-Solver als auch der Sympy-Solver die Aufgabe als lösbar/unlösbar betrachten

    assert is_consistent == sympy_is_satisfiable, \
        f"Konsistenz-Mismatch! Solver: {is_consistent}, SymPy: {sympy_is_satisfiable}"

    if not is_consistent:
        return


    # CHECK B: Die Lösung beider Solver müssen übereinstimmen

    concrete_assignments = {k: v for k, v in solver_solution.items() if v is not None}      # Variablenbelegungen mit 'None' vorerst ignorieren 
    
    constrained_expression = full_expression.subs(concrete_assignments)     # Lösung des Solvers in die SymPy Formel einsetzen und Lösbarkeit prüfen
    check = satisfiable(constrained_expression)
    
    assert check is not False, \
        f"Die Lösung des Solvers {concrete_assignments} führt zu einem Widerspruch in SymPy!"
    

    none_vars = [k for k, v in solver_solution.items() if v is None]
    
    for var in none_vars:
        # Prüfung, ob wirklich kein konkreter Schluss möglich ist, wenn der BucketElimination-Solver 'None' ausgibt

        can_be_true = satisfiable(And(constrained_expression, var))
        
        assert can_be_true is not False, (
            f"Freedom-Check fehlgeschlagen bei Variable '{var}': "
            f"Solver sagt 'None' (beliebig), aber logisch ist 'True' unmöglich "
            f"(d.h. die Variable MÜSSTE 'False' sein), "
            f"unter den gegebenen Fixwerten: {concrete_assignments}."
        )
        
        can_be_false = satisfiable(And(constrained_expression, Not(var)))
        
        assert can_be_false is not False, (
            f"Freedom-Check fehlgeschlagen bei Variable '{var}': "
            f"Solver sagt 'None' (beliebig), aber logisch ist 'False' unmöglich "
            f"(d.h. die Variable MÜSSTE 'True' sein), "
            f"unter den gegebenen Fixwerten: {concrete_assignments}."
        )   
    




# ---  Testfälle ---

def test_simple_modus_ponens():
    """
    (P1) A -> B
    (P2) A
    """
    A, B = symbols('A B')
    premises = [Implies(A, B), A]
    vars_list = [A, B]
    
    task = Task(TaskType.DIRECT_INFERENCE, 1, premises, vars_list)
    solver = BucketElimination(task)
    solution = solver.get_solution()
    
    verify_solution_against_sympy(premises, solution, solver.final_consistency)


def test_contradiction():
    """
    (P1) A
    (P2) NICHT A
    """
    A = symbols('A')
    premises = [A, Not(A)]
    vars_list = [A]
    
    task = Task(TaskType.DIRECT_INFERENCE, 1, premises, vars_list)
    solver = BucketElimination(task)
    solution = solver.get_solution()
    
    verify_solution_against_sympy(premises, solution, solver.final_consistency)


def test_complex_chain_with_freedom():
    """
    (P1) A UND B
    (P2) B -> (C ODER D)
    """
    A, B, C, D = symbols('A B C D')
    p1 = And(A, B)
    p2 = Or(Not(B), Or(C, D))
    
    premises = [p1, p2]
    vars_list = [A, B, C, D]
    
    task = Task(TaskType.DIRECT_INFERENCE, 2, premises, vars_list)
    solver = BucketElimination(task)
    solution = solver.get_solution()
    
    verify_solution_against_sympy(premises, solution, solver.final_consistency)


def test_tautology_handling():
    """
    (P1) A ODER NICHT A 
    (P2) B
    """
    A, B = symbols('A B')
    premises = [Or(A, Not(A)), B]
    vars_list = [A, B]
    
    task = Task(TaskType.DIRECT_INFERENCE, 1, premises, vars_list)
    solver = BucketElimination(task)
    solution = solver.get_solution()
    

    
    verify_solution_against_sympy(premises, solution, solver.final_consistency)





def test_complex_case_split():
    """
    (P1) E ODER (C UND NICHT E)
    (P2) E -> (B <-> D)
    (P3) B ODER (A UND C)
    (P4) NICHT A ODER NICHT D ODER (E UND NICHT E)
    (P5) NICHT C <-> (NICHT A UND NICHT D)
    (P6) (B UND C) XOR (D ODER NICHT A)
     """
    
    A, B, C, D, E = symbols('A B C D E')
    vars_list = [A, B, C, D, E]

    p1 = Or(E, And(C, Not(E)))
    p2 = Implies(E, Equivalent(B, D))
    p3 = Or(B, And(A, C))
    p4 = Or(Not(A), Not(D), And(E, Not(E)))
    p5 = Equivalent(Not(C), And(Not(A), Not(D)))
    p6 = Xor(And(B, C), Or(D, Not(A)))

    premises = [p1, p2, p3, p4, p5, p6]

    task = Task(TaskType.CASE_SPLIT, 3, premises, vars_list)
    solver = BucketElimination(task)
    solution = solver.get_solution()

    verify_solution_against_sympy(premises, solution, solver.final_consistency)


if __name__ == "__main__":

    sys.exit(pytest.main(["-v", __file__]))