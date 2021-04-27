from . import aProcess
from .libs import *

class aWorker(aProcess):
    _WORKER = 0 #stores the definition order of workers
    def __init__(self, semaphore): # semaphore: asyncio.Semaphore
        super().__init__()
        self.cmd = ['worker/worker.py','-D']
        self.semaphore = semaphore
        self.name = 'worker-'+ str(aWorker._WORKER)
        self.display_color = Fore.CYAN
        self.style = Style.BRIGHT + self.display_color
        aWorker._WORKER += 1

    async def write(self, string:str):
        if 'Worker is ready for process press ENTER.' in string:
            # await asyncio.sleep(0.5)
            await self.async_q.put(self.style_display('I m ready...'))
            self.process.stdin.write(b'\n')
            self.semaphore.release() #Now manager can write '\n'
        if  'Next job press Enter' == string:
            await self.async_q.put(self.style_display('Go to the next job...'))
            self.process.stdin.write(b'\n')

    def thread_exec(self):
        print(f'Worker-THREAD: Is maiN? '
              f'{threading.current_thread() is threading.main_thread()}')
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.create_task())
            # loop.run_forever()
        except RuntimeError:
            print("Finish!")
        finally:
            loop.close()
