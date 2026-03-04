"""
Worker-Modul für parallele Task-Generierung.

Dieses Modul wird von prefill_tasks.py importiert und enthält die Worker-Funktion
für ProcessPoolExecutor. Es darf KEINE Django-Imports auf Modul-Ebene haben,
da es in gespawnten Prozessen vor django.setup() importiert wird.
"""


def refill_worker(task_type: str, level: int) -> dict:
    """
    Worker-Funktion für parallele Ausführung.
    Wird in separatem Prozess ausgeführt.
    
    WICHTIG: Alle Django-Imports müssen INNERHALB dieser Funktion sein,
    da auf Windows "spawn" verwendet wird und django.setup() zuerst
    aufgerufen werden muss.
    """
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logic_trainer.settings')
    
    import django
    django.setup()
    
    # Jetzt können Django-abhängige Imports erfolgen
    from apps.generate_tasks.services import task_pregeneration_service
    
    before = task_pregeneration_service.count_unsolved_tasks(task_type, level)
    to_generate = task_pregeneration_service.get_refill_count(task_type, level)
    
    if to_generate == 0:
        return {
            'task_type': task_type,
            'level': level,
            'before': before,
            'generated': 0,
            'skipped': True
        }
    
    generated = task_pregeneration_service.refill_tasks(task_type, level)
    after = task_pregeneration_service.count_unsolved_tasks(task_type, level)
    
    return {
        'task_type': task_type,
        'level': level,
        'before': before,
        'generated': generated,
        'after': after,
        'skipped': False
    }
