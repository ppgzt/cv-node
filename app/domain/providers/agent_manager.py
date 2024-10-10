import time, threading

from app.domain.agents.system_monitor_agent import SystemMonitorAgent

class AgentManager:

    def __init__(self):

        self.agents = [
            # lambda: SystemMonitorAgent()
        ]

        # run agent
        def handling(agent_name: str, factory, sleep_time: int = 0.5):
            agent = factory()
            
            while True:
                if self.event.is_set():
                    try:               
                        agent.run()
                    
                    except Exception as err:
                        print(f'{agent_name} - Unexpected {err=}, {type(err)=}')
                    
                    time.sleep(sleep_time)
                else:
                    print(f'waiting')
                    self.event.wait()
        
        self.event = threading.Event()

        self.threads = []
        for agent in self.agents:
            t = threading.Thread(target = handling, args=(f'System Monitor Agent', agent,))
            self.threads.append(t)            
            t.start()

        print('Agent monitor on')
        
    def run(self):    
        self.event.set()