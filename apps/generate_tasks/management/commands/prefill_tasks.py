"""
Management Command: prefill_tasks

Füllt den Task-Pool auf TARGET_TASKS_PER_COMBINATION (200) Tasks
pro task_type/level Kombination auf.

Hinweis: Tasks werden user-spezifisch verwaltet. Jeder User hat seinen
eigenen "ungelösten" Pool. Nachgenerierung erfolgt automatisch wenn ein
User alle verfügbaren Tasks eines Levels gelöst hat (Batch-Größe: 20).

Verwendung:
    python manage.py prefill_tasks              # Alle Kombinationen parallel
    python manage.py prefill_tasks --sequential # Sequenziell (eine Kombination nach der anderen)
    python manage.py prefill_tasks --status     # Nur Status anzeigen
    python manage.py prefill_tasks --type CASE_SPLIT --level 3  # Nur bestimmte Kombination
    python manage.py prefill_tasks --workers 4  # Anzahl paralleler Prozesse (Default: CPU-Kerne)
"""
import multiprocessing
from multiprocessing import Process, Queue
from queue import Empty
from django.core.management.base import BaseCommand
from tqdm import tqdm
import time

from apps.generate_tasks.services import task_pregeneration_service, TARGET_TASKS_PER_COMBINATION
from core.task_generator.Task import get_all_task_types, get_levels_for_task_type

# Worker-Funktion aus separatem Modul (keine Django-Imports auf Modul-Ebene)
from .prefill_worker import refill_worker, worker_wrapper


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
            f'Ziel: {TARGET_TASKS_PER_COMBINATION} Tasks pro Kombination\n'
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
        total_tasks = 0
        total_target = 0
        
        for s in status_list:
            total_tasks += s['total_count']
            total_target += s['target']
            
            if s['needs_refill']:
                style = self.style.WARNING
                indicator = '⚠️'
            else:
                style = self.style.SUCCESS
                indicator = '✓'
            
            self.stdout.write(style(
                f"  {indicator} {s['task_type']} Level {s['level']}: "
                f"{s['total_count']}/{s['target']} Tasks"
            ))
        
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO(
            f'Total: {total_tasks}/{total_target} Tasks'
        ))
    
    def _refill_single(self, task_type: str, level: int):
        """Füllt eine einzelne Kombination auf"""
        before = task_pregeneration_service.count_total_tasks(task_type, level)
        to_generate = task_pregeneration_service.get_refill_count(task_type, level)
        
        self.stdout.write(
            f'{task_type} Level {level}: {before} vorhanden, '
            f'generiere {to_generate}...'
        )
        
        generated = task_pregeneration_service.refill_tasks(task_type, level)
        after = task_pregeneration_service.count_total_tasks(task_type, level)
        
        self.stdout.write(self.style.SUCCESS(
            f'  → Fertig: {generated} generiert, jetzt {after} Tasks'
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
        """Füllt alle Kombinationen sequenziell auf"""
        self.stdout.write('Fülle alle Kombinationen sequenziell auf...\n')
        
        # Sammle alle Kombinationen
        combinations = []
        for task_type in get_all_task_types():
            for level in get_levels_for_task_type(task_type):
                combinations.append((task_type.name, level))
        
        total_generated = 0
        
        with tqdm(combinations, desc="Generiere Tasks", unit="Level") as pbar:
            for task_type, level in pbar:
                pbar.set_postfix_str(f"{task_type} L{level}")
                
                before = task_pregeneration_service.count_total_tasks(task_type, level)
                to_generate = task_pregeneration_service.get_refill_count(task_type, level)
                
                if to_generate > 0:
                    generated = task_pregeneration_service.refill_tasks(task_type, level)
                    total_generated += generated
        
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
        
        self._run_parallel(combinations, workers)
    
    def _run_parallel(self, combinations: list, workers: int = None):
        """Führt Refill parallel für gegebene Kombinationen aus mit Live-Fortschrittsbalken"""
        if workers is None:
            workers = min(multiprocessing.cpu_count(), len(combinations))
        
        # Queue für Fortschrittsupdates von allen Workern
        progress_queue = Queue()
        
        # Erstelle Fortschrittsbalken für jede Kombination
        bars = {}
        before_counts = {}  # Speichere initiale Task-Anzahl pro Kombination
        
        for i, (task_type, level) in enumerate(combinations):
            key = (task_type, level)
            # Kürze task_type für bessere Darstellung
            short_name = task_type[:12]
            bars[key] = tqdm(
                total=TARGET_TASKS_PER_COMBINATION,
                desc=f"{short_name} L{level}",
                position=i,
                leave=True,
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            )
            before_counts[key] = 0
        
        # Starte Worker-Prozesse (max workers gleichzeitig)
        active_processes = []
        pending = list(combinations)
        completed = set()
        total_generated = 0
        errors = []
        
        while pending or active_processes:
            # Starte neue Prozesse wenn Kapazität frei ist
            while pending and len(active_processes) < workers:
                task_type, level = pending.pop(0)
                p = Process(target=worker_wrapper, args=(task_type, level, progress_queue))
                p.start()
                active_processes.append((p, task_type, level))
            
            # Verarbeite Queue-Nachrichten (non-blocking)
            while True:
                try:
                    msg = progress_queue.get_nowait()
                    key = (msg['task_type'], msg['level'])
                    bar = bars.get(key)
                    
                    if msg['type'] == 'start':
                        # Setze initialen Wert basierend auf vorhandenen Tasks
                        before_counts[key] = msg['before']
                        if bar:
                            bar.n = msg['before']
                            bar.refresh()
                    
                    elif msg['type'] == 'progress':
                        # Aktualisiere Fortschritt: before + generated
                        if bar:
                            bar.n = before_counts[key] + msg['generated']
                            bar.refresh()
                    
                    elif msg['type'] == 'done':
                        completed.add(key)
                        if bar:
                            if msg.get('skipped'):
                                bar.n = bar.total
                            else:
                                bar.n = msg.get('after', bar.total)
                                total_generated += msg.get('generated', 0)
                            bar.refresh()
                    
                    elif msg['type'] == 'error':
                        errors.append(f"{msg['task_type']} Level {msg['level']}: {msg.get('error', 'Unknown')}")
                        completed.add(key)
                
                except Empty:
                    break  # Queue ist leer
            
            # Prüfe welche Prozesse fertig sind
            still_active = []
            for p, task_type, level in active_processes:
                if p.is_alive():
                    still_active.append((p, task_type, level))
                else:
                    p.join()
            active_processes = still_active
            
            # Kurze Pause um CPU zu schonen
            if active_processes:
                time.sleep(0.1)
        
        # Schließe alle Balken
        for bar in bars.values():
            bar.close()
        
        # Zusammenfassung
        self.stdout.write('')
        if errors:
            self.stdout.write(self.style.ERROR(f'\nFehler bei {len(errors)} Kombinationen:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Fertig: {total_generated} Tasks generiert ==='
        ))
        self._show_status()
