"""
Evaluierungsskript 1: Aufgabengenerierung — Akzeptanzraten und Laufzeiten

Erzeugt für jede Kombination aus Aufgabentyp und Level eine konfigurierbare
Anzahl an Aufgaben und protokolliert dabei:
  - Anzahl der verworfenen Kandidaten pro akzeptierter Aufgabe
  - Generierungsdauer pro Aufgabe (in Sekunden)
  - Lösedauer des Solvers pro Aufgabe (in Sekunden)

Die Ergebnisse werden als pandas DataFrame in einer CSV-Datei gespeichert.
Jede Zeile entspricht einer generierten Aufgabe.

Verwendung:
    python eval_generation.py [--output ergebnisse.csv]
"""

import sys
import os
import time
import random
import argparse
from typing import List, Dict, Tuple, Any

import pandas as pd

# Projekt-Root zum Pfad hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(core_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sympy import symbols, srepr
from core.task_generator.generate_tasks import (
    random_formula,
    is_good_task_type_direct_inference,
    is_good_task_type_case_split,
    print_logical_pretty,
)
from core.task_generator.Task import (
    Task, TaskType, DifficultySpec, DIFFICULTY_CONFIG,
)
from core.logic_engine.solver.MarginalSolver import BucketElimination


# ============================================================================
# Konfiguration: Anzahl zu generierender Aufgaben pro Aufgabentyp und Level
# ============================================================================
SAMPLE_SIZES: Dict[Tuple[str, int], int] = {
    ("direct_inference", 1): 100,
    ("direct_inference", 2): 100,
    ("direct_inference", 3): 100,
    ("direct_inference", 4): 100,
    ("case_split", 1): 50,
    ("case_split", 2): 30,
    ("case_split", 3): 20,
}


def task_type_from_str(s: str) -> TaskType:
    return TaskType.DIRECT_INFERENCE if s == "direct_inference" else TaskType.CASE_SPLIT


def generate_task_with_metrics(
    task_type: TaskType, level: int, spec: DifficultySpec
) -> Dict[str, Any]:
    """
    Erzeugt eine einzelne gültige Aufgabe und protokolliert Metriken.
    """
    num_vars = random.randint(*spec.num_vars_range)
    var_names = ["A", "B", "C", "D", "E", "F", "G", "H"][:num_vars]
    vars_tuple = symbols(" ".join(var_names))
    task_vars = (vars_tuple,) if num_vars == 1 else list(vars_tuple)

    candidates_tried = 0
    start = time.perf_counter()

    for _ in range(50_000):
        num_premises = random.randint(*spec.num_premises_range)
        premises = [
            random_formula(task_vars, spec.max_depth, spec.allowed_ops, spec.op_weights)
            for _ in range(num_premises)
        ]
        candidates_tried += 1

        is_valid = False
        if task_type == TaskType.DIRECT_INFERENCE:
            is_valid = is_good_task_type_direct_inference(premises, list(task_vars), level)
        elif task_type == TaskType.CASE_SPLIT:
            is_valid = is_good_task_type_case_split(premises, list(task_vars))

        if is_valid:
            elapsed = time.perf_counter() - start
            task = Task(
                task_type=task_type, level=level,
                premises=premises, variables=list(task_vars),
            )
            return {
                "candidates_tried": candidates_tried,
                "generation_time_s": elapsed,
                "task": task,
            }

    elapsed = time.perf_counter() - start
    raise RuntimeError(
        f"Keine gültige Aufgabe nach 50.000 Kandidaten "
        f"({task_type.name} Level {level}, {elapsed:.1f}s)"
    )


def solve_and_measure(task: Task) -> Tuple[float, Dict]:
    """
    Löst eine Aufgabe mit dem BucketElimination-Solver und misst die Dauer.
    """
    solver = BucketElimination(task)
    start = time.perf_counter()
    solver.solve()
    solution = solver.get_solution()
    elapsed = time.perf_counter() - start
    return elapsed, solution


