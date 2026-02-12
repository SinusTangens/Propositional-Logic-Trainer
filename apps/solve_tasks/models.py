from django.db import models
from django.conf import settings


class SolutionCache(models.Model):
	"""Optionaler Cache für Solver-Ergebnisse einer konkreten Task-Konfiguration.

	Hilfreich, falls das Lösen teuer ist und wiederverwendet werden kann.
	"""

	task_id = models.IntegerField(help_text="ID der Task")
	solver_name = models.CharField(max_length=100, help_text="z.B. 'marginal_solver'")
	result = models.JSONField()
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Solution Cache"
		verbose_name_plural = "Solution Caches"
		indexes = [models.Index(fields=["task_id", "solver_name"])]

	def __str__(self):
		return f"Cache task={self.task_id} solver={self.solver_name}"
