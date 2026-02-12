from django.db import models


class FeedbackRule(models.Model):
	"""Eine Regel, die zu einer Aufgabe passendes Feedback erzeugt.

	Beispiel: für TaskType DIRECT_INFERENCE und level 2 eine bestimmte Nachricht.
	"""

	TASK_TYPE_CHOICES = [
		("DIRECT_INFERENCE", "Direct inference"),
		("CASE_SPLIT", "Case split"),
	]

	name = models.CharField(max_length=100)
	task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
	min_level = models.IntegerField(default=1)
	max_level = models.IntegerField(default=4)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Feedback-Regel"
		verbose_name_plural = "Feedback-Regeln"

	def __str__(self):
		return f"{self.name} ({self.task_type} L{self.min_level}-{self.max_level})"
