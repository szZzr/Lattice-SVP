from . import aProcess
from .libs import *

class aManager(aProcess):
    def __init__(self,w_semaphore:asyncio.Semaphore, p_semaphore:asyncio.Semaphore,
                 no_workers:int, settings:dict):
        '''
        param settings: is a dict with flags consists terminal command.
        format of dict -> {'mode':str, 'request':int, 'dimensions':int, 'bits':int, 'blocksize':int}
        '''
        super().__init__('manager')
        self.cmd = ['-m', 'manager', '--simulate',
                    f'-B {settings["basis"].lower()}',
                    f'-R {settings["R"]}',
                    f'-{settings["mode"]} {settings["request"]}',
                    f'-d {settings["dimensions"]}',
                    f'-b {settings["bits"]}',
                    '-bs', f'{settings["blocksize"]}']
        self.w_semaphore = w_semaphore
        self.p_semaphore = p_semaphore
        self.no_workers = no_workers
        self.display_color = Fore.RED
        self.style = Style.BRIGHT + self.display_color

    async def write(self, string:str):
        if 'Press ENTER if workers are ready' in string:
            await self.async_q.put(self.style_display('\"Waiting for workers...\"'))
            for i in range(self.no_workers):
                await self.w_semaphore.acquire()
            self.process.stdin.write(b'\n')
            self.p_semaphore.release() #To open the port
            await self.async_q.put(self.style_display('\"Workers are ready...\"'))
