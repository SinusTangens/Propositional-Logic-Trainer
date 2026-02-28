from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sympy import Symbol, sympify

from apps.generate_tasks.models import Task
from apps.users.models import UserProgress, Attempt
from .models import SolutionCache

from core.task_generator.Task import Task as CoreTask, TaskType
from core.logic_engine.solver.MarginalSolver import BucketElimination
from core.logic_engine.feedback.FeedbackEngine import FeedbackEngine
from core.logic_engine.feedback.UserInput import UserInput


def create_core_task_from_db(db_task: Task) -> CoreTask:
    """Erstellt ein CoreTask-Objekt aus einem Datenbank-Task."""
    variables = [Symbol(v) for v in db_task.variables]
    premises = [sympify(p) for p in db_task.premises_sympy]
    
    return CoreTask(
        task_type=TaskType[db_task.task_type],
        level=db_task.level,
        variables=variables,
        premises=premises
    )


def get_cached_solution(task_id: int) -> dict | None:
    """Prüft ob eine gecachte Lösung existiert."""
    cache = SolutionCache.objects.filter(
        task_id=task_id,
        solver_name='bucket_elimination'
    ).first()
    
    if cache:
        return cache.result
    return None


def cache_solution(task_id: int, solution: dict, user=None):
    """Speichert eine Lösung im Cache."""
    SolutionCache.objects.update_or_create(
        task_id=task_id,
        solver_name='bucket_elimination',
        defaults={
            'result': solution,
            'created_by': user if user and user.is_authenticated else None
        }
    )


