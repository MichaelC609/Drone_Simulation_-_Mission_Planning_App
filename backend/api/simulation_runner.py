#Responsible for starting, stopping and running the simulation in the background
#Simulation runs forever in the background

class SimulationRunner:
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine

    def start(self):
        ...

    def stop(self):
        ...

    def run(self):
        ...
