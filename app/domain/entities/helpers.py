from datetime import datetime

class ClockWatch:

    def __init__(self, key: str):
        self.cron = [('key', key)]
    
    def watch(self, step_name: str, method):
        start = datetime.now()
        obj = method()
        self.cron.append((step_name, (datetime.now() - start).total_seconds()))
        
        return obj