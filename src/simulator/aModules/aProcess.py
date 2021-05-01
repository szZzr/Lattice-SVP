from .libs import *

class aProcess:
    PATH:str = None
    jQUEUE:janus.Queue= None
    pidQUEUE:queue.Queue = queue.Queue()
    def __init__(self, file_name:str='', display_name :str = None):
        self.path = aProcess.PATH
        self.async_q = aProcess.jQUEUE.async_q
        # self.sync_q = aProcess.jQUEUE.sync_q
        self.cmd = [file_name + '.py']
        self.name = display_name if display_name is not None else file_name
        self.display_color = ''
        self.style = ''
        self.process = None

    async def write(self, string:str): #virtual-function
        pass

    def style_display(self,string:str):
        return self.style +f'\t{self.name}:\t\t{string}'+ Style.RESET_ALL

    async def display(self):
        while not self.process.stdout.at_eof():
            output = await self.process.stdout.readline()
            string = output.decode("utf-8").strip()
            await self.async_q.put(self.display_color + f'\t{self.name}:\t{string}' + Fore.RESET)
            await self.write(string)
            #await asyncio.sleep(0.001) # NOTE: CHECK ME


    async def create_task(self):  # async_qrimported_libs
        try:
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, *self.cmd, #limit = 1024 * 1024,
                stdin=asp.PIPE, stdout=asp.PIPE, stderr=asp.STDOUT, cwd=self.path)
            await asyncio.sleep(0.1)
        except:
            print(f'\nProcess [{self.process.pid}] \'{self.name}\' has failed!')
            exit()
        finally:
            aProcess.pidQUEUE.put(self.process.pid)
        print(f"{self.name}:[{self.process.pid}]")
        await self.display()

    def terminate_processes(self):
        print(Style.RESET_ALL)
        while not aProcess.pidQUEUE.empty():
            pid = aProcess.pidQUEUE.get()
            if psutil.pid_exists(pid):
                print(f"\tkill pid: {pid}")
                psutil.Process(pid).terminate()
            aProcess.pidQUEUE.task_done()
