"""
Evaluierungsskript 2: Korrektheit des Solvers

Lädt die von eval_generation.py erzeugte CSV-Datei und verifiziert
jede Solver-Lösung gegen SymPy als unabhängige Referenz.

Drei Prüfungen pro Aufgabe:
  A) Übereinstimmung bei Erfüllbarkeit (konsistent / inkonsistent)
  B) Konkrete Belegungen: Einsetzen der Solver-Lösung in die Originalformel
  C) Freiheitsgrade: Für jede Variable mit Solver-Ergebnis "None" wird
     geprüft, ob tatsächlich beide Wahrheitswerte möglich sind

Die Ergebnisse werden als pandas DataFrame in einer CSV-Datei gespeichert.

Verwendung:
    python eval_solver_correctness.py [--input eval_generation_results.csv]
                                      [--output eval_correctness_results.csv]
"""

import sys
import os
import time
import argparse
from typing import Dict, Any

import pandas as pd

# Projekt-Root zum Pfad hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(core_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sympy import symbols, And, Not, satisfiable, sympify
from core.task_generator.Task import Task, TaskType
from core.logic_engine.solver.MarginalSolver import BucketElimination


def reconstruct_task(row: pd.Series) -> Task:
    """Rekonstruiert ein Task-Objekt aus einer DataFrame-Zeile."""
    var_names = row["variables"].split(",")
    if len(var_names) == 1:
        task_vars = [symbols(var_names[0])]
    else:
        task_vars = list(symbols(" ".join(var_names)))

    repr_strings = row["premises_repr"].split(" | ")
    premises = [sympify(r) for r in repr_strings]

    task_type = (
        TaskType.DIRECT_INFERENCE if row["task_type"] == "direct_inference"
        else TaskType.CASE_SPLIT
    )
    return Task(
        task_type=task_type,
        level=int(row["level"]),
        premises=premises,
        variables=task_vars,
    )


def verify_single_task(task: Task) -> Dict[str, Any]:
    """
    Verifiziert eine einzelne Aufgabe: Solver-Ergebnis gegen SymPy.
    """
    result = {
        "passed": True,
        "check_A": "PASS",
        "check_B": "PASS",
        "check_C": "PASS",
        "error": "",
    }

    try:
        solver = BucketElimination(task)
        solver.solve()
        solver_solution = solver.get_solution()
        is_consistent = solver.final_consistency

        # SymPy-Referenz
        full_expr = And(*task.premises)
        sympy_models_iter = satisfiable(full_expr, all_models=True)
        sympy_models = list(sympy_models_iter)
        sympy_is_sat = sympy_models != [False]

        # --- CHECK A: Konsistenz ---
        if is_consistent != sympy_is_sat:
            result["passed"] = False
            result["check_A"] = "FAIL"
            result["error"] = (
                f"Konsistenz-Mismatch: Solver={is_consistent}, SymPy={sympy_is_sat}"
            )
            return result

        if not is_consistent:
            result["check_B"] = "SKIP"
            result["check_C"] = "SKIP"
            return result

        # --- CHECK B: Konkrete Belegungen ---
        concrete = {k: v for k, v in solver_solution.items() if v is not None}
        constrained_expr = full_expr.subs(concrete)
        check_b = satisfiable(constrained_expr)

        if check_b is False:
            result["passed"] = False
            result["check_B"] = "FAIL"
            result["error"] = (
                f"Solver-Belegung {concrete} führt zu Widerspruch in SymPy"
            )
            return result

        # --- CHECK C: Freiheitsgrade ---
        none_vars = [k for k, v in solver_solution.items() if v is None]

        if not none_vars:
            result["check_C"] = "SKIP"
            return result

        for var in none_vars:
            can_true = satisfiable(And(constrained_expr, var))
            can_false = satisfiable(And(constrained_expr, Not(var)))

            if can_true is False or can_false is False:
                result["passed"] = False
                result["check_C"] = "FAIL"
                result["error"] = (
                    f"Variable {var}: Solver sagt None, "
                    f"aber can_true={can_true is not False}, "
                    f"can_false={can_false is not False}"
                )
                return result

    except Exception as e:
        result["passed"] = False
        result["check_A"] = "ERROR"
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def run_verification(input_path: str, output_path: str):
    """Hauptroutine: Lädt Aufgaben und verifiziert jede gegen SymPy."""

    df_in = pd.read_csv(input_path, encoding="utf-8")
    print(f"  {len(df_in)} Aufgaben geladen aus {input_path}\n")

    rows = []

    for combo_key, group in df_in.groupby(["task_type", "level"]):
        type_str, level = combo_key
        n = len(group)

        print(f"{'='*60}")
        print(f"  {type_str}_L{level}: {n} Aufgaben verifizieren")
        print(f"{'='*60}")

        combo_passed = 0
        combo_failed = 0
        start = time.perf_counter()

        for idx, (_, row) in enumerate(group.iterrows()):
            task = reconstruct_task(row)
            vresult = verify_single_task(task)

            if vresult["passed"]:
                combo_passed += 1
            else:
                combo_failed += 1

            rows.append({
                "task_type": type_str,
                "level": int(level),
                "passed": vresult["passed"],
                "check_A": vresult["check_A"],
                "check_B": vresult["check_B"],
                "check_C": vresult["check_C"],
                "error": vresult["error"],
            })

            if (idx + 1) % max(1, n // 5) == 0 or (idx + 1) == n:
                print(f"  [{idx+1}/{n}]  "
                      f"Passed: {combo_passed}  Failed: {combo_failed}")

        elapsed = time.perf_counter() - start
        status = "ALLE BESTANDEN" if combo_failed == 0 else f"{combo_failed} FEHLER"
        print(f"  => {status}  ({elapsed:.2f}s)\n")

    # Ergebnis-DataFrame
    df_out = pd.DataFrame(rows)
    df_out.to_csv(output_path, index=False, encoding="utf-8")

    # Zusammenfassung
    print(f"{'='*60}")
    print(f"  ZUSAMMENFASSUNG")
    print(f"{'='*60}")

    summary = df_out.groupby(["task_type", "level"]).agg(
        n_tested=("passed", "count"),
        n_passed=("passed", "sum"),
        n_failed=("passed", lambda x: (~x).sum()),
    )
    summary["error_rate_pct"] = (summary["n_failed"] / summary["n_tested"]) * 100

    print(summary.to_string())

    total = len(df_out)
    total_passed = df_out["passed"].sum()
    total_failed = total - total_passed
    print(f"\n  Gesamt: {total} getestet  |  {total_passed} bestanden  |  {total_failed} fehlgeschlagen")
    print(f"  Fehlerrate: {100 * total_failed / total:.2f}%")
    print(f"  Gespeichert: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verifikation des Solvers gegen SymPy"
    )
    default_input = os.path.join(os.path.dirname(__file__), "eval_generation_results.csv")
    default_output = os.path.join(os.path.dirname(__file__), "eval_correctness_results.csv")

    parser.add_argument("--input", "-i", default=default_input,
                        help="Pfad zur Generierungs-CSV-Datei")
    parser.add_argument("--output", "-o", default=default_output,
                        help="Pfad für die Verifikations-CSV-Datei")
    args = parser.parse_args()
    run_verification(args.input, args.output)