def serialize_solution(solution: Dict) -> str:
    """Serialisiert die Solver-Lösung als kompakten String, z.B. 'A=True;B=False;C=None'."""
    parts = []
    for var, val in solution.items():
        val_str = str(val) if val is not None else "None"
        parts.append(f"{var}={val_str}")
    return ";".join(parts)


def run_evaluation(output_path: str):
    """Hauptroutine: Generiert Aufgaben und speichert alle Metriken als DataFrame."""

    rows: List[Dict[str, Any]] = []
    total_tasks = sum(SAMPLE_SIZES.values())
    completed = 0

    for (type_str, level), n_tasks in SAMPLE_SIZES.items():
        task_type = task_type_from_str(type_str)
        spec = DIFFICULTY_CONFIG[(task_type, level)]
        combo_key = f"{type_str}_L{level}"

        print(f"\n{'='*60}")
        print(f"  {combo_key}: {n_tasks} Aufgaben generieren")
        print(f"{'='*60}")

        running_cand = []
        running_gen = []
        running_solve = []

        for i in range(n_tasks):
            try:
                result = generate_task_with_metrics(task_type, level, spec)
            except RuntimeError as e:
                print(f"  FEHLER bei Aufgabe {i+1}: {e}")
                continue

            task = result["task"]
            gen_time = result["generation_time_s"]
            candidates = result["candidates_tried"]

            solve_time, solution = solve_and_measure(task)

            running_cand.append(candidates)
            running_gen.append(gen_time)
            running_solve.append(solve_time)

            rows.append({
                "task_type": type_str,
                "level": level,
                "candidates_tried": candidates,
                "generation_time_s": round(gen_time, 6),
                "solve_time_s": round(solve_time, 6),
                "n_variables": len(task.variables),
                "n_premises": len(task.premises),
                "premises_pretty": " | ".join(print_logical_pretty(p) for p in task.premises),
                "premises_repr": " | ".join(srepr(p) for p in task.premises),
                "variables": ",".join(str(v) for v in task.variables),
                "solution": serialize_solution(solution),
            })

            completed += 1
            if (i + 1) % max(1, n_tasks // 10) == 0 or (i + 1) == n_tasks:
                avg_cand = sum(running_cand) / len(running_cand)
                avg_gen = sum(running_gen) / len(running_gen)
                avg_solve = sum(running_solve) / len(running_solve)
                print(f"  [{i+1}/{n_tasks}]  "
                      f"⌀ Kandidaten: {avg_cand:>8.1f}  "
                      f"⌀ Gen: {avg_gen:>8.4f}s  "
                      f"⌀ Solve: {avg_solve:>8.6f}s  "
                      f"(Gesamt: {completed}/{total_tasks})")

    # DataFrame erstellen und speichern
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")

    # Zusammenfassung aus dem DataFrame berechnen und anzeigen
    print(f"\n{'='*60}")
    print(f"  ZUSAMMENFASSUNG")
    print(f"{'='*60}")

    summary = df.groupby(["task_type", "level"]).agg(
        n=("candidates_tried", "count"),
        cand_mean=("candidates_tried", "mean"),
        cand_median=("candidates_tried", "median"),
        cand_min=("candidates_tried", "min"),
        cand_max=("candidates_tried", "max"),
        cand_std=("candidates_tried", "std"),
        gen_mean=("generation_time_s", "mean"),
        gen_median=("generation_time_s", "median"),
        gen_total=("generation_time_s", "sum"),
        solve_mean=("solve_time_s", "mean"),
        solve_median=("solve_time_s", "median"),
    )
    summary["acceptance_rate_pct"] = (1 / summary["cand_mean"]) * 100

    print(summary.to_string())
    print(f"\n  Gesamt: {len(df)} Aufgaben generiert")
    print(f"  Gespeichert: {output_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluierung der Aufgabengenerierung (Akzeptanzraten & Laufzeiten)"
    )
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(os.path.dirname(__file__), "eval_generation_results.csv"),
        help="Pfad für die Ergebnis-CSV-Datei",
    )
    args = parser.parse_args()
    run_evaluation(args.output)