class SolveTaskView(APIView):
    """
    Endpoint zum Lösen einer Aufgabe.
    
    POST /api/solve/
    {
        "task_id": 1,
        "answers": {
            "A": "wahr",      // "wahr", "falsch", "kein"
            "B": "falsch"
        }
    }
    
    Returns:
    {
        "is_correct": true/false,
        "results": {
            "A": { "user_answer": "wahr", "correct_answer": "wahr", "is_correct": true },
            "B": { "user_answer": "falsch", "correct_answer": "falsch", "is_correct": true }
        },
        "all_correct": true/false,
        "progress": { ... }  // Wenn eingeloggt
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task_id = request.data.get('task_id')
        user_answers = request.data.get('answers', {})
        
        if not task_id:
            return Response(
                {'error': 'task_id erforderlich'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Task laden
        try:
            db_task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': f'Task mit ID {task_id} nicht gefunden'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prüfen ob gecachte Lösung existiert
        cached = get_cached_solution(task_id)
        
        if cached:
            correct_solution = cached
        else:
            # Task in CoreTask konvertieren und lösen
            try:
                core_task = create_core_task_from_db(db_task)
                solver = BucketElimination(core_task)
                solver.solve()
                raw_solution = solver.get_solution()
                
                if raw_solution is None:
                    # Widersprüchliches System
                    correct_solution = {str(v): 'contradiction' for v in core_task.variables}
                else:
                    # Lösung in String-Format konvertieren (Python-Begriffe: True/False/None)
                    correct_solution = {}
                    for var, val in raw_solution.items():
                        if val is True:
                            correct_solution[str(var)] = 'True'
                        elif val is False:
                            correct_solution[str(var)] = 'False'
                        else:  # None = Unbekannt
                            correct_solution[str(var)] = 'None'
                
                # Lösung cachen
                cache_solution(task_id, correct_solution, request.user)
                
            except Exception as e:
                return Response(
                    {'error': f'Fehler beim Lösen: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Antworten vergleichen
        results = {}
        all_correct = True
        
        for var_name in db_task.variables:
            user_answer = user_answers.get(var_name, '')
            correct_answer = correct_solution.get(var_name, 'None')
            
            is_var_correct = user_answer == correct_answer
            if not is_var_correct:
                all_correct = False
            
            results[var_name] = {
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_var_correct
            }
        
        user = request.user
        progress_update = None
        
        # Statistiken und Progress aktualisieren
        user.total_solved += 1
        if all_correct:
            user.correct_solved += 1
            # Globale Streak erhöhen (seitenübergreifend)
            user.current_streak += 1
            # Highscore aktualisieren wenn neue Bestleistung
            if user.current_streak > user.highscore_streak:
                user.highscore_streak = user.current_streak
        else:
            # Bei falscher Antwort: globale Streak zurücksetzen
            user.current_streak = 0
        user.save()
        
        # Progress aktualisieren (Level-spezifisch)
        progress_obj, created = UserProgress.objects.get_or_create(
            user=user,
            task_type=db_task.task_type
        )
        progress_update = progress_obj.record_answer(all_correct)
        
        # Attempt speichern
        Attempt.objects.create(
            user=user,
            task=db_task,
            solution=user_answers,
            is_correct=all_correct,
            feedback=''
        )
        
        response_data = {
            'is_correct': all_correct,
            'results': results,
            'progress': progress_update,
            'user_progress': user.get_progress(),
            'stats': {
                'totalSolved': user.total_solved,
                'correctSolved': user.correct_solved,
                'highscoreStreak': user.highscore_streak,
                'currentStreak': user.current_streak
            }
        }
        
        return Response(response_data)


class GetFeedbackView(APIView):
    """
    Endpoint zum Abrufen von detailliertem Feedback für eine Variable.
    
    POST /api/feedback/
    {
        "task_id": 1,
        "variable": "A",
        "user_answer": "wahr"
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task_id = request.data.get('task_id')
        variable_name = request.data.get('variable')
        user_answer = request.data.get('user_answer')
        
        if not all([task_id, variable_name, user_answer]):
            return Response(
                {'error': 'task_id, variable und user_answer erforderlich'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Task laden
        try:
            db_task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': f'Task mit ID {task_id} nicht gefunden'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Task in CoreTask konvertieren
            core_task = create_core_task_from_db(db_task)
            
            # Solver und FeedbackEngine erstellen
            solver = BucketElimination(core_task)
            feedback_engine = FeedbackEngine(solver)
            
            # Variable finden
            variable = Symbol(variable_name)
            
            # UserInput konvertieren (Python-Begriffe: True/False/None)
            if user_answer == 'True':
                user_input = UserInput.TRUE
            elif user_answer == 'False':
                user_input = UserInput.FALSE
            else:
                user_input = UserInput.UNKNOWN
            
            # Feedback generieren
            feedback_text = feedback_engine.generate_feedback(variable, user_input)
            
            return Response({
                'variable': variable_name,
                'feedback': feedback_text
            })
            
        except Exception as e:
            return Response(
                {'error': f'Fehler beim Generieren des Feedbacks: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetSolutionView(APIView):
    """
    Endpoint zum direkten Abrufen der Lösung einer Aufgabe.
    (Für Debug/Admin oder nach dem Lösen)
    
    GET /api/solution/{task_id}/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        try:
            db_task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': f'Task mit ID {task_id} nicht gefunden'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prüfen ob gecachte Lösung existiert
        cached = get_cached_solution(task_id)
        
        if cached:
            return Response({'solution': cached, 'cached': True})
        
        try:
            core_task = create_core_task_from_db(db_task)
            solver = BucketElimination(core_task)
            solver.solve()
            raw_solution = solver.get_solution()
            
            if raw_solution is None:
                solution = {str(v): 'contradiction' for v in db_task.variables}
            else:
                solution = {}
                for var, val in raw_solution.items():
                    if val is True:
                        solution[str(var)] = 'True'
                    elif val is False:
                        solution[str(var)] = 'False'
                    else:
                        solution[str(var)] = 'None'
            
            # Cachen
            cache_solution(task_id, solution, request.user)
            
            return Response({'solution': solution, 'cached': False})
            
        except Exception as e:
            return Response(
                {'error': f'Fehler beim Lösen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
