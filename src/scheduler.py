import schedule
import time
from datetime import datetime, time as dt_time
from typing import Callable, Optional
from .config import Config


class TaskScheduler:
    def __init__(self, config: Config):
        self.config = config.task
        self.enable_schedule = self.config.get('enable_schedule', False)
        self.cron = self.config.get('cron')
        self.start_time = self.config.get('start_time')
        self.end_time = self.config.get('end_time')
        self._is_running = False

    def is_within_time_window(self) -> bool:
        if not self.start_time or not self.end_time:
            return True
        now = datetime.now().time()
        start = datetime.strptime(self.start_time, '%H:%M').time()
        end = datetime.strptime(self.end_time, '%H:%M').time()
        return start <= now <= end

    def start(self, task_func: Callable, *args, **kwargs):
        if not self.enable_schedule:
            return

        if self.cron:
            parts = self.cron.split()
            if len(parts) == 5:
                schedule.every().minute.do(task_func, *args, **kwargs)
            elif len(parts) == 6 or len(parts) == 7:
                schedule.every().minute.do(task_func, *args, **kwargs)

        self._is_running = True
        self._run_scheduler(task_func, *args, **kwargs)

    def _run_scheduler(self, task_func: Callable, *args, **kwargs):
        while self._is_running:
            if self.is_within_time_window():
                schedule.run_pending()
            time.sleep(1)

    def stop(self):
        self._is_running = False
        schedule.clear()

    def run_now(self, task_func: Callable, *args, **kwargs):
        task_func(*args, **kwargs)

    def set_cron(self, cron_expression: str):
        self.cron = cron_expression
        schedule.clear()
        if cron_expression:
            parts = cron_expression.split()
            if len(parts) >= 5:
                schedule.every().minute.do(lambda: None)
