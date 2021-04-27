from . import aProcess
from .libs import *

class aSecretary(aProcess):
    def __init__(self):
        super().__init__('manager/secretary','secretary')
        self.display_color = Fore.YELLOW
