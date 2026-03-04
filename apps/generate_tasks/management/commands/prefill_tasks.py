"""
Management Command: prefill_tasks

Füllt den Task-Pool auf TARGET_TASKS_PER_COMBINATION (200) ungelöste Tasks
pro task_type/level Kombination auf.

Verwendung:
    python manage.py prefill_tasks              # Alle Kombinationen parallel
    python manage.py prefill_tasks --sequential # Sequenziell (eine Kombination nach der anderen)
    python manage.py prefill_tasks --status     # Nur Status anzeigen
    python manage.py prefill_tasks --type CASE_SPLIT --level 3  # Nur bestimmte Kombination
    python manage.py prefill_tasks --workers 4  # Anzahl paralleler Prozesse (Default: CPU-Kerne)
"""
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from django.core.management.base import BaseCommand

from apps.generate_tasks.services import task_pregeneration_service, TARGET_TASKS_PER_COMBINATION
from core.task_generator.Task import get_all_task_types, get_levels_for_task_type

# Worker-Funktion aus separatem Modul (keine Django-Imports auf Modul-Ebene)
from .prefill_worker import refill_worker


class Command(BaseCommand):
    help = 'Füllt den Task-Pool mit vorgenerierten Tasks auf'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Zeigt nur den aktuellen Status an, ohne zu generieren'
        )
        parser.add_argument(
            '--type',
            type=str,
            help='Nur bestimmten TaskType auffüllen (z.B. DIRECT_INFERENCE)'
        )
        parser.add_argument(
            '--level',
            type=int,
            help='Nur bestimmtes Level auffüllen (erfordert --type)'
        )
        parser.add_argument(
            '--sequential',
            action='store_true',
            help='Sequenzielle Ausführung statt parallel (langsamer, aber weniger Ressourcen)'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=None,
            help='Anzahl paralleler Worker-Prozesse (Default: Anzahl CPU-Kerne)'
        )

    def handle(self, *args, **options):
        show_status_only = options['status']
        filter_type = options['type']
        filter_level = options['level']
        sequential = options['sequential']
        workers = options['workers']
        
        if show_status_only:
            self._show_status()
            return
        
        self.stdout.write(self.style.NOTICE(
            f'Ziel: {TARGET_TASKS_PER_COMBINATION} ungelöste Tasks pro Kombination\n'
        ))
        
        if filter_type and filter_level:
            # Nur bestimmte Kombination (immer sequenziell)
            self._refill_single(filter_type, filter_level)
        elif filter_type:
            # Alle Levels für einen Type
            self._refill_type(filter_type, sequential, workers)
        else:
            # Alle Kombinationen
            if sequential:
                self._refill_all_sequential()
            else:
                self._refill_all_parallel(workers)
    
    def _show_status(self):
        """Zeigt den Status aller Kombinationen an"""
        self.stdout.write(self.style.HTTP_INFO('=== Task-Pool Status ===\n'))
        
        status_list = task_pregeneration_service.get_all_combinations_status()
        total_unsolved = 0
        total_target = 0
        
        for s in status_list:
            total_unsolved += s['unsolved_count']
            total_target += s['target']
            
            if s['needs_refill']:
                style = self.style.WARNING
                indicator = '⚠️'
            else:
                style = self.style.SUCCESS
                indicator = '✓'
            
            self.stdout.write(style(
                f"  {indicator} {s['task_type']} Level {s['level']}: "
                f"{s['unsolved_count']}/{s['target']} ungelöst"
            ))
        
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO(
            f'Total: {total_unsolved}/{total_target} ungelöste Tasks'
        ))
    
    def _refill_single(self, task_type: str, level: int):
        """Füllt eine einzelne Kombination auf"""
        before = task_pregeneration_service.count_unsolved_tasks(task_type, level)
        to_generate = task_pregeneration_service.get_refill_count(task_type, level)
        
        self.stdout.write(
            f'{task_type} Level {level}: {before} vorhanden, '
            f'generiere {to_generate}...'
        )
        
        generated = task_pregeneration_service.refill_tasks(task_type, level)
        after = task_pregeneration_service.count_unsolved_tasks(task_type, level)
        
        self.stdout.write(self.style.SUCCESS(
            f'  → Fertig: {generated} generiert, jetzt {after} ungelöst'
        ))
    
    def _refill_type(self, task_type: str, sequential: bool = False, workers: int = None):
        """Füllt alle Levels eines TaskTypes auf"""
        try:
            from core.task_generator.Task import TaskType
            tt = TaskType[task_type]
        except KeyError:
            self.stdout.write(self.style.ERROR(f'Ungültiger TaskType: {task_type}'))
            return
        
        levels = get_levels_for_task_type(tt)
        self.stdout.write(f'Fülle {task_type} auf (Levels: {levels})...\n')
        
        if sequential:
            for level in levels:
                self._refill_single(task_type, level)
        else:
            # Parallel für diesen TaskType
            combinations = [(task_type, level) for level in levels]
            self._run_parallel(combinations, workers)
    
    def _refill_all_sequential(self):
        """Füllt alle Kombinationen sequenziell auf (alte Methode)"""
        self.stdout.write('Fülle alle Kombinationen sequenziell auf...\n')
        
        total_generated = 0
        
        for task_type in get_all_task_types():
            self.stdout.write(self.style.HTTP_INFO(f'\n--- {task_type.name} ---'))
            
            for level in get_levels_for_task_type(task_type):
                before = task_pregeneration_service.count_unsolved_tasks(task_type.name, level)
                to_generate = task_pregeneration_service.get_refill_count(task_type.name, level)
                
                if to_generate == 0:
                    self.stdout.write(f'  Level {level}: {before} vorhanden ✓')
                    continue
                
                self.stdout.write(
                    f'  Level {level}: {before} vorhanden, generiere {to_generate}...',
                    ending=''
                )
                self.stdout.flush()
                
                generated = task_pregeneration_service.refill_tasks(task_type.name, level)
                total_generated += generated
                
                self.stdout.write(self.style.SUCCESS(f' {generated} ✓'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Fertig: {total_generated} Tasks generiert ==='
        ))
        self._show_status()
    
    def _refill_all_parallel(self, workers: int = None):
        """Füllt alle Kombinationen parallel auf"""
        # Sammle alle Kombinationen die aufgefüllt werden müssen
        combinations = []
        for task_type in get_all_task_types():
            for level in get_levels_for_task_type(task_type):
                combinations.append((task_type.name, level))
        
        if workers is None:
            workers = min(multiprocessing.cpu_count(), len(combinations))
        
        self.stdout.write(self.style.NOTICE(
            f'Starte parallele Generierung mit {workers} Worker-Prozessen...\n'
        ))
        self.stdout.write(f'Kombinationen zu verarbeiten: {len(combinations)}\n')
        
        self._run_parallel(combinations, workers)
    
    def _run_parallel(self, combinations: list, workers: int = None):
        """Führt Refill parallel für gegebene Kombinationen aus"""
        if workers is None:
            workers = min(multiprocessing.cpu_count(), len(combinations))
        
        total_generated = 0
        completed = 0
        
        # ProcessPoolExecutor für CPU-intensive SymPy-Berechnungen
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Starte alle Jobs
            futures = {
                executor.submit(refill_worker, task_type, level): (task_type, level)
                for task_type, level in combinations
            }
            
            # Verarbeite Ergebnisse sobald sie fertig sind
            for future in as_completed(futures):
                task_type, level = futures[future]
                completed += 1
                
                try:
                    result = future.result()
                    
                    if result['skipped']:
                        self.stdout.write(
                            f'[{completed}/{len(combinations)}] '
                            f'{result["task_type"]} Level {result["level"]}: '
                            f'{result["before"]} vorhanden ✓'
                        )
                    else:
                        total_generated += result['generated']
                        self.stdout.write(self.style.SUCCESS(
                            f'[{completed}/{len(combinations)}] '
                            f'{result["task_type"]} Level {result["level"]}: '
                            f'{result["generated"]} generiert '
                            f'({result["before"]} → {result["after"]})'
                        ))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'[{completed}/{len(combinations)}] '
                        f'{task_type} Level {level}: Fehler - {e}'
                    ))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Fertig: {total_generated} Tasks generiert ==='
        ))
        self._show_status()
