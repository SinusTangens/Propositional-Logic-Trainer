"""
Worker-Modul für parallele Task-Generierung.

Dieses Modul wird von prefill_tasks.py importiert und enthält die Worker-Funktion
für ProcessPoolExecutor. Es darf KEINE Django-Imports auf Modul-Ebene haben,
da es in gespawnten Prozessen vor django.setup() importiert wird.
"""


def worker_wrapper(task_type: str, level: int, progress_queue):
    """Wrapper für den Worker-Prozess - fängt Exceptions ab"""
    try:
        refill_worker(task_type, level, progress_queue)
    except Exception as e:
        progress_queue.put({
            'type': 'error',
            'task_type': task_type,
            'level': level,
            'error': str(e)
        })


def refill_worker(task_type: str, level: int, progress_queue=None) -> dict:
    """
    Worker-Funktion für parallele Ausführung.
    Wird in separatem Prozess ausgeführt.
    
    Args:
        task_type: String-Name des TaskType
        level: Level-Nummer
        progress_queue: Optional - Queue für Live-Fortschrittsupdates
    
    WICHTIG: Alle Django-Imports müssen INNERHALB dieser Funktion sein,
    da auf Windows "spawn" verwendet wird und django.setup() zuerst
    aufgerufen werden muss.
    """
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logic_trainer.settings')
    
    import django
    django.setup()
    
    from apps.generate_tasks.services import (
        task_pregeneration_service, 
        TARGET_TASKS_PER_COMBINATION,
        MAX_RETRIES_PER_TASK
    )
    from apps.generate_tasks.models import Task
    from core.task_generator.Task import TaskType
    from core.task_generator.generate_tasks import TaskGenerator, print_logical_pretty
    from sympy import srepr
    
    before = task_pregeneration_service.count_total_tasks(task_type, level)
    to_generate = task_pregeneration_service.get_refill_count(task_type, level)
    
    # Sende initialen Status
    if progress_queue:
        progress_queue.put({
            'type': 'start',
            'task_type': task_type,
            'level': level,
            'before': before,
            'to_generate': to_generate,
            'target': TARGET_TASKS_PER_COMBINATION
        })
    
    if to_generate == 0:
        if progress_queue:
            progress_queue.put({
                'type': 'done',
                'task_type': task_type,
                'level': level,
                'generated': 0,
                'skipped': True
            })
        return {
            'task_type': task_type,
            'level': level,
            'before': before,
            'generated': 0,
            'skipped': True
        }
    
    # Generiere Tasks einzeln mit Fortschrittsmeldung
    generator = task_pregeneration_service.generator
    generated = 0
    
    try:
        tt = TaskType[task_type]
    except KeyError:
        if progress_queue:
            progress_queue.put({
                'type': 'error',
                'task_type': task_type,
                'level': level,
                'error': f'Ungültiger TaskType: {task_type}'
            })
        return {
            'task_type': task_type,
            'level': level,
            'before': before,
            'generated': 0,
            'skipped': False,
            'error': f'Ungültiger TaskType: {task_type}'
        }
    
    for i in range(to_generate):
        # Versuche mit Retries
        success = False
        for retry in range(MAX_RETRIES_PER_TASK):
            try:
                task = generator.generate_task(tt, level)
                premises_str = [print_logical_pretty(p) for p in task.premises]
                premises_sympy = [srepr(p) for p in task.premises]
                variables_str = [str(v) for v in task.variables]
                
                Task.objects.create(
                    task_type=tt.name,
                    level=level,
                    premises=premises_str,
                    premises_sympy=premises_sympy,
                    variables=variables_str
                )
                generated += 1
                success = True
                break
            except RuntimeError:
                if retry < MAX_RETRIES_PER_TASK - 1:
                    continue
            except Exception:
                break
        
        # Sende Fortschrittsupdate nach jeder erfolgreichen Generierung
        if progress_queue and success:
            progress_queue.put({
                'type': 'progress',
                'task_type': task_type,
                'level': level,
                'generated': generated,
                'total': to_generate
            })
    
    after = task_pregeneration_service.count_total_tasks(task_type, level)
    
    # Sende Abschluss
    if progress_queue:
        progress_queue.put({
            'type': 'done',
            'task_type': task_type,
            'level': level,
            'generated': generated,
            'after': after,
            'skipped': False
        })
    
    return {
        'task_type': task_type,
        'level': level,
        'before': before,
        'generated': generated,
        'after': after,
        'skipped': False
    }
