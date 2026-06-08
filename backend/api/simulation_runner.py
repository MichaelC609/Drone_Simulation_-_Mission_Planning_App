#########################################################
# File: Simulation.py                                   #
# Purpose: Run SimulationEngine forever, manage         #
#   background task lifecycle, support start/stop       #     
# Requirements:                                         #
# #######################################################      

#necessary imports
import asyncio
from simulation.simulation_engine import SimulationEngine

class SimulationRunner:
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine
        self.task = None
        self.running = False

    ########################################################
    #start(): responsible for preventing duplicate starts  #
    #         and creating background tasks                #
    #returns: stores running task -- void return           #
    ########################################################
    def start(self):
        #return task if already exists
        if self.task:
            return self.task
        
        #create task
        self.task = asyncio.create_task(
            self.run()
        )

        self.running = True

    ########################################################
    #run(): executes simulation forever, advances sim time #
    #         and handles task cancellation                #
    #returns: stores running task -- void return           #
    ########################################################
    async def run(self):
        try:
            while True:
                self.simulation_engine.tick()

                await asyncio.sleep(self.simulation_engine.dt)

        except asyncio.CancelledError:
            raise

    ########################################################
    #stop(): cancels running task, awaits cleanup and      #
    #         resets the state                             #
    #async function that runs concurrently                 #
    ########################################################
    async def stop(self):
        #do nothing if there are no tasks running
        if self.task is None:
            return
        
        #cancel task and catch cancellation error
        self.task.cancel()
        try:
            await self.task

        except asyncio.CancelledError:
            pass

        #perform cleanup
        self.task = None
        self.running = False
            
