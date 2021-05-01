from . import aProcess
from .libs import *

class aPot(aProcess):
    def __init__(self, semaphore: asyncio.Semaphore, basis:str='random'):
        # super().__init__('pot/tempPot', 'pot')
        super().__init__('pot')    
        self.cmd = ['-m', 'pot','--manual-basis',f'{basis.lower()}']
        self.semaphore = semaphore
        self.display_color = Fore.MAGENTA
        self.style = Style.BRIGHT + self.display_color

    async def write(self, string: str):
        if 'To open the pot press ENTER' in string:
            # await self.semaphore.acquire() # Waiting until workers are ready
            self.process.stdin.write(b'\n')
            await self.async_q.put(self.style_display('\t\"Pot is open...\"'))
            await asyncio.sleep(2)
