import janus, asyncio, sys
from signal import SIGINT, SIGTERM
from .aModules import *
from . import cur_path

class Executor:
    PATH:str = cur_path + '/src/Lattice_SVP'
    def __init__(self, options):
        self.settings = {}
        self.processes = []
        if options.depth > options.nodes:
            self.settings['mode'],self.settings['request'] = 'D', options.depth # DEPTH
        elif options.depth < options.nodes:
            self.settings['mode'],self.settings['request'] = 'N', options.nodes  # NODES
        else:
            print(f'Mode initialization has failed.\noptions: {options}')
            return
        self.settings.update({
            'basis' : options.basis,
            'R' : options.R,
            'dimensions': options.dimensions,
            'bits': options.bits,
            'blocksize': options.blocksize
        })
            #raise Exception('Mode initialization has failed.')
        self.workers = options.workers
        self.display_q = janus.Queue()
        self.aProc_killer = None
        ### NOTE: Setup aProcess-es
        aProcess.PATH = Executor.PATH
        aProcess.jQUEUE = self.display_q

    async def close(self):
        await self.pending_tasks()
        self.aProc_killer()
        self.display_q.close()
        await asyncio.gather(self.display_q.wait_closed())
        await asyncio.sleep(0.1)

    def handler(self, sig, future:asyncio.futures):
        import time
        loop = asyncio.get_event_loop()
        print(f"\b\b\nGot signal...! Keyboard Interrupt -> {sig!s}")
        try:
            time.sleep(0.2)
            aProcess().terminate_processes()
            future.done()
            loop.stop()
            loop.remove_signal_handler(SIGTERM)
            loop.add_signal_handler(SIGINT, lambda: None)
        finally:
            print("Handler has Finished")

    async def async_show(self):
        while True:  # async_q.unfinished_tasks >0
            data = await self.display_q.async_q.get()
            print(f"{data}")
            self.display_q.async_q.task_done()
            await asyncio.sleep(0.01)

    async def pending_tasks(self):
        loop = asyncio.get_event_loop()
        pending = asyncio.Task.all_tasks(loop=loop)
        for task in pending:
            if not task.done():
                try:
                    task.cancel()
                    await task
                except asyncio.CancelledError:
                    print(f"Cancelled-Task: {task._repr_info()[1]}")

    def init_aProcesses(self):
        worker_sem = asyncio.Semaphore(0)  # Usage: Waiting for workers to load
        pot_sem = asyncio.Semaphore(0)

        ### NOTE: Create SubProcesses
        #processes = []
        print(f'settings: {self.settings}')
        manager = aManager(worker_sem, pot_sem,  # SEMAPHORES
                           no_workers=self.workers,
                           settings = self.settings)
        pot = aPot(pot_sem, self.settings['basis'])

        self.processes.append(manager.create_task())
        self.processes.append(pot.create_task())
        self.processes.append(aSecretary().create_task())
        for worker in range(self.workers):
            self.processes.append(aWorker(worker_sem).create_task())
        self.aProc_killer = manager.terminate_processes

    async def run(self, timeout:int=10):
        loop = asyncio.get_event_loop()
        self.init_aProcesses() # init self.processes
        show_task = loop.create_task(self.async_show()) # init displayer

        ### NOTE: Starting async execution
        group = asyncio.shield(asyncio.gather(show_task, *self.processes))
        for sig in (SIGTERM, SIGINT):
            loop.add_signal_handler(sig, self.handler, sig, group)
        try:
            await asyncio.wait_for(group, timeout=timeout)
        except asyncio.TimeoutError:
            print("\n\tProcesses Complete\n")
