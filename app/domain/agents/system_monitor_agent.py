import psutil, time
from datetime import datetime

class Agent:

    def stop(self):
        pass

class SystemMonitorAgent(Agent):

    def __init__(self):
        self.sleep_time = 0.1
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            # Calling psutil.cpu_precent() for 5 seconds
            cpu_percent = psutil.cpu_percent(5)
            print(f'The CPU usage is: {(datetime.now(), cpu_percent)}')

            # Getting usage of virtual_memory
            memory = psutil.virtual_memory()
            print(f'RAM memory. Available: {memory[1] / 1000000000} GB | % used: {memory[2]}')

            time.sleep(self.sleep_time)

    def stop(self):
        self.running = False