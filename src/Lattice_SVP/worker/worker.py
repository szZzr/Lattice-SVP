import zmq,asyncio, pickle as pkl
from numpy.linalg import norm
from .worker_process import WorkerProcess

class Worker:
    def __init__(self, requests: dict, threads: int):
        self.requests = requests
        self.threads = threads
        self.info = {}
        self.m_connect = None # connect to manager
        self.p_connect = None # connect to pot

        self.semaphore = asyncio.Semaphore()

    def info_gathering(self):
        '''
        Collect information for the task's procedure

        This method implements the Publish-Subscribe pattern of
        zmq, according with that connects with manager's secretary
        node which one is a publisher, and subscribes information about
        following task processing. The information includes a dictionary
        with the following details
        Boost1: ( B,M, norms, R, n )
        these details equiped the processing method which follows.
        :return:
        '''
        context = zmq.Context()
        info_channel = context.socket(zmq.SUB)
        info_channel.connect(self.requests['secretary'])
        info_channel.setsockopt_string(zmq.SUBSCRIBE, '')
        self.info = pkl.loads(info_channel.recv())

    def task_processing(self, task: bytes) -> bytes:
        '''
        Enumeration procedure to find the SVP.

        This method invokes the core of the Schnorr and Euchner
        algorithm. The enumeration algorithm has implemented in
        cython module using parallel processing this module setting
        up in the present method.
        :param task: Serialized task's parameters
        :type task: bytes
        :return:
        '''
        result = WorkerProcess.intro(self.threads,
                                     self.info['B'],
                                     self.info['M'],
                                     self.info['norms'],
                                     self.info['R'],
                                     self.info['n'],
                                     boost2=task)
        return result

    def connect(self, Context):
        context = Context() # zmq.Context()
        self.m_connect  = context.socket(zmq.PULL)
        self.m_connect.connect(self.requests['manager'])
        self.p_connect = context.socket(zmq.PUSH)
        self.p_connect.connect(self.requests['pot'])

    async def receive(self):
        await self.semaphore.acquire()
        atask = await self.m_connect.recv()
        print('I RECEIVED')
        self.semaphore.release()
        return atask

    async def atask_assignment(self):
        '''
        Collects tasks and sends the results to pot

        First of all this method established the communication
        between worker-manager and worker-pot according with zmq
        pattern pipeline. After all gets each task from the manager
        accomplish each one and set the results to the pot, this
        procedure repeated infinitely.
        '''
        try:
            # loop = asyncio.get_event_loop()
            id = 1
            while True:
                atask = await asyncio.wait_for(self.m_connect.recv(), timeout=0.1)
                print(f"{''.join(['-' for i in range(30)])}")
                print(f"Task-{id} has received.")
                result = self.task_processing(atask)
                # result = loop.run_in_executor(None, self.task_processing, atask)
                await self.p_connect.send(result)
                print(f'--|Result: {pkl.loads(result)}' )
                print(f"{''.join(['-' for i in range(30)])}\n")
                id += 1
                # atask = await asyncio.wait_for(self.m_connect.recv(), timeout=1)
                print('Next job press Enter')
                input()
        except asyncio.TimeoutError:
            print("--- No more tasks! ---")

    def task_assignment(self):
        '''
        Collects tasks and sends the results to pot

        First of all this method established the communication
        between worker-manager and worker-pot according with zmq
        pattern pipeline. After all gets each task from the manager
        accomplish each one and set the results to the pot, this
        procedure repeated infinitely.
        '''
        id = 1
        while True:
            task = self.m_connect.recv()
            print(f"{''.join(['-' for i in range(30)])}")
            print(f"Task-{id} has received.")
            result = self.task_processing(task)
            self.p_connect.send(result)
            print(f'--|Result: {pkl.loads(result)}' )
            print(f"{''.join(['-' for i in range(30)])}\n")
            id += 1

    def test(self, boost1: bytes, boost2: list):
        """
        Testing module with standard inputs

        This method just test the cython module WorkerProcess
        given the standard serialized inputs.
        :param boost1: Serialize dictionary with these data ( B,M, norms, R, n )
        :type boost1: bytes
        :param boost2: A list with serialized tasks
        :type boost2: list
        :return:
        """
        self.info = pkl.loads(boost1)
        results = []
        for i, b2 in enumerate(boost2):
            print("\n--- Task", i + 1, "---")
            result = self.task_processing(b2)
            results += pkl.loads(result)
            print("\nThe reuslt: ", result,"\n\n")

        results.sort(key=lambda lb: norm(lb))
        it = iter(results)
        best = next(it)
        while norm(best) == 0:
            best = next(it)
        print("\n\n===Results===\n", results)
        print("\n\nThe best one: ", norm(best))
        return norm(best)
