from . import aProcess
from .libs import *

class aTemp(aProcess):
    def __init__(self):  # semaphore: asyncio.Semaphore
        super().__init__('temptest', 'TEMP')
        self.display_color = Fore.LIGHTGREEN_EX
        self.loop = asyncio.new_event_loop()
        self.other_loop: asyncio.AbstractEventLoop = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()

    async def run(self):
        for i in range(4):
            await self.async_q.put(self.style_display('P-4-OK'))
            await asyncio.sleep(0.4)

    async def run_proc(self):
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, *self.cmd,
            stdin=asp.PIPE, stdout=asp.PIPE, stderr=asp.STDOUT, cwd=self.path)
        aProcess.pidQUEUE.put(self.process.pid)
        print(f"{self.name}:[{self.process.pid}]")
        # self.loop.create_task(self.display())
        print(f'dir: {dir(self.process)}')
        await asyncio.sleep(0.5)
        print('START')
        while True:
            output = await self.process.stdout.readline()
            string = output.decode("utf-8").strip()
            if len(string)>1:
                print(f'\tprint: {string}')
                self.jQUEUE.sync_q.put_nowait(string)
        # await self.process.wait()


    def show(self, loop:asyncio.AbstractEventLoop = None):
        try:
            # self.other_loop = loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.set_debug(True)
            self.loop.run_until_complete(self.run_proc())
            # self.loop.run_forever()
        except RuntimeError:
            print("Finish!")

