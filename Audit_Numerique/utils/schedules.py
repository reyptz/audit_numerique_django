from celery import Celery
from celery.schedules import crontab

app = Celery('tasks')
app.conf.beat_schedule = {
    'audit-daily-task': {
        'task': 'tasks.audit_transactions',
        'schedule': crontab(hour=0, minute=0),  # Tous les jours à 00h00
    },
